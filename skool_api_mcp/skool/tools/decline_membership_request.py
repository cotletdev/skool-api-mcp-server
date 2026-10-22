"""Decline membership request."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import group_info, group_name, require_admin, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "request_id": {"type": "string", "description": "request_id from list_membership_requests."},
    },
    "required": ["group", "request_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"request_id": "688c3c9966c84690b934622ddfdb3531", "status": "declined"}


@tool(
    name="decline_membership_request",
    title="Decline membership request",
    access="write",
    confirm=True,
    description="Decline an applicant's request to join.",
    details=(
        "Declines one pending request, as Skool's Decline button does. Admins and moderators only. By "
        "default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/membership-requests/{request_id}/decline",
    example_response=EXAMPLE_RESPONSE,
)
async def decline_membership_request(ctx: ToolContext, args: dict[str, Any]) -> Any:
    require_admin(await group_info(ctx, group_name(args["group"])), moderators=True)
    # A request is a member in the "pending" role; Skool's own Approve/Decline change that role.
    await write(ctx, "POST", f"/members/{args['request_id']}/role", body={"new": "declined"})
    return {"request_id": args["request_id"], "status": "declined"}
