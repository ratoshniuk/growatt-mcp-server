EXPECTED_TOOLS = {
    # plants
    "get_plants",
    "get_plant_details",
    "get_plant_data",
    "get_plant_energy",
    "get_user_plants",
    "add_plant",
    "modify_plant",
    # devices
    "get_devices",
    "get_device_info",
    "get_device_last_data",
    "get_device_history",
    "check_device_sn",
    "get_dataloggers",
    "add_datalogger",
    "add_storage_device",
    # control
    "set_device_on_off",
    "set_device_power",
    "read_device_parameter",
    "set_device_parameter",
    # max
    "get_max_data",
    "get_max_batch_data",
    "set_max_parameter",
    # users
    "list_users",
    "check_user",
    "register_user",
    "modify_user",
}


async def test_all_tools_registered(app):
    names = {t.name for t in await app.list_tools()}
    assert names == EXPECTED_TOOLS


async def test_every_tool_has_a_description(app):
    for tool in await app.list_tools():
        assert tool.description and tool.description.strip(), tool.name


async def test_state_changing_tools_say_so(app):
    for tool in await app.list_tools():
        if tool.name.split("_")[0] in {"set", "add", "modify", "register"}:
            assert "Changes state" in (tool.description or ""), tool.name
