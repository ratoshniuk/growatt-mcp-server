"""Pinned description of the Growatt ShineServer Public API this client was written against.

The MCP server has no way to ask Growatt which API revision it is talking to, so the
contract is pinned here instead. ``tests/contract/test_api_contract.py`` checks that every request
the client sends matches the endpoints and parameter names in the pinned Postman collection,
and that the collection file itself has not changed without this pin being updated.

To adopt a newer collection: replace ``tests/fixtures/shineserver_public.postman_collection.json``
(strip any real tokens first), run the tests, review the diff, then update the fields below.
"""

from __future__ import annotations

API_CONTRACT = {
    "name": "ShineServer Public",
    "source": "Postman collection exported by Growatt",
    "postman_id": "bcc659f1-4ba7-4c5d-a7ad-526d3c8c8fd9",
    "docs": "https://www.showdoc.com.cn/2598832417617967/11558377939801334",
    "captured": "2026-09-21",
    "sha256": "015240502c69382e75ccd1f6804f2f23cce0d9594940eda6b7e498df8b777481",
    "fixture": "tests/fixtures/shineserver_public.postman_collection.json",
}
