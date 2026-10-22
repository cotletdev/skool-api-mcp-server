#!/usr/bin/env python3
"""Show your unread Skool Chat (DM) conversations with the full message thread.

python unread_messages.py
python unread_messages.py --all --out inbox.json
"""

import argparse

from skool_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="Include conversations without unread messages")
    parser.add_argument("--max", type=int, default=50, help="Max conversations (default 50)")
    parser.add_argument("--out", help="Save to .json instead of printing")
    args = parser.parse_args()

    params = {"unread_only": not args.all, "limit": 30}
    rows = []
    for conv in paginate("list_conversations", params, "conversations", args.max):
        thread = call("get_conversation", {"conversation_id": conv["conversation_id"]})
        rows.append({**conv, "messages": thread.get("messages", [])})
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
