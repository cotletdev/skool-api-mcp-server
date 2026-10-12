#!/usr/bin/env python3
"""Approve pending Skool membership requests, all of them or only those whose answers match your keywords.

    python approve_membership_requests.py --group yourgroup --dry-run
    python approve_membership_requests.py --group yourgroup --match business --match agency
    python approve_membership_requests.py --group yourgroup --all

Your Skool AutoDM, if set, goes out on every approval. By default Cotlet asks
you to confirm each approval; switch that off for this tool in the Cotlet
dashboard to run it on a schedule (cron, GitHub Actions).
"""
import argparse

from cotlet_client import call, paginate, run


def matches(request: dict, keywords: list[str]) -> bool:
    text = " ".join(a.get("answer", "") for a in request.get("answers", [])).lower()
    return any(k.lower() in text for k in keywords)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--match", action="append", default=[], help="Approve if any answer contains this word (repeatable)")
    parser.add_argument("--all", action="store_true", help="Approve every pending request")
    parser.add_argument("--dry-run", action="store_true", help="Only show who would be approved")
    args = parser.parse_args()
    if not args.all and not args.match:
        parser.error("pass --match WORD (one or more) or --all")

    requests = list(paginate("list_membership_requests", {"group": args.group, "limit": 100}, "requests"))
    chosen = [r for r in requests if args.all or matches(r, args.match)]
    print(f"{len(requests)} pending, {len(chosen)} to approve")
    for req in chosen:
        if args.dry_run:
            print(f"  would approve {req['name']} ({req['request_id']})")
            continue
        result = call("approve_membership_request", {"group": args.group, "request_id": req["request_id"]})
        print(f"  {req['name']}: {result.get('status')}")


if __name__ == "__main__":
    run(main)
