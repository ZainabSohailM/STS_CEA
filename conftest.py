from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import helpers  


# --- Basic config fixtures -------------------------------------------------- #
@pytest.fixture(scope="session")
def base_url() -> str:
    return helpers.BASE_URL


# --- Playwright browser configuration --------------------------------------- #
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True,
            "viewport": {"width": 1366, "height": 900}}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, browser_name):
    if browser_name == "chromium":
        return {**browser_type_launch_args, "channel": "msedge"}
    return browser_type_launch_args


@pytest.fixture
def bc_page(page):
    from playwright.sync_api import expect as _expect
    _expect.set_options(timeout=helpers.ACTION_TIMEOUT)
    page.set_default_timeout(helpers.ACTION_TIMEOUT)
    page.set_default_navigation_timeout(helpers.NAV_TIMEOUT)
    return page


@pytest.fixture
def shot(page, request):
    """Best-effort success screenshot (never fails the test)."""
    def _take(label: str):
        safe = f"{request.node.name}_{label}".replace("/", "_")
        path = helpers.SCREENSHOTS_DIR / f"{safe}.png"
        try:
            page.screenshot(path=str(path), full_page=False, timeout=20000)
            return path
        except Exception:
            return None
    return _take


# --- Screenshot on failure -------------------------------------------------- #
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            safe = item.name.replace("/", "_").replace("[", "_").replace("]", "_")
            try:
                page.screenshot(path=str(helpers.SCREENSHOTS_DIR / f"FAILED_{safe}.png"),
                                full_page=False, timeout=15000)
            except Exception:
                pass


# --- Local test API (for the CRUD tests) ------------------------------------ #
def _free(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0


def _wait_up(url, timeout=20.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.3)
    return False


@pytest.fixture(scope="session")
def local_api():
    from urllib.parse import urlparse
    import os

    url = helpers.LOCAL_API_URL
    parsed = urlparse(url)
    proc = None
    if _free(parsed.hostname, parsed.port):
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / "local_api.py")],
            cwd=str(ROOT), env={**os.environ, "PORT": str(parsed.port)},
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    assert _wait_up(f"{url}/health"), "local test API failed to start"
    requests.post(f"{url}/reset", timeout=5)
    yield url
    if proc is not None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
