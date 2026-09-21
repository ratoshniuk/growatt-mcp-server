"""Tools that change inverter state."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ..api import GrowattClient
from ._common import DeviceSn, DeviceType, OptionalPlantId, Registrar, run

SetType = Annotated[
    str,
    Field(description='VPP parameter name, e.g. "set_param_1" or "set_param_23" (discharge cut-off SOC).'),
]


def register(reg: Registrar, client: GrowattClient) -> None:
    @reg.write()
    async def set_device_on_off(
        device_sn: DeviceSn,
        device_type: DeviceType,
        turn_on: Annotated[bool, Field(description="True to turn on, False to shut down.")],
    ) -> str:
        """Turn a device on or off. Changes state on Growatt's side."""
        return await run(client.control.set_on_off(device_sn, device_type, turn_on))

    @reg.write()
    async def set_device_power(
        device_sn: DeviceSn,
        device_type: DeviceType,
        value: Annotated[
            int,
            Field(ge=0, description="Inverters: percent 0-100. NOAH devices: watts 0-800. NEXA devices: watts 0-1000."),
        ],
    ) -> str:
        """Set the active power limit of a device. Changes state on Growatt's side."""
        return await run(client.control.set_power(device_sn, device_type, value))

    @reg.read()
    async def read_device_parameter(device_sn: DeviceSn, device_type: DeviceType, set_type: SetType) -> str:
        """Read a VPP (Virtual Power Plant) parameter from a device."""
        return await run(client.control.read_vpp_parameter(device_sn, device_type, set_type))

    @reg.write()
    async def set_device_parameter(
        device_sn: DeviceSn,
        device_type: DeviceType,
        set_type: SetType,
        value: Annotated[
            str,
            Field(
                description="Parameter value. Time schedules take a JSON array such as "
                '[{"percentage":0,"startTime":120,"endTime":179}].'
            ),
        ],
        plant_id: OptionalPlantId = "",
    ) -> str:
        """Write a VPP (Virtual Power Plant) parameter on a device. Changes state on Growatt's side."""
        return await run(client.control.set_vpp_parameter(device_sn, device_type, set_type, value, plant_id or None))
