"""Like post."""

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
        "post_id": {"type": "string", "description": "post_id from list_posts, or comment_id from get_post."},
        "liked": {"type": "boolean", "description": "false takes the like back. Default: true."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06", "liked": True}


@tool(
    name="like_post",
    title="Like post or comment",
    access="write",
    confirm=False,
    description="Like a post or a comment, or take the like back.",
    details=(
        "Likes a post or a comment as the heart under it does; liked false takes the like back. A like "
        "gives the author a point on the leaderboard and Skool notifies them. Skool limits fast liking: "
        "too many in a row come back as rate_limited. Runs without asking first: undone with one call."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/like",
    example_response=EXAMPLE_RESPONSE,
)
async def like_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group_name(args["group"])
    liked = args.get("liked", True)
    vote = {"old": "", "new": "up"} if liked else {"old": "up", "new": ""}
    await write(ctx, "PUT", f"/posts/{args['post_id']}/vote", body=vote)
    return {"post_id": args["post_id"], "liked": liked}
