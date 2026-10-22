"""Get event."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, group_name
from skool_api_mcp.skool.events import event

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

EXAMPLE_RESPONSE: dict[str, Any] = {
    "event_id": "2ff67da14c4242b7abb3449b869a4b42",
    "title": "Weekly Q&A",
    "description": "Bring your questions.",
    "start": "2026-10-25T16:00:00Z",
    "end": "2026-10-25T17:00:00Z",
    "timezone": "America/New_York",
    "location_type": "zoom",
    "location": "https://zoom.us/j/123456789",
    "access": "all",
    "recurring": False,
}


@tool(
    name="get_event",
    title="Get event",
    access="read",
    confirm=False,
    description="One calendar event with its full description, place and access.",
    details=(
        "Returns one event of the group's calendar: title, description, start and end in UTC, the event's "
        "time zone, where it happens and who can see it."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/events/{event_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_event(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group_name(args["group"])
    return event(await api(ctx, f"/calendar-events/{args['event_id']}"))
