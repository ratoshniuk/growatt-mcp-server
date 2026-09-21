import pytest

from growatt_mcp.api.max import MAX_SET_PARAM_SLOTS


async def test_data_info(client, recorder):
    await client.max.data_info("MAX1")
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/device/max/max_data_info", {"device_sn": "MAX1"})


async def test_batch_data_joins_serials(client, recorder):
    await client.max.batch_data(["MAX1", "MAX2"], page_num=2)
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/device/max/maxs_data")
    assert c.query == {"pageNum": "2", "maxs": "MAX1,MAX2"}


async def test_batch_data_accepts_preformatted_string(client, recorder):
    await client.max.batch_data("MAX1,MAX2")
    assert recorder.last.query["maxs"] == "MAX1,MAX2"


async def test_set_parameter_pads_all_slots(client, recorder):
    await client.max.set_parameter("MAX1", "pv_active_p_rate", [100, 1])
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/maxSet")
    assert c.query["max_sn"] == "MAX1"
    assert c.query["type"] == "pv_active_p_rate"
    assert c.query["param1"] == "100"
    assert c.query["param2"] == "1"
    assert all(c.query[f"param{i}"] == "" for i in range(3, MAX_SET_PARAM_SLOTS + 1))
    assert f"param{MAX_SET_PARAM_SLOTS + 1}" not in c.query


async def test_set_parameter_rejects_too_many_values(client):
    with pytest.raises(ValueError, match="at most"):
        await client.max.set_parameter("MAX1", "x", ["v"] * (MAX_SET_PARAM_SLOTS + 1))
