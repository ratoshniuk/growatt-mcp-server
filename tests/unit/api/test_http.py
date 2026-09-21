import httpx
import pytest

from growatt_mcp.api import GrowattAPIError, GrowattClient, GrowattError, GrowattHTTPError, GrowattTransportError
from growatt_mcp.api.http import check_api_error, clean_params
from growatt_mcp.config import Settings


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
    assert "nope" not in str(exc.value), "body must not leak into the exception message"


async def test_non_json_body_raises(client, recorder):
    recorder.respond(raw_body="<html>maintenance</html>")
    with pytest.raises(GrowattError, match="non-JSON"):
        await client.plants.list()


@pytest.mark.parametrize("exc_type", [httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError])
async def test_transport_errors_are_wrapped(exc_type):
    def boom(request: httpx.Request) -> httpx.Response:
        raise exc_type("down", request=request)

    async with GrowattClient("t", base_url="https://api.test", transport=httpx.MockTransport(boom)) as c:
        with pytest.raises(GrowattTransportError) as exc:
            await c.plants.list()
    assert exc_type.__name__ in exc.value.reason
    assert exc.value.path == "/v1/plant/list"


async def test_none_params_are_dropped(client, recorder):
    await client.plants.details(None)
    assert recorder.last.query == {}


async def test_values_are_stringified(client, recorder):
    await client.plants.energy(123, "2026-01-01", "2026-01-07", page=2, perpage=50)
    assert recorder.last.query["plant_id"] == "123"
    assert recorder.last.query["page"] == "2"


def test_clean_params_rendering():
    assert clean_params({"a": 5.0, "b": 3.3, "c": True, "d": False, "e": None, "f": "x", "g": 7}) == {
        "a": "5",
        "b": "3.3",
        "c": "1",
        "d": "0",
        "f": "x",
        "g": "7",
    }
    assert clean_params(None) is None
    assert clean_params({}) is None


@pytest.mark.parametrize("payload", [{"error_code": 0}, {"code": 0}, {"code": "0"}, {"data": 1}, [1, 2], "x", None])
def test_check_api_error_accepts_success_shapes(payload):
    check_api_error(payload, "GET", "/x")


async def test_context_manager_closes_transport(recorder):
    c = GrowattClient("t", base_url="https://api.test", transport=httpx.MockTransport(recorder))
    assert not c.is_closed
    async with c:
        await c.plants.list()
    assert c.is_closed


async def test_from_settings_forwards_everything(recorder):
    settings = Settings(token="tok", base_url="https://regional.test/", timeout=7.5)
    c = GrowattClient.from_settings(settings, transport=httpx.MockTransport(recorder))
    try:
        await c.plants.list()
    finally:
        await c.close()
    assert recorder.last.headers["token"] == "tok"
    assert recorder.last.headers["host"] == "regional.test"
    assert c._http._http.timeout.read == 7.5


def test_error_hierarchy():
    for cls in (GrowattAPIError, GrowattHTTPError, GrowattTransportError):
        assert issubclass(cls, GrowattError)
