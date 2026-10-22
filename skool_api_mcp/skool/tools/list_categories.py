"""List categories."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, page_data
from skool_api_mcp.skool.settings import category

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"group": GROUP_PROP},
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "categories": [
        {
            "category_id": "427f23fa7e854b4cb2a4b236c61af239",
            "name": "General discussion",
            "description": "Discuss anything here",
            "who_can_post": "members",
            "sort": "default",
            "posts": 42,
        }
    ]
}


@tool(
    name="list_categories",
    title="List categories",
    access="read",
    confirm=False,
    description="The feed categories of a group: name, who can post, sort order, post count.",
    details=(
        "Lists the categories a group's feed is split into, in the order the group shows them. "
        "who_can_post is members or admins; sort is how the category orders its posts (default, new, "
        "top_week, top_month, top_year). create_post and update_post take the name."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/categories",
    example_response=EXAMPLE_RESPONSE,
)
async def list_categories(ctx: ToolContext, args: dict[str, Any]) -> Any:
    # The feed page carries the labels; api2 /labels is admin-only.
    group = group_name(args["group"])
    props = await page_data(ctx, group, {"group": group})
    labels = (props.get("currentGroup") or {}).get("labels") or []
    return {"categories": [category(label) for label in labels]}
