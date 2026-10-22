"""Invite members by email."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "emails": {
            "type": "array",
            "items": {"type": "string", "format": "email"},
            "minItems": 1,
            "maxItems": 50,
            "description": "Up to 50 addresses.",
        },
        "course_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Long course ids to unlock for them on joining (from create_course or get_course).",
        },
    },
    "required": ["group", "emails"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"invited": ["ana@example.com"], "status": "sent"}


@tool(
    name="invite_members",
    title="Invite members by email",
    access="write",
    confirm=True,
    description="Email people an invitation that lets them straight into the group. Admins only.",
    details=(
        "Sends Skool's invitation email to each address, as Invite people, Invite by email does; whoever "
        "accepts joins without a membership request. Addresses already in the group are skipped by Skool. "
        "Admins only. Emails reach people outside the group, so by default you confirm each call; you can "
        "switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/invitations",
    example_response=EXAMPLE_RESPONSE,
)
async def invite_members(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    emails = sorted({email.strip().lower() for email in args["emails"] if "@" in email})
    if not emails:
        raise ToolError("Give at least one email address.", ErrorCode.INVALID_INPUT)
    body = {"emails": emails, "course_ids": args.get("course_ids") or []}
    await write(ctx, "POST", f"/groups/{group_name(args['group'])}/invite", body=body)
    return {"invited": emails, "status": "sent"}
