"""Update group rule."""

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
        "title": {"type": "string", "maxLength": 30, "description": "Rule title, up to 30 characters."},
        "description": {"type": "string", "description": "What the rule means, shown under the title."},
    },
    "required": ["group", "number"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "rules": [{"number": 1, "title": "Be kind", "description": "Keep it constructive."}]
}


@tool(
    name="update_group_rule",
    title="Update group rule",
    access="write",
    confirm=False,
    description="Change the title or text of a group rule. Admins only.",
    details=(
        "Edits one rule, as Settings, Rules, Edit does: fields you leave out stay. Returns the whole new "
        "list. Admins only. Runs without asking first: nobody is notified."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /groups/{group}/rules/{number}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_group_rule(ctx: ToolContext, args: dict[str, Any]) -> Any:
    info = await admin_group(ctx, args)
    current = (await api(ctx, f"/groups/{info['id']}/rules")).get("rules") or []
    number = checked_number(args["number"], current, "rules")
    rule = current[number - 1]
    body = {
        "title": (args.get("title") or rule.get("title") or "").strip(),
        "content": (args["description"] if "description" in args else rule.get("content") or "").strip(),
    }
    return {"rules": _rules(await write(ctx, "PUT", f"/groups/{info['id']}/rules/{number}", body=body))}
