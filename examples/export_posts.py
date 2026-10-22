#!/usr/bin/env python3
"""Export posts from a Skool community feed: title, author, category, likes, comments, date.

python export_posts.py --group yourgroup --out posts.csv
python export_posts.py --group yourgroup --category Announcements --since 2026-10-01T00:00:00Z
python export_posts.py --group yourgroup --max 200 --out posts.json
"""

import argparse

from skool_api_mcp.scripting import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--category", help="Only posts in this category")
    parser.add_argument("--since", help="Only posts created after this time (ISO 8601)")
    parser.add_argument("--max", type=int, help="Stop after this many posts")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    params = {"group": args.group, "category": args.category, "since": args.since, "limit": 50}
    write_rows(list(paginate("list_posts", params, "posts", args.max)), args.out)


if __name__ == "__main__":
    run(main)
