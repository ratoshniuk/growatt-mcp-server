"""Tools for device discovery and readings."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from ._common import run


def register(app: FastMCP, client: GrowattClient) -> None:
    @app.tool()
    async def get_devices(plant_id: str = "", page: int = 1) -> str:
        """List devices. Provide plant_id to filter by plant, or omit for all devices on the account.

        The response includes each device's type ("min", "sph", "max", ...), which other tools need.

        Args:
            plant_id: Plant ID to filter by. If omitted, lists all devices (paginated).
            page: Page number when listing all devices (default 1).
        """
        return await run(client.devices.list(plant_id or None, page))

    @app.tool()
    async def get_device_info(device_sn: str, device_type: str) -> str:
        """Get static information for a device: model, firmware, configured settings.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
        """
        return await run(client.devices.info(device_sn, device_type))

    @app.tool()
    async def get_device_last_data(device_sn: str, device_type: str) -> str:
        """Get the latest real-time reading: PV power, load, grid import/export, battery SOC, temperatures, faults.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
        """
        return await run(client.devices.last_data(device_sn, device_type))

    @app.tool()
    async def get_device_history(device_sn: str, device_type: str, date: str) -> str:
        """Get five-minute readings for a single device for one day.

        The "calendar" field is an epoch built from the plant's local wall-clock interpreted as UTC+8;
        treat it as UTC and add 8 hours to get local time.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", "wit", etc.
            date: Date to query (YYYY-MM-DD).
        """
        return await run(client.devices.history(device_sn, device_type, date))

    @app.tool()
    async def check_device_sn(sn: str) -> str:
        """Look up a serial number to learn its device type and whether it is already registered.

        Args:
            sn: Device serial number.
        """
        return await run(client.devices.check_sn(sn))

    @app.tool()
    async def get_dataloggers(plant_id: str) -> str:
        """List the dataloggers (ShineWiFi / ShineLAN sticks) attached to a plant.

        Args:
            plant_id: Plant ID.
        """
        return await run(client.devices.list_dataloggers(plant_id))

    @app.tool()
    async def add_datalogger(c_user_id: str, plant_id: str, sn: str) -> str:
        """Attach a datalogger to a plant. Changes state on Growatt's side.

        Args:
            c_user_id: ID of the end user who owns the plant.
            plant_id: Plant ID.
            sn: Datalogger serial number.
        """
        return await run(client.devices.add_datalogger(c_user_id, plant_id, sn))

    @app.tool()
    async def add_storage_device(c_user_id: str, plant_id: str, sn: str) -> str:
        """Attach a storage (battery) device to a plant. Changes state on Growatt's side.

        Args:
            c_user_id: ID of the end user who owns the plant.
            plant_id: Plant ID.
            sn: Storage device serial number.
        """
        return await run(client.devices.add_storage(c_user_id, plant_id, sn))
