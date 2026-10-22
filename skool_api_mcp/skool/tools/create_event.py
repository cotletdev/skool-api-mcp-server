"""Create event."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.events import ACCESS_PROPS, LOCATION_PROPS, access, event, location, when, zone
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "title": {"type": "string", "description": "Event title."},
        "start": {"type": "string", "description": "Start, ISO 8601. Without an offset it is read in timezone."},
        "duration_minutes": {"type": "integer", "minimum": 15, "description": "Length in minutes. Default: 60."},
        "timezone": {
            "type": "string",
            "description": "IANA zone the event is shown in, e.g. America/New_York. Default: UTC.",
        },
        "description": {"type": "string", "description": "What the event is about."},
        **LOCATION_PROPS,
        **ACCESS_PROPS,
    },
    "required": ["group", "title", "start"],
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
    name="create_event",
    title="Create event",
    access="write",
    confirm=True,
    description="Add an event to a group's calendar. Admins only.",
    details=(
        "Adds a one-time event to the Calendar tab, as Add event does: title, start, length, time zone, "
        "description, where (a Zoom or Meet link, an address or any URL) and who sees it. Skool reminds "
        "members before it starts. Admins only. Members see it at once, so by default you confirm each "
        "call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/events",
    example_response=EXAMPLE_RESPONSE,
)
async def create_event(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    tz = zone(args.get("timezone"))
    start, end = when(args["start"], args.get("duration_minutes") or 60, tz)
    body = {
        "group_id": info["id"],
        "start_time": start,
        "end_time": end,
        "metadata": {
            "title": args["title"].strip(),
            "description": (args.get("description") or "").strip(),
            "timezone": tz.key,
            "reminder_disabled": 0,
            "cover_image": "",
            "location": location(args),
            "privacy": access(args),
        },
    }
    return event(await write(ctx, "POST", "/calendar-events", body=body), args.get("location"))
