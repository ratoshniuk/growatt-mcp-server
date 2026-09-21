"""MCP tool definitions, one module per API area."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from . import control, devices, max, plants, users

TOOL_MODULES = (plants, devices, control, max, users)


def register_tools(app: FastMCP, client: GrowattClient) -> None:
    """Register every tool from every module on ``app``."""
    for module in TOOL_MODULES:
        module.register(app, client)


__all__ = ["TOOL_MODULES", "register_tools"]
