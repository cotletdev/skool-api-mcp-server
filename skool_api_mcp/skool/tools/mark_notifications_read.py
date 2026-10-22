"""Mark notifications read."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import group_name, write
from skool_api_mcp.skool.settings import group_id

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Only this group's, by URL name. Default: all groups."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"group": None, "status": "read"}


@tool(
    name="mark_notifications_read",
    title="Mark notifications read",
    access="write",
    confirm=False,
    description="Mark all your notifications read, everywhere or in one group.",
    details=(
        "Clears the unread count on the bell, as Mark all as read does, for every group or only the one "
        "given. Changes only this account's notifications, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /notifications/read",
    example_response=EXAMPLE_RESPONSE,
)
async def mark_notifications_read(ctx: ToolContext, args: dict[str, Any]) -> Any:
    body: dict[str, Any] = {"cmd": "read", "all": True, "group_id": ""}
    if args.get("group"):
        group_name(args["group"])
        body.update(all=False, group_id=await group_id(ctx, args))
    await write(ctx, "POST", "/messages", body=body)
    return {"group": args.get("group"), "status": "read"}
