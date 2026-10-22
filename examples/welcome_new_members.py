#!/usr/bin/env python3
"""Send everyone who joined your Skool group in the last N days a personal welcome DM with your Start Here course link.

    python welcome_new_members.py --group yourgroup --days 7 --dry-run
    python welcome_new_members.py --group yourgroup --days 7 --course "Start Here"

The message template can use {first_name}, {name} and {course_url}.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from skool_api_mcp.scripting import call, paginate, run

DEFAULT_TEMPLATE = "Hi {first_name}, welcome to the community! Start here, it takes 10 minutes: {course_url}"


def course_url(group: str, title: str | None) -> str:
    courses = call("list_courses", {"group": group}).get("courses", [])
    for course in courses:
        if title is None or course["title"].lower() == title.lower():
            modules = course.get("modules") or []
            if modules:
                return modules[0]["url"]
    return f"https://www.skool.com/{group}/classroom"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--course", help="Course title to link (default: the first course)")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--dry-run", action="store_true", help="Print the messages without sending")
    args = parser.parse_args()

    since = (date.today() - timedelta(days=args.days)).isoformat()
    url = course_url(args.group, args.course)
    members = paginate(
        "list_members", {"group": args.group, "joined_since": since, "role": "member", "limit": 100}, "members"
    )
    for member in members:
        text = args.template.format(first_name=member["name"].split()[0], name=member["name"], course_url=url)
        if args.dry_run:
            print(f"--> {member['name']}: {text}")
            continue
        result = call("send_message", {"member_id": member["member_id"], "body": text})
        print(f"{member['name']}: {result.get('status')}")


if __name__ == "__main__":
    run(main)
