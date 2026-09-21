# Growatt MCP Server

[![CI](https://github.com/ratoshniuk/growatt-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ratoshniuk/growatt-mcp-server/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/protocol-MCP-6f42c1.svg)](https://modelcontextprotocol.io)

An [MCP](https://modelcontextprotocol.io) server that lets AI assistants (Claude Code, Claude Desktop, Cursor, VS Code, Codex, Gemini CLI and any other MCP client) read and control a Growatt solar installation through the official **Growatt ShineServer Public API**.

Ask things like "how much did my panels generate today?", "what is the battery SOC?", "compare today with yesterday hour by hour", or "set the discharge cut-off to 15%", and the assistant calls the right endpoint for you.

- **Complete API coverage.** All 27 documented endpoints are implemented and exposed as 26 tools.
- **Contract-tested.** Every request is verified against a pinned endpoint contract, so upstream changes are caught by CI, not by users.
- **Typed, tested, linted.** `mypy --strict`, 130+ tests, ruff, pip-audit, and a server start-up smoke test on Python 3.11 to 3.13.
- **Safe by design.** State-changing tools carry MCP `readOnlyHint=false` / `destructiveHint=true` annotations and can be disabled with `GROWATT_READ_ONLY=1`. Errors from Growatt come back as structured JSON the assistant can read.

## Table of contents

- [Tools](#tools)
- [Requirements](#requirements)
- [Getting a Growatt API token](#getting-a-growatt-api-token)
- [Installation](#installation)
- [Connecting to an MCP client](#connecting-to-an-mcp-client)
- [Configuration](#configuration)
- [Example prompts](#example-prompts)
- [Notes and gotchas](#notes-and-gotchas)
- [API version and contract testing](#api-version-and-contract-testing)
- [Official Growatt resources](#official-growatt-resources)
- [Project layout](#project-layout)
- [Development](#development)
- [Disclaimer](#disclaimer)
- [License](#license)

## Tools

Tools marked **writes** change state on Growatt's side. They are annotated as non-read-only so MCP clients can ask for confirmation, and they disappear entirely when the server runs with `GROWATT_READ_ONLY=1`.

### Plants (power stations)

| Tool | Endpoint | Description |
|---|---|---|
| `get_plants` | `GET /v1/plant/list` | Plants visible to the account |
| `get_plant_details` | `POST /v1/plant/details` | Name, location, peak power, timezone |
| `get_plant_data` | `GET /v1/plant/data` | Today's / monthly / yearly / total energy, current power |
| `get_plant_energy` | `GET /v1/plant/energy` | Daily, monthly or yearly history (max 7 days per call) |
| `get_user_plants` | `POST /v1/plant/user_plant_list` | Plants of a specific end user |
| `add_plant` **writes** | `POST /v1/plant/add` | Create a plant for an end user |
| `modify_plant` **writes** | `POST /v1/plant/modify` | Rename a plant or change its currency |

### Devices

| Tool | Endpoint | Description |
|---|---|---|
| `get_devices` | `GET /v1/device/list`, `POST /v4/new-api/queryDeviceList` | Devices of a plant, or all devices paginated |
| `get_device_info` | `POST /v4/new-api/queryDeviceInfo` | Model, firmware, configured settings |
| `get_device_last_data` | `POST /v4/new-api/queryLastData` | Real-time PV, load, grid, battery SOC, temperatures, faults |
| `get_device_history` | `POST /v4/new-api/queryHistoricalData` | Five-minute readings for one day |
| `check_device_sn` | `GET /v1/device/check/sn` | Device type and registration status of a serial |
| `get_dataloggers` | `GET /v1/device/datalogger/list` | ShineWiFi / ShineLAN sticks on a plant |
| `add_datalogger` **writes** | `POST /v1/device/datalogger/add` | Attach a datalogger to a plant |
| `add_storage_device` **writes** | `POST /v1/device/storage/add` | Attach a storage device to a plant |

### Control

| Tool | Endpoint | Description |
|---|---|---|
| `set_device_on_off` **writes** | `POST /v4/new-api/setOnOrOff` | Switch a device on or off |
| `set_device_power` **writes** | `POST /v4/new-api/setPower` | Active power limit (percent, or watts for NOAH/NEXA) |
| `read_device_parameter` | `POST /v4/new-api/readVppParameter` | Read a VPP parameter, e.g. discharge cut-off SOC |
| `set_device_parameter` **writes** | `POST /v4/new-api/setVppParameter` | Write a VPP parameter or time schedule |

### MAX-series inverters

| Tool | Endpoint | Description |
|---|---|---|
| `get_max_data` | `GET /v1/device/max/max_data_info` | Latest data for one MAX inverter |
| `get_max_batch_data` | `POST /v1/device/max/maxs_data` | Latest data for several MAX inverters |
| `set_max_parameter` **writes** | `POST /v1/maxSet` | Write a register on a MAX inverter |

### Users (installer / distributor accounts)

| Tool | Endpoint | Description |
|---|---|---|
| `list_users` | `GET /v1/user/c_user_list` | End-user accounts managed by this account |
| `check_user` | `POST /v1/user/check_user` | Whether a user name exists |
| `register_user` **writes** | `POST /v1/user/user_register` | Create an end-user account |
| `modify_user` **writes** | `POST /v1/user/modify` | Update an end-user's mobile number |

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Growatt account with at least one plant, and an API token

## Getting a Growatt API token

The token is issued in the **ShinePhone** mobile app (the same app you use to monitor the plant). No developer registration is needed.

1. Open ShinePhone, log in with your Growatt account and tap **Me** in the bottom bar.
2. On the **Me** screen, tap your username at the top.
3. In the profile, tap **API Token** (last row).
4. Tap the copy icon next to the token value.
5. Make sure **Use Status** is switched on, otherwise the API rejects the token.

| Step 1 | Step 2 | Step 3 | Steps 4–5 |
|---|---|---|---|
| ![Dashboard](docs/images/1-dashboard.jpg) | ![Me screen](docs/images/2-me.jpg) | ![Profile](docs/images/3-profile.jpg) | ![API Token](docs/images/4-api-token.jpg) |

Screenshots show Growatt's ShinePhone app and are used for illustration only.

Keep the token private: it grants full read and write access to your installation, including inverter settings. If it leaks, open the same screen and tap **Reopen** to issue a new one.

## Installation

```bash
git clone https://github.com/ratoshniuk/growatt-mcp-server.git growatt-mcp
cd growatt-mcp
uv sync
```

Quick check that the server starts (it speaks MCP over stdio, so it waits for input; press Ctrl+C to exit):

```bash
GROWATT_TOKEN=your_token uv run growatt-mcp
uv run growatt-mcp --version
```

If the token is missing the server exits with code 2 and explains where to get one.

Without uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
GROWATT_TOKEN=your_token growatt-mcp
```

## Connecting to an MCP client

The server speaks MCP over stdio, so it works with any MCP-capable client. There are two ways to launch it:

- **From a local clone** (recommended if you want to edit the code):
  `uv --directory /absolute/path/to/growatt-mcp run growatt-mcp`
- **Straight from GitHub, no clone** (uvx downloads and caches it):
  `uvx --from git+https://github.com/ratoshniuk/growatt-mcp-server growatt-mcp`

The examples below use the local-clone form. To use the no-clone form, replace `"command": "uv"` with `"command": "uvx"` and the args with `["--from", "git+https://github.com/ratoshniuk/growatt-mcp-server", "growatt-mcp"]`. Some GUI clients don't inherit your shell `PATH`; if the server fails to start, use the full path from `which uv` or `which uvx`.

Restart the client after saving its configuration.

### Claude Code

```bash
claude mcp add growatt \
  -e GROWATT_TOKEN=your_token \
  -- uv --directory /absolute/path/to/growatt-mcp run growatt-mcp
```

Add `-s user` to make it available in every project instead of only the current one.

### Claude Desktop

Edit `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "growatt": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": {
        "GROWATT_TOKEN": "your_token"
      }
    }
  }
}
```

### Cursor

Settings → MCP → Add new global MCP server, or edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project). Same format as Claude Desktop:

```json
{
  "mcpServers": {
    "growatt": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "your_token" }
    }
  }
}
```

### VS Code (GitHub Copilot agent mode)

Create `.vscode/mcp.json` in your workspace, or run **MCP: Add Server** from the command palette. VS Code can prompt for the token so it is not stored in plain text:

```json
{
  "inputs": [
    { "id": "growatt-token", "type": "promptString", "description": "Growatt API token", "password": true }
  ],
  "servers": {
    "growatt": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "${input:growatt-token}" }
    }
  }
}
```

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json` (or Settings → Cascade → MCP Servers → Manage):

```json
{
  "mcpServers": {
    "growatt": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "your_token" }
    }
  }
}
```

### Cline (VS Code extension)

Open the MCP Servers panel → Configure MCP Servers, which opens `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "growatt": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "your_token" },
      "disabled": false
    }
  }
}
```

### Zed

Add to `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "growatt": {
      "source": "custom",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "your_token" }
    }
  }
}
```

### OpenAI Codex CLI

Codex uses TOML. Add to `~/.codex/config.toml`:

```toml
[mcp_servers.growatt]
command = "uv"
args = ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"]
env = { GROWATT_TOKEN = "your_token" }
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "growatt": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "env": { "GROWATT_TOKEN": "your_token" }
    }
  }
}
```

### OpenCode

This repository ships an `opencode.json`, so launching `opencode` from a clone picks the server up automatically. It reads the token from the `GROWATT_TOKEN` environment variable. For a global setup, add the same block to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "growatt": {
      "type": "local",
      "command": ["uv", "--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"],
      "environment": { "GROWATT_TOKEN": "your_token" }
    }
  }
}
```

### Continue

Add to `~/.continue/config.yaml`:

```yaml
mcpServers:
  - name: growatt
    command: uv
    args: ["--directory", "/absolute/path/to/growatt-mcp", "run", "growatt-mcp"]
    env:
      GROWATT_TOKEN: your_token
```

### Any other client, or testing without a client

Point the client at the stdio command above. To poke at the tools interactively, use the MCP Inspector:

```bash
GROWATT_TOKEN=your_token npx @modelcontextprotocol/inspector \
  uv --directory /absolute/path/to/growatt-mcp run growatt-mcp
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROWATT_TOKEN` | yes | | ShinePhone API token |
| `GROWATT_REGION` | no | `global` | Picks the regional API host: `global` / `eu` (`openapi.growatt.com`), `cn` (`openapi-cn.growatt.com`), `us` (`openapi-us.growatt.com`) |
| `GROWATT_BASE_URL` | no | | Explicit API host (https only); overrides `GROWATT_REGION` |
| `GROWATT_TIMEOUT` | no | `30` | HTTP timeout in seconds |
| `GROWATT_READ_ONLY` | no | `0` | Set to `1` to register only the read tools; the ten state-changing tools are not exposed at all |

## Example prompts

- "List my plants and show today's generation."
- "Get the latest data from inverter YOUR_DEVICE_SN (type `min`) and tell me the battery SOC and grid import."
- "Fetch the 5-minute history for today and yesterday and compare hourly PV, load and battery charge."
- "Read `set_param_23` on my inverter." (discharge cut-off SOC)
- "Which dataloggers are attached to plant 123?"

## Notes and gotchas

- **Device types.** Most tools need a `device_type` such as `min`, `sph`, `spa`, `max`, `inv`, `wit`, `tlx`. `get_devices` returns the right value for each device.
- **Timestamps in history data.** The `calendar` field is a Unix epoch built from the plant's local wall-clock interpreted as UTC+8. To get local time, treat the epoch as UTC and add 8 hours.
- **"Today" counters undercount at night.** Fields like `etoUserToday` only accumulate while the inverter is running. On hybrid systems that idle overnight at the battery cut-off SOC, grid import from the meter is still visible in `pacToUserTotal` of the 5-minute history, so integrate that series for a true figure.
- **Errors are data.** When a call fails, the tool returns `{"error": {"type": "api" | "http" | "transport" | "client", ...}}` instead of raising, so the assistant can explain what went wrong. Non-JSON HTTP error bodies are not forwarded.
- **Rate limits.** The Growatt API throttles aggressive polling. Prefer `get_device_history` (one call per day) over repeated `get_device_last_data`.
- **Date ranges.** `get_plant_energy` accepts at most 7 days per request; page through for longer periods.

## API version and contract testing

Growatt does not publish version numbers for the ShineServer Public API, and there is no endpoint that reports which revision a server runs. This project pins the contract instead:

| | |
|---|---|
| API | Growatt ShineServer Public API (v1 and v4 "new-api" endpoints) |
| Documented by | community-maintained Postman collection **ShineServer Public** (workspace `gold-water-163355`, id `bcc659f1-4ba7-4c5d-a7ad-526d3c8c8fd9`), which links Growatt's own API documentation |
| Captured | 2026-09-21 |
| Fixture | [`tests/fixtures/shineserver_public_endpoints.json`](tests/fixtures/shineserver_public_endpoints.json): methods, paths and parameter names only, derived from the collection. No example values, credentials or identifiers |
| Pinned in | [`src/growatt_mcp/api/contract.py`](src/growatt_mcp/api/contract.py): source, capture date, SHA-256 of the fixture |
| Coverage | 27 endpoints in the contract, 27 implemented, exposed as 26 tools |

[`tests/contract/test_api_contract.py`](tests/contract/test_api_contract.py) sends every client method through a mock transport and checks that its HTTP method, path, and parameter names and placement (query string vs form body) exist in the contract. It also fails if the contract contains an endpoint the client does not implement, if the client has a method the test table does not cover, or if the fixture changes without the pin being updated.

To adopt a newer collection, follow [CONTRIBUTING.md](CONTRIBUTING.md#updating-the-api-contract); the failing tests report exactly which endpoints or parameters changed.

## Official Growatt resources

- Growatt: <https://en.growatt.com/>
- ShineServer monitoring platform: <https://server.growatt.com/>
- ShinePhone app (where the API token is issued): iOS App Store and Google Play, search "ShinePhone"
- API documentation (linked from Growatt's Postman collection): <https://www.showdoc.com.cn/2598832417617967/11558377939801334>
- Regional API hosts: `https://openapi.growatt.com` (global / Europe), `https://openapi-cn.growatt.com` (China), `https://openapi-us.growatt.com` (North America)
- Growatt platform terms: <https://openapi.growatt.com/userTerms/termsOfUse_en.html>
- Community Postman workspace "Growatt Public" (the source of the endpoint contract): <https://www.postman.com/gold-water-163355/workspace/growatt-public>

## Project layout

```
src/growatt_mcp/
  __init__.py        package version and public exports
  __main__.py        python -m growatt_mcp
  config.py          Settings from GROWATT_* environment variables
  server.py          create_app(), CLI entry point
  api/               async client for the Growatt API
    http.py          auth header, JSON decoding, error translation
    errors.py        GrowattError, GrowattHTTPError, GrowattAPIError
    client.py        GrowattClient facade: .users .plants .devices .control .max
    users.py, plants.py, devices.py, control.py, max_inverters.py   one class per endpoint group
    contract.py      pinned API contract (Postman id, date, SHA-256)
  tools/             MCP tools, one module per endpoint group
    _common.py       Registrar (read/write annotations, read-only mode), shared parameter types, error-to-JSON wrapper
    plants.py, devices.py, control.py, max_inverters.py, users.py
tests/
  conftest.py        recording mock transport, client and app fixtures
  unit/              config, server, api/*, tools/*
  contract/          client requests vs the pinned Postman collection
  fixtures/          endpoint contract (methods, paths, parameter names)
scripts/
  derive_contract.py regenerates the fixture from a Postman export
```

The client is usable on its own, without MCP:

```python
from growatt_mcp import GrowattClient

async with GrowattClient(token) as client:
    plants = await client.plants.list()
    latest = await client.devices.last_data("YOUR_DEVICE_SN", "min")
```

## Development

```bash
uv sync --group dev
uv run growatt-mcp        # run the server
uv run ruff check .       # lint
uv run ruff format .      # format
uv run mypy               # type check (strict)
uv run pytest             # tests
```

CI runs lint, format check, mypy, tests, a server start-up smoke test on Python 3.11, 3.12 and 3.13, and pip-audit for every push and pull request. GitHub Actions are pinned to commit SHAs and Dependabot keeps them and the lockfile current. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

## Disclaimer

This is an independent, community project. It is not affiliated with, endorsed by, or supported by Growatt. Growatt, ShineServer and ShinePhone are trademarks of Shenzhen Growatt New Energy Co., Ltd. Use of the Growatt Public API is subject to [Growatt's terms](https://openapi.growatt.com/userTerms/termsOfUse_en.html). Commands that change inverter settings are executed at your own risk. See [SECURITY.md](SECURITY.md) for the threat model and how to report issues.

## License

[MIT](LICENSE) © Maksym Ratoshniuk
