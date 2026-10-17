"""Tiny client for the Skool API hosted by Cotlet (https://cotlet.dev).

Every script in this repo imports it. Standard library only, Python 3.9+.

    from cotlet_client import call
    groups = call("list_groups")["groups"]

Set COTLET_API_KEY in your environment or in a .env file next to the scripts.
Get a key at https://cotlet.dev/app/signup?app=skool
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterator

API_BASE = os.environ.get("COTLET_API_BASE", "https://cotlet.dev/api/v1")
APP = "skool"
SIGNUP_URL = "https://cotlet.dev/app/signup?app=skool"
DOCS_URL = "https://cotlet.dev/integrations/skool-api-mcp-server"
USER_AGENT = "cotletdev-skool-api-mcp-server/1.0 (+https://github.com/cotletdev/skool-api-mcp-server)"


class CotletError(Exception):
    """An error returned by the API, with the code and the link to act on."""

    def __init__(self, status: int, body: dict[str, Any]):
        self.status = status
        self.code = body.get("error", "unknown_error")
        self.body = body
        link = body.get("browser_url") or body.get("connect_url") or body.get("request_access_url") or body.get("docs_url")
        message = body.get("message", "The request failed.")
        super().__init__(f"{self.code}: {message}" + (f"\n  -> {link}" if link else ""))


def _load_dotenv() -> None:
    """Read KEY=value lines from .env next to this file, without overriding the environment."""
    path = Path(__file__).with_name(".env")
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def api_key() -> str:
    _load_dotenv()
    key = os.environ.get("COTLET_API_KEY", "").strip()
    if not key:
        sys.exit(
            "COTLET_API_KEY is not set.\n"
            f"1. Request access and get your key: {SIGNUP_URL}\n"
            "2. Connect your Skool account once in the Cotlet console.\n"
            "3. export COTLET_API_KEY=cotlet_...  (or put it in .env)"
        )
    return key


def _request(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload or {}).encode() if method == "POST" else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key()}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as err:
            body = json.loads(err.read() or b"{}")
            if err.code == 429 and attempt < 4:
                time.sleep(int(err.headers.get("Retry-After", "5")))
                continue
            raise CotletError(err.code, body) from None
    raise CotletError(429, {"error": "rate_limited", "message": "Still rate limited after 5 tries."})


def wait_for_call(call_id: str, confirm_url: str, timeout: int = 900) -> dict[str, Any]:
    """Write actions wait for your OK by default. Poll until you approve or decline."""
    print(f"Waiting for your OK: {confirm_url}", file=sys.stderr)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(5)
        _, body = _request("GET", f"{API_BASE}/calls/{call_id}")
        if body.get("status") not in ("awaiting_confirmation", "running", "queued"):
            return body.get("result", body)
    raise TimeoutError(f"No confirmation within {timeout}s for call {call_id}.")


def call(endpoint: str, params: dict[str, Any] | None = None, wait: bool = True) -> dict[str, Any]:
    """Call one Skool endpoint, e.g. call("list_members", {"group": "yourgroup"})."""
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    status, body = _request("POST", f"{API_BASE}/{APP}/{endpoint}", clean)
    if status == 202 and body.get("status") == "awaiting_confirmation":
        return wait_for_call(body["call_id"], body["confirm_url"]) if wait else body
    return body


def paginate(endpoint: str, params: dict[str, Any], key: str, max_items: int | None = None) -> Iterator[dict[str, Any]]:
    """Yield every item of a list endpoint, following next_cursor."""
    params = dict(params)
    seen = 0
    while True:
        page = call(endpoint, params)
        for item in page.get(key, []):
            yield item
            seen += 1
            if max_items and seen >= max_items:
                return
        cursor = page.get("next_cursor")
        if not cursor:
            return
        params["cursor"] = cursor


def write_rows(rows: list[dict[str, Any]], out: str | None) -> None:
    """Print JSON to stdout, or save .csv / .json when a path is given."""
    if not out:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    path = Path(out)
    if path.suffix.lower() == ".csv":
        fields: list[str] = []
        for row in rows:
            fields += [k for k in row if k not in fields]
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})
    else:
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(rows)} rows to {path}", file=sys.stderr)


def run(main) -> None:
    """Run a script's main() and turn API errors into a readable message."""
    try:
        main()
    except CotletError as err:
        sys.exit(f"Error {err.status} {err}")
    except KeyboardInterrupt:
        sys.exit(130)
