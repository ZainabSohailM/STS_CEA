from __future__ import annotations

import uuid

import pytest
import requests

from helpers import sample_crystal

pytestmark = [pytest.mark.api]


@pytest.fixture
def created_crystal(local_api):
    payload = sample_crystal(uuid.uuid4().hex[:8])
    resp = requests.post(f"{local_api}/api/crystals", json=payload, timeout=10)
    assert resp.status_code == 201, resp.text
    record = resp.json()
    yield record
    requests.delete(f"{local_api}/api/crystals/{record['id']}", timeout=10)


# --------------------------------------------------------------------------- #
# API-01 — CREATE (POST)
# --------------------------------------------------------------------------- #
def test_api01_create_post(local_api):
    payload = sample_crystal(uuid.uuid4().hex[:8])
    resp = requests.post(f"{local_api}/api/crystals", json=payload, timeout=10)

    assert resp.status_code == 201
    body = resp.json()
    assert isinstance(body.get("id"), int)
    assert body["name"] == payload["name"]
    assert body["category"] == payload["category"]

    # State check: the new record is actually retrievable.
    read = requests.get(f"{local_api}/api/crystals/{body['id']}", timeout=10)
    assert read.status_code == 200
    assert read.json()["name"] == payload["name"]

    requests.delete(f"{local_api}/api/crystals/{body['id']}", timeout=10)


# --------------------------------------------------------------------------- #
# API-02 — READ (GET)
# --------------------------------------------------------------------------- #
def test_api02_read_get(local_api, created_crystal):
    cid = created_crystal["id"]

    one = requests.get(f"{local_api}/api/crystals/{cid}", timeout=10)
    assert one.status_code == 200
    assert one.json()["id"] == cid

    # Read all — the created record must be present in the collection.
    all_resp = requests.get(f"{local_api}/api/crystals", timeout=10)
    assert all_resp.status_code == 200
    ids = [c["id"] for c in all_resp.json()]
    assert cid in ids


# --------------------------------------------------------------------------- #
# API-03 — UPDATE (PUT)
# --------------------------------------------------------------------------- #
def test_api03_update_put(local_api, created_crystal):
    cid = created_crystal["id"]
    new_desc = "Updated by API-03 test"
    new_price = 99.99

    resp = requests.put(
        f"{local_api}/api/crystals/{cid}",
        json={"description": new_desc, "price": new_price},
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["description"] == new_desc
    assert body["price"] == new_price
    # Name must be unchanged 
    assert body["name"] == created_crystal["name"]

    # State check: re-read confirms persistence.
    read = requests.get(f"{local_api}/api/crystals/{cid}", timeout=10).json()
    assert read["description"] == new_desc
    assert read["price"] == new_price


# --------------------------------------------------------------------------- #
# API-04 — DELETE (DELETE)
# --------------------------------------------------------------------------- #
def test_api04_delete(local_api):
    payload = sample_crystal(uuid.uuid4().hex[:8])
    cid = requests.post(f"{local_api}/api/crystals", json=payload, timeout=10).json()["id"]

    resp = requests.delete(f"{local_api}/api/crystals/{cid}", timeout=10)
    assert resp.status_code == 204
    assert resp.text == ""

    read = requests.get(f"{local_api}/api/crystals/{cid}", timeout=10)
    assert read.status_code == 404


# --------------------------------------------------------------------------- #
# Negative API checks 
# --------------------------------------------------------------------------- #
@pytest.mark.negative
def test_api_create_missing_name_returns_400(local_api):
    resp = requests.post(f"{local_api}/api/crystals", json={"category": "X"}, timeout=10)
    assert resp.status_code == 400


@pytest.mark.negative
def test_api_get_unknown_id_returns_404(local_api):
    resp = requests.get(f"{local_api}/api/crystals/123456789", timeout=10)
    assert resp.status_code == 404
