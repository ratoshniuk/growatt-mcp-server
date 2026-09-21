"""Endpoints that change inverter state (``/v4/new-api/set*`` and VPP parameters)."""

from __future__ import annotations

from typing import Any

from ._base import Resource


class ControlAPI(Resource):
    async def set_on_off(self, device_sn: str, device_type: str, on: bool) -> Any:
        """Switch a device on (``True``) or off (``False``)."""
        return await self._http.post(
            "/v4/new-api/setOnOrOff",
            params={"deviceSn": device_sn, "deviceType": device_type, "value": 1 if on else 0},
        )

    async def set_power(self, device_sn: str, device_type: str, value: int) -> Any:
        """Set the active power limit: percent for inverters, watts for NOAH/NEXA devices."""
        return await self._http.post(
            "/v4/new-api/setPower",
            params={"deviceSn": device_sn, "deviceType": device_type, "value": value},
        )

    async def read_vpp_parameter(self, device_sn: str, device_type: str, set_type: str) -> Any:
        """Read a VPP parameter such as ``set_param_23`` (discharge cut-off SOC)."""
        return await self._http.post(
            "/v4/new-api/readVppParameter",
            data={"deviceSn": device_sn, "deviceType": device_type, "setType": set_type},
        )

    async def set_vpp_parameter(
        self,
        device_sn: str,
        device_type: str,
        set_type: str,
        value: str,
        plant_id: str | int | None = None,
    ) -> Any:
        """Write a VPP parameter. Time-schedule parameters take a JSON array as ``value``."""
        return await self._http.post(
            "/v4/new-api/setVppParameter",
            data={
                "deviceSn": device_sn,
                "deviceType": device_type,
                "setType": set_type,
                "value": value,
                "plant_id": plant_id,
            },
        )
