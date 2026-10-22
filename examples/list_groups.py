#!/usr/bin/env python3
"""List every Skool group your account belongs to, with your role and member count.

    python list_groups.py
    python list_groups.py --out groups.csv

The `group` value of each row is what the other scripts take as --group
(e.g. "yourgroup" for skool.com/yourgroup).
"""

import argparse

from skool_api_mcp.scripting import call, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()
    write_rows(call("list_groups").get("groups", []), args.out)


if __name__ == "__main__":
    run(main)
