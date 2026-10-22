"""Get leaderboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, page_data, person

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "period": {"type": "string", "enum": ["7d", "30d", "all"], "description": "7d, 30d or all time. Default: 30d."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "period": "30d",
    "leaders": [
        {
            "rank": 1,
            "points": 957,
            "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
            "name": "Ana Lopez",
            "profile_url": "https://www.skool.com/@ana-lopez-4127",
        }
    ],
    "your_rank": {"rank": 14, "points": 37},
    "updated_at": "2026-10-18T15:54:52.416543Z",
}


@tool(
    name="get_leaderboard",
    title="Get leaderboard",
    access="read",
    confirm=False,
    description="The group's top 10 members by points for the last 7 days, 30 days or all time, and your rank.",
    details=(
        "Returns the Leaderboards tab: the top 10 members by points earned in the period (one point per "
        "like received), with your own rank and points when you are on the board. Skool recounts it every "
        "few minutes; updated_at says when."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/leaderboard",
    example_response=EXAMPLE_RESPONSE,
)
async def get_leaderboard(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    props = await page_data(ctx, f"{group}/-/leaderboards", {"group": group})
    period = args.get("period") or "30d"
    board_key, self_key = {
        "7d": ("past7Days", "self7Days"),
        "30d": ("past30Days", "self30Days"),
        "all": ("allTime", "selfAllTime"),
    }[period]
    board = props.get(board_key) or {}
    mine = props.get(self_key) or {}
    leaders = [
        {"rank": row.get("rank"), "points": row.get("points"), **person(row.get("user"))}
        for row in board.get("users") or []
    ]
    return {
        "period": period,
        "leaders": leaders,
        "your_rank": {"rank": mine.get("rank"), "points": mine.get("points")} if mine else None,
        "updated_at": board.get("updatedAt"),
    }
