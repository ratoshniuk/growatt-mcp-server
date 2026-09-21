"""Tools for end-user account management (installer / distributor accounts)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from ._common import run


def register(app: FastMCP, client: GrowattClient) -> None:
    @app.tool()
    async def list_users(page: int = 1, perpage: int = 100) -> str:
        """List end-user accounts managed by this Growatt account.

        Args:
            page: Page number (default 1).
            perpage: Results per page (default 100).
        """
        return await run(client.users.list(page, perpage))

    @app.tool()
    async def check_user(user_name: str) -> str:
        """Check whether a Growatt user name exists.

        Args:
            user_name: User name to check.
        """
        return await run(client.users.check(user_name))

    @app.tool()
    async def register_user(
        user_name: str,
        user_password: str,
        user_email: str,
        user_type: int,
        user_country: str,
    ) -> str:
        """Create an end-user account under this Growatt account. Changes state on Growatt's side.

        Args:
            user_name: Login name for the new user.
            user_password: Password for the new user.
            user_email: Email address of the new user.
            user_type: Growatt user type code.
            user_country: Country name as used by Growatt.
        """
        return await run(client.users.register(user_name, user_password, user_email, user_type, user_country))

    @app.tool()
    async def modify_user(c_user_id: str, mobile: str) -> str:
        """Update an end-user's mobile number. Changes state on Growatt's side.

        Args:
            c_user_id: End-user ID.
            mobile: New mobile number.
        """
        return await run(client.users.modify(c_user_id, mobile))
