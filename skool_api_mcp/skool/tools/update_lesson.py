"""Update lesson."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.courses import to_doc
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "lesson_id": {"type": "string", "description": "lesson_id from get_course or create_lesson."},
        "title": {"type": "string", "description": "New title."},
        "body": {"type": "string", "description": "New text, replacing the old."},
        "video_url": {"type": "string", "description": "New video link; empty string removes the video."},
    },
    "required": ["group", "lesson_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "lesson_id": "4585d17f546b4ff48ae6058ad34761d9",
    "title": "Lesson 1: the offer",
    "status": "updated",
}


@tool(
    name="update_lesson",
    title="Update lesson",
    access="write",
    confirm=False,
    description="Change a lesson's title, text or video link. Admins only.",
    details=(
        "Edits one lesson page, as its Edit does: fields you leave out stay, body replaces the whole "
        "text. Members who completed it keep it completed. Admins only. Runs without asking first: nobody "
        "is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/lessons/{lesson_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_lesson(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    body: dict[str, Any] = {}
    if "title" in args:
        body["title"] = args["title"]
    if "body" in args:
        body["desc"] = to_doc(args["body"])
    if "video_url" in args:
        body["video_link"] = args["video_url"]
    if not body:
        raise ToolError("Give title, body or video_url to change.", ErrorCode.INVALID_INPUT)
    unit = await write(ctx, "PUT", f"/courses/{args['lesson_id']}", body=body)
    return {
        "lesson_id": unit.get("id") or args["lesson_id"],
        "title": (unit.get("metadata") or {}).get("title"),
        "status": "updated",
    }
