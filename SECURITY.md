# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's private
vulnerability reporting on this repository ("Security" tab → "Report a vulnerability").
You will get an acknowledgement within a few days.

## Scope and threat model

- The server runs locally, speaks MCP over stdio and never opens a network port.
- The only secret is the Growatt API token. It is read from `GROWATT_TOKEN`, sent to Growatt
  as an HTTP header over HTTPS, and never logged or included in error messages.
- Ten tools change state on your inverter or account. They are annotated as non-read-only so
  MCP clients can ask for confirmation, and they can be disabled entirely with `GROWATT_READ_ONLY=1`.
- Data returned by Growatt is passed to the assistant as tool output. The server instructions tell
  the assistant to treat it as untrusted content; non-JSON HTTP error bodies are not forwarded.

## Supply chain

Dependencies are hash-pinned in `uv.lock`, checked with `pip-audit` in CI, and updated by Dependabot.
GitHub Actions are pinned to commit SHAs.

## If your token leaks

Open ShinePhone → Me → your username → API Token and issue a new one; the old token stops working.
