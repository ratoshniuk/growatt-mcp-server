"""MCP tool definitions, one module per API area."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..api import GrowattClient
from . import control, devices, max_inverters, plants, users
from ._common import Registrar

TOOL_MODULES = (plants, devices, control, max_inverters, users)


def register_tools(app: FastMCP, client: GrowattClient, *, read_only: bool = False) -> None:
    """Register every tool from every module on ``app``. With ``read_only``, skip state-changing tools."""
    registrar = Registrar(app, read_only=read_only)
    for module in TOOL_MODULES:
        module.register(registrar, client)


__all__ = ["TOOL_MODULES", "register_tools"]
