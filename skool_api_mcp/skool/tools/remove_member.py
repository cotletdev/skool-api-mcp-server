"""Remove member."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_info, group_name, require_admin, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "membership_id": {"type": "string", "description": "membership_id from list_members."},
    },
    "required": ["group", "membership_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"membership_id": "7915f251cdf14c32a201bf1cf7b12c98", "status": "removed"}


@tool(
    name="remove_member",
    title="Remove member",
    access="write",
    confirm=True,
    description="Remove a member from the group, or lift a ban. Admins only.",
    details=(
        "Removes one member, as Membership settings, Remove does: they lose access but may ask to join "
        "again. On a banned member it lifts the ban the same way, as Unban does. Their posts stay. Admins "
        "and moderators. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/memberships/{membership_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def remove_member(ctx: ToolContext, args: dict[str, Any]) -> Any:
    require_admin(await group_info(ctx, group_name(args["group"])), moderators=True)
    # Skool's Remove and Unban both set the "declined" role: out of the group, free to ask again.
    await write(ctx, "POST", f"/members/{args['membership_id']}/role", body={"new": "declined"})
    return {"membership_id": args["membership_id"], "status": "removed"}
