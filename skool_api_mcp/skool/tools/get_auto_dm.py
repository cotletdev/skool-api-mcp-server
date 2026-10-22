"""Get AutoDM."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, full_name, group_name
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "enabled": True,
    "message": "Hey #NAME#, welcome to #GROUPNAME#!",
    "sender": "Jordan Price",
}


@tool(
    name="get_auto_dm",
    title="Get AutoDM",
    access="read",
    confirm=False,
    description="The welcome message Skool sends every new member, and whether it is on. Admins only.",
    details=(
        "Returns the group's AutoDM: the chat message Skool sends each new member when they are approved, "
        "who it comes from and whether it is on. #NAME# and #GROUPNAME# in the text become the member's "
        "first name and the group's name. Admins only."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/auto-dm",
    example_response=EXAMPLE_RESPONSE,
)
async def get_auto_dm(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    answer = await api(ctx, f"/groups/{info['id']}/auto-dm")
    # On or off is a group setting (the AutoDM plugin), not part of the AutoDM answer.
    meta = (await api(ctx, f"/groups/{group_name(args['group'])}")).get("metadata") or {}
    return {
        "enabled": str(meta.get("plugin_auto_dm_enabled", "0")) == "1",
        "message": answer.get("auto_dm_message") or "",
        "sender": full_name(answer.get("auto_dm_user")),
    }
