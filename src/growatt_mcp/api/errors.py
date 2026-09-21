"""Exception hierarchy for the Growatt API client."""

from __future__ import annotations

from typing import Any


class GrowattError(Exception):
    """Base class for every error raised by the client."""


class GrowattTransportError(GrowattError):
    """The request never produced an HTTP response: DNS, connection, TLS or timeout failure."""

    def __init__(self, reason: str, method: str, path: str) -> None:
        self.reason = reason
        self.method = method
        self.path = path
        super().__init__(f"{method} {path} failed: {reason}")


class GrowattHTTPError(GrowattError):
    """The API answered with a non-2xx HTTP status."""

    def __init__(self, status_code: int, body: str, method: str, path: str) -> None:
        self.status_code = status_code
        self.body = body
        self.method = method
        self.path = path
        super().__init__(f"{method} {path} failed with HTTP {status_code}")


class GrowattAPIError(GrowattError):
    """The API answered 200 but reported a non-zero ``error_code`` (v1) or ``code`` (v4)."""

    def __init__(self, code: int | str, message: str, payload: Any, method: str, path: str) -> None:
        self.code = code
        self.message = message
        self.payload = payload
        self.method = method
        self.path = path
        super().__init__(f"{method} {path} returned error {code}: {message or 'no message'}")
