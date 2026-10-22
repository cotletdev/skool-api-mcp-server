"""Get group stats."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import api, group_info, group_name, require_admin

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "period": {"type": "string", "enum": ["7d", "30d", "90d"], "description": "7d, 30d or 90d. Default: 30d."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "group": "yourgroup",
    "period": "30d",
    "members_total": 1284,
    "members_new": 96,
    "members_churned": 31,
    "mrr": {"amount": 4123.0, "currency": "USD"},
}


@tool(
    name="get_group_stats",
    title="Get group stats",
    access="read",
    confirm=False,
    description="Total, new and churned members and monthly recurring revenue for a period. Admins only.",
    details=(
        "Returns figures from the group's admin dashboard: members_total today, members_new in the period, "
        "members_churned as the dashboard counts it, and monthly recurring revenue in US dollars. For 7d "
        "and 30d members_new is the growth of the daily member count; for 90d it sums the last three "
        "months of the dashboard's members chart. Skool computes these in the background, so a call can "
        "take up to about 15 seconds. Admins only; other accounts get APP_PERMISSION_DENIED."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/stats",
    example_response=EXAMPLE_RESPONSE,
)
async def get_group_stats(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    info = await group_info(ctx, group)
    require_admin(info)
    period = args.get("period") or "30d"
    days = int(period[:-1])
    overview = await _computed(ctx, f"/groups/{info['id']}/analytics-overview-v2", {})
    members_total = overview.get("num_members", 0)
    if days <= 30:
        # Skool's admin dashboard series covers exactly the last 30 days, one point a day, newest first.
        series = await api(ctx, f"/groups/{info['id']}/admin-metrics", {"range": "30d", "amt": "monthly"})
        totals = [point.get("value") or 0 for point in series.get("total_members") or []]
        start = totals[min(days, len(totals)) - 1] if totals else members_total
        members_new = max(members_total - start, 0)
    else:
        chart = await _computed(ctx, f"/groups/{info['id']}/analytics-v2", {"chart": "members"})
        items = (chart.get("chart_data") or {}).get("items") or []
        members_new = sum(int(item.get("new") or 0) for item in items[-3:])
    mrr = overview.get("mrr") or 0
    return {
        "group": group,
        "period": period,
        "members_total": members_total,
        "members_new": members_new,
        "members_churned": overview.get("churned_members", 0),
        "mrr": {"amount": mrr / 100, "currency": "USD"},
    }


async def _computed(ctx: ToolContext, path: str, params: dict[str, Any]) -> dict[str, Any]:
    """Skool computes analytics in the background: the first answer is a token to ask again with."""
    answer = await api(ctx, path, params)
    for _ in range(8):
        if "token" not in answer:
            return answer.get("data") or {}
        await asyncio.sleep(1.5)
        answer = await api(ctx, path, {**params, "token": answer["token"]})
    raise ToolError("Skool did not finish the stats in time; try again.", ErrorCode.TARGET_ERROR)
