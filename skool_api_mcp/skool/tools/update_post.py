"""Update post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_info, group_name, require_author_or_moderator, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id from list_posts (not the slug)."},
        "title": {"type": "string", "description": "New title. Left out: unchanged."},
        "body": {"type": "string", "description": "New text, replacing the old. Left out: unchanged."},
        "category": {"type": "string", "description": "Move the post to this category, by name."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "title": "Week 12 challenge: ship one landing page",
    "status": "updated",
    "edited_at": "2026-10-18T15:51:07.680728Z",
}


@tool(
    name="update_post",
    title="Update post",
    access="write",
    confirm=True,
    description="Change the title, text or category of a post you wrote, or any post as an admin.",
    details=(
        "Edits a post in place, as Skool's Edit post does: fields you leave out stay as they are, and body "
        "replaces the whole text. Skool marks the post as edited. Your own posts, or any post when you are "
        "a group admin. By default you confirm each edit; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/posts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    body: dict[str, Any] = {}
    if "title" in args:
        body["title"] = args["title"]
    if "body" in args:
        body["content"] = args["body"]
    if category := (args.get("category") or "").strip():
        info = await group_info(ctx, group_name(args["group"]))
        labels = {name.lower(): label_id for name, label_id in info["labels"].items()}
        if category.lower() not in labels:
            names = ", ".join(info["labels"]) or "none"
            raise ToolError(f"No category '{category}' in this group. Categories: {names}.", ErrorCode.INVALID_INPUT)
        body["labels"] = labels[category.lower()]
    if not body:
        raise ToolError("Give title, body or category to change.", ErrorCode.INVALID_INPUT)
    await require_author_or_moderator(ctx, group_name(args["group"]), args["post_id"])
    post = await write(ctx, "POST", f"/posts/{args['post_id']}/update", body=body)
    return {
        "post_id": post.get("id") or args["post_id"],
        "title": (post.get("metadata") or {}).get("title"),
        "status": "updated",
        "edited_at": post.get("updated_at"),
    }
