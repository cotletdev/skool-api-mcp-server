"""Get course."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB
from skool_api_mcp.skool.courses import COURSE_PROP, course_page, group_of, lesson

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "course_id": COURSE_PROP,
    },
    "required": ["group", "course_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "course_id": "4b1c2d3e",
    "title": "Funnel Basics",
    "description": "Five short lessons.",
    "published": True,
    "lessons": [
        {
            "lesson_id": "4585d17f546b4ff48ae6058ad34761d9",
            "title": "Lesson 1: the offer",
            "kind": "lesson",
            "published": True,
            "url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e?md=4585d17f546b4ff48ae6058ad34761d9",
        }
    ],
    "url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e",
}


@tool(
    name="get_course",
    title="Get course",
    access="read",
    confirm=False,
    description="One course with its lessons and folders in Classroom order; get_lesson reads a lesson.",
    details=(
        "Returns one Classroom course: title, description, whether it is published, and its lessons in "
        "order. Folders come as kind folder, followed by their lessons. get_lesson returns a lesson's "
        "text and video. Only courses this account can open; admins also see drafts."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/courses/{course_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_course(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_of(args)
    props = await course_page(ctx, group, args["course_id"])
    course = props["course"]["course"]
    meta = course.get("metadata") or {}
    lessons: list[dict[str, Any]] = []

    def walk(nodes: list[dict[str, Any]]) -> None:
        for node in nodes:
            lessons.append(lesson(group, course, node.get("course") or {}))
            walk(node.get("children") or [])

    walk(props["course"].get("children") or [])
    return {
        "course_id": course.get("name"),
        "title": meta.get("title"),
        "description": meta.get("desc") or "",
        "published": course.get("state") == 2,
        "lessons": lessons,
        "url": f"{WEB}/{group}/classroom/{course.get('name')}",
    }
