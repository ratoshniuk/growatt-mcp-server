# Contributing

Thanks for taking the time to contribute.

## Setup

```bash
git clone https://github.com/ratoshniuk/growatt-mcp-server.git
cd growatt-mcp-server
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
5. Update the tool table in `README.md` and add a line to `CHANGELOG.md`.

## Updating the API collection

Export the collection from Postman, strip real tokens and serial numbers, replace
`tests/fixtures/shineserver_public.postman_collection.json`, run the tests, then update
`sha256` and `captured` in `src/growatt_mcp/api/contract.py`.

## Security

Never commit a Growatt token. `.gitignore` excludes `.env`, `.mcp.json` and similar files, and the
contract tests fail if the fixture contains anything that looks like a token.
