"""Pinned description of the Growatt ShineServer Public API this client was written against.

Growatt does not version the API and the server has no endpoint that reports a revision, so the
contract is pinned here instead. ``tests/contract/test_api_contract.py`` checks that every request the
client sends matches the endpoints and parameter names in the pinned fixture, and that the fixture has
not changed without this pin being updated.

The fixture is a file authored for this project: it lists only HTTP methods, paths and parameter names,
derived from the community-maintained Postman collection "ShineServer Public" that documents the API.
No example values, credentials or identifiers from the collection are kept.

To adopt a newer collection: regenerate ``tests/fixtures/shineserver_public_endpoints.json`` (see
CONTRIBUTING.md), run the tests, review the diff, then update the fields below.
"""

from __future__ import annotations

API_CONTRACT = {
    "name": "Growatt ShineServer Public API",
    "source": "community-maintained Postman collection 'ShineServer Public' (workspace gold-water-163355)",
    "source_url": "https://www.postman.com/gold-water-163355/workspace/growatt-public",
    "postman_id": "bcc659f1-4ba7-4c5d-a7ad-526d3c8c8fd9",
    "docs": "https://www.showdoc.com.cn/2598832417617967/11558377939801334",
    "captured": "2026-09-21",
    "sha256": "4f4715a4fa3b28d6d505fa8adc880234ddbe22e75ee216fa6a9a0c450349655c",
    "fixture": "tests/fixtures/shineserver_public_endpoints.json",
}
