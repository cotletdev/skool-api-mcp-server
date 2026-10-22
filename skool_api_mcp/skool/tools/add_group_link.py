"""Add group link."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group
from skool_api_mcp.skool.tools.list_group_links import _links

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "label": {"type": "string", "maxLength": 34, "description": "Link text, up to 34 characters."},
        "url": {"type": "string", "format": "uri", "description": "Where the link goes."},
    },
    "required": ["group", "label", "url"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"links": [{"number": 1, "label": "Website", "url": "https://example.com"}]}


@tool(
    name="add_group_link",
    title="Add group link",
    access="write",
    confirm=False,
    description="Add a link to the group's sidebar. Admins only.",
    details=(
        "Adds a link after the existing ones in the group's sidebar, as Settings, Links, Add does, and "
        "returns the whole new list. Admins only. Nobody is notified and it is undone with "
        "delete_group_link, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/links",
    example_response=EXAMPLE_RESPONSE,
)
async def add_group_link(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    link = {"url": args["url"].strip(), "label": args["label"].strip(), "public": False}
    return {"links": _links(await write(ctx, "POST", f"/groups/{info['id']}/links", body=link))}
