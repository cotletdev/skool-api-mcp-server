"""Create course."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, api, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "title": {"type": "string", "maxLength": 50, "description": "Course title, up to 50 characters."},
        "description": {
            "type": "string",
            "maxLength": 500,
            "description": "Shown on the course card, up to 500 characters.",
        },
        "published": {
            "type": "boolean",
            "description": "true shows it to members now; default false keeps it a draft.",
        },
        "min_level": {
            "type": "integer",
            "minimum": 1,
            "maximum": 9,
            "description": "Unlock only from this level up. Default: open to all members.",
        },
    },
    "required": ["group", "title"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "course_id": "37ec34ad",
    "title": "Funnel Basics",
    "published": False,
    "url": "https://www.skool.com/yourgroup/classroom/37ec34ad",
}


@tool(
    name="create_course",
    title="Create course",
    access="write",
    confirm=False,
    description="Add a course to the group's Classroom, as a draft or published. Admins only.",
    details=(
        "Creates a Classroom course, as Classroom, New course does, as a draft unless published is true. "
        "Open to all members, or only from min_level up. Paid and time-unlocked courses are set in Skool. "
        "Add lessons with create_lesson. Admins only. A draft is seen by admins only, so it runs without "
        "asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/courses",
    example_response=EXAMPLE_RESPONSE,
)
async def create_course(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    metadata: dict[str, Any] = {
        "title": args["title"].strip(),
        "desc": (args.get("description") or "").strip(),
        # Skool's access types: 1 open to all members, 2 from a level up.
        "privacy": 2 if args.get("min_level") else 1,
        "min_tier": 0,
        "lock_free_trial": 0,
    }
    if args.get("min_level"):
        metadata["min_access_level"] = args["min_level"]
    body = {
        "group_id": info["id"],
        "user_id": (await api(ctx, "/self")).get("id", ""),
        "unit_type": "course",
        "state": 2 if args.get("published") else 1,
        "metadata": metadata,
    }
    course = await write(ctx, "POST", "/courses", body=body)
    group = args["group"].strip().lower()
    return {
        "course_id": course.get("name"),
        "title": (course.get("metadata") or {}).get("title"),
        "published": course.get("state") == 2,
        "url": f"{WEB}/{group}/classroom/{course.get('name')}",
    }
