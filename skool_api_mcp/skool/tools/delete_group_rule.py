"""Delete group rule."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, write
from skool_api_mcp.skool.settings import admin_group, checked_number
from skool_api_mcp.skool.tools.list_group_rules import _rules

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "number": {"type": "integer", "description": "Rule number from list_group_rules."},
    },
    "required": ["group", "number"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "rules": [{"number": 1, "title": "Be kind", "description": "Keep it constructive."}]
}


@tool(
    name="delete_group_rule",
    title="Delete group rule",
    access="write",
    confirm=True,
    description="Delete a group rule. Admins only.",
    details=(
        "Deletes one rule, as Settings, Rules, Delete does; the rules after it move up a number. Returns "
        "the whole new list. Admins only. By default you confirm each call; you can switch that off for "
        "this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /groups/{group}/rules/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_group_rule(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    current = (await api(ctx, f"/groups/{info['id']}/rules")).get("rules") or []
    number = checked_number(args["number"], current, "rules")
    return {"rules": _rules(await write(ctx, "DELETE", f"/groups/{info['id']}/rules/{number}"))}
