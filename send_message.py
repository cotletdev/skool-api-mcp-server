#!/usr/bin/env python3
"""Send a Skool Chat direct message to one member, as you.

    python send_message.py --member-id m_8c41d2 --body "Yes, the call is recorded."

Member IDs come from export_members.py or unread_messages.py.
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--member-id", required=True)
    parser.add_argument("--body", required=True, help="Message text")
    args = parser.parse_args()
    print(json.dumps(call("send_message", {"member_id": args.member_id, "body": args.body}), indent=2))


if __name__ == "__main__":
    run(main)
