"""Facade that groups the endpoint resources behind one authenticated HTTP session."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ..config import DEFAULT_BASE_URL
from .control import ControlAPI
from .devices import DevicesAPI
from .http import HttpClient
from .max_inverters import MaxAPI
from .plants import PlantsAPI
from .users import UsersAPI

if TYPE_CHECKING:
    from ..config import Settings


class GrowattClient:
    """Async client for the Growatt ShineServer Public API.

    Usage::

        async with GrowattClient(token) as client:
            plants = await client.plants.list()
            latest = await client.devices.last_data("SN", "min")
    """

    def __init__(
        self,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = HttpClient(token=token, base_url=base_url, timeout=timeout, transport=transport)
        self.users = UsersAPI(self._http)
        self.plants = PlantsAPI(self._http)
        self.devices = DevicesAPI(self._http)
        self.control = ControlAPI(self._http)
        self.max = MaxAPI(self._http)

    @classmethod
    def from_settings(cls, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> GrowattClient:
        return cls(token=settings.token, base_url=settings.base_url, timeout=settings.timeout, transport=transport)

    @property
    def is_closed(self) -> bool:
        return self._http.is_closed

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> GrowattClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()
