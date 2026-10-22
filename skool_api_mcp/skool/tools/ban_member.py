"""Ban member."""

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
        "member_id": {"type": "string", "description": "member_id from list_members; needed with delete_recent_posts."},
        "delete_recent_posts": {
            "type": "boolean",
            "description": "Also delete their recent posts and comments, as Skool offers. Default: false.",
        },
    },
    "required": ["group", "membership_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "membership_id": "7915f251cdf14c32a201bf1cf7b12c98",
    "status": "banned",
    "recent_posts_deleted": False,
}


@tool(
    name="ban_member",
    title="Ban member",
    access="write",
    confirm=True,
    description="Ban a member from the group, optionally deleting their recent posts. Admins only.",
    details=(
        "Bans one member, as Membership settings, Ban does: they lose access and cannot ask to join "
        "again. delete_recent_posts also removes their recent posts and comments, which cannot be undone. "
        "A paid member's subscription is not cancelled by this. remove_member lifts a ban. Admins and "
        "moderators. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/memberships/{membership_id}/ban",
    example_response=EXAMPLE_RESPONSE,
)
async def ban_member(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await group_info(ctx, group_name(args["group"]))
    require_admin(info, moderators=True)
    deleted = bool(args.get("delete_recent_posts") and args.get("member_id"))
    if deleted:
        await write(ctx, "POST", f"/groups/{info['id']}/delete-user-recent-posts", params={"user": args["member_id"]})
    await write(ctx, "POST", f"/members/{args['membership_id']}/role", body={"new": "banned"})
    return {"membership_id": args["membership_id"], "status": "banned", "recent_posts_deleted": deleted}
