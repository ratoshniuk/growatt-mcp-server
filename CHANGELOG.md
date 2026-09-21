# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-09-21

### Added
- Full coverage of the Growatt ShineServer Public API Postman collection (26 endpoints):
  user management, plant creation and modification, dataloggers, storage devices,
  MAX-series inverter data and settings.
- 13 new MCP tools: `get_user_plants`, `add_plant`, `modify_plant`, `get_dataloggers`,
  `add_datalogger`, `add_storage_device`, `get_max_data`, `get_max_batch_data`,
  `set_max_parameter`, `list_users`, `check_user`, `register_user`, `modify_user`.
- `GROWATT_REGION` (`global`/`eu`/`cn`/`us`) and `GROWATT_TIMEOUT` settings.
- `growatt-mcp --version`.
- Structured error reporting: API and HTTP errors are returned to the assistant as JSON.
- API contract pin (`growatt_mcp.api.contract`) and contract tests against an endpoint contract
  derived from the community Postman collection (methods, paths, parameter names and placement).
- `GROWATT_READ_ONLY=1` hides every state-changing tool; all tools carry MCP read-only /
  destructive annotations and per-parameter descriptions.
- Numeric plant and user IDs are accepted by the tools.
- Transport failures (DNS, connection, timeout) are reported as `{"error": {"type": "transport"}}`.
- `mypy --strict` type checking, `py.typed` marker, GitHub Actions CI with pip-audit, SHA-pinned
  actions, Dependabot, `SECURITY.md`.

### Changed
- Package restructured into `api/` (one module per endpoint group behind a `GrowattClient`
  facade) and `tools/` (one module per group). `GrowattClient` methods moved to resources:
  `client.plant_list()` is now `client.plants.list()`, and so on.
- Non-zero `error_code` / `code` in a 200 response now raises `GrowattAPIError` instead of
  being returned silently.
- The HTTP client is closed when the MCP server's lifespan ends; `GROWATT_BASE_URL` must be https.
- httpx request logging is silenced so query parameters never reach client log files.
- Non-JSON HTTP error bodies are no longer forwarded to the assistant.

## [0.1.0] - 2026-09-21

### Added
- Initial release: 13 tools covering plants, devices, real-time and historical data,
  on/off, power limit and VPP parameters.
