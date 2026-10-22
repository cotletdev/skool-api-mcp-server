"""Mark lesson complete."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "lesson_id": {"type": "string", "description": "lesson_id from get_course."},
        "completed": {"type": "boolean", "description": "false marks it not done. Default: true."},
    },
    "required": ["group", "lesson_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"lesson_id": "4585d17f546b4ff48ae6058ad34761d9", "completed": True}


@tool(
    name="mark_lesson_complete",
    title="Mark lesson complete",
    access="write",
    confirm=False,
    description="Mark a lesson done in your own course progress, or undo it.",
    details=(
        "Ticks a lesson as done for this account, as the lesson's Mark as done does; completed false "
        "clears it. Changes only your own progress bar, so it runs without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/lessons/{lesson_id}/completion",
    example_response=EXAMPLE_RESPONSE,
)
async def mark_lesson_complete(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group_name(args["group"])
    completed = args.get("completed", True)
    await write(ctx, "POST", f"/courses/{args['lesson_id']}/{'mark-done' if completed else 'mark-undone'}")
    return {"lesson_id": args["lesson_id"], "completed": completed}
