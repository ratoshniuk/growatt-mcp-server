async def test_register(client, recorder):
    await client.users.register("bob", "pw", "bob@example.test", 1, "Portugal")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/user/user_register")
    assert c.query == {
        "user_name": "bob",
        "user_password": "pw",
        "user_email": "bob@example.test",
        "user_type": "1",
        "user_country": "Portugal",
    }


async def test_modify(client, recorder):
    await client.users.modify("42", "+351900000000")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/user/modify")
    assert c.query == {"c_user_id": "42", "mobile": "+351900000000"}


async def test_check(client, recorder):
    await client.users.check("bob")
    c = recorder.last
    assert (c.method, c.path) == ("POST", "/v1/user/check_user")
    assert c.query == {"user_name": "bob"}


async def test_list_defaults(client, recorder):
    await client.users.list()
    c = recorder.last
    assert (c.method, c.path) == ("GET", "/v1/user/c_user_list")
    assert c.query == {"page": "1", "perpage": "100"}
