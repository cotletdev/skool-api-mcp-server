"""Update group About text."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "about": {
            "type": "string",
            "description": "The new About text, replacing the old. Plain text, line breaks kept.",
        },
    },
    "required": ["group", "about"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"group": "yourgroup", "status": "updated"}


@tool(
    name="update_group_about",
    title="Update group About text",
    access="write",
    confirm=True,
    description="Replace the text on the group's About page. Admins only.",
    details=(
        "Replaces the description on the group's About page, the one visitors read before they join, as "
        "editing it on the About page does. Images and videos on the page stay. Admins only. Everyone who "
        "opens the page sees the change, so by default you confirm each call; you can switch that off for "
        "this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/about",
    example_response=EXAMPLE_RESPONSE,
)
async def update_group_about(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    path = f"/groups/{info['id']}/update-landing-page-description"
    await write(ctx, "POST", path, body={"description": args["about"]})
    return {"group": args["group"], "status": "updated"}
