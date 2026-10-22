"""Update event."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, write
from skool_api_mcp.skool.events import (
    ACCESS,
    ACCESS_PROPS,
    LOCATION_PROPS,
    LOCATIONS,
    access,
    event,
    location,
    when,
    zone,
)
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "event_id": {"type": "string", "description": "event_id from list_events."},
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
    name="update_event",
    title="Update event",
    access="write",
    confirm=True,
    description="Change a calendar event's title, time, place or access. Admins only.",
    details=(
        "Edits one event, as the event's Edit does: fields you leave out stay as they are. A new start "
        "keeps the old length unless duration_minutes is given. For a recurring event this changes the "
        "whole series. Admins only. Members see the change at once, so by default you confirm each call; "
        "you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/events/{event_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_event(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    old = await api(ctx, f"/calendar-events/{args['event_id']}")
    meta = old.get("metadata") or {}
    tz = zone(args.get("timezone") or meta.get("timezone"))
    start, end = old.get("start_time"), old.get("end_time")
    if "start" in args or "duration_minutes" in args or "timezone" in args:
        minutes = args.get("duration_minutes") or _minutes(start, end)
        start, end = when(args.get("start") or start, minutes, tz)
    place = json_field(meta.get("location")) or {}
    rule = json_field(meta.get("privacy")) or {}
    merged = {
        "location_type": args.get("location_type") or _key(LOCATIONS, place.get("location_type"), "link"),
        "location": args.get("location", place.get("location_info")),
        "access": args.get("access") or _key(ACCESS, rule.get("privacy_type", 0), "all"),
        "min_level": args.get("min_level", rule.get("min_access_level")),
        "course_id": args.get("course_id", rule.get("access_course")),
    }
    body = {
        "group_id": info["id"],
        "start_time": start,
        "end_time": end,
        "metadata": {
            "title": (args.get("title") or meta.get("title") or "").strip(),
            "description": args.get("description", meta.get("description") or ""),
            "timezone": tz.key,
            "reminder_disabled": meta.get("reminder_disabled", 0),
            "cover_image": meta.get("cover_image", ""),
            "location": location(merged),
            "privacy": access(merged),
        },
    }
    if old.get("recurrence"):
        body["recurrence"] = old["recurrence"]
    answer = await write(ctx, "PUT", f"/calendar-events/{args['event_id']}", body=body)
    return event(answer, merged["location"])


def _minutes(start: str, end: str) -> int:
    span = datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.fromisoformat(start.replace("Z", "+00:00"))
    return max(15, int(span.total_seconds() // 60))


def _key(names: dict[str, int], value: int | None, default: str) -> str:
    return next((name for name, number in names.items() if number == value), default)
