"""Delete event."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "event_id": {"type": "string", "description": "event_id from list_events."},
    },
    "required": ["group", "event_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"event_id": "2ff67da14c4242b7abb3449b869a4b42", "status": "deleted"}


@tool(
    name="delete_event",
    title="Delete event",
    access="write",
    confirm=True,
    description="Delete a calendar event. Admins only.",
    details=(
        "Deletes one event from the Calendar tab, as the event's Delete does; for a recurring event the "
        "whole series goes. It cannot be undone. Admins only. By default you confirm each call; you can "
        "switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/events/{event_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_event(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    await write(ctx, "DELETE", f"/calendar-events/{args['event_id']}")
    return {"event_id": args["event_id"], "status": "deleted"}
