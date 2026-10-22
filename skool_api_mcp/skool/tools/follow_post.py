"""Follow post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id from list_posts (not the slug)."},
        "following": {"type": "boolean", "description": "false stops the notifications. Default: true."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06", "following": True}


@tool(
    name="follow_post",
    title="Follow post",
    access="write",
    confirm=False,
    description="Get notified of new comments on a post, or stop.",
    details=(
        "Follows a post so new comments land in your Skool notifications, as the post menu's Follow does; "
        "following false unfollows. You follow your own posts from the start. Changes only your own "
        "notifications, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/follow",
    example_response=EXAMPLE_RESPONSE,
)
async def follow_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group_name(args["group"])
    following = args.get("following", True)
    await write(ctx, "POST", f"/posts/{args['post_id']}/{'follow' if following else 'unfollow'}")
    return {"post_id": args["post_id"], "following": following}
