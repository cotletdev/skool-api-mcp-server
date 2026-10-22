"""Delete post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, require_author_or_moderator, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id from list_posts, or comment_id from get_post."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06", "status": "deleted"}


@tool(
    name="delete_post",
    title="Delete post or comment",
    access="write",
    confirm=True,
    description="Delete a post or a comment for good: yours, or anyone's as an admin.",
    details=(
        "Deletes a post with its comments, or a single comment (pass its comment_id), as Skool's Delete "
        "does. Skool keeps no trash, so this cannot be undone. Your own posts and comments, or anyone's "
        "when you are a group admin or moderator. By default you confirm each call; you can switch that "
        "off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/posts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await require_author_or_moderator(ctx, group_name(args["group"]), args["post_id"])
    await write(ctx, "DELETE", f"/posts/{args['post_id']}")
    return {"post_id": args["post_id"], "status": "deleted"}
