"""Contract tests: the client must only send requests that exist in the pinned API contract.

1. The pinned fixture is byte-for-byte the one recorded in ``growatt_mcp.api.contract``.
   Updating the fixture without updating the pin fails loudly, so API changes get reviewed.
2. Every request the client can send (method, path, parameter names and whether they travel in the
   query string or the form body) appears in the fixture. Renamed or removed endpoints and parameters
   are caught before they reach a user.
3. Every endpoint in the fixture is implemented by the client, so additions on Growatt's side surface
   as a failing test instead of going unnoticed.
4. The fixture contains parameter *names* only: no values, so no credentials or identifiers.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

import pytest

from growatt_mcp.api import API_CONTRACT, GrowattClient

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / API_CONTRACT["fixture"]

Endpoint = tuple[str, str]


def load_contract() -> dict[Endpoint, dict[str, set[str]]]:
    data = json.loads(FIXTURE.read_text())
    return {(e["method"], e["path"]): {"query": set(e["query"]), "body": set(e["body"])} for e in data["endpoints"]}


@pytest.fixture(scope="module")
def contract() -> dict[Endpoint, dict[str, set[str]]]:
    return load_contract()


# --------------------------------------------------------------------------- pin checks


def test_fixture_matches_pinned_sha256():
    actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert actual == API_CONTRACT["sha256"], (
        "The API contract fixture changed. Review the diff, then update "
        "API_CONTRACT['sha256'] and API_CONTRACT['captured'] in src/growatt_mcp/api/contract.py."
    )


def test_fixture_provenance_matches_pin():
    data = json.loads(FIXTURE.read_text())
    assert data["source"]["postman_id"] == API_CONTRACT["postman_id"]
    assert data["captured"] == API_CONTRACT["captured"]


def test_fixture_holds_names_only():
    """Only methods, paths and parameter names: nothing that could be a credential or an identifier."""
    data = json.loads(FIXTURE.read_text())
    for endpoint in data["endpoints"]:
        assert set(endpoint) == {"method", "path", "query", "body", "documented_as"}
        assert endpoint["path"].startswith("/v")
        for name in endpoint["query"] + endpoint["body"]:
            assert name.replace("_", "").isalnum(), name
            assert len(name) < 20, name


# --------------------------------------------------------------------------- client vs contract

# Every public client method with representative arguments. ``test_every_client_method_is_covered``
# fails if a method is added to the api package without an entry here.
CLIENT_CALLS: dict[str, Callable[[GrowattClient], Awaitable[object]]] = {
    "users.register": lambda c: c.users.register("u", "p", "e", 1, "NL"),
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
async def test_client_request_matches_contract(name, client, recorder, contract):
    await CLIENT_CALLS[name](client)
    assert len(recorder.calls) == 1
    call = recorder.last
    endpoint = (call.method, call.path)
    assert endpoint in contract, f"{name}: {call.method} {call.path} is not in the API contract"
    for placement in ("query", "body"):
        sent = set(getattr(call, placement))
        unknown = sent - contract[endpoint][placement]
        assert not unknown, (
            f"{name}: {placement} parameters {sorted(unknown)} not documented for {call.method} {call.path}"
        )


async def test_every_contract_endpoint_is_implemented(client, recorder, contract):
    for call in CLIENT_CALLS.values():
        await call(client)
    implemented = {(c.method, c.path) for c in recorder.calls}
    missing = set(contract) - implemented
    assert not missing, f"endpoints in the contract that the client does not implement: {sorted(missing)}"


async def test_every_client_method_is_covered():
    """Every public coroutine on every resource must appear in CLIENT_CALLS."""
    async with GrowattClient("t") as client:
        expected = set()
        for group in ("users", "plants", "devices", "control", "max"):
            resource = getattr(client, group)
            for attr in dir(resource):
                if not attr.startswith("_") and callable(getattr(resource, attr)):
                    expected.add(f"{group}.{attr}")
    covered = {name.split("(")[0] for name in CLIENT_CALLS}
    assert expected == covered
