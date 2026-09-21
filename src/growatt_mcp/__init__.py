from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

from . import tools
from .client import GrowattClient


def main() -> None:
    token = os.environ.get("GROWATT_TOKEN")
    if not token:
        print("Error: GROWATT_TOKEN environment variable is required.", file=sys.stderr)
        print("Get your token from the ShinePhone app: Me > username > API Token", file=sys.stderr)
        sys.exit(1)

    app = FastMCP("Growatt Solar v0.1")
    client = GrowattClient(token=token)
    tools.configure(client)
    tools.register_tools(app)
    app.run()
