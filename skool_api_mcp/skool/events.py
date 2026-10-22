"""Calendar events (recorded 18.10.2026): api2 `/calendar-events`, the month view from the calendar page.

Skool keeps location and access as JSON strings inside metadata; numbers below are Skool's own.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.helpers import json_field

LOCATIONS = {"zoom": 1, "meet": 2, "address": 3, "link": 4, "skool_call": 5, "skool_webinar": 6}
ACCESS = {"all": 0, "level": 1, "course": 2}

LOCATION_PROPS: dict[str, Any] = {
    "location_type": {
        "type": "string",
        "enum": list(LOCATIONS),
        "description": "zoom, meet, address or link (default), skool_call or skool_webinar.",
    },
    "location": {"type": "string", "description": "The Zoom or Meet link, the address or the URL."},
}
ACCESS_PROPS: dict[str, Any] = {
    "access": {
        "type": "string",
        "enum": list(ACCESS),
        "description": "Who sees it: all members (default), members from min_level up, or a course's members.",
    },
    "min_level": {"type": "integer", "minimum": 1, "maximum": 9, "description": "With access level."},
    "course_id": {"type": "string", "description": "With access course: course_id from list_courses."},
}


def zone(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or "UTC")
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ToolError("timezone must be an IANA name such as America/New_York.", ErrorCode.INVALID_INPUT) from exc


def when(start: str, minutes: int, tz: ZoneInfo) -> tuple[str, str]:
    """Skool's start and end: local time in the event's zone with its offset, as the calendar form sends."""
    try:
        moment = datetime.fromisoformat(start.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ToolError("start must be ISO 8601, e.g. 2026-10-25T18:00.", ErrorCode.INVALID_INPUT) from exc
    moment = moment.replace(tzinfo=tz) if moment.tzinfo is None else moment.astimezone(tz)
    return moment.isoformat(timespec="seconds"), (moment + timedelta(minutes=minutes)).isoformat(timespec="seconds")


def location(args: dict[str, Any]) -> str:
    kind = args.get("location_type") or "link"
    return json.dumps({"location_type": LOCATIONS[kind], "location_info": (args.get("location") or "").strip()})


def access(args: dict[str, Any]) -> str:
    kind = args.get("access") or "all"
    rule: dict[str, Any] = {"privacy_type": ACCESS[kind]}
    if kind == "level":
        if not args.get("min_level"):
            raise ToolError("access level needs min_level (1 to 9).", ErrorCode.INVALID_INPUT)
        rule["min_access_level"] = args["min_level"]
    if kind == "course":
        if not args.get("course_id"):
            raise ToolError("access course needs course_id.", ErrorCode.INVALID_INPUT)
        rule["access_course"] = args["course_id"]
    return json.dumps(rule)


def utc(value: str | None) -> str | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(item: dict[str, Any], fallback_location: str | None = None) -> dict[str, Any]:
    """An event as the tools return it; a write's answer hides the location, so the caller passes what it sent."""
    meta = item.get("metadata") or {}
    place = json_field(meta.get("location")) or {}
    rule = json_field(meta.get("privacy")) or {}
    kinds: dict[object, str] = {value: name for name, value in LOCATIONS.items()}
    accesses: dict[object, str] = {value: name for name, value in ACCESS.items()}
    start, end = item.get("start_time") or item.get("startTime"), item.get("end_time") or item.get("endTime")
    return {
        "event_id": item.get("id"),
        "title": meta.get("title"),
        "description": meta.get("description") or "",
        "start": utc(start),
        "end": utc(end),
        "timezone": meta.get("timezone"),
        "location_type": kinds.get(place.get("location_type")),
        "location": place.get("location_info") or fallback_location or "",
        "access": accesses.get(rule.get("privacy_type", 0), "all"),
        "recurring": bool(item.get("recurrence")),
    }
