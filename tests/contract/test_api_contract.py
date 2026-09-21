"""Contract tests: the client must only send requests that exist in the pinned Postman collection.

1. The pinned collection file is byte-for-byte the one recorded in ``growatt_mcp.api.contract``.
   Updating the collection without updating the pin fails loudly, so API changes get reviewed.
2. Every request the client can send (method, path, parameter names) appears in the collection.
   Renamed or removed endpoints and parameters are caught before they reach a user.
3. Every endpoint in the collection is implemented by the client, so additions on Growatt's side
   surface as a failing test instead of going unnoticed.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from growatt_mcp.api import API_CONTRACT, GrowattClient

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / API_CONTRACT["fixture"]

Endpoint = tuple[str, str]


# --------------------------------------------------------------------------- collection parsing


def _iter_requests(items):
    for item in items:
        if "item" in item:
            yield from _iter_requests(item["item"])
        else:
            yield item


def _endpoint_path(url) -> str | None:
    raw = url["raw"] if isinstance(url, dict) else url
    parts = urlsplit(raw.replace("{{baseUrl}}", "https://host"))
    return parts.path if parts.netloc and parts.path else None


def load_collection() -> dict[Endpoint, set[str]]:
    """Map (METHOD, /path) -> union of accepted parameter names (query + urlencoded body)."""
    data = json.loads(FIXTURE.read_text())
    endpoints: dict[Endpoint, set[str]] = {}
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
def collection() -> dict[Endpoint, set[str]]:
    return load_collection()


# --------------------------------------------------------------------------- pin checks


def test_fixture_matches_pinned_sha256():
    actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert actual == API_CONTRACT["sha256"], (
        "The Postman collection fixture changed. Review the API diff, then update "
        "API_CONTRACT['sha256'] and API_CONTRACT['captured'] in src/growatt_mcp/api/contract.py."
    )


def test_fixture_matches_pinned_postman_id():
    data = json.loads(FIXTURE.read_text())
    assert data["info"]["_postman_id"] == API_CONTRACT["postman_id"]


def test_fixture_contains_no_real_token():
    """Growatt tokens are 32 lowercase base36 characters. Only the ``{{token}}`` variable may appear."""
    text = FIXTURE.read_text()
    data = json.loads(text)
    for item in _iter_requests(data["item"]):
        for header in item["request"].get("header") or []:
            if header.get("key", "").lower() == "token":
                assert header.get("value") == "{{token}}", f"literal token in request {item['name']!r}"
    for variable in data.get("variable") or []:
        if variable.get("key") == "token":
            assert variable.get("value") == "<token>"
    suspicious = [
        m.group(0)
        for m in re.finditer(r"\b[a-z0-9]{32}\b", text)
        if re.search(r"[a-z]", m.group(0))  # a bare 32-digit number is not a token
        and "showdoc.com.cn/p/" not in text[max(0, m.start() - 40) : m.start()]
    ]
    assert not suspicious, f"fixture contains something that looks like an API token: {suspicious}"


def test_fixture_contains_no_hardcoded_identifiers():
    """Serial numbers and plant ids must be Postman variables or placeholders, not real devices."""
    text = FIXTURE.read_text()
    for pattern in (r"deviceSn=(?!\{\{)[A-Z0-9]{10}", r"plant_id=(?!\{\{)\d{5,}", r'"value": "[A-Z0-9]{10}"'):
        assert re.search(pattern, text) is None, f"hardcoded identifier matches {pattern!r}"


# --------------------------------------------------------------------------- client vs collection

# Every public client method with representative arguments. Keep this in sync with the api package;
# ``test_every_client_method_is_covered`` fails if a method is added without an entry here.
CLIENT_CALLS: dict[str, Callable[[GrowattClient], Awaitable[object]]] = {
    "users.register": lambda c: c.users.register("u", "p", "e", 1, "PT"),
    "users.modify": lambda c: c.users.modify("1", "m"),
    "users.check": lambda c: c.users.check("u"),
    "users.list": lambda c: c.users.list(),
    "plants.list": lambda c: c.plants.list(),
    "plants.details": lambda c: c.plants.details("1"),
    "plants.data": lambda c: c.plants.data("1"),
    "plants.energy": lambda c: c.plants.energy("1", "2026-01-01", "2026-01-07"),
    "plants.add": lambda c: c.plants.add("1", "n", 1.0),
    "plants.modify": lambda c: c.plants.modify("1", "2", "n", "0"),
    "plants.list_for_user": lambda c: c.plants.list_for_user("u"),
    "devices.list(plant)": lambda c: c.devices.list("1"),
    "devices.list(all)": lambda c: c.devices.list(),
    "devices.info": lambda c: c.devices.info("SN", "min"),
    "devices.last_data": lambda c: c.devices.last_data("SN", "min"),
    "devices.history": lambda c: c.devices.history("SN", "min", "2026-01-01"),
    "devices.check_sn": lambda c: c.devices.check_sn("SN"),
    "devices.list_dataloggers": lambda c: c.devices.list_dataloggers("1"),
    "devices.add_datalogger": lambda c: c.devices.add_datalogger("1", "2", "SN"),
    "devices.add_storage": lambda c: c.devices.add_storage("1", "2", "SN"),
    "control.set_on_off": lambda c: c.control.set_on_off("SN", "min", True),
    "control.set_power": lambda c: c.control.set_power("SN", "min", 50),
    "control.read_vpp_parameter": lambda c: c.control.read_vpp_parameter("SN", "min", "set_param_1"),
    "control.set_vpp_parameter": lambda c: c.control.set_vpp_parameter("SN", "min", "set_param_23", "10", "1"),
    "max.data_info": lambda c: c.max.data_info("SN"),
    "max.batch_data": lambda c: c.max.batch_data(["SN"]),
    "max.set_parameter": lambda c: c.max.set_parameter("SN", "pv_active_p_rate", [100, 1]),
}


@pytest.mark.parametrize("name", sorted(CLIENT_CALLS))
async def test_client_request_exists_in_collection(name, client, recorder, collection):
    await CLIENT_CALLS[name](client)
    assert len(recorder.calls) == 1
    call = recorder.last
    endpoint = (call.method, call.path)
    assert endpoint in collection, f"{name}: {call.method} {call.path} is not in the Postman collection"
    unknown = set(call.params) - collection[endpoint]
    assert not unknown, f"{name}: parameters {sorted(unknown)} are not documented for {call.method} {call.path}"


async def test_every_collection_endpoint_is_implemented(client, recorder, collection):
    for call in CLIENT_CALLS.values():
        await call(client)
    implemented = {(c.method, c.path) for c in recorder.calls}
    missing = set(collection) - implemented
    assert not missing, f"endpoints in the collection that the client does not implement: {sorted(missing)}"


def test_every_client_method_is_covered():
    """Every public coroutine on every resource must appear in CLIENT_CALLS."""
    client = GrowattClient("t")
    expected = set()
    for group in ("users", "plants", "devices", "control", "max"):
        resource = getattr(client, group)
        for attr in dir(resource):
            if not attr.startswith("_") and callable(getattr(resource, attr)):
                expected.add(f"{group}.{attr}")
    covered = {name.split("(")[0] for name in CLIENT_CALLS}
    assert expected == covered
