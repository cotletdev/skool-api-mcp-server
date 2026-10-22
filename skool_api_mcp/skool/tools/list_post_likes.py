"""List post likes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import limit
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, group_name, person

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id from list_posts, or comment_id from get_post."},
        "limit": {"type": "integer", "description": "1 to 100. Default: 50."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "likes": [
        {
            "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
            "name": "Ana Lopez",
            "profile_url": "https://www.skool.com/@ana-lopez-4127",
        }
    ],
}


@tool(
    name="list_post_likes",
    title="List post likes",
    access="read",
    confirm=False,
    description="Who liked a post or a comment.",
    details=(
        "Lists the members who liked a post or a comment, as the like count under it opens, newest first, "
        "up to 100. member_id is what send_message and get_member take."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/posts/{post_id}/likes",
    example_response=EXAMPLE_RESPONSE,
)
async def list_post_likes(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group_name(args["group"])
    wanted = limit(args, 50, 100)
    likes: list[dict[str, Any]] = []
    # Skool hands out at most 10 per request.
    while len(likes) < wanted:
        params = {"limit": 10, "offset": len(likes)}
        answer = await api(ctx, f"/posts/{args['post_id']}/upvote-users", params)
        likes.extend(person(user) for user in answer.get("users") or [])
        if not answer.get("has_more"):
            break
    return {"post_id": args["post_id"], "likes": likes[:wanted]}
