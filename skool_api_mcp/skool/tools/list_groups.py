"""List groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, api, price_label, role_name

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "groups": [
        {
            "group": "yourgroup",
            "name": "Landing Page Lab",
            "role": "admin",
            "members": 1284,
            "price": "$49/month",
            "url": "https://www.skool.com/yourgroup",
        },
        {
            "group": "creator-club",
            "name": "Creator Club",
            "role": "member",
            "members": 9310,
            "price": "free",
            "url": "https://www.skool.com/creator-club",
        },
    ]
}


@tool(
    name="list_groups",
    title="List groups",
    access="read",
    confirm=False,
    description="Skool groups of your account, with your role (or pending), member count and price.",
    details=(
        "Returns up to 50 Skool groups of your account: groups you own, groups you joined and groups you "
        "asked to join. role is admin, moderator, member, or pending while your request waits for approval "
        "(a pending group shows no posts or members yet). Use group as the group parameter of the other "
        "tools. members is the count Skool shows on the group page; price is the membership price or free."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups",
    example_response=EXAMPLE_RESPONSE,
)
async def list_groups(ctx: ToolContext, args: dict[str, Any]) -> Any:
    # members=true adds the account's own membership of each group; a request to join has role pending.
    answer = await api(ctx, "/self/groups", {"limit": 50, "prefs": "false", "members": "true"})
    memberships = {item.get("group_id"): item for item in answer.get("members") or []}
    groups = []
    for item in answer.get("groups") or []:
        meta = item.get("metadata") or {}
        membership = memberships.get(item.get("id")) or {}
        groups.append(
            {
                "group": item.get("name"),
                "name": meta.get("display_name") or item.get("name"),
                "role": role_name(membership.get("role")),
                "members": meta.get("total_members"),
                "price": price_label(meta),
                "url": f"{WEB}/{item.get('name')}",
            }
        )
    return {"groups": groups}
