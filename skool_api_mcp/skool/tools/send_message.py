"""Send message."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import api, group_info, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "member_id": {
            "type": "string",
            "description": "member_id from list_members, or with.member_id from list_conversations.",
        },
        "body": {"type": "string", "description": "Message text."},
        "group": {
            "type": "string",
            "description": "Group URL name you share with the member. Default: the first of your groups that works.",
        },
    },
    "required": ["member_id", "body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversation_id": "7c3e9a1b2d4f4e6a8b0c1d2e3f4a5b6c",
    "message_id": "0f1e2d3c4b5a49687766554433221100",
    "status": "sent",
    "sent_at": "2026-10-03T07:05:00.000000Z",
}


@tool(
    name="send_message",
    title="Send message",
    access="write",
    confirm=True,
    description="Send a direct message in Skool Chat to a member, starting a conversation if needed.",
    details=(
        "Sends a direct message in Skool Chat to one member and starts a conversation if there is none "
        "yet. Skool opens the chat in a group you both belong to: pass group, else the first of your "
        "groups that Skool accepts is used. Skool refuses a message to yourself, and a group can limit "
        "chat by level. Messages go out under your name and cannot be deleted through Cotlet; by default "
        "you confirm each one, and you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /members/{member_id}/messages",
    example_response=EXAMPLE_RESPONSE,
)
async def send_message(ctx: ToolContext, args: dict[str, Any]) -> Any:
    # Skool opens (or finds) the chat with a member through a chat request for a group both are in
    # (`g`, the group's id; 400 "invalid group ID" without it, 18.10.2026). The self chat is refused (400).
    if args.get("group"):
        groups = [(await group_info(ctx, group_name(args["group"])))["id"]]
    else:
        answer = await api(ctx, "/self/groups", {"limit": 50, "prefs": "false"})
        groups = [item["id"] for item in answer.get("groups") or [] if item.get("id")]
    chat: dict[str, Any] = {}
    for group_id in groups:
        try:
            chat = await write(ctx, "POST", f"/users/{args['member_id']}/chat-request", params={"g": group_id})
            break
        except ToolError as exc:
            if exc.code != ErrorCode.TARGET_ERROR or group_id == groups[-1]:
                raise
    channel = (chat.get("channel") or {}).get("id")
    if not channel:
        raise ToolError("Skool did not open a chat with this member.", ErrorCode.TARGET_ERROR)
    message = await write(ctx, "POST", f"/channels/{channel}/messages", body={"content": args["body"]})
    sent = message.get("created_at") or datetime.now(UTC).isoformat()
    return {"conversation_id": channel, "message_id": message.get("id"), "status": "sent", "sent_at": sent}
