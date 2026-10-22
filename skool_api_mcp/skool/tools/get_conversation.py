"""Get conversation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import limit
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import api

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "conversation_id": {
            "type": "string",
            "description": "conversation_id from list_conversations or send_message.",
        },
        "limit": {"type": "integer", "description": "1 to 100. Default: 50."},
    },
    "required": ["conversation_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversation_id": "7c3e9a1b2d4f4e6a8b0c1d2e3f4a5b6c",
    "messages": [
        {
            "from": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
            "body": "Is the Thursday call recorded?",
            "sent_at": "2026-10-02T16:02:00.000000Z",
        },
        {"from": "You", "body": "Yes, the replay goes up on Friday.", "sent_at": "2026-10-02T16:10:00.000000Z"},
    ],
}


@tool(
    name="get_conversation",
    title="Get conversation",
    access="read",
    confirm=False,
    description="The latest messages of one Skool Chat conversation, oldest first.",
    details=(
        "Returns up to limit latest messages of one Skool Chat conversation, oldest first. from is You for "
        "your own messages and the other member's member_id otherwise; their name is in "
        "list_conversations. Reading does not mark the conversation read."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /conversations/{conversation_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_conversation(ctx: ToolContext, args: dict[str, Any]) -> Any:
    channel_id = args["conversation_id"].strip()
    wanted = limit(args, 50, 100)
    answer = await api(ctx, f"/channels/{channel_id}/messages", {"before": wanted, "after": 0})
    me = (await api(ctx, "/self")).get("id")
    messages = [
        {
            # "You" for this account; otherwise the other member's id (list_conversations has the name).
            "from": "You"
            if (message.get("metadata") or {}).get("src") == me
            else (message.get("metadata") or {}).get("src"),
            "body": (message.get("metadata") or {}).get("content", ""),
            "sent_at": message.get("created_at"),
        }
        for message in answer.get("messages") or []
    ]
    return {"conversation_id": channel_id, "messages": messages[-wanted:]}
