from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl

import httpx
import pytest
import pytest_asyncio

from growatt_mcp.api import GrowattClient
from growatt_mcp.server import create_app

OK_V1 = {"error_code": 0, "error_msg": "", "data": {}}


@dataclass
class Call:
    method: str
    path: str
    query: dict[str, str]
    body: dict[str, str]
    headers: dict[str, str]

    @property
    def params(self) -> dict[str, str]:
        """Query and form-body parameters merged; the API accepts both interchangeably."""
        return {**self.query, **self.body}


@dataclass
class Recorder:
    """httpx mock transport handler that records requests and returns a configurable response."""

    calls: list[Call] = field(default_factory=list)
    status: int = 200
    payload: Any = None
    raw_body: str | None = None

    def respond(self, payload: Any = None, status: int = 200, raw_body: str | None = None) -> None:
        self.payload, self.status, self.raw_body = payload, status, raw_body

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = dict(parse_qsl(request.content.decode())) if request.content else {}
        self.calls.append(
            Call(
                method=request.method.upper(),
                path=request.url.path,
                query=dict(request.url.params),
                body=body,
                headers=dict(request.headers),
            )
        )
        if self.raw_body is not None:
            return httpx.Response(self.status, content=self.raw_body)
        return httpx.Response(self.status, json=OK_V1 if self.payload is None else self.payload)

    @property
    def last(self) -> Call:
        assert self.calls, "no request was made"
        return self.calls[-1]


@pytest.fixture
def recorder() -> Recorder:
    return Recorder()


@pytest_asyncio.fixture
async def client(recorder: Recorder):
    async with GrowattClient("test-token", base_url="https://api.test", transport=httpx.MockTransport(recorder)) as c:
        yield c


@pytest.fixture
def app(client: GrowattClient):
    return create_app(client)


@pytest.fixture
def read_only_app(client: GrowattClient):
    return create_app(client, read_only=True)


async def call_tool(app, name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Invoke a FastMCP tool and return its JSON-decoded text output."""
    result = await app.call_tool(name, arguments or {})
    content = result[0] if isinstance(result, tuple) else result
    return json.loads(content[0].text)
