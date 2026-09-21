import pytest

from tests.conftest import call_tool


async def test_success_returns_api_payload(app, recorder):
    recorder.respond({"error_code": 0, "error_msg": "", "data": {"count": 1}})
    assert await call_tool(app, "get_plants") == {"error_code": 0, "error_msg": "", "data": {"count": 1}}


async def test_api_error_is_returned_not_raised(app, recorder):
    recorder.respond({"error_code": 10011, "error_msg": "error_permission_denied"})
    out = await call_tool(app, "get_plants")
    assert out["error"]["type"] == "api"
    assert out["error"]["code"] == 10011
    assert out["error"]["message"] == "error_permission_denied"


async def test_http_error_is_returned_not_raised(app, recorder):
    recorder.respond({"x": 1}, status=503)
    out = await call_tool(app, "get_plants")
    assert out["error"]["type"] == "http"
    assert out["error"]["status"] == 503
    assert "x" in out["error"]["message"]


async def test_non_json_is_returned_as_client_error(app, recorder):
    recorder.respond(raw_body="<html/>")
    out = await call_tool(app, "get_plants")
    assert out["error"]["type"] == "client"


async def test_empty_plant_id_means_all(app, recorder):
    await call_tool(app, "get_plant_details", {"plant_id": ""})
    assert recorder.last.query == {}
    await call_tool(app, "get_devices", {"plant_id": ""})
    assert recorder.last.path == "/v4/new-api/queryDeviceList"


async def test_set_device_on_off_maps_bool(app, recorder):
    await call_tool(app, "set_device_on_off", {"device_sn": "SN", "device_type": "min", "turn_on": False})
    assert recorder.last.query["value"] == "0"


async def test_modify_plant_omits_empty_fields(app, recorder):
    await call_tool(app, "modify_plant", {"c_user_id": "1", "plant_id": "2"})
    assert recorder.last.query == {"c_user_id": "1", "plant_id": "2"}


async def test_get_max_batch_data_joins_list(app, recorder):
    await call_tool(app, "get_max_batch_data", {"device_sns": ["A", "B"]})
    assert recorder.last.query["maxs"] == "A,B"


async def test_set_max_parameter_value_error_propagates(app):
    with pytest.raises(Exception, match="at most"):
        await app.call_tool("set_max_parameter", {"device_sn": "A", "setting_type": "x", "values": ["1"] * 20})


async def test_register_user_forwards_all_fields(app, recorder):
    args = {
        "user_name": "bob",
        "user_password": "pw",
        "user_email": "bob@example.test",
        "user_type": 1,
        "user_country": "Portugal",
    }
    await call_tool(app, "register_user", args)
    assert recorder.last.query == {k: str(v) for k, v in args.items()}
