"""Regenerate tests/fixtures/shineserver_public_endpoints.json from a Postman collection export.

Usage: uv run python scripts/derive_contract.py /path/to/ShineServer_Public.postman_collection.json

Only HTTP methods, paths and parameter names are kept. The raw collection is third-party content and
may contain example credentials; do not commit it.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "shineserver_public_endpoints.json"


def _walk(items: list[dict[str, Any]], folder: str = ""):
    for item in items:
        if "item" in item:
            yield from _walk(item["item"], f"{folder}/{item['name']}")
        else:
            yield folder.strip("/"), item


def derive(collection: dict[str, Any]) -> dict[str, Any]:
    endpoints: dict[tuple[str, str], dict[str, Any]] = {}
    for folder, item in _walk(collection["item"]):
        request = item["request"]
        url = request["url"]
        raw = url["raw"] if isinstance(url, dict) else url
        parts = urlsplit(raw.replace("{{baseUrl}}", "https://host"))
        if not (parts.netloc and parts.path):
            continue
        key = (request["method"].upper(), parts.path)
        entry = endpoints.setdefault(key, {"query": set(), "body": set(), "documented_as": []})
        if isinstance(url, dict):
            entry["query"] |= {q["key"] for q in url.get("query") or []}
        body = request.get("body") or {}
        entry["body"] |= {p["key"] for p in body.get("urlencoded") or body.get("formdata") or []}
        entry["documented_as"].append(f"{folder} / {item['name']}")
    return {
        "name": "Growatt ShineServer Public API endpoint contract",
        "description": (
            "Derived from the community-maintained Postman collection 'ShineServer Public' "
            "(workspace gold-water-163355), which documents Growatt's ShineServer Public API. "
            "Only HTTP methods, paths and parameter names are kept; no example values, credentials or identifiers."
        ),
        "source": {
            "postman_id": collection["info"].get("_postman_id"),
            "workspace": "https://www.postman.com/gold-water-163355/workspace/growatt-public",
            "docs": "https://www.showdoc.com.cn/2598832417617967/11558377939801334",
        },
        "captured": dt.date.today().isoformat(),
        "endpoints": [
            {
                "method": method,
                "path": path,
                "query": sorted(entry["query"]),
                "body": sorted(entry["body"]),
                "documented_as": entry["documented_as"],
            }
            for (method, path), entry in sorted(endpoints.items(), key=lambda kv: (kv[0][1], kv[0][0]))
        ],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    collection = json.loads(Path(argv[1]).read_text())
    contract = derive(collection)
    OUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"wrote {OUT.relative_to(ROOT)}: {len(contract['endpoints'])} endpoints")
    print(f"update src/growatt_mcp/api/contract.py: sha256={digest} captured={contract['captured']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
