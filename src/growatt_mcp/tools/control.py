"""Tools that change inverter state."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from ._common import run


def register(app: FastMCP, client: GrowattClient) -> None:
    @app.tool()
    async def set_device_on_off(device_sn: str, device_type: str, turn_on: bool) -> str:
        """Turn a device on or off. Changes state on Growatt's side.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", etc.
            turn_on: True to turn on, False to shut down.
        """
        return await run(client.control.set_on_off(device_sn, device_type, turn_on))

    @app.tool()
    async def set_device_power(device_sn: str, device_type: str, value: int) -> str:
        """Set the active power limit of a device. Changes state on Growatt's side.

        For inverters the value is a percentage 0-100. For NOAH devices it is watts 0-800,
        for NEXA devices watts 0-1000.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "max", "inv", etc.
            value: Power value (percent or watts depending on the device type).
        """
        return await run(client.control.set_power(device_sn, device_type, value))

    @app.tool()
    async def read_device_parameter(device_sn: str, device_type: str, set_type: str) -> str:
        """Read a VPP (Virtual Power Plant) parameter from a device.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "wit", etc.
            set_type: Parameter name, e.g. "set_param_1" or "set_param_23" (discharge cut-off SOC).
        """
        return await run(client.control.read_vpp_parameter(device_sn, device_type, set_type))

    @app.tool()
    async def set_device_parameter(device_sn: str, device_type: str, set_type: str, value: str) -> str:
        """Write a VPP (Virtual Power Plant) parameter on a device. Changes state on Growatt's side.

        Args:
            device_sn: Device serial number.
            device_type: Device type: "sph", "spa", "min", "wit", etc.
            set_type: Parameter name, e.g. "set_param_23" for discharge cut-off SOC.
            value: Parameter value. Time schedules take a JSON array such as
                   [{"percentage":0,"startTime":120,"endTime":179}].
        """
        return await run(client.control.set_vpp_parameter(device_sn, device_type, set_type, value))
