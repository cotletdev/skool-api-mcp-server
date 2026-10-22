"""Set AutoDM."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "message": {
            "type": "string",
            "description": "New welcome text. #NAME# and #GROUPNAME# are filled in by Skool.",
        },
        "enabled": {"type": "boolean", "description": "Turn the AutoDM on or off. Pro plan only."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"group": "yourgroup", "message_updated": True, "enabled": True}


@tool(
    name="set_auto_dm",
    title="Set AutoDM",
    access="write",
    confirm=True,
    description="Change the welcome message new members get, or turn it on or off. Admins only.",
    details=(
        "Changes the group's AutoDM, the chat message Skool sends each new member on approval. message "
        "replaces the text; enabled turns it on or off, which Skool allows only on the Pro plan. Admins "
        "only. Every new member gets the result, so by default you confirm each call; you can switch that "
        "off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/auto-dm",
    example_response=EXAMPLE_RESPONSE,
)
async def set_auto_dm(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    if "message" not in args and "enabled" not in args:
        raise ToolError("Give message or enabled to change.", ErrorCode.INVALID_INPUT)
    base = f"/groups/{info['id']}"
    if "message" in args:
        await write(ctx, "POST", f"{base}/update-auto-dm-message", body={"auto_dm_message": args["message"]})
    if "enabled" in args:
        await write(ctx, "POST", f"{base}/{'enable' if args['enabled'] else 'disable'}-auto-dm")
    return {"group": args["group"], "message_updated": "message" in args, "enabled": args.get("enabled")}
