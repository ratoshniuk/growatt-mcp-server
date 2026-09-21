from __future__ import annotations

import json
from typing import Any

from .client import GrowattClient

_client: GrowattClient | None = None


def configure(client: GrowattClient) -> None:
    global _client
    _client = client


def _c() -> GrowattClient:
    assert _client is not None, "GrowattClient not configured"
    return _client


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def register_tools(app: Any) -> Any:

    @app.tool()
    async def get_plants() -> str:
        """List all plants (solar installations) associated with your Growatt account."""
        return _json(await _c().plant_list())

    @app.tool()
    async def get_plant_details(plant_id: str = "") -> str:
        """Get basic information about a power plant.

        Args:
            plant_id: Plant ID. If omitted, returns details for all plants.
        """
        return _json(await _c().plant_details(plant_id or None))

    @app.tool()
    async def get_plant_data(plant_id: str) -> str:
        """Get current energy overview for a plant (today's generation, total, etc.).

        Args:
            plant_id: Plant ID.
        """
        return _json(await _c().plant_data(plant_id))

    @app.tool()
    async def get_plant_energy(
        plant_id: str,
        start_date: str,
        end_date: str,
        time_unit: str = "day",
        page: int = 1,
        perpage: int = 30,
    ) -> str:
        """Get historical energy generation data for a plant.

        Args:
            plant_id: Plant ID.
            start_date: Start date (YYYY-MM-DD). Date interval cannot exceed 7 days.
            end_date: End date (YYYY-MM-DD).
            time_unit: Granularity: "day", "month", or "year".
            page: Page number (default 1).
            perpage: Results per page (default 30, max 100).
        """
        return _json(await _c().plant_energy(plant_id, start_date, end_date, time_unit, page, perpage))

    @app.tool()
    async def get_devices(plant_id: str = "", page: int = 1) -> str:
        """List devices. Provide plant_id to filter by plant, or omit for all devices.

        Args:
            plant_id: Plant ID to filter by. If omitted, lists all devices.
            page: Page number (default 1).
        """
        return _json(await _c().device_list(plant_id or None, page))

    @app.tool()
    async def get_device_info(device_sn: str, device_type: str) -> str:
        """Get detailed info for a specific device.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
        """
        return _json(await _c().device_info(device_sn, device_type))

    @app.tool()
    async def get_device_last_data(device_sn: str, device_type: str) -> str:
        """Get the latest real-time data from a device (power, voltage, SOC, etc.).

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
        """
        return _json(await _c().device_last_data(device_sn, device_type))

    @app.tool()
    async def get_device_history(device_sn: str, device_type: str, date: str) -> str:
        """Get detailed historical data for a single device for one day.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
            date: Date to query (YYYY-MM-DD).
        """
        return _json(await _c().device_historical_data(device_sn, device_type, date))

    @app.tool()
    async def check_device_sn(sn: str) -> str:
        """Look up a device serial number to check its type and status.

        Args:
            sn: Device serial number to check.
        """
        return _json(await _c().device_check_sn(sn))

    @app.tool()
    async def set_device_on_off(device_sn: str, device_type: str, turn_on: bool) -> str:
        """Turn a device on or off.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", etc.
            turn_on: True to turn on, False to shut down.
        """
        return _json(await _c().set_on_off(device_sn, device_type, 1 if turn_on else 0))

    @app.tool()
    async def set_device_power(device_sn: str, device_type: str, value: int) -> str:
        """Set active power rate for a device.

        For inverters: percentage 0-100.
        For NOAH devices: power in watts 0-800W.
        For NEXA devices: power in watts 0-1000W.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", etc.
            value: Power value (percentage or watts depending on device type).
        """
        return _json(await _c().set_power(device_sn, device_type, value))

    @app.tool()
    async def read_device_parameter(device_sn: str, device_type: str, set_type: str) -> str:
        """Read a VPP (Virtual Power Plant) parameter from a device.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "wit", etc.
            set_type: Parameter type to read (e.g. "set_param_1", "set_param_23").
        """
        return _json(await _c().read_vpp_parameter(device_sn, device_type, set_type))

    @app.tool()
    async def set_device_parameter(device_sn: str, device_type: str, set_type: str, value: str) -> str:
        """Set a VPP (Virtual Power Plant) parameter on a device.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "wit", etc.
            set_type: Parameter type to set (e.g. "set_param_23" for discharge cut-off SOC).
            value: Parameter value. For time schedules, use JSON like:
                   [{"percentage":0,"startTime":120,"endTime":179}]
        """
        return _json(await _c().set_vpp_parameter(device_sn, device_type, set_type, value))

    return app
