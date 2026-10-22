#!/usr/bin/env python3
"""Publish a post to a Skool community feed, as you, and optionally pin it.

    python create_post.py --group yourgroup --category Announcements \
        --title "Week 12 challenge" --body-file post.md --pin

Links and images go in the body as URLs. Admin-only categories need an admin account.
"""

import argparse
import json
from pathlib import Path

from skool_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--category", required=True, help="Category name, e.g. Announcements")
    parser.add_argument("--title", required=True)
    body = parser.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="Post text")
    body.add_argument("--body-file", help="Read the post text from a file (Markdown or plain text)")
    parser.add_argument("--pin", action="store_true", help="Pin the post to the top of the feed (admins)")
    args = parser.parse_args()

    text = args.body if args.body is not None else Path(args.body_file).read_text(encoding="utf-8")
    post = call("create_post", {"group": args.group, "title": args.title, "body": text, "category": args.category})
    print(json.dumps(post, indent=2))
    if args.pin and post.get("post_id"):
        print(json.dumps(call("pin_post", {"group": args.group, "post_id": post["post_id"]}), indent=2))


if __name__ == "__main__":
    run(main)
