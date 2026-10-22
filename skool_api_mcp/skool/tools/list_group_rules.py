"""List group rules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api
from skool_api_mcp.skool.settings import group_id

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"group": GROUP_PROP},
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "rules": [{"number": 1, "title": "Be kind", "description": "Keep it constructive."}]
}


@tool(
    name="list_group_rules",
    title="List group rules",
    access="read",
    confirm=False,
    description="The rules of a group, numbered as the group shows them.",
    details=(
        "Lists the group rules members agree to, numbered from 1 in the order the group shows them. "
        "update_group_rule and delete_group_rule take the number."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/rules",
    example_response=EXAMPLE_RESPONSE,
)
async def list_group_rules(ctx: ToolContext, args: dict[str, Any]) -> Any:
    answer = await api(ctx, f"/groups/{await group_id(ctx, args)}/rules")
    return {"rules": _rules(answer)}


def _rules(answer: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"number": n, "title": rule.get("title"), "description": rule.get("content") or ""}
        for n, rule in enumerate(answer.get("rules") or [], start=1)
    ]
