"""Add group rule."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, write
from skool_api_mcp.skool.settings import admin_group
from skool_api_mcp.skool.tools.list_group_rules import _rules

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "title": {"type": "string", "maxLength": 30, "description": "Rule title, up to 30 characters."},
        "description": {"type": "string", "description": "What the rule means, shown under the title."},
    },
    "required": ["group", "title"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "rules": [{"number": 1, "title": "Be kind", "description": "Keep it constructive."}]
}


@tool(
    name="add_group_rule",
    title="Add group rule",
    access="write",
    confirm=False,
    description="Add a rule at the end of the group rules. Admins only.",
    details=(
        "Adds a rule after the existing ones, as Settings, Rules, Add does, and returns the whole new "
        "list. Admins only. Nobody is notified and it is undone with delete_group_rule, so it runs "
        "without asking first."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /groups/{group}/rules",
    example_response=EXAMPLE_RESPONSE,
)
async def add_group_rule(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    rule = {"title": args["title"].strip(), "content": (args.get("description") or "").strip()}
    return {"rules": _rules(await write(ctx, "POST", f"/groups/{info['id']}/rules", body=rule))}
