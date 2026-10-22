"""List group links."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP
from skool_api_mcp.skool.settings import group_record, meta_list

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"group": GROUP_PROP},
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"links": [{"number": 1, "label": "Website", "url": "https://example.com"}]}


@tool(
    name="list_group_links",
    title="List group links",
    access="read",
    confirm=False,
    description="The links on a group's sidebar, numbered as the group shows them.",
    details=(
        "Lists the links the group shows in its sidebar under the description, numbered from 1. "
        "update_group_link and delete_group_link take the number."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/links",
    example_response=EXAMPLE_RESPONSE,
)
async def list_group_links(ctx: ToolContext, args: dict[str, Any]) -> Any:
    return {"links": _links({"links": meta_list(await group_record(ctx, args), "links")})}


def _links(answer: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"number": n, "label": link.get("label"), "url": link.get("url")}
        for n, link in enumerate(answer.get("links") or [], start=1)
    ]
