"""Delete membership question."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group, numbered

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "number": {
            "type": "integer",
            "minimum": 1,
            "description": "Question number, from add_membership_question or get_group.",
        },
    },
    "required": ["group", "number"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "questions": [{"number": 1, "question": "What brings you here?", "type": "text", "options": None}]
}


@tool(
    name="delete_membership_question",
    title="Delete membership question",
    access="write",
    confirm=False,
    description="Remove a membership question. Admins only.",
    details=(
        "Removes one membership question; the ones after it move up a number. Returns the questions left. "
        "Admins only. Runs without asking first: nobody is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/membership-questions/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_membership_question(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    path = f"/groups/{info['id']}/delete-survey-question"
    answer = await write(ctx, "DELETE", path, params={"idx": args["number"] - 1})
    return {"questions": numbered(answer.get("survey"), ("question", "type", "options"))}
