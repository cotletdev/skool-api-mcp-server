"""Search members."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import limit
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, person
from skool_api_mcp.skool.settings import group_id

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "query": {"type": "string", "description": "Part of a name or handle."},
        "limit": {"type": "integer", "description": "1 to 30. Default: 10."},
    },
    "required": ["group", "query"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "members": [
        {
            "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
            "name": "Ana Lopez",
            "profile_url": "https://www.skool.com/@ana-lopez-4127",
        }
    ]
}


@tool(
    name="search_members",
    title="Search members",
    access="read",
    confirm=False,
    description="Find members of a group by name, as the @mention box does.",
    details=(
        "Searches the group's members by name or handle, as typing @ in a post does, best matches first. "
        "member_id is what get_member and send_message take; list_members pages through everyone."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/members/search",
    example_response=EXAMPLE_RESPONSE,
)
async def search_members(ctx: ToolContext, args: dict[str, Any]) -> Any:
    body = {"query": args["query"].strip(), "group_id": await group_id(ctx, args), "limit": limit(args, 10, 30)}
    answer = await api(ctx, "/search/users", method="POST", body=body)
    return {"members": [person(user) for user in answer.get("users") or []]}
