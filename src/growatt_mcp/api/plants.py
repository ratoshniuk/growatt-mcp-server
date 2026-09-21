"""Plant (power station) endpoints (``/v1/plant/*``)."""

from __future__ import annotations

from typing import Any

from ._base import Resource


class PlantsAPI(Resource):
    async def list(self) -> Any:
        """All plants visible to the token owner."""
        return await self._http.get("/v1/plant/list")

    async def details(self, plant_id: str | int | None = None) -> Any:
        """Basic information about one plant, or all plants when ``plant_id`` is omitted."""
        return await self._http.post("/v1/plant/details", params={"plant_id": plant_id})

    async def data(self, plant_id: str | int) -> Any:
        """Current overview: today's / monthly / yearly / total energy and current power."""
        return await self._http.get("/v1/plant/data", params={"plant_id": plant_id})

    async def energy(
        self,
        plant_id: str | int,
        start_date: str,
        end_date: str,
        time_unit: str = "day",
        page: int = 1,
        perpage: int = 30,
    ) -> Any:
        """Historical generation. ``time_unit`` is ``day``, ``month`` or ``year``; max 7 days per call."""
        return await self._http.get(
            "/v1/plant/energy",
            params={
                "plant_id": plant_id,
                "start_date": start_date,
                "end_date": end_date,
                "time_unit": time_unit,
                "page": page,
                "perpage": perpage,
            },
        )

    async def add(self, c_user_id: str | int, name: str, peak_power: float) -> Any:
        """Create a plant for an end user. ``peak_power`` is in kWp."""
        return await self._http.post(
            "/v1/plant/add",
            params={"c_user_id": c_user_id, "name": name, "peak_power": peak_power},
        )

    async def modify(
        self,
        c_user_id: str | int,
        plant_id: str | int,
        name: str | None = None,
        currency: str | int | None = None,
    ) -> Any:
        """Rename a plant and/or change its currency code."""
        return await self._http.post(
            "/v1/plant/modify",
            params={"c_user_id": c_user_id, "plant_id": plant_id, "name": name, "currency": currency},
        )

    async def list_for_user(self, user_name: str) -> Any:
        """Plants that belong to a specific end user."""
        return await self._http.post("/v1/plant/user_plant_list", params={"user_name": user_name})
