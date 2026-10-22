"""Publish course."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.courses import COURSE_PROP, course_id
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "course_id": COURSE_PROP,
        "published": {"type": "boolean", "description": "true publishes, false turns it back into a draft."},
    },
    "required": ["group", "course_id", "published"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"course_id": "37ec34ad", "published": True}


@tool(
    name="set_course_published",
    title="Publish course",
    access="write",
    confirm=True,
    description="Publish a draft course to members, or turn it back into a draft. Admins only.",
    details=(
        "Publishes a Classroom course so members who have access see it, or turns it back into a draft "
        "only admins see, as the course's Published switch does. Members' progress is kept. Admins only. "
        "Publishing shows the course to members, so by default you confirm each call; you can switch that "
        "off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/courses/{course_id}/published",
    example_response=EXAMPLE_RESPONSE,
)
async def set_course_published(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    target = await course_id(ctx, args["group"].strip().lower(), args["course_id"])
    state = "published" if args["published"] else "draft"
    try:
        await write(ctx, "PUT", f"/courses/{target}/state", params={"state": state})
    except ToolError as exc:
        # Skool refuses a switch to the state the course already has; the caller got what it asked.
        if "same state" not in str(exc):
            raise
    return {"course_id": args["course_id"], "published": args["published"]}
