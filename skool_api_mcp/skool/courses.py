"""Classroom (recorded 18.10.2026): list_courses gives a course's short name, api2 `/courses` wants its id.

A course is a tree of units: `course`, then optional `set` (folder), then `module` (a lesson page).
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.skool.client import WEB, group_name, page_data

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

_ID = re.compile(r"^[0-9a-f]{32}$")

COURSE_PROP: dict[str, Any] = {"type": "string", "description": "course_id from list_courses or create_course."}


async def course_id(ctx: ToolContext, group: str, course: str) -> str:
    """The course's id for api2, from its short name (what list_courses returns) or the id itself."""
    course = course.strip().rsplit("/", 1)[-1].split("?")[0]
    if _ID.match(course):
        return course
    props = await page_data(ctx, f"{group}/classroom/{course}", {"group": group, "course": course})
    found = ((props.get("course") or {}).get("course") or {}).get("id")
    if not found:
        raise ToolError(
            "Skool has no such course in this group, or this account cannot open it.", ErrorCode.TARGET_ERROR
        )
    return found


async def course_page(ctx: ToolContext, group: str, course: str, lesson_id: str | None = None) -> dict[str, Any]:
    """The course page: its tree, and the text of one lesson (the one opened, `md`). Members and admins alike."""
    name = course.strip().rsplit("/", 1)[-1].split("?")[0]
    params = {"group": group, "course": name, **({"md": lesson_id} if lesson_id else {})}
    props = await page_data(ctx, f"{group}/classroom/{name}", params)
    if not (props.get("course") or {}).get("course"):
        raise ToolError(
            "Skool has no such course in this group, or this account cannot open it.", ErrorCode.TARGET_ERROR
        )
    return props


def lesson(group: str, course: dict[str, Any], unit: dict[str, Any]) -> dict[str, Any]:
    meta = unit.get("metadata") or {}
    kind = unit.get("unitType") or unit.get("unit_type")
    return {
        "lesson_id": unit.get("id"),
        "title": meta.get("title"),
        "kind": "folder" if kind == "set" else "lesson",
        "published": unit.get("state") == 2,
        "url": f"{WEB}/{group}/classroom/{course.get('name')}?md={unit.get('id')}",
    }


# Lesson text is the classroom editor's document: "[v2]" and a JSON list of ProseMirror nodes.
_DOC = "[v2]"


def to_doc(text: str) -> str:
    """Plain text as the editor saves it: a blank line starts a paragraph, a line break stays one."""
    paragraphs = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        content: list[dict[str, Any]] = []
        for number, line in enumerate(block.split("\n")):
            if number:
                content.append({"type": "hardBreak"})
            if line:
                content.append({"type": "text", "text": line})
        paragraphs.append({"type": "paragraph", **({"content": content} if content else {})})
    return _DOC + json.dumps(paragraphs, ensure_ascii=False, separators=(",", ":"))


def to_text(desc: str | None) -> str:
    """The editor's document as plain text: paragraphs, line breaks, list items with a dash."""
    if not desc or not desc.startswith(_DOC):
        return desc or ""
    try:
        nodes = json.loads(desc[len(_DOC) :])
    except ValueError:
        return ""

    def text(node: dict[str, Any]) -> str:
        kind = node.get("type")
        if kind == "text":
            return node.get("text", "")
        if kind == "hardBreak":
            return "\n"
        inner = "".join(text(child) for child in node.get("content") or [])
        if kind == "listItem":
            return f"- {inner.strip()}\n"
        return inner

    blocks = [text(node).strip("\n") for node in nodes]
    return "\n\n".join(block for block in blocks if block)


def group_of(args: dict[str, Any]) -> str:
    return group_name(args["group"])
