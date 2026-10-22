"""Set member role."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "membership_id": {"type": "string", "description": "membership_id from list_members."},
        "role": {
            "type": "string",
            "enum": ["admin", "moderator", "member"],
            "description": "admin, moderator or member.",
        },
    },
    "required": ["group", "membership_id", "role"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"membership_id": "7915f251cdf14c32a201bf1cf7b12c98", "role": "moderator"}


@tool(
    name="set_member_role",
    title="Set member role",
    access="write",
    confirm=True,
    description="Make a member an admin or moderator, or back to a member. Admins only.",
    details=(
        "Changes one member's role, as the member's Membership settings do: admin (full control), "
        "moderator (can remove posts and members) or member. Skool allows moderators only on the Pro "
        "plan. The group owner keeps their role. Admins only. By default you confirm each call; you can "
        "switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/memberships/{membership_id}/role",
    example_response=EXAMPLE_RESPONSE,
)
async def set_member_role(ctx: ToolContext, args: dict[str, Any]) -> Any:
    await admin_group(ctx, args)
    raw = {"admin": "group-admin", "moderator": "group-moderator", "member": "member"}[args["role"]]
    await write(ctx, "POST", f"/members/{args['membership_id']}/role", body={"new": raw})
    return {"membership_id": args["membership_id"], "role": args["role"]}
