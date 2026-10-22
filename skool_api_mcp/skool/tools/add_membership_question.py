"""Add membership question."""

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
    "required": ["group", "question"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "questions": [{"number": 1, "question": "What brings you here?", "type": "text", "options": None}]
}


@tool(
    name="add_membership_question",
    title="Add membership question",
    access="write",
    confirm=False,
    description="Add a question people answer when they ask to join the group. Admins only.",
    details=(
        "Adds a membership question, as Settings, Membership questions does; Skool asks up to 3 and only "
        "one of type email. Answers show next to each request in list_membership_requests. Returns all "
        "questions. Admins only. Runs without asking first: nobody is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/membership-questions",
    example_response=EXAMPLE_RESPONSE,
)
async def add_membership_question(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    kind = args.get("type") or "text"
    body: dict[str, Any] = {"question": args["question"].strip(), "type": kind}
    if kind == "options":
        body["options"] = [option.strip() for option in args.get("options") or [] if option.strip()]
    answer = await write(ctx, "POST", f"/groups/{info['id']}/add-survey-question", body=body)
    return {"questions": numbered(answer.get("survey"), ("question", "type", "options"))}
