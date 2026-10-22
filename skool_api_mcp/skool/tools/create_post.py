"""Create post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, group_info, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "title": {"type": "string", "description": "Post title."},
        "body": {"type": "string", "description": "Post text. Links are kept as typed."},
        "category": {
            "type": "string",
            "description": "Category name as the group shows it, any letter case.",
        },
        "poll_options": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 10,
            "description": "Answers of a poll under the post, 2 to 10. Members vote with vote_on_poll.",
        },
    },
    "required": ["group", "title", "body", "category"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "status": "published",
    "category": "Announcements",
    "url": "https://www.skool.com/yourgroup/week-12-challenge-ship-one-landing-page",
    "created_at": "2026-10-03T07:00:00.000000Z",
}


async def _category(ctx: ToolContext, group: str, category: str) -> tuple[dict[str, Any], str, str]:
    """The group, the label id and the name of the category as Skool spells it; INVALID_INPUT lists the real ones."""
    info = await group_info(ctx, group)
    wanted = category.strip().lower()
    for name, label_id in info["labels"].items():
        if name.lower() == wanted:
            return info, label_id, name
    names = ", ".join(info["labels"]) or "none"
    raise ToolError(f"No category '{category}' in this group. Categories: {names}.", ErrorCode.INVALID_INPUT)


async def check_post(ctx: ToolContext, args: dict[str, Any]) -> None:
    """Before approval: an unknown group or category fails now, not after the owner said yes."""
    await _category(ctx, group_name(args["group"]), args["category"])


@tool(
    name="create_post",
    title="Create post",
    access="write",
    confirm=True,
    description="Publish a post to the community feed in a category, as you.",
    details=(
        "Publishes a post to the group's feed in one of its categories, under your name. The category is "
        "checked before the call waits for your approval: a wrong name fails at once with the group's "
        "categories in the message. poll_options adds a poll under the text. Text only; images and files "
        "are not uploaded. By default you confirm each post; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/posts",
    example_response=EXAMPLE_RESPONSE,
    check=check_post,
)
async def create_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    info, label, category = await _category(ctx, group, args["category"])
    metadata = {"title": args["title"], "content": args["body"], "labels": label, "action": 0}
    if options := [option.strip() for option in args.get("poll_options") or [] if option.strip()]:
        poll = await write(ctx, "POST", "/polls", body={"group_id": info["id"], "options": options})
        metadata["poll"] = poll.get("poll_id")
    post = await write(
        ctx,
        "POST",
        "/posts",
        params={"follow": "true"},
        body={"post_type": "generic", "group_id": info["id"], "root_id": "", "parent_id": "", "metadata": metadata},
    )
    return {
        "post_id": post.get("id"),
        "status": "published",
        "category": category,
        "url": f"{WEB}/{group}/{post.get('name')}",
        "created_at": post.get("created_at"),
    }
