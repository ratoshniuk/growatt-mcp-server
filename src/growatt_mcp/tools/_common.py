"""Helpers shared by the tool modules."""

from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any

from ..api import GrowattAPIError, GrowattError, GrowattHTTPError


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
        return to_json({"error": {"type": "http", "status": exc.status_code, "message": exc.body[:500]}})
    except GrowattError as exc:
        return to_json({"error": {"type": "client", "message": str(exc)}})
