#!/usr/bin/env python3
"""Export the members of a Skool group to CSV or JSON: name, role, level, points, join date, profile URL.

    python export_members.py --group yourgroup --out members.csv
    python export_members.py --group yourgroup --role admin
    python export_members.py --group yourgroup --since 2026-10-01 --out new-this-month.csv

Works for groups your own account belongs to. Pages are followed automatically.
"""
import argparse

from cotlet_client import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup for skool.com/yourgroup")
    parser.add_argument("--role", choices=["all", "admin", "moderator", "member"], default="all")
    parser.add_argument("--since", help="Only members who joined on or after this date (YYYY-MM-DD)")
    parser.add_argument("--max", type=int, help="Stop after this many members")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    params = {"group": args.group, "role": args.role, "joined_since": args.since, "limit": 100}
    rows = list(paginate("list_members", params, "members", args.max))
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
