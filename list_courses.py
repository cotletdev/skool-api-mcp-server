#!/usr/bin/env python3
"""List Classroom courses of a Skool group with their modules, unlock rule and URLs.

    python list_courses.py --group yourgroup
    python list_courses.py --group yourgroup --out courses.csv
"""
import argparse

from cotlet_client import call, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = []
    for course in call("list_courses", {"group": args.group}).get("courses", []):
        for i, module in enumerate(course.get("modules") or [{}], start=1):
            rows.append({"course_id": course["course_id"], "course": course["title"], "unlock": course["unlock"],
                         "module_no": i if module else None, "module": module.get("title"), "url": module.get("url")})
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
