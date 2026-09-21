"""Tools for plants (power stations)."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ..api import GrowattClient
from ._common import OptionalPlantId, Page, PlantId, Registrar, UserId, run


def register(reg: Registrar, client: GrowattClient) -> None:
    @reg.read()
    async def get_plants() -> str:
        """List all plants (solar installations) visible to this Growatt account."""
        return await run(client.plants.list())

    @reg.read()
    async def get_plant_details(plant_id: OptionalPlantId = "") -> str:
        """Get basic information about a plant: name, location, peak power, timezone."""
        return await run(client.plants.details(plant_id or None))

    @reg.read()
    async def get_plant_data(plant_id: PlantId) -> str:
        """Get the current energy overview for a plant: today's, monthly, yearly and total energy, current power."""
        return await run(client.plants.data(plant_id))

    @reg.read()
    async def get_plant_energy(
        plant_id: PlantId,
        start_date: Annotated[str, Field(description="Start date, YYYY-MM-DD. The interval may not exceed 7 days.")],
        end_date: Annotated[str, Field(description="End date, YYYY-MM-DD.")],
        time_unit: Annotated[str, Field(description='Granularity: "day", "month" or "year".')] = "day",
        page: Page = 1,
        perpage: Annotated[int, Field(ge=1, le=100, description="Results per page, max 100.")] = 30,
    ) -> str:
        """Get historical energy generation for a plant."""
        return await run(client.plants.energy(plant_id, start_date, end_date, time_unit, page, perpage))

    @reg.read()
    async def get_user_plants(
        user_name: Annotated[str, Field(description="Growatt user name of the end user.")],
    ) -> str:
        """List the plants that belong to a specific end user (installer / distributor accounts)."""
        return await run(client.plants.list_for_user(user_name))

    @reg.write()
    async def add_plant(
        c_user_id: UserId,
        name: Annotated[str, Field(description="Plant name.")],
        peak_power: Annotated[float, Field(gt=0, description="Installed peak power in kWp.")],
    ) -> str:
        """Create a new plant for an end user. Changes state on Growatt's side."""
        return await run(client.plants.add(c_user_id, name, peak_power))

    @reg.write()
    async def modify_plant(
        c_user_id: UserId,
        plant_id: PlantId,
        name: Annotated[str, Field(description="New plant name. Empty keeps the current one.")] = "",
        currency: Annotated[
            str, Field(description="Currency code as used by Growatt. Empty keeps the current one.")
        ] = "",
    ) -> str:
        """Rename a plant and/or change its currency. Changes state on Growatt's side."""
        return await run(client.plants.modify(c_user_id, plant_id, name or None, currency or None))
