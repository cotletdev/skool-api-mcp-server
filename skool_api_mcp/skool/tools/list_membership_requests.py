"""List membership requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field, limit, page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import full_name, group_info, group_name, page_data, require_admin

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "limit": {"type": "integer", "description": "1 to 30. Default: 30."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "requests": [
        {
            "request_id": "688c3c9966c84690b934622ddfdb3531",
            "name": "Tom Becker",
            "requested_at": "2026-10-03T07:45:00.000000Z",
            "answers": [
                {"question": "What are you building?", "answer": "A SaaS for dental clinics, launching in November."}
            ],
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_membership_requests",
    title="List membership requests",
    access="read",
    confirm=False,
    description=(
        "Pending requests to join, with each applicant's Membership Questions answers. Admins and moderators only."
    ),
    details=(
        "Lists requests to join a private group, 30 to a page, oldest first within the page, with the "
        "answers each applicant gave to your Membership Questions. Only admins and moderators see "
        "requests; other accounts get APP_PERMISSION_DENIED. Pass request_id to "
        "approve_membership_request or decline_membership_request."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/membership-requests",
    example_response=EXAMPLE_RESPONSE,
)
async def list_membership_requests(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    require_admin(await group_info(ctx, group), moderators=True)
    page = page_cursor(args.get("cursor"))
    props = await page_data(ctx, f"{group}/-/members", {"group": group, "t": "pending", "p": page})
    requests = []
    for user in props.get("users") or []:
        member = user.get("member") or {}
        requests.append(
            {
                "request_id": member.get("id"),
                "name": full_name(user),
                "requested_at": member.get("requestedAt") or member.get("createdAt"),
                "answers": _answers(member),
            }
        )
    requests.sort(key=lambda item: item["requested_at"] or "")
    more = page < int(props.get("totalPages") or 1)
    return {"requests": requests[: limit(args, 30, 30)], "next_cursor": str(page + 1) if more else None}


def _answers(member: dict[str, Any]) -> list[dict[str, str]]:
    """Membership Questions answers; Skool keeps them as JSON in the member's metadata."""
    survey = json_field((member.get("metadata") or {}).get("survey"))
    items = survey.get("survey") if isinstance(survey, dict) else survey
    return [
        {"question": str(item.get("question", "")), "answer": str(item.get("answer", ""))}
        for item in items or []
        if isinstance(item, dict)
    ]
