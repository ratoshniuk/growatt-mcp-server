"""Thin HTTP layer: authentication header, JSON decoding and error translation."""

from __future__ import annotations

import json
from typing import Any

import httpx

from .errors import GrowattAPIError, GrowattError, GrowattHTTPError, GrowattTransportError

Params = dict[str, Any]


def check_api_error(payload: Any, method: str, path: str) -> None:
    """Raise :class:`GrowattAPIError` when a JSON payload carries a non-zero status code.

    v1 endpoints answer ``{"error_code": 0, "error_msg": "", "data": ...}``;
    v4 endpoints answer ``{"code": 0, "message": "SUCCESSFUL_OPERATION", "data": ...}``.
    """
    if not isinstance(payload, dict):
        return
    code = payload.get("error_code", payload.get("code"))
    if code in (None, 0, "0"):
        return
    message = payload.get("error_msg") or payload.get("message") or ""
    raise GrowattAPIError(code, str(message), payload, method, path)


class HttpClient:
    """Minimal async wrapper around :class:`httpx.AsyncClient` for the Growatt API."""

    def __init__(
        self,
        token: str,
        base_url: str,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"token": token},
            timeout=timeout,
            transport=transport,
        )

    @property
    def is_closed(self) -> bool:
        return self._http.is_closed

    async def close(self) -> None:
        await self._http.aclose()

    async def get(self, path: str, params: Params | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, params: Params | None = None, data: Params | None = None) -> Any:
        return await self._request("POST", path, params=params, data=data)

    async def _request(self, method: str, path: str, params: Params | None = None, data: Params | None = None) -> Any:
        try:
            response = await self._http.request(method, path, params=clean_params(params), data=clean_params(data))
        except httpx.HTTPError as exc:
            raise GrowattTransportError(f"{type(exc).__name__}: {exc}", method, path) from exc
        return self._handle(response, method, path)

    @staticmethod
    def _handle(response: httpx.Response, method: str, path: str) -> Any:
        if response.is_error:
            raise GrowattHTTPError(response.status_code, response.text, method, path)
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise GrowattError(f"{method} {path} returned a non-JSON body: {response.text[:200]}") from exc
        check_api_error(payload, method, path)
        return payload


def clean_params(values: Params | None) -> dict[str, str] | None:
    """Drop ``None`` values and render the rest the way the API expects them.

    Booleans become ``1``/``0``, whole-number floats lose their ``.0``, everything else is ``str()``.
    """
    if not values:
        return None
    return {key: _render(value) for key, value in values.items() if value is not None}


def _render(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
