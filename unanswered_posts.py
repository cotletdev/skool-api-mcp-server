#!/usr/bin/env python3
"""Find recent Skool posts that nobody has commented on yet, so you (or your agent) can reply.

    python unanswered_posts.py --group yourgroup --days 7
"""
import argparse
from datetime import datetime, timedelta, timezone

from cotlet_client import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--days", type=int, default=7, help="Look back this many days (default 7)")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    posts = paginate("list_posts", {"group": args.group, "since": since, "limit": 50}, "posts")
    write_rows([p for p in posts if not p.get("comments")], args.out)


if __name__ == "__main__":
    run(main)
