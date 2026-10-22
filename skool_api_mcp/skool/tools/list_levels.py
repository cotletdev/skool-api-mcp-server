"""List levels."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP
from skool_api_mcp.skool.settings import group_record, meta_list

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "levels": [{"level": 1, "name": "Level 1", "title": "Newbie", "percent_of_members": 80}]
}


@tool(
    name="list_levels",
    title="List levels",
    access="read",
    confirm=False,
    description="The group's 9 levels with their custom titles and how many members reached each.",
    details=(
        "Lists the 9 levels of the group's leaderboard: the level number, Skool's name for it, the title "
        "the admins gave it (empty when none) and the share of members at that level. Points come from "
        "likes; get_leaderboard ranks the members."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/levels",
    example_response=EXAMPLE_RESPONSE,
)
async def list_levels(ctx: ToolContext, args: dict[str, Any]) -> Any:
    return {"levels": [_level(level) for level in meta_list(await group_record(ctx, args), "levels")]}


def _level(level: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": level.get("number"),
        "name": level.get("name"),
        "title": level.get("title") or "",
        "percent_of_members": level.get("percent_of_members", level.get("percentOfMembers")),
    }
