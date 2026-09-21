"""Tools for plants (power stations)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from ._common import run


def register(app: FastMCP, client: GrowattClient) -> None:
    @app.tool()
    async def get_plants() -> str:
        """List all plants (solar installations) visible to this Growatt account."""
        return await run(client.plants.list())

    @app.tool()
    async def get_plant_details(plant_id: str = "") -> str:
        """Get basic information about a plant (name, location, peak power, timezone).

        Args:
            plant_id: Plant ID. If omitted, returns details for all plants.
        """
        return await run(client.plants.details(plant_id or None))

    @app.tool()
    async def get_plant_data(plant_id: str) -> str:
        """Get the current energy overview for a plant: today's, monthly, yearly and total energy, current power.

        Args:
            plant_id: Plant ID.
        """
        return await run(client.plants.data(plant_id))

    @app.tool()
    async def get_plant_energy(
        plant_id: str,
        start_date: str,
        end_date: str,
        time_unit: str = "day",
        page: int = 1,
        perpage: int = 30,
    ) -> str:
        """Get historical energy generation for a plant.

        Args:
            plant_id: Plant ID.
            start_date: Start date (YYYY-MM-DD). The interval cannot exceed 7 days.
            end_date: End date (YYYY-MM-DD).
            time_unit: Granularity: "day", "month" or "year".
            page: Page number (default 1).
            perpage: Results per page (default 30, max 100).
        """
        return await run(client.plants.energy(plant_id, start_date, end_date, time_unit, page, perpage))

    @app.tool()
    async def get_user_plants(user_name: str) -> str:
        """List the plants that belong to a specific end user (installer / distributor accounts).

        Args:
            user_name: Growatt user name of the end user.
        """
        return await run(client.plants.list_for_user(user_name))

    @app.tool()
    async def add_plant(c_user_id: str, name: str, peak_power: float) -> str:
        """Create a new plant for an end user. Changes state on Growatt's side.

        Args:
            c_user_id: ID of the end user who will own the plant.
            name: Plant name.
            peak_power: Installed peak power in kWp.
        """
        return await run(client.plants.add(c_user_id, name, peak_power))

    @app.tool()
    async def modify_plant(c_user_id: str, plant_id: str, name: str = "", currency: str = "") -> str:
        """Rename a plant and/or change its currency. Changes state on Growatt's side.

        Args:
            c_user_id: ID of the end user who owns the plant.
            plant_id: Plant ID.
            name: New plant name (leave empty to keep).
            currency: Currency code as used by Growatt (leave empty to keep).
        """
        return await run(client.plants.modify(c_user_id, plant_id, name or None, currency or None))
