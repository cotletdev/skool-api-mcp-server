"""Update group link."""

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
        "label": {"type": "string", "maxLength": 34, "description": "Link text, up to 34 characters."},
        "url": {"type": "string", "format": "uri", "description": "Where the link goes."},
    },
    "required": ["group", "number"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"links": [{"number": 1, "label": "Website", "url": "https://example.com"}]}


@tool(
    name="update_group_link",
    title="Update group link",
    access="write",
    confirm=False,
    description="Change the text or address of a sidebar link. Admins only.",
    details=(
        "Edits one sidebar link, as Settings, Links, Edit does: fields you leave out stay. Returns the "
        "whole new list. Admins only. Runs without asking first: nobody is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/links/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_group_link(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    current = (await api(ctx, f"/groups/{info['id']}/links")).get("links") or []
    number = checked_number(args["number"], current, "links")
    link = current[number - 1]
    body = {
        "url": (args.get("url") or link.get("url") or "").strip(),
        "label": (args.get("label") or link.get("label") or "").strip(),
        "public": False,
    }
    return {"links": _links(await write(ctx, "PUT", f"/groups/{info['id']}/links/{number}", body=body))}
