"""Tools specific to MAX-series (commercial string) inverters."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ..api import GrowattClient
from ..api.max_inverters import MAX_SET_PARAM_SLOTS
from ._common import Page, Registrar, run

MaxSn = Annotated[str, Field(description="MAX inverter serial number.")]


def register(reg: Registrar, client: GrowattClient) -> None:
    @reg.read()
    async def get_max_data(device_sn: MaxSn) -> str:
        """Get the latest data for one MAX-series inverter."""
        return await run(client.max.data_info(device_sn))

    @reg.read()
    async def get_max_batch_data(
        device_sns: Annotated[list[str], Field(min_length=1, description="Serial numbers of the MAX inverters.")],
        page_num: Page = 1,
    ) -> str:
        """Get the latest data for several MAX-series inverters in one call."""
        return await run(client.max.batch_data(device_sns, page_num))

    @reg.write()
    async def set_max_parameter(
        device_sn: MaxSn,
        setting_type: Annotated[str, Field(description='Growatt register name, e.g. "pv_active_p_rate".')],
        values: Annotated[
            list[str],
            Field(
                min_length=1,
                max_length=MAX_SET_PARAM_SLOTS,
                description=f"Values for param1..param{MAX_SET_PARAM_SLOTS} in order, as many as the setting needs.",
            ),
        ],
    ) -> str:
        """Write a setting on a MAX-series inverter. Changes state on Growatt's side."""
        return await run(client.max.set_parameter(device_sn, setting_type, values))
