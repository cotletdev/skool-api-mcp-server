"""Create category."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import SORTS, WRITE_ROLES, admin_group, category

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "name": {"type": "string", "maxLength": 30, "description": "Category name, up to 30 characters."},
        "who_can_post": {
            "type": "string",
            "enum": ["members", "admins"],
            "description": "members (default) or admins only.",
        },
        "sort": {
            "type": "string",
            "enum": list(SORTS),
            "description": "How the category orders posts. Default: default.",
        },
    },
    "required": ["group", "name"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "category_id": "6773ce70b0474fb9ba94b9eb9ace9aea",
    "name": "Wins",
    "description": "",
    "who_can_post": "members",
    "sort": "default",
    "posts": 0,
}


@tool(
    name="create_category",
    title="Create category",
    access="write",
    confirm=False,
    description="Add a category to a group's feed. Admins only.",
    details=(
        "Adds a feed category, as Settings, Categories, Add does. Skool picks its color. who_can_post "
        "admins makes an announcements-style category only admins post in. Admins only. Members see the "
        "new category at once but nobody is notified, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/categories",
    example_response=EXAMPLE_RESPONSE,
)
async def create_category(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    metadata = {
        "display_name": args["name"].strip(),
        "default_sort": SORTS[args.get("sort") or "default"],
        "post_write_role": WRITE_ROLES[args.get("who_can_post") or "members"],
    }
    label = await write(ctx, "POST", "/labels", body={"group_id": info["id"], "metadata": metadata})
    return category(label)
