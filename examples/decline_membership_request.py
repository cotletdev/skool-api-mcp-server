#!/usr/bin/env python3
"""Decline one pending Skool membership request. The applicant gets no reason.

    python decline_membership_request.py --group yourgroup --request-id r_51e0aa

Get request IDs from list_membership_requests.py.
"""

import argparse
import json

from skool_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    result = call("decline_membership_request", {"group": args.group, "request_id": args.request_id})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(main)
