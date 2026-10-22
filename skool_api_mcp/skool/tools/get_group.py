"""Get group."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, api, group_name, price_label
from skool_api_mcp.skool.settings import survey

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "group_id": "944c1d1440c34da5a77558c74c9f8176",
    "group": "yourgroup",
    "name": "Landing Page Lab",
    "about": "A community for people who ship landing pages every week.",
    "private": True,
    "price": "$49/month",
    "members": 1284,
    "admins": 3,
    "posts": 5120,
    "courses": 4,
    "pending_requests": 7,
    "reported_posts": 0,
    "owner": "Jordan Price",
    "membership_questions": [{"number": 1, "question": "What brings you here?", "type": "text", "options": None}],
    "created_at": "2024-01-29T08:35:21.973835Z",
    "url": "https://www.skool.com/yourgroup",
}


@tool(
    name="get_group",
    title="Get group",
    access="read",
    confirm=False,
    description="A group's name, About text, privacy, price, counts, owner and membership questions.",
    details=(
        "Returns one group as its About page and Settings show it: name, the About text, whether it is "
        "private, the price, member, admin, post and course counts, and the owner. Admins also get "
        "pending_requests, reported_posts and the membership questions; for others these are 0 and empty."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_group(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    answer = await api(ctx, f"/groups/{group}")
    meta = answer.get("metadata") or {}
    owner = json_field(meta.get("owner")) or {}
    return {
        "group_id": answer.get("id"),
        "group": answer.get("name") or group,
        "name": meta.get("display_name"),
        "about": meta.get("lp_description") or meta.get("description") or "",
        "private": str(meta.get("privacy", "0")) == "1",
        "price": price_label(meta),
        "members": int(meta.get("total_members") or 0),
        "admins": int(meta.get("total_admins") or 0),
        "posts": int(meta.get("total_posts") or 0),
        "courses": int(meta.get("num_courses") or 0),
        "pending_requests": int(meta.get("total_requests") or 0),
        "reported_posts": int(meta.get("total_reports") or 0),
        "owner": " ".join(filter(None, (owner.get("first_name"), owner.get("last_name")))) or owner.get("name"),
        "membership_questions": survey(meta),
        "created_at": answer.get("created_at"),
        "url": f"{WEB}/{answer.get('name') or group}",
    }
