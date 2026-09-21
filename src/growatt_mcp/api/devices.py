"""Device discovery and data endpoints (``/v1/device/*`` and ``/v4/new-api/query*``)."""

from __future__ import annotations

from typing import Any

from ._base import Resource


class DevicesAPI(Resource):
    async def list(self, plant_id: str | int | None = None, page: int = 1) -> Any:
        """Devices of one plant (v1) or every device on the account, paginated (v4)."""
        if plant_id is not None:
            return await self._http.get("/v1/device/list", params={"plant_id": plant_id})
        return await self._http.post("/v4/new-api/queryDeviceList", data={"page": page})

    async def info(self, device_sn: str, device_type: str) -> Any:
        """Static information about a device (model, firmware, settings)."""
        return await self._http.post(
            "/v4/new-api/queryDeviceInfo",
            data={"deviceSn": device_sn, "deviceType": device_type},
        )

    async def last_data(self, device_sn: str, device_type: str) -> Any:
        """Latest real-time reading: PV power, load, grid, battery SOC, temperatures, faults."""
        return await self._http.post(
            "/v4/new-api/queryLastData",
            data={"deviceSn": device_sn, "deviceType": device_type},
        )

    async def history(self, device_sn: str, device_type: str, date: str) -> Any:
        """Five-minute readings for one device on one day (``YYYY-MM-DD``)."""
        return await self._http.post(
            "/v4/new-api/queryHistoricalData",
            data={"deviceSn": device_sn, "deviceType": device_type, "date": date},
        )

    async def check_sn(self, sn: str) -> Any:
        """Look up a serial number: device type and whether it is registered."""
        return await self._http.get("/v1/device/check/sn", params={"sn": sn})

    async def list_dataloggers(self, plant_id: str | int) -> Any:
        """Dataloggers (ShineWiFi / ShineLAN sticks) attached to a plant."""
        return await self._http.get("/v1/device/datalogger/list", params={"plant_id": plant_id})

    async def add_datalogger(self, c_user_id: str | int, plant_id: str | int, sn: str) -> Any:
        """Attach a datalogger to a plant."""
        return await self._http.post(
            "/v1/device/datalogger/add",
            params={"c_user_id": c_user_id, "plant_id": plant_id, "sn": sn},
        )

    async def add_storage(self, c_user_id: str | int, plant_id: str | int, sn: str) -> Any:
        """Attach a storage (battery) device to a plant."""
        return await self._http.post(
            "/v1/device/storage/add",
            params={"c_user_id": c_user_id, "plant_id": plant_id, "sn": sn},
        )
