"""Tools for end-user account management (installer / distributor accounts)."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ..api import GrowattClient
from ._common import Page, Registrar, UserId, run

UserName = Annotated[str, Field(description="Growatt login name.")]


def register(reg: Registrar, client: GrowattClient) -> None:
    @reg.read()
    async def list_users(
        page: Page = 1,
        perpage: Annotated[int, Field(ge=1, description="Results per page.")] = 100,
    ) -> str:
        """List end-user accounts managed by this Growatt account."""
        return await run(client.users.list(page, perpage))

    @reg.read()
    async def check_user(user_name: UserName) -> str:
        """Check whether a Growatt user name exists."""
        return await run(client.users.check(user_name))

    @reg.write()
    async def register_user(
        user_name: UserName,
        user_password: Annotated[str, Field(description="Password for the new user. Passes through the assistant.")],
        user_email: Annotated[str, Field(description="Email address of the new user.")],
        user_type: Annotated[int, Field(description="Growatt user type code.")],
        user_country: Annotated[str, Field(description="Country name as used by Growatt.")],
    ) -> str:
        """Create an end-user account under this Growatt account. Changes state on Growatt's side."""
        return await run(client.users.register(user_name, user_password, user_email, user_type, user_country))

    @reg.write()
    async def modify_user(
        c_user_id: UserId,
        mobile: Annotated[str, Field(description="New mobile number.")],
    ) -> str:
        """Update an end-user's mobile number. Changes state on Growatt's side."""
        return await run(client.users.modify(c_user_id, mobile))
