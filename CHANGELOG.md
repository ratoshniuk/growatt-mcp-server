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
- API contract pin (`growatt_mcp.api.contract`) and contract tests against the Postman collection.
- `mypy --strict` type checking, `py.typed` marker, GitHub Actions CI.

### Changed
- Package restructured into `api/` (one module per endpoint group behind a `GrowattClient`
  facade) and `tools/` (one module per group). `GrowattClient` methods moved to resources:
  `client.plant_list()` is now `client.plants.list()`, and so on.
- Non-zero `error_code` / `code` in a 200 response now raises `GrowattAPIError` instead of
  being returned silently.

## [0.1.0] - 2026-09-21

### Added
- Initial release: 13 tools covering plants, devices, real-time and historical data,
  on/off, power limit and VPP parameters.
