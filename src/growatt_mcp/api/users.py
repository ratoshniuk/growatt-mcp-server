"""User management endpoints (``/v1/user/*``).

These are meant for installers and distributors who manage end-user ("C user") accounts.
"""

from __future__ import annotations

from typing import Any

from ._base import Resource


class UsersAPI(Resource):
    async def register(
        self,
        user_name: str,
        user_password: str,
        user_email: str,
        user_type: int,
        user_country: str,
    ) -> Any:
        """Create an end-user account under the token owner."""
        return await self._http.post(
            "/v1/user/user_register",
            params={
                "user_name": user_name,
                "user_password": user_password,
                "user_email": user_email,
                "user_type": user_type,
                "user_country": user_country,
            },
        )

    async def modify(self, c_user_id: str, mobile: str) -> Any:
        """Update an end-user's mobile number."""
        return await self._http.post("/v1/user/modify", params={"c_user_id": c_user_id, "mobile": mobile})

    async def check(self, user_name: str) -> Any:
        """Check whether a user name exists / is available."""
        return await self._http.post("/v1/user/check_user", params={"user_name": user_name})

    async def list(self, page: int = 1, perpage: int = 100) -> Any:
        """List end-user accounts managed by the token owner."""
        return await self._http.get("/v1/user/c_user_list", params={"page": page, "perpage": perpage})
