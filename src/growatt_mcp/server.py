"""MCP server assembly and command-line entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from mcp.server.fastmcp import FastMCP

from .api import GrowattClient
from .config import ConfigError, load_settings
from .tools import register_tools

INSTRUCTIONS = """Tools for a Growatt solar installation via the ShineServer Public API.

Typical flow: get_plants -> get_devices(plant_id) -> get_device_last_data(device_sn, device_type).
Device types are strings such as "min", "sph", "spa", "max", "inv", "wit", "tlx"; get_devices returns them.
Tools whose name starts with set_, add_, modify_ or register_ change state on Growatt's side. Confirm with the
user before calling them.
"""


def create_app(client: GrowattClient) -> FastMCP:
    """Create a FastMCP application with every Growatt tool registered against ``client``."""
    from . import __version__

    app = FastMCP(f"Growatt Solar v{__version__}", instructions=INSTRUCTIONS)
    register_tools(app, client)
    return app


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    from . import __version__

    parser = argparse.ArgumentParser(prog="growatt-mcp", description="MCP server for Growatt solar installations.")
    parser.add_argument("--version", action="version", version=f"growatt-mcp {__version__}")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    _parse_args(argv)
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    client = GrowattClient.from_settings(settings)
    create_app(client).run()
