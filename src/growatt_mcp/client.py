from __future__ import annotations

import os
from typing import Any

import httpx


class GrowattClient:
    """Thin async HTTP client for the Growatt ShineServer Public API (v1 + v4)."""

    def __init__(self, token: str | None = None, base_url: str | None = None) -> None:
        self.token = token or os.environ["GROWATT_TOKEN"]
        self.base_url = (base_url or os.environ.get("GROWATT_BASE_URL", "https://openapi.growatt.com")).rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"token": self.token},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        r = await self._http.get(path, params=params)
        r.raise_for_status()
        return r.json()

    async def _post(self, path: str, params: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> Any:
        r = await self._http.post(path, params=params, data=data)
        r.raise_for_status()
        return r.json()

    async def plant_list(self) -> Any:
        return await self._get("/v1/plant/list")

    async def plant_details(self, plant_id: str | None = None) -> Any:
        params = {}
        if plant_id:
            params["plant_id"] = plant_id
        return await self._post("/v1/plant/details", params=params)

    async def plant_data(self, plant_id: str) -> Any:
        return await self._get("/v1/plant/data", params={"plant_id": plant_id})

    async def plant_energy(
        self,
        plant_id: str,
        start_date: str,
        end_date: str,
        time_unit: str = "day",
        page: int = 1,
        perpage: int = 30,
    ) -> Any:
        return await self._get("/v1/plant/energy", params={
            "plant_id": plant_id,
            "start_date": start_date,
            "end_date": end_date,
            "time_unit": time_unit,
            "page": str(page),
            "perpage": str(perpage),
        })

    async def device_list(self, plant_id: str | None = None, page: int = 1) -> Any:
        if plant_id:
            return await self._get("/v1/device/list", params={"plant_id": plant_id})
        return await self._post("/v4/new-api/queryDeviceList", data={"page": str(page)})

    async def device_info(self, device_sn: str, device_type: str) -> Any:
        return await self._post("/v4/new-api/queryDeviceInfo", data={
            "deviceSn": device_sn,
            "deviceType": device_type,
        })

    async def device_last_data(self, device_sn: str, device_type: str) -> Any:
        return await self._post("/v4/new-api/queryLastData", data={
            "deviceSn": device_sn,
            "deviceType": device_type,
        })

    async def device_historical_data(self, device_sn: str, device_type: str, date: str) -> Any:
        return await self._post("/v4/new-api/queryHistoricalData", data={
            "deviceSn": device_sn,
            "deviceType": device_type,
            "date": date,
        })

    async def device_check_sn(self, sn: str) -> Any:
        return await self._get("/v1/device/check/sn", params={"sn": sn})

    async def set_on_off(self, device_sn: str, device_type: str, value: int) -> Any:
        return await self._post("/v4/new-api/setOnOrOff", params={
            "deviceSn": device_sn,
            "deviceType": device_type,
            "value": str(value),
        })

    async def set_power(self, device_sn: str, device_type: str, value: int) -> Any:
        return await self._post("/v4/new-api/setPower", params={
            "deviceSn": device_sn,
            "deviceType": device_type,
            "value": str(value),
        })

    async def read_vpp_parameter(self, device_sn: str, device_type: str, set_type: str) -> Any:
        return await self._post("/v4/new-api/readVppParameter", data={
            "deviceSn": device_sn,
            "deviceType": device_type,
            "setType": set_type,
        })

    async def set_vpp_parameter(self, device_sn: str, device_type: str, set_type: str, value: str) -> Any:
        return await self._post("/v4/new-api/setVppParameter", data={
            "deviceSn": device_sn,
            "deviceType": device_type,
            "setType": set_type,
            "value": value,
        })
