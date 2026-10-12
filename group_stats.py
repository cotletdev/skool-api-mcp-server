#!/usr/bin/env python3
"""Get a Skool group's members, new joins, churn and MRR for the last 7, 30 or 90 days. Admins only.

    python group_stats.py --group yourgroup --period 7d
"""
import argparse

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--group", required=True, help="Group URL name, e.g. yourgroup")
    parser.add_argument("--period", choices=["7d", "30d", "90d"], default="30d")
    args = parser.parse_args()

    s = call("get_group_stats", {"group": args.group, "period": args.period})
    mrr = s.get("mrr") or {}
    churn = (s["members_churned"] / s["members_total"] * 100) if s.get("members_total") else 0
    print(f"Skool group:  {s['group']}  ({s['period']})")
    print(f"Members:      {s['members_total']}")
    print(f"New:          +{s['members_new']}")
    print(f"Churned:      -{s['members_churned']}  ({churn:.1f}%)")
    print(f"MRR:          {mrr.get('amount', 0):,} {mrr.get('currency', '')}")


if __name__ == "__main__":
    run(main)
