"""List conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import limit, page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import api, full_name

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "unread_only": {"type": "boolean", "description": "Only conversations with unread messages."},
        "limit": {"type": "integer", "description": "1 to 30 (Skool refuses more). Default: 20."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversations": [
        {
            "conversation_id": "7c3e9a1b2d4f4e6a8b0c1d2e3f4a5b6c",
            "with": {"member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60", "name": "Ana Lopez"},
            "unread": 2,
            "last_message": "Is the Thursday call recorded?",
            "updated_at": "2026-10-02T16:02:00.000000Z",
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_conversations",
    title="List conversations",
    access="read",
    confirm=False,
    description="Your Skool Chat inbox: who, unread count and last message preview.",
    details=(
        "Lists your Skool Chat conversations across all groups, most recent first, with the other member, "
        "unread count and the last message. Set unread_only to see only what needs an answer. Pass "
        "next_cursor back as cursor for the next page."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /conversations",
    example_response=EXAMPLE_RESPONSE,
)
async def list_conversations(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page = page_cursor(args.get("cursor"))
    wanted = limit(args, 20, 30)
    params = {
        "offset": (page - 1) * wanted,
        "limit": wanted,
        "last": "true",
        "unread-only": "true" if args.get("unread_only") else "false",
    }
    answer = await api(ctx, "/self/chat-channels", params)
    channels = answer.get("channels") or []
    conversations = [
        {
            "conversation_id": channel.get("id"),
            "with": {"member_id": (channel.get("user") or {}).get("id"), "name": full_name(channel.get("user"))},
            "unread": (channel.get("metadata") or {}).get("num_unread", 0),
            "last_message": ((channel.get("last_message") or {}).get("metadata") or {}).get("content", ""),
            "updated_at": channel.get("last_message_at") or channel.get("updated_at"),
        }
        for channel in channels
    ]
    return {"conversations": conversations, "next_cursor": str(page + 1) if len(channels) == wanted else None}
