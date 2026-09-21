import json

import httpx
from mcp.server.fastmcp import FastMCP

from growatt_mcp import tools
from growatt_mcp.client import GrowattClient

EXPECTED_TOOLS = {
    "get_plants",
    "get_plant_details",
    "get_plant_data",
    "get_plant_energy",
    "get_devices",
    "get_device_info",
    "get_device_last_data",
    "get_device_history",
    "check_device_sn",
    "set_device_on_off",
    "set_device_power",
    "read_device_parameter",
    "set_device_parameter",
}


def build_app(handler):
    client = GrowattClient(token="t", base_url="https://example.test")
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://example.test")
    tools.configure(client)
    return tools.register_tools(FastMCP("test")), client


async def test_all_tools_registered():
    app, client = build_app(lambda r: httpx.Response(200, json={}))
    try:
        names = {t.name for t in await app.list_tools()}
    finally:
        await client.close()
    assert names == EXPECTED_TOOLS


async def test_tool_returns_pretty_json():
    app, client = build_app(lambda r: httpx.Response(200, json={"error_code": 0, "data": {"count": 1}}))
    try:
        result = await app.call_tool("get_plants", {})
    finally:
        await client.close()
    text = result[0][0].text if isinstance(result, tuple) else result[0].text
    assert json.loads(text) == {"error_code": 0, "data": {"count": 1}}


async def test_set_device_on_off_maps_bool_to_int():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={"code": 0})

    app, client = build_app(handler)
    try:
        await app.call_tool("set_device_on_off", {"device_sn": "SN", "device_type": "min", "turn_on": False})
    finally:
        await client.close()
    assert seen["params"]["value"] == "0"
