"""Pin comment."""

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
        "post_id": {"type": "string", "description": "post_id the comment is under."},
        "comment_id": {"type": "string", "description": "comment_id from get_post."},
        "pinned": {"type": "boolean", "description": "false unpins. Default: true."},
    },
    "required": ["group", "post_id", "comment_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "comment_id": "9d2b6e1f3a4c4b5d8e7f6a5b4c3d2e1f",
    "pinned": True,
}


@tool(
    name="pin_comment",
    title="Pin comment",
    access="write",
    confirm=False,
    description="Pin a comment to the top of a post's comments, or unpin it.",
    details=(
        "Pins one comment above the others under a post, as the comment menu's Pin does; pinned false "
        "unpins it. Group admins and moderators only. Sends nothing to anyone and is undone with one "
        "call, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/comments/{comment_id}/pin",
    example_response=EXAMPLE_RESPONSE,
)
async def pin_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:
    require_admin(await group_info(ctx, group_name(args["group"])), moderators=True)
    pinned = args.get("pinned", True)
    action = "pin-comment" if pinned else "unpin-comment"
    await write(ctx, "POST", f"/posts/{args['post_id']}/{action}", params={"comment": args["comment_id"]})
    return {"post_id": args["post_id"], "comment_id": args["comment_id"], "pinned": pinned}
