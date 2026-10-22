#!/usr/bin/env python3
"""Pin or unpin a Skool post: on the feed (up to 3) or on a Classroom page (up to 12). Admins only.

python pin_post.py --group yourgroup --post-id a3f9c2e1b7d84c06
python pin_post.py --group yourgroup --post-id a3f9c2e1b7d84c06 --unpin
"""

import argparse
import json

from skool_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--unpin", action="store_true")
    parser.add_argument("--course-page-id", help="Pin to this Classroom page instead of the feed")
    args = parser.parse_args()
    params = {
        "group": args.group,
        "post_id": args.post_id,
        "pinned": not args.unpin,
        "course_page_id": args.course_page_id,
    }
    print(json.dumps(call("pin_post", params), indent=2))


if __name__ == "__main__":
    run(main)
