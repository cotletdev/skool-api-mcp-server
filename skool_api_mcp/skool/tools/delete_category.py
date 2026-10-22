"""Delete category."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "category_id": {"type": "string", "description": "category_id from list_categories."},
        "move_posts_to": {
            "type": "string",
            "description": "category_id that gets the deleted category's posts. Default: the first other one.",
        },
    },
    "required": ["group", "category_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "category_id": "6773ce70b0474fb9ba94b9eb9ace9aea",
    "status": "deleted",
    "posts_moved_to": "427f23fa7e854b4cb2a4b236c61af239",
}


@tool(
    name="delete_category",
    title="Delete category",
    access="write",
    confirm=True,
    description="Delete a feed category and move its posts to another. Admins only.",
    details=(
        "Deletes a category, as Settings, Categories, Delete does. Its posts are not deleted: Skool moves "
        "them to move_posts_to, or to the group's first other category. A group keeps at least one "
        "category. Admins only. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/categories/{category_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_category(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    target = args.get("move_posts_to") or next(
        (label for label in info["labels"].values() if label != args["category_id"]), None
    )
    if not target:
        raise ToolError("A group keeps at least one category; this is the last one.", ErrorCode.INVALID_INPUT)
    await write(ctx, "DELETE", f"/labels/{args['category_id']}", params={"migrate": target})
    return {"category_id": args["category_id"], "status": "deleted", "posts_moved_to": target}
