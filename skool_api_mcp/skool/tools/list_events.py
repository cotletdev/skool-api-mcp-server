"""List events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, page_data
from skool_api_mcp.skool.events import event

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "month": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}$", "description": "YYYY-MM. Default: this month."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "month": "2026-10",
    "timezone": "America/New_York",
    "events": [
        {
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
    ],
}


@tool(
    name="list_events",
    title="List events",
    access="read",
    confirm=False,
    description="Events on a group's calendar in one month: title, time, place and who can join.",
    details=(
        "Lists the events of one month on the group's Calendar tab, as the month view shows them, "
        "recurring events once per date. start and end are UTC; timezone is the calendar's zone. "
        "get_event returns one event, create_event adds one."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/events",
    example_response=EXAMPLE_RESPONSE,
)
async def list_events(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    params: dict[str, Any] = {"group": group}
    if month := args.get("month"):
        try:
            # Skool's calendar takes any moment inside the month it shows.
            params["calDate"] = int(datetime.strptime(f"{month}-15", "%Y-%m-%d").replace(tzinfo=UTC).timestamp())
        except ValueError as exc:
            raise ToolError("month must be YYYY-MM.", ErrorCode.INVALID_INPUT) from exc
    props = await page_data(ctx, f"{group}/calendar", params)
    return {
        "month": month or datetime.now(UTC).strftime("%Y-%m"),
        "timezone": props.get("timezone"),
        "events": [event(item) for item in props.get("events") or []],
    }
