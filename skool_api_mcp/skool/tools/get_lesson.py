"""Get lesson."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP
from skool_api_mcp.skool.courses import COURSE_PROP, course_page, group_of, lesson, to_text

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "course_id": COURSE_PROP,
        "lesson_id": {"type": "string", "description": "lesson_id from get_course or list_courses."},
    },
    "required": ["group", "course_id", "lesson_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "lesson_id": "4585d17f546b4ff48ae6058ad34761d9",
    "title": "Lesson 1: the offer",
    "kind": "lesson",
    "published": True,
    "url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e?md=4585d17f546b4ff48ae6058ad34761d9",
    "body": "Start with the one thing you sell.\n\nThen write it down in one line.",
    "video_url": "https://www.youtube.com/watch?v=abc123",
    "uploaded_video": False,
}


@tool(
    name="get_lesson",
    title="Get lesson",
    access="read",
    confirm=False,
    description="One lesson's text and video link.",
    details=(
        "Returns one Classroom lesson as its page shows it: the text (formatting dropped, paragraphs and "
        "list items kept) and the linked video. uploaded_video is true when the video was uploaded to "
        "Skool; that video and attached files are not returned. Only lessons this account can open."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/courses/{course_id}/lessons/{lesson_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_lesson(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_of(args)
    props = await course_page(ctx, group, args["course_id"], args["lesson_id"])
    course = props["course"]["course"]
    found = None
    stack = list(props["course"].get("children") or [])
    while stack:
        node = stack.pop()
        unit = node.get("course") or {}
        if unit.get("id") == args["lesson_id"]:
            found = unit
            break
        stack.extend(node.get("children") or [])
    if not found:
        raise ToolError("This course has no such lesson.", ErrorCode.TARGET_ERROR)
    meta = found.get("metadata") or {}
    return {
        **lesson(group, course, found),
        "body": to_text(meta.get("desc")),
        "video_url": meta.get("videoLink") or None,
        "uploaded_video": bool(meta.get("videoId")),
    }
