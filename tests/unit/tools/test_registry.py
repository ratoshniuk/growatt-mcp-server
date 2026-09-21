READ_TOOLS = {
    "get_plants",
    "get_plant_details",
    "get_plant_data",
    "get_plant_energy",
    "get_user_plants",
    "get_devices",
    "get_device_info",
    "get_device_last_data",
    "get_device_history",
    "check_device_sn",
    "get_dataloggers",
    "read_device_parameter",
    "get_max_data",
    "get_max_batch_data",
    "list_users",
    "check_user",
}
WRITE_TOOLS = {
    "add_plant",
    "modify_plant",
    "add_datalogger",
    "add_storage_device",
    "set_device_on_off",
    "set_device_power",
    "set_device_parameter",
    "set_max_parameter",
    "register_user",
    "modify_user",
}
EXPECTED_TOOLS = READ_TOOLS | WRITE_TOOLS


async def test_all_tools_registered(app):
    names = {t.name for t in await app.list_tools()}
    assert names == EXPECTED_TOOLS
    assert len(names) == 26


async def test_read_only_mode_hides_write_tools(read_only_app):
    names = {t.name for t in await read_only_app.list_tools()}
    assert names == READ_TOOLS


async def test_annotations_match_tool_kind(app):
    for tool in await app.list_tools():
        assert tool.annotations is not None, tool.name
        if tool.name in WRITE_TOOLS:
            assert tool.annotations.readOnlyHint is False, tool.name
            assert tool.annotations.destructiveHint is True, tool.name
            assert "Changes state" in (tool.description or ""), tool.name
        else:
            assert tool.annotations.readOnlyHint is True, tool.name


async def test_every_tool_and_parameter_has_a_description(app):
    for tool in await app.list_tools():
        assert tool.description and tool.description.strip(), tool.name
        for name, prop in tool.inputSchema.get("properties", {}).items():
            assert prop.get("description"), f"{tool.name}.{name} has no description"


async def test_input_schema_types(app):
    schemas = {t.name: t.inputSchema["properties"] for t in await app.list_tools()}
    assert schemas["set_device_on_off"]["turn_on"]["type"] == "boolean"
    assert schemas["get_max_batch_data"]["device_sns"]["type"] == "array"
    assert schemas["set_device_power"]["value"]["type"] == "integer"
    assert {"type": "string"} in schemas["get_plant_data"]["plant_id"]["anyOf"]
    assert {"type": "integer"} in schemas["get_plant_data"]["plant_id"]["anyOf"]
