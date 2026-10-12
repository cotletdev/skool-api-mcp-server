#!/usr/bin/env python3
"""Get one Skool post with its full body, attachments and the whole comment tree.

    python get_post.py --group yourgroup --post-id a3f9c2e1b7d84c06
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--post-id", required=True, help="Post ID from export_posts.py")
    args = parser.parse_args()
    print(json.dumps(call("get_post", {"group": args.group, "post_id": args.post_id}), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run(main)
