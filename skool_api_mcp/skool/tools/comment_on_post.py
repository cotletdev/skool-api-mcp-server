"""Comment on post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import group_info, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "post_id": {"type": "string", "description": "post_id from list_posts (not the slug)."},
        "body": {"type": "string", "description": "Comment text."},
        "parent_comment_id": {
            "type": "string",
            "description": "comment_id from get_post: reply under that comment instead of the post.",
        },
    },
    "required": ["group", "post_id", "body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "comment_id": "9d2b6e1f3a4c4b5d8e7f6a5b4c3d2e1f",
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "parent_comment_id": None,
    "status": "published",
}


@tool(
    name="comment_on_post",
    title="Comment on post",
    access="write",
    confirm=True,
    description="Comment on a post, or reply to a comment, as you.",
    details=(
        "Adds a comment to a post, or a reply under an existing comment when parent_comment_id is set. "
        "The comment appears under your name. By default you confirm each comment; you can switch that "
        "off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/posts/{post_id}/comments",
    example_response=EXAMPLE_RESPONSE,
)
async def comment_on_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await group_info(ctx, group_name(args["group"]))
    parent = args.get("parent_comment_id") or args["post_id"]
    comment = await write(
        ctx,
        "POST",
        "/posts",
        body={
            "post_type": "comment",
            "group_id": info["id"],
            "root_id": args["post_id"],
            "parent_id": parent,
            "metadata": {"title": "", "content": args["body"], "action": 0},
        },
    )
    return {
        "comment_id": comment.get("id"),
        "post_id": args["post_id"],
        "parent_comment_id": args.get("parent_comment_id"),
        "status": "published",
    }
