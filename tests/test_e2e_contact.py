from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.crossbrowser]

INCOMPLETE_MSG = "email form is incomplete"


def _goto_contact(page, base_url):
    page.goto(base_url, wait_until="domcontentloaded")
    expect(page.locator("#contact")).to_be_visible(timeout=20000)
    page.locator("#contact").scroll_into_view_if_needed()


# --------------------------------------------------------------------------- #
# CON-01 (negative) — submitting an empty form triggers the validation alert.
# --------------------------------------------------------------------------- #
@pytest.mark.negative
def test_con01_empty_form_validation_alert(bc_page, base_url, shot):
    _goto_contact(bc_page, base_url)

    messages = []
    bc_page.on("dialog", lambda d: (messages.append(d.message), d.dismiss()))

    bc_page.click("#send-email-button", no_wait_after=True)
    bc_page.wait_for_timeout(500)
    assert any(INCOMPLETE_MSG.lower() in m.lower() for m in messages), (
        f"expected an incompleteness alert, got: {messages}"
    )
    shot("contact_validation")


# --------------------------------------------------------------------------- #
# CON-02 (positive) — a fully filled form submits; the request is stubbed so no
# real email is sent, and no validation alert is raised.
# --------------------------------------------------------------------------- #
@pytest.mark.functional
def test_con02_valid_form_submits(bc_page, base_url, shot):
    _goto_contact(bc_page, base_url)

    hit = {"count": 0}

    def handler(route):
        hit["count"] += 1
        route.fulfill(status=200, content_type="application/json", body="{}")

    # Intercept the outbound support-email call (ApiUrl.Email = /api/email).
    bc_page.route(re.compile(r"/api/email"), handler)

    dialogs = []
    bc_page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

    bc_page.fill("#name", "Test Student")
    bc_page.fill("#email", "student@example.com")
    bc_page.fill("#subject", "CEA automated functional test")
    bc_page.fill("#message", "This request was intercepted locally; no email was sent.")
    bc_page.click("#send-email-button", no_wait_after=True)
    bc_page.wait_for_timeout(1000)

    assert not any(INCOMPLETE_MSG.lower() in d.lower() for d in dialogs), (
        f"valid form should not raise the incompleteness alert: {dialogs}"
    )
    assert hit["count"] >= 1, "the support-email request should have been issued (and stubbed)"
    shot("contact_submitted")


# --------------------------------------------------------------------------- #
# CON-03 (negative) — a partially filled form (missing email+subject) is rejected.
# --------------------------------------------------------------------------- #
@pytest.mark.negative
def test_con03_partial_form_rejected(bc_page, base_url):
    _goto_contact(bc_page, base_url)

    messages = []
    bc_page.on("dialog", lambda d: (messages.append(d.message), d.dismiss()))

    bc_page.fill("#name", "Only Name Provided")
    bc_page.click("#send-email-button", no_wait_after=True)
    bc_page.wait_for_timeout(500)
    assert any(INCOMPLETE_MSG.lower() in m.lower() for m in messages), (
        f"expected an incompleteness alert for a partial form, got: {messages}"
    )
