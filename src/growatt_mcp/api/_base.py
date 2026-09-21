from __future__ import annotations

from .http import HttpClient


class Resource:
    """Base class for an endpoint group that shares one :class:`HttpClient`."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
