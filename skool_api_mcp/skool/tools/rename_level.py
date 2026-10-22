"""Rename level."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group
from skool_api_mcp.skool.tools.list_levels import _level

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "level": {"type": "integer", "minimum": 1, "maximum": 9, "description": "Level number, 1 to 9."},
        "title": {
            "type": "string",
            "description": "The title members see at that level. Empty string: back to the plain name.",
        },
    },
    "required": ["group", "level", "title"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"level": 2, "name": "Level 2", "title": "Regular", "percent_of_members": 14}


@tool(
    name="rename_level",
    title="Rename level",
    access="write",
    confirm=False,
    description="Give one of the group's 9 levels its own title. Admins only.",
    details=(
        "Sets the title members see next to a level, as Settings, Gamification does; an empty title goes "
        "back to Skool's plain name. The points needed per level are Skool's and do not change. Admins "
        "only. Runs without asking first: undone with one call."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/levels/{level}",
    example_response=EXAMPLE_RESPONSE,
)
async def rename_level(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    level = await write(ctx, "PUT", f"/groups/{info['id']}/levels/{args['level']}", body={"title": args["title"]})
    return _level(level)
