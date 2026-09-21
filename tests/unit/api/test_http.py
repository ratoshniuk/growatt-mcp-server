import pytest

from growatt_mcp.api import GrowattAPIError, GrowattError, GrowattHTTPError
from growatt_mcp.api.http import check_api_error


async def test_token_header_and_base_url(client, recorder):
    await client.plants.list()
    assert recorder.last.headers["token"] == "test-token"
    assert recorder.last.path == "/v1/plant/list"


async def test_v1_error_code_raises(client, recorder):
    recorder.respond({"error_code": 10011, "error_msg": "error_permission_denied", "data": None})
    with pytest.raises(GrowattAPIError) as exc:
        await client.plants.list()
    assert exc.value.code == 10011
    assert exc.value.message == "error_permission_denied"
    assert exc.value.method == "GET"
    assert exc.value.path == "/v1/plant/list"


async def test_v4_code_raises(client, recorder):
    recorder.respond({"code": 3, "message": "DEVICE_NOT_FOUND", "data": None})
    with pytest.raises(GrowattAPIError, match="DEVICE_NOT_FOUND"):
        await client.devices.last_data("SN", "min")


async def test_v4_success_is_returned(client, recorder):
    payload = {"code": 0, "message": "SUCCESSFUL_OPERATION", "data": {"min": [{"bdc1Soc": 64}]}}
    recorder.respond(payload)
    assert await client.devices.last_data("SN", "min") == payload


async def test_http_error_raises(client, recorder):
    recorder.respond({"detail": "nope"}, status=401)
    with pytest.raises(GrowattHTTPError) as exc:
        await client.plants.list()
    assert exc.value.status_code == 401
    assert "nope" in exc.value.body


async def test_non_json_body_raises(client, recorder):
    recorder.respond(raw_body="<html>maintenance</html>")
    with pytest.raises(GrowattError, match="non-JSON"):
        await client.plants.list()


async def test_none_params_are_dropped(client, recorder):
    await client.plants.details(None)
    assert recorder.last.query == {}


async def test_values_are_stringified(client, recorder):
    await client.plants.energy(123, "2026-01-01", "2026-01-07", page=2, perpage=50)
    assert recorder.last.query["plant_id"] == "123"
    assert recorder.last.query["page"] == "2"


@pytest.mark.parametrize("payload", [{"error_code": 0}, {"code": 0}, {"code": "0"}, {"data": 1}, [1, 2], "x", None])
def test_check_api_error_accepts_success_shapes(payload):
    check_api_error(payload, "GET", "/x")


def test_error_hierarchy():
    assert issubclass(GrowattAPIError, GrowattError)
    assert issubclass(GrowattHTTPError, GrowattError)
