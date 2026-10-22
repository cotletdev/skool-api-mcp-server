"""Group settings an admin edits in Settings: categories, rules, links, levels, membership questions.

Rules and links have no ids: Skool numbers them from 1 in the order the group shows them, and every change
answers with the whole new list. Paths take the group's id.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.helpers import json_field
from skool_api_mcp.skool.client import api, group_info, group_name, require_admin

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

# Who may post in a category and how it sorts, as the category form names them (Skool's numbers and keys).
WRITE_ROLES = {"members": 4, "admins": 3}
SORTS = {"default": "newest-cm", "new": "newest", "top_week": "best-1w", "top_month": "best-1m", "top_year": "best-1y"}


async def admin_group(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    info = await group_info(ctx, group_name(args["group"]))
    require_admin(info)
    return info


async def group_record(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    """The group as any member may read it. Its links and levels ride along in metadata: the separate
    `/groups/{id}/links`, `/labels` and `/levels` answer a member 401, which reads as signed out."""
    group = await api(ctx, f"/groups/{group_name(args['group'])}")
    if not group.get("id"):
        raise ToolError("Skool has no such group, or this account cannot see it.", ErrorCode.TARGET_ERROR)
    return group


async def group_id(ctx: ToolContext, args: dict[str, Any]) -> str:
    """The group's id for a read; any member can call it."""
    return (await group_record(ctx, args))["id"]


def meta_list(group: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = json_field((group.get("metadata") or {}).get(key)) or {}
    return value.get(key) or [] if isinstance(value, dict) else []


def category(label: dict[str, Any]) -> dict[str, Any]:
    """A label from api2 (snake_case) or from a page (camelCase)."""
    meta = label.get("metadata") or {}
    raw_role = meta.get("post_write_role", meta.get("postWriteRole"))
    raw_sort = meta.get("default_sort") or meta.get("defaultSort") or "newest-cm"
    roles: dict[object, str] = {value: name for name, value in WRITE_ROLES.items()}
    role = roles.get(raw_role, "members")
    sort = {value: name for name, value in SORTS.items()}.get(raw_sort, "default")
    return {
        "category_id": label.get("id"),
        "name": meta.get("display_name") or meta.get("displayName"),
        "description": meta.get("description") or "",
        "who_can_post": role,
        "sort": sort,
        "posts": meta.get("posts", 0),
    }


def numbered(items: list[dict[str, Any]] | None, fields: tuple[str, ...]) -> list[dict[str, Any]]:
    return [{"number": n, **{f: item.get(f) for f in fields}} for n, item in enumerate(items or [], start=1)]


def survey(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    questions = json_field(metadata.get("survey")) or []
    if isinstance(questions, dict):
        questions = questions.get("survey") or questions.get("questions") or []
    return numbered(questions, ("question", "type", "options"))


def checked_number(number: int, items: list[Any] | None, what: str) -> int:
    count = len(items or [])
    if not 1 <= number <= count:
        raise ToolError(
            f"The group has {what} 1 to {count}." if count else f"The group has no {what}.", ErrorCode.INVALID_INPUT
        )
    return number
