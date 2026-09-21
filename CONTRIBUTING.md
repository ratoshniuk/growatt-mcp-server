# Contributing

Thanks for taking the time to contribute.

## Setup

```bash
git clone https://github.com/ratoshniuk/growatt-mcp-server.git
cd growatt-mcp-server   # or whatever directory you cloned into
uv sync --group dev
```

## Before you open a pull request

```bash
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pytest
```

CI runs the same four commands plus a server start-up smoke test on Python 3.11, 3.12 and 3.13.

## Adding or changing an endpoint

1. Add the method to the matching resource in `src/growatt_mcp/api/` (`plants.py`, `devices.py`, ...).
2. Add a unit test in `tests/unit/api/` asserting the exact HTTP method, path and parameters.
3. Add the call to `CLIENT_CALLS` in `tests/contract/test_api_contract.py`. The contract test will
   fail if the request does not exist in the pinned Postman collection.
4. Expose it as a tool in `src/growatt_mcp/tools/` and add its name to `tests/unit/tools/test_registry.py`.
   State-changing tools must say "Changes state on Growatt's side." in their description.
5. Read tools use `@reg.read()`, state-changing tools `@reg.write()`; describe every parameter with `Field(description=...)`.
6. Update the tool table in `README.md` and add a line to `CHANGELOG.md`.

## Updating the API contract

The fixture `tests/fixtures/shineserver_public_endpoints.json` holds only HTTP methods, paths and
parameter names. It is derived from the community Postman collection "ShineServer Public"; the raw
collection is not stored in this repository because it is third-party content and contains example
values. To refresh it:

1. Export the collection from Postman to a file outside the repository.
2. Run `uv run python scripts/derive_contract.py /path/to/collection.json`, which rewrites the fixture.
3. Run `uv run pytest`; the contract tests report what changed.
4. Update `sha256` and `captured` in `src/growatt_mcp/api/contract.py` and add a changelog entry.

## Licensing of contributions

By submitting a contribution you agree that it is licensed under the project's MIT license.

## Security

Never commit a Growatt token. `.gitignore` excludes `.env`, `.mcp.json` and similar files, and the
contract fixture holds parameter names only, so it cannot carry a token.
