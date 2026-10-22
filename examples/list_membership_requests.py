#!/usr/bin/env python3
"""List pending requests to join a Skool group, with each applicant's Membership Questions answers.

    python list_membership_requests.py --group yourgroup
    python list_membership_requests.py --group yourgroup --out requests.csv

Admins and moderators only.
"""

import argparse

from skool_api_mcp.scripting import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = []
    for req in paginate("list_membership_requests", {"group": args.group, "limit": 100}, "requests"):
        answers = req.pop("answers", [])
        req["answers"] = " | ".join(f"{a['question']}: {a['answer']}" for a in answers)
        rows.append(req)
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
