"""List members."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field, limit, page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, full_name, group_name, page_data, role_name

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "joined_since": {
            "type": "string",
            "format": "date",
            "description": "Only members who joined on or after this date.",
        },
        "role": {
            "type": "string",
            "enum": ["all", "admin", "moderator", "member"],
            "description": "all, admin, moderator or member. Default: all.",
        },
        "status": {
            "type": "string",
            "enum": ["active", "banned", "churned", "cancelling"],
            "description": "Which members tab: active (default), banned, churned (left) or cancelling (paid groups).",
        },
        "limit": {"type": "integer", "description": "1 to 30. Default: 30."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "members": [
        {
            "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
            "membership_id": "7915f251cdf14c32a201bf1cf7b12c98",
            "name": "Ana Lopez",
            "role": "member",
            "level": 2,
            "points": 14,
            "joined_at": "2026-10-01T18:21:00.000000Z",
            "profile_url": "https://www.skool.com/@ana-lopez-4127",
        }
    ],
    "next_cursor": "2",
}


@tool(
    name="list_members",
    title="List members",
    access="read",
    confirm=False,
    description="Members of a group with role, level, points and join date, newest first; also banned or churned.",
    details=(
        "Lists members of one group, newest approved first, 30 to a page; pass next_cursor back as cursor "
        "for the next page. status picks Skool's tab: active members (admins included), banned, churned "
        "(left the group) or cancelling (paid groups). role admin or moderator asks Skool for the admins "
        "only. joined_at is when the member was approved. level is the Skool level (1 to 9) and points the "
        "likes that count toward it. joined_since filters within the page. member_id is the person "
        "(send_message, get_member); membership_id is their place in this group (set_member_role, "
        "ban_member, remove_member)."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/members",
    example_response=EXAMPLE_RESPONSE,
)
async def list_members(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    page = page_cursor(args.get("cursor"))
    wanted = limit(args, 30, 30)
    role = args.get("role") or "all"
    params: dict[str, Any] = {"group": group, "p": page}
    if (status := args.get("status")) and status != "active":
        params["t"] = status
    # Since 10.2026 the active tab holds admins too; admin=true is Skool's own "Admins" filter on it.
    if role in ("admin", "moderator"):
        params["admin"] = "true"
    props = await page_data(ctx, f"{group}/-/members", params)
    joined_since = args.get("joined_since")
    members = []
    for user in props.get("users") or []:
        member = user.get("member") or {}
        member_role = role_name(member.get("role"))
        if role != "all" and member_role != role:
            continue
        joined = member.get("approvedAt") or member.get("createdAt")
        if joined_since and (joined or "")[:10] < joined_since:
            continue
        stats = json_field((user.get("metadata") or {}).get("spData")) or {}
        members.append(
            {
                "member_id": user.get("id"),
                "membership_id": member.get("id"),
                "name": full_name(user),
                "role": member_role,
                "level": stats.get("lv"),
                "points": stats.get("pts"),
                "joined_at": joined,
                "profile_url": f"{WEB}/@{user.get('name')}",
            }
        )
    more = page < int(props.get("totalPages") or 1)
    return {"members": members[:wanted], "next_cursor": str(page + 1) if more else None}
