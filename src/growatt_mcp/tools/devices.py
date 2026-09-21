"""Tools for device discovery and readings."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ..api import GrowattClient
from ._common import DeviceSn, DeviceType, OptionalPlantId, Page, PlantId, Registrar, UserId, run


def register(reg: Registrar, client: GrowattClient) -> None:
    @reg.read()
    async def get_devices(plant_id: OptionalPlantId = "", page: Page = 1) -> str:
        """List devices with their type ("min", "sph", "max", ...), which the other tools need.

        With a plant_id, returns every device of that plant (page is ignored). Without it, returns all
        devices on the account, paginated.
        """
        return await run(client.devices.list(plant_id or None, page))

    @reg.read()
    async def get_device_info(device_sn: DeviceSn, device_type: DeviceType) -> str:
        """Get static information for a device: model, firmware, configured settings."""
        return await run(client.devices.info(device_sn, device_type))

    @reg.read()
    async def get_device_last_data(device_sn: DeviceSn, device_type: DeviceType) -> str:
        """Get the latest real-time reading: PV power, load, grid import/export, battery SOC, temperatures, faults."""
        return await run(client.devices.last_data(device_sn, device_type))

    @reg.read()
    async def get_device_history(
        device_sn: DeviceSn,
        device_type: DeviceType,
        date: Annotated[str, Field(description="Day to query, YYYY-MM-DD.")],
    ) -> str:
        """Get five-minute readings for a single device for one day.

        The "calendar" field is an epoch built from the plant's local wall-clock interpreted as UTC+8;
        treat it as UTC and add 8 hours to get local time.
        """
        return await run(client.devices.history(device_sn, device_type, date))

    @reg.read()
    async def check_device_sn(sn: DeviceSn) -> str:
        """Look up a serial number to learn its device type and whether it is already registered."""
        return await run(client.devices.check_sn(sn))

    @reg.read()
    async def get_dataloggers(plant_id: PlantId) -> str:
        """List the dataloggers (ShineWiFi / ShineLAN sticks) attached to a plant."""
        return await run(client.devices.list_dataloggers(plant_id))

    @reg.write()
    async def add_datalogger(
        c_user_id: UserId,
        plant_id: PlantId,
        sn: Annotated[str, Field(description="Datalogger serial number.")],
    ) -> str:
        """Attach a datalogger to a plant. Changes state on Growatt's side."""
        return await run(client.devices.add_datalogger(c_user_id, plant_id, sn))

    @reg.write()
    async def add_storage_device(
        c_user_id: UserId,
        plant_id: PlantId,
        sn: Annotated[str, Field(description="Storage device serial number.")],
    ) -> str:
        """Attach a storage (battery) device to a plant. Changes state on Growatt's side."""
        return await run(client.devices.add_storage(c_user_id, plant_id, sn))
