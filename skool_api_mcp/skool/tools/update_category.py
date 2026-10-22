"""Update category."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import SORTS, WRITE_ROLES, admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "category_id": {"type": "string", "description": "category_id from list_categories."},
        "name": {"type": "string", "maxLength": 30, "description": "New name."},
        "who_can_post": {"type": "string", "enum": ["members", "admins"], "description": "members or admins."},
        "sort": {"type": "string", "enum": list(SORTS), "description": "How the category orders posts."},
    },
    "required": ["group", "category_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"category_id": "6773ce70b0474fb9ba94b9eb9ace9aea", "status": "updated"}


@tool(
    name="update_category",
    title="Update category",
    access="write",
    confirm=False,
    description="Rename a category or change who can post in it and how it sorts. Admins only.",
    details=(
        "Changes a feed category, as Settings, Categories, Edit does: fields you leave out stay. Posts "
        "already in it stay too. Admins only. Nobody is notified and it is undone with one call, so it "
        "runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/categories/{category_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_category(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    body: dict[str, Any] = {}
    if name := (args.get("name") or "").strip():
        body["display_name"] = name
    if role := args.get("who_can_post"):
        body["post_write_role"] = WRITE_ROLES[role]
    if sort := args.get("sort"):
        body["default_sort"] = SORTS[sort]
    if not body:
        raise ToolError("Give name, who_can_post or sort to change.", ErrorCode.INVALID_INPUT)
    await write(ctx, "PUT", f"/labels/{args['category_id']}", body=body)
    return {"category_id": args["category_id"], "status": "updated"}
