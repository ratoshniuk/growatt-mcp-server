async def test_list_by_plant_uses_v1(client, recorder):
    await client.devices.list("10")
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/device/list", {"plant_id": "10"})


async def test_list_all_uses_v4_with_page(client, recorder):
    await client.devices.list(page=3)
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/queryDeviceList")
    assert c.body == {"page": "3"}
    assert c.query == {}


async def test_info(client, recorder):
    await client.devices.info("SN", "sph")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/queryDeviceInfo")
    assert c.body == {"deviceSn": "SN", "deviceType": "sph"}


async def test_last_data(client, recorder):
    await client.devices.last_data("SN", "min")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/queryLastData")
    assert c.body == {"deviceSn": "SN", "deviceType": "min"}


async def test_history(client, recorder):
    await client.devices.history("SN", "min", "2026-09-21")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v4/new-api/queryHistoricalData")
    assert c.body == {"deviceSn": "SN", "deviceType": "min", "date": "2026-09-21"}


async def test_check_sn(client, recorder):
    await client.devices.check_sn("SN")
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/device/check/sn", {"sn": "SN"})


async def test_list_dataloggers(client, recorder):
    await client.devices.list_dataloggers(10)
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/device/datalogger/list", {"plant_id": "10"})


async def test_add_datalogger(client, recorder):
    await client.devices.add_datalogger("42", "10", "DL1")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/device/datalogger/add")
    assert c.query == {"c_user_id": "42", "plant_id": "10", "sn": "DL1"}


async def test_add_storage(client, recorder):
    await client.devices.add_storage("42", "10", "ST1")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/device/storage/add")
    assert c.query == {"c_user_id": "42", "plant_id": "10", "sn": "ST1"}
