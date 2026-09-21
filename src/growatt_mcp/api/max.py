"""Endpoints specific to MAX-series (commercial string) inverters (``/v1/device/max/*``, ``/v1/maxSet``)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ._base import Resource

MAX_SET_PARAM_SLOTS = 19


class MaxAPI(Resource):
    async def data_info(self, device_sn: str) -> Any:
        """Latest data for one MAX inverter."""
        return await self._http.get("/v1/device/max/max_data_info", params={"device_sn": device_sn})

    async def batch_data(self, device_sns: Sequence[str] | str, page_num: int = 1) -> Any:
        """Latest data for several MAX inverters at once."""
        maxs = device_sns if isinstance(device_sns, str) else ",".join(device_sns)
        return await self._http.post("/v1/device/max/maxs_data", params={"pageNum": page_num, "maxs": maxs})

    async def set_parameter(self, device_sn: str, setting_type: str, values: Sequence[str | int | float]) -> Any:
        """Write a setting on a MAX inverter.

        ``setting_type`` is the Growatt register name, e.g. ``pv_active_p_rate``. ``values`` fills
        ``param1``..``param19`` in order; unused slots are sent as empty strings as the API expects.
        """
        if len(values) > MAX_SET_PARAM_SLOTS:
            raise ValueError(f"maxSet accepts at most {MAX_SET_PARAM_SLOTS} parameters, got {len(values)}")
        params: dict[str, Any] = {"max_sn": device_sn, "type": setting_type}
        for index in range(MAX_SET_PARAM_SLOTS):
            params[f"param{index + 1}"] = values[index] if index < len(values) else ""
        return await self._http.post("/v1/maxSet", params=params)
