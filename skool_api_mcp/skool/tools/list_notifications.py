"""List notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field, limit
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, api, group_name
from skool_api_mcp.skool.settings import group_id

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {
            "type": "string",
            "description": "Only this group's notifications, by URL name. Default: all groups.",
        },
        "unread_only": {"type": "boolean", "description": "Only unread ones. Default: false."},
        "limit": {"type": "integer", "description": "1 to 30. Default: 30."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "notifications": [
        {
            "notification_id": "3ab1153a13c342549710cccadd93a552",
            "type": "new-post",
            "title": "New post",
            "text": "from Ana Lopez",
            "content": "Week 12 challenge: ship one landing page",
            "group": "Landing Page Lab",
            "post_id": "68cd45914ba548098c414da3f7e73bc3",
            "url": "https://www.skool.com/yourgroup/week-12-challenge?p=68cd4591",
            "unread": True,
            "created_at": "2026-10-18T13:56:53.99275Z",
        }
    ],
    "next_cursor": "MTc5MjMz",
}


@tool(
    name="list_notifications",
    title="List notifications",
    access="read",
    confirm=False,
    description="Your Skool notifications: new posts, comments, mentions, likes and approvals, newest first.",
    details=(
        "Lists the bell's notifications for this account, newest first, from all groups or one: what "
        "happened (type, such as new-post, comment, mention, like), the line Skool shows, the post it is "
        "about and a link. unread_only keeps the unread ones. Reading them does not mark them read; "
        "mark_notifications_read does."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /notifications",
    example_response=EXAMPLE_RESPONSE,
)
async def list_notifications(ctx: ToolContext, args: dict[str, Any]) -> Any:
    params: dict[str, Any] = {"limit": limit(args, 30, 30), "type": "all"}
    if args.get("group"):
        group_name(args["group"])
        params.update(type="group", group=await group_id(ctx, args))
    if args.get("cursor"):
        params["cursor"] = args["cursor"]
    answer = await api(ctx, "/self/notifications", params)
    items = []
    for message in answer.get("messages") or []:
        data = json_field((message.get("metadata") or {}).get("data")) or {}
        if args.get("unread_only") and not message.get("unread"):
            continue
        items.append(
            {
                "notification_id": message.get("id"),
                "type": message.get("action") or data.get("action"),
                "title": data.get("display_name"),
                "text": data.get("text"),
                "content": data.get("content"),
                "group": data.get("group_display_name"),
                "post_id": data.get("root_post_id") or data.get("post_id"),
                "url": f"{WEB}{data['link_as']}" if data.get("link_as") else None,
                "unread": bool(message.get("unread")),
                "created_at": message.get("created_at"),
            }
        )
    return {"notifications": items, "next_cursor": answer.get("cursor") if answer.get("has_more") else None}
