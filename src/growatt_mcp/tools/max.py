"""Tools specific to MAX-series (commercial string) inverters."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from ._common import run


def register(app: FastMCP, client: GrowattClient) -> None:
    @app.tool()
    async def get_max_data(device_sn: str) -> str:
        """Get the latest data for one MAX-series inverter.

        Args:
            device_sn: MAX inverter serial number.
        """
        return await run(client.max.data_info(device_sn))

    @app.tool()
    async def get_max_batch_data(device_sns: list[str], page_num: int = 1) -> str:
        """Get the latest data for several MAX-series inverters in one call.

        Args:
            device_sns: Serial numbers of the MAX inverters.
            page_num: Page number (default 1).
        """
        return await run(client.max.batch_data(device_sns, page_num))

    @app.tool()
    async def set_max_parameter(device_sn: str, setting_type: str, values: list[str]) -> str:
        """Write a setting on a MAX-series inverter. Changes state on Growatt's side.

        Args:
            device_sn: MAX inverter serial number.
            setting_type: Growatt register name, e.g. "pv_active_p_rate".
            values: Values for param1..param19 in order; only pass as many as the setting needs.
        """
        return await run(client.max.set_parameter(device_sn, setting_type, values))
