import pytest


@pytest.mark.parametrize(("on", "expected"), [(True, "1"), (False, "0")])
async def test_set_on_off(client, recorder, on, expected):
    await client.control.set_on_off("SN", "min", on)
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/setOnOrOff")
    assert c.query == {"deviceSn": "SN", "deviceType": "min", "value": expected}


async def test_set_power(client, recorder):
    await client.control.set_power("SN", "inv", 50)
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/setPower")
    assert c.query == {"deviceSn": "SN", "deviceType": "inv", "value": "50"}


async def test_read_vpp_parameter(client, recorder):
    await client.control.read_vpp_parameter("SN", "min", "set_param_23")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/readVppParameter")
    assert c.body == {"deviceSn": "SN", "deviceType": "min", "setType": "set_param_23"}


async def test_set_vpp_parameter(client, recorder):
    await client.control.set_vpp_parameter("SN", "min", "set_param_23", "15")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/setVppParameter")
    assert c.body == {"deviceSn": "SN", "deviceType": "min", "setType": "set_param_23", "value": "15"}


async def test_set_vpp_parameter_with_plant_id(client, recorder):
    await client.control.set_vpp_parameter("SN", "sph", "set_param_1", "x", plant_id=10)
    assert recorder.last.body["plant_id"] == "10"
