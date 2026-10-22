"""Turn comments on or off."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_info, group_name, require_admin, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id from list_posts (not the slug)."},
        "enabled": {"type": "boolean", "description": "false turns comments off, true back on."},
    },
    "required": ["group", "post_id", "enabled"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06", "comments_enabled": False}


@tool(
    name="set_post_comments",
    title="Turn comments on or off",
    access="write",
    confirm=False,
    description="Turn comments on a post off, or back on.",
    details=(
        "Turns comments off on a post, as the post menu's Turn off comments does: existing comments stay, "
        "nobody can add new ones. enabled true turns them back on. Group admins and moderators only. "
        "Runs without asking first: undone with one call."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/commenting",
    example_response=EXAMPLE_RESPONSE,
)
async def set_post_comments(ctx: ToolContext, args: dict[str, Any]) -> Any:
    require_admin(await group_info(ctx, group_name(args["group"])), moderators=True)
    action = "enable-comments" if args["enabled"] else "disable-comments"
    await write(ctx, "POST", f"/posts/{args['post_id']}/{action}")
    return {"post_id": args["post_id"], "comments_enabled": args["enabled"]}
