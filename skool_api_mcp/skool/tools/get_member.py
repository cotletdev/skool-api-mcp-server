"""Get member."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, api, full_name
from skool_api_mcp.skool.settings import group_id

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "member_id": {"type": "string", "description": "member_id from list_members, search_members or get_post."},
    },
    "required": ["group", "member_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
    "name": "Ana Lopez",
    "bio": "Copywriter for SaaS landing pages.",
    "level": 3,
    "points": 41,
    "online": False,
    "last_online_at": "2026-10-18T14:02:11Z",
    "timezone": "America/Chicago",
    "profile_url": "https://www.skool.com/@ana-lopez-4127",
}


@tool(
    name="get_member",
    title="Get member",
    access="read",
    confirm=False,
    description="One member's profile in a group: name, bio, role, level, points and when they were last online.",
    details=(
        "Returns the profile card Skool shows when you click a member in the group: name, bio, role in "
        "this group, level and points, whether they are online and when they last were, and their time "
        "zone. Never their email or other private details."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/members/{member_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_member(ctx: ToolContext, args: dict[str, Any]) -> Any:
    user = await api(ctx, f"/users/{args['member_id']}", {"group": await group_id(ctx, args)})
    meta = user.get("metadata") or {}
    stats = json_field(meta.get("sp_data")) or {}
    last = meta.get("last_offline")
    return {
        "member_id": user.get("id"),
        "name": full_name(user),
        "bio": meta.get("bio") or "",
        "level": stats.get("lv"),
        "points": stats.get("pts"),
        "online": bool(meta.get("online")),
        "last_online_at": datetime.fromtimestamp(last / 1e9, UTC).isoformat(timespec="seconds") if last else None,
        "timezone": meta.get("timezone") or user.get("time_zone"),
        "profile_url": f"{WEB}/@{user.get('name')}",
    }
