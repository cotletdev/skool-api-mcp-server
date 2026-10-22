"""Create lesson."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, write
from skool_api_mcp.skool.courses import COURSE_PROP, course_id, lesson, to_doc
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "course_id": COURSE_PROP,
        "title": {"type": "string", "description": "Lesson title."},
        "body": {"type": "string", "description": "Lesson text. A blank line starts a new paragraph."},
        "video_url": {
            "type": "string",
            "format": "uri",
            "description": "YouTube, Vimeo, Loom or Wistia link shown above the text.",
        },
        "published": {"type": "boolean", "description": "false keeps it a draft. Default: true."},
    },
    "required": ["group", "course_id", "title"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "lesson_id": "4585d17f546b4ff48ae6058ad34761d9",
    "title": "Lesson 1: the offer",
    "kind": "lesson",
    "published": True,
    "url": "https://www.skool.com/yourgroup/classroom/37ec34ad?md=4585d17f546b4ff48ae6058ad34761d9",
}


@tool(
    name="create_lesson",
    title="Create lesson",
    access="write",
    confirm=False,
    description="Add a lesson at the end of a course, with text and a video link. Admins only.",
    details=(
        "Adds a lesson page at the end of a course, as the course's Add page does: title, text and an "
        "optional video link that Skool plays above it. Uploaded videos and files are not supported. "
        "Published unless published is false; in a draft course nobody but admins sees it either way. "
        "Admins only. Runs without asking first: nobody is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/courses/{course_id}/lessons",
    example_response=EXAMPLE_RESPONSE,
)
async def create_lesson(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    group = args["group"].strip().lower()
    root = await course_id(ctx, group, args["course_id"])
    metadata: dict[str, Any] = {
        "title": args["title"].strip(),
        "desc": to_doc(args.get("body") or ""),
        "resources": "[]",
    }
    if args.get("video_url"):
        metadata["video_link"] = args["video_url"].strip()
    body = {
        "group_id": info["id"],
        "user_id": (await api(ctx, "/self")).get("id", ""),
        "unit_type": "module",
        "state": 1 if args.get("published") is False else 2,
        "root_id": root,
        "parent_id": root,
        "metadata": metadata,
    }
    unit = await write(ctx, "POST", "/courses", body=body)
    return lesson(group, {"name": args["course_id"].strip().rsplit("/", 1)[-1]}, unit)
