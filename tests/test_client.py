import json

import httpx
import pytest

from growatt_mcp.client import GrowattClient


def make_client(handler):
    client = GrowattClient(token="test-token", base_url="https://example.test")
    client._http = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
        headers={"token": "test-token"},
    )
    return client


async def test_plant_list_sends_token_header():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["token"] = request.headers.get("token")
        return httpx.Response(200, json={"error_code": 0, "data": {"plants": []}})

    client = make_client(handler)
    try:
        result = await client.plant_list()
    finally:
        await client.close()

    assert seen["url"] == "https://example.test/v1/plant/list"
    assert seen["token"] == "test-token"
    assert result["error_code"] == 0


async def test_plant_energy_query_params():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={"error_code": 0, "data": {"energys": []}})

    client = make_client(handler)
    try:
        await client.plant_energy("123", "2026-09-15", "2026-09-21", time_unit="day", page=2, perpage=50)
    finally:
        await client.close()

    assert seen["params"] == {
        "plant_id": "123",
        "start_date": "2026-09-15",
        "end_date": "2026-09-21",
        "time_unit": "day",
        "page": "2",
        "perpage": "50",
    }


async def test_device_last_data_posts_form_body():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = request.content.decode()
        return httpx.Response(200, json={"code": 0, "data": {}})

    client = make_client(handler)
    try:
        await client.device_last_data("SN123", "min")
    finally:
        await client.close()

    assert seen["method"] == "POST"
    assert seen["path"] == "/v4/new-api/queryLastData"
    assert "deviceSn=SN123" in seen["body"]
    assert "deviceType=min" in seen["body"]


async def test_http_error_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    client = make_client(handler)
    try:
        with pytest.raises(httpx.HTTPStatusError):
            await client.plant_list()
    finally:
        await client.close()


def test_token_required_when_env_missing(monkeypatch):
    monkeypatch.delenv("GROWATT_TOKEN", raising=False)
    with pytest.raises(KeyError):
        GrowattClient()


async def test_response_is_parsed_json():
    payload = {"code": 0, "data": {"min": [{"bdc1Soc": 64}]}}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=json.dumps(payload))

    client = make_client(handler)
    try:
        assert await client.device_last_data("SN", "min") == payload
    finally:
        await client.close()
