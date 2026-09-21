"""MCP server for Growatt solar inverters, batteries and grid data."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("growatt-mcp")
except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
    __version__ = "0.0.0"

from .api import GrowattAPIError, GrowattClient, GrowattError, GrowattHTTPError
from .config import ConfigError, Settings, load_settings
from .server import create_app, main

__all__ = [
    "ConfigError",
    "GrowattAPIError",
    "GrowattClient",
    "GrowattError",
    "GrowattHTTPError",
    "Settings",
    "__version__",
    "create_app",
    "load_settings",
    "main",
]
