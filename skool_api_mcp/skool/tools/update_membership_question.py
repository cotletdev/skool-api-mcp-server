"""Update membership question."""

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
        "question": {"type": "string", "maxLength": 150, "description": "The question, up to 150 characters."},
        "type": {
            "type": "string",
            "enum": ["text", "email", "options"],
            "description": "text (default), email or options (multiple choice, one answer).",
        },
        "options": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 4,
            "description": "Up to 4 answers when type is options.",
        },
    },
    "required": ["group", "number", "question"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "questions": [{"number": 1, "question": "What brings you here?", "type": "text", "options": None}]
}


@tool(
    name="update_membership_question",
    title="Update membership question",
    access="write",
    confirm=False,
    description="Change a membership question. Admins only.",
    details=(
        "Replaces one membership question with new text, type and answers. Requests already waiting keep "
        "the answers they gave. Returns all questions. Admins only. Runs without asking first: nobody is "
        "notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/membership-questions/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_membership_question(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    kind = args.get("type") or "text"
    body: dict[str, Any] = {"question": args["question"].strip(), "type": kind}
    if kind == "options":
        body["options"] = [option.strip() for option in args.get("options") or [] if option.strip()]
    path = f"/groups/{info['id']}/update-survey-question"
    answer = await write(ctx, "POST", path, params={"idx": args["number"] - 1}, body=body)
    return {"questions": numbered(answer.get("survey"), ("question", "type", "options"))}
