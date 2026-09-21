async def test_list(client, recorder):
    await client.plants.list()
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/plant/list", {})


async def test_details_with_and_without_id(client, recorder):
    await client.plants.details("10")
    assert (recorder.last.method, recorder.last.path) == ("POST", "/v1/plant/details")
    assert recorder.last.query == {"plant_id": "10"}
    await client.plants.details()
    assert recorder.last.query == {}


async def test_data(client, recorder):
    await client.plants.data(10)
    c = recorder.last
    assert (c.method, c.path, c.query) == ("GET", "/v1/plant/data", {"plant_id": "10"})


async def test_energy(client, recorder):
    await client.plants.energy("10", "2026-09-15", "2026-09-21", time_unit="month", page=2, perpage=50)
    c = recorder.last
    assert (c.method, c.path) == ("GET", "/v1/plant/energy")
    assert c.query == {
        "plant_id": "10",
        "start_date": "2026-09-15",
        "end_date": "2026-09-21",
        "time_unit": "month",
        "page": "2",
        "perpage": "50",
    }


async def test_add(client, recorder):
    await client.plants.add("42", "Roof", 3.3)
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/plant/add")
    assert c.query == {"c_user_id": "42", "name": "Roof", "peak_power": "3.3"}


async def test_modify_only_sends_given_fields(client, recorder):
    await client.plants.modify("42", "10", name="Roof 2")
    assert recorder.last.query == {"c_user_id": "42", "plant_id": "10", "name": "Roof 2"}
    await client.plants.modify("42", "10", currency=0)
    assert recorder.last.query == {"c_user_id": "42", "plant_id": "10", "currency": "0"}


async def test_list_for_user(client, recorder):
    await client.plants.list_for_user("bob")
    c = recorder.last
    assert (c.method, c.path, c.query) == ("POST", "/v1/plant/user_plant_list", {"user_name": "bob"})
