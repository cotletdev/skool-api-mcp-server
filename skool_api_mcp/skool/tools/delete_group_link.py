"""Delete group link."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, write
from skool_api_mcp.skool.settings import admin_group, checked_number
from skool_api_mcp.skool.tools.list_group_links import _links

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "number": {"type": "integer", "description": "Link number from list_group_links."},
    },
    "required": ["group", "number"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"links": [{"number": 1, "label": "Website", "url": "https://example.com"}]}


@tool(
    name="delete_group_link",
    title="Delete group link",
    access="write",
    confirm=True,
    description="Remove a link from the group's sidebar. Admins only.",
    details=(
        "Removes one sidebar link, as Settings, Links, Delete does; the links after it move up a number. "
        "Returns the whole new list. Admins only. By default you confirm each call; you can switch that "
        "off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/links/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_group_link(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    current = (await api(ctx, f"/groups/{info['id']}/links")).get("links") or []
    number = checked_number(args["number"], current, "links")
    return {"links": _links(await write(ctx, "DELETE", f"/groups/{info['id']}/links/{number}"))}
