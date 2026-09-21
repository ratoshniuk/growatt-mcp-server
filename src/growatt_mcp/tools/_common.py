"""Helpers shared by the tool modules."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from ..api import GrowattAPIError, GrowattError, GrowattHTTPError, GrowattTransportError

READ_ANNOTATIONS = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)
WRITE_ANNOTATIONS = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True)

# Parameter types shared across tools, with descriptions that end up in the tool's input schema.
PlantId = Annotated[str | int, Field(description="Plant ID, as returned by get_plants.")]
OptionalPlantId = Annotated[
    str | int, Field(description="Plant ID, as returned by get_plants. Empty means all plants.")
]
DeviceSn = Annotated[str, Field(description="Device serial number.")]
DeviceType = Annotated[
    str,
    Field(description='Device type such as "min", "sph", "spa", "max", "inv", "wit", "tlx". get_devices returns it.'),
]
UserId = Annotated[str | int, Field(description="End-user ID (c_user_id) as returned by list_users.")]
Page = Annotated[int, Field(ge=1, description="Page number, starting at 1.")]


ToolDecorator = Callable[[Callable[..., Any]], Callable[..., Any]]


class Registrar:
    """Registers tools on a FastMCP app, tagging them as read-only or state-changing.

    With ``read_only=True`` the state-changing tools are silently not registered.
    """

    def __init__(self, app: FastMCP, *, read_only: bool = False) -> None:
        self.app = app
        self.read_only = read_only

    def read(self) -> ToolDecorator:
        return self.app.tool(annotations=READ_ANNOTATIONS)

    def write(self) -> ToolDecorator:
        if self.read_only:
            return lambda fn: fn
        return self.app.tool(annotations=WRITE_ANNOTATIONS)


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


async def run(call: Awaitable[Any]) -> str:
    """Await an API call and render the result, or a structured error, as JSON text.

    Errors are returned rather than raised so the assistant sees what Growatt said
    (wrong token, unknown device, parameter out of range) instead of a generic tool failure.
    """
    try:
        return to_json(await call)
    except GrowattAPIError as exc:
        return to_json({"error": {"type": "api", "code": exc.code, "message": exc.message, "payload": exc.payload}})
    except GrowattHTTPError as exc:
        return to_json({"error": {"type": "http", "status": exc.status_code, "message": _http_reason(exc)}})
    except GrowattTransportError as exc:
        return to_json({"error": {"type": "transport", "message": exc.reason}})
    except GrowattError as exc:
        return to_json({"error": {"type": "client", "message": str(exc)}})


def _http_reason(exc: GrowattHTTPError) -> Any:
    """Return the JSON body of an HTTP error if there is one; otherwise only a short, generic reason.

    Non-JSON bodies (HTML error pages, captive portals) are not forwarded to the model.
    """
    try:
        return json.loads(exc.body)
    except (json.JSONDecodeError, TypeError):
        return f"HTTP {exc.status_code} from {exc.method} {exc.path} (non-JSON body omitted)"
