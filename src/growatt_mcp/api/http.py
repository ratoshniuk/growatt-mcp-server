"""Thin HTTP layer: authentication header, JSON decoding and error translation."""

from __future__ import annotations

import json
from typing import Any

import httpx

from .errors import GrowattAPIError, GrowattError, GrowattHTTPError

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

    async def close(self) -> None:
        await self._http.aclose()

    async def get(self, path: str, params: Params | None = None) -> Any:
        response = await self._http.get(path, params=_clean(params))
        return self._handle(response, "GET", path)

    async def post(self, path: str, params: Params | None = None, data: Params | None = None) -> Any:
        response = await self._http.post(path, params=_clean(params), data=_clean(data))
        return self._handle(response, "POST", path)

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


def _clean(values: Params | None) -> dict[str, str] | None:
    """Drop ``None`` values and stringify the rest, which is what the API expects."""
    if not values:
        return None
    return {key: str(value) for key, value in values.items() if value is not None}
