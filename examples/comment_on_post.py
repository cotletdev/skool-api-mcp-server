#!/usr/bin/env python3
"""Comment on a Skool post, or reply under a comment, as you.

python comment_on_post.py --group yourgroup --post-id a3f9c2e1b7d84c06 --body "Great first week!"
python comment_on_post.py --group yourgroup --post-id a3f9c2e1b7d84c06 --reply-to c_77ab --body "Thanks!"
"""

import argparse
import json

from skool_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--body", required=True, help="Comment text")
    parser.add_argument("--reply-to", help="Comment ID to reply under")
    args = parser.parse_args()
    params = {"group": args.group, "post_id": args.post_id, "body": args.body, "parent_comment_id": args.reply_to}
    print(json.dumps(call("comment_on_post", params), indent=2))


if __name__ == "__main__":
    run(main)
