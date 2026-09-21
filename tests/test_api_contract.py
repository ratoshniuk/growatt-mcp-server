"""Contract tests: the client must only send requests that exist in the pinned Postman collection.

Two things are checked:

1. The pinned collection file is byte-for-byte the one recorded in ``growatt_mcp.api_contract``.
   Updating the collection without updating the pin fails loudly, so API changes get reviewed.
2. Every request the client can send (method, path, parameter names) appears in the collection.
   Renamed or removed endpoints and parameters are caught before they reach a user.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from growatt_mcp.api_contract import API_CONTRACT
from growatt_mcp.client import GrowattClient

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / API_CONTRACT["fixture"]


# --------------------------------------------------------------------------- collection parsing


def _iter_requests(items):
    for item in items:
        if "item" in item:
            yield from _iter_requests(item["item"])
        else:
            yield item


def _endpoint_path(url) -> str | None:
    raw = url["raw"] if isinstance(url, dict) else url
    raw = raw.replace("{{baseUrl}}", "https://host")
    parts = urlsplit(raw)
    return parts.path if parts.netloc and parts.path else None


def load_collection() -> dict[tuple[str, str], set[str]]:
    """Map (METHOD, /path) -> union of accepted parameter names (query + urlencoded body)."""
    data = json.loads(FIXTURE.read_text())
    endpoints: dict[tuple[str, str], set[str]] = {}
    for item in _iter_requests(data["item"]):
        req = item["request"]
        path = _endpoint_path(req["url"])
        if path is None:
            continue
        params: set[str] = set()
        if isinstance(req["url"], dict):
            params |= {q["key"] for q in req["url"].get("query") or []}
        body = req.get("body") or {}
        params |= {p["key"] for p in body.get("urlencoded") or body.get("formdata") or []}
        endpoints.setdefault((req["method"].upper(), path), set()).update(params)
    return endpoints


@pytest.fixture(scope="module")
def collection():
    return load_collection()


# --------------------------------------------------------------------------- pin checks


def test_fixture_matches_pinned_sha256():
    actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert actual == API_CONTRACT["sha256"], (
        "The Postman collection fixture changed. Review the API diff, then update "
        "API_CONTRACT['sha256'] and API_CONTRACT['captured'] in src/growatt_mcp/api_contract.py."
    )


def test_fixture_matches_pinned_postman_id():
    data = json.loads(FIXTURE.read_text())
    assert data["info"]["_postman_id"] == API_CONTRACT["postman_id"]


def test_fixture_contains_no_real_token():
    text = FIXTURE.read_text()
    # 32 hex chars is the Growatt token format; ignore showdoc page ids, which look the same but live in URLs.
    suspicious = [
        m.group(0)
        for m in re.finditer(r"\b[0-9a-f]{32}\b", text)
        if "showdoc.com.cn/p/" not in text[max(0, m.start() - 40) : m.start()]
    ]
    assert not suspicious, f"fixture contains something that looks like an API token: {suspicious}"


# --------------------------------------------------------------------------- client vs collection


class Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, set[str]]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        params = set(request.url.params.keys())
        if request.content:
            params |= set(parse_qs(request.content.decode()).keys())
        self.calls.append((request.method.upper(), request.url.path, params))
        return httpx.Response(200, json={"code": 0, "error_code": 0, "data": {}})


def make_client(handler) -> GrowattClient:
    client = GrowattClient(token="t", base_url="https://host")
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://host")
    return client


# Every public client method with representative arguments.
CLIENT_CALLS = {
    "plant_list": lambda c: c.plant_list(),
    "plant_details": lambda c: c.plant_details("1"),
    "plant_data": lambda c: c.plant_data("1"),
    "plant_energy": lambda c: c.plant_energy("1", "2026-01-01", "2026-01-07"),
    "device_list(plant)": lambda c: c.device_list("1"),
    "device_list(all)": lambda c: c.device_list(),
    "device_info": lambda c: c.device_info("SN", "min"),
    "device_last_data": lambda c: c.device_last_data("SN", "min"),
    "device_historical_data": lambda c: c.device_historical_data("SN", "min", "2026-01-01"),
    "device_check_sn": lambda c: c.device_check_sn("SN"),
    "set_on_off": lambda c: c.set_on_off("SN", "min", 1),
    "set_power": lambda c: c.set_power("SN", "min", 50),
    "read_vpp_parameter": lambda c: c.read_vpp_parameter("SN", "min", "set_param_1"),
    "set_vpp_parameter": lambda c: c.set_vpp_parameter("SN", "min", "set_param_23", "10"),
}


@pytest.mark.parametrize("name", sorted(CLIENT_CALLS))
async def test_client_request_exists_in_collection(name, collection):
    rec = Recorder()
    client = make_client(rec)
    try:
        await CLIENT_CALLS[name](client)
    finally:
        await client.close()

    assert len(rec.calls) == 1
    method, path, params = rec.calls[0]
    assert (method, path) in collection, f"{name}: {method} {path} is not in the Postman collection"
    unknown = params - collection[(method, path)]
    assert not unknown, f"{name}: parameters {sorted(unknown)} are not documented for {method} {path}"


# Endpoints in the collection that this client intentionally does not implement.
# If Growatt adds a new endpoint to the collection, the test below fails until it is
# either implemented in client.py or listed here.
KNOWN_UNIMPLEMENTED = {
    ("POST", "/v1/user/user_register"),
    ("POST", "/v1/user/modify"),
    ("POST", "/v1/user/check_user"),
    ("GET", "/v1/user/c_user_list"),
    ("POST", "/v1/plant/add"),
    ("POST", "/v1/plant/modify"),
    ("POST", "/v1/plant/user_plant_list"),
    ("POST", "/v1/device/datalogger/add"),
    ("GET", "/v1/device/datalogger/list"),
    ("POST", "/v1/device/storage/add"),
    ("GET", "/v1/device/max/max_data_info"),
    ("POST", "/v1/maxSet"),
    ("POST", "/v1/device/max/maxs_data"),
}


async def test_every_collection_endpoint_is_implemented_or_listed(collection):
    implemented: set[tuple[str, str]] = set()
    for call in CLIENT_CALLS.values():
        rec = Recorder()
        client = make_client(rec)
        try:
            await call(client)
        finally:
            await client.close()
        implemented.add(rec.calls[0][:2])

    unaccounted = set(collection) - implemented - KNOWN_UNIMPLEMENTED
    assert not unaccounted, f"new endpoints in the collection, decide whether to implement them: {sorted(unaccounted)}"

    stale = KNOWN_UNIMPLEMENTED - set(collection)
    assert not stale, f"endpoints listed as unimplemented no longer exist in the collection: {sorted(stale)}"
