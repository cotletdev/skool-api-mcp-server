"""List reported posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, full_name, group_info, group_name, page_data, require_admin

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
    "posts": [
        {
            "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
            "title": "DM me for a free audit",
            "author": "Sam Lee",
            "preview": "I have spots for 3 people...",
            "url": "https://www.skool.com/yourgroup/dm-me-for-a-free-audit",
        }
    ],
    "total": 1,
}


@tool(
    name="list_reported_posts",
    title="List reported posts",
    access="read",
    confirm=False,
    description="Posts members reported to the admins, waiting for review. Admins and moderators only.",
    details=(
        "Lists the posts in the group's Reported queue that members flagged against the rules. "
        "delete_post removes one. Admins and moderators only."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/posts/reported",
    example_response=EXAMPLE_RESPONSE,
)
async def list_reported_posts(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    require_admin(await group_info(ctx, group), moderators=True)
    props = await page_data(ctx, f"{group}/-/reports", {"group": group})
    posts = []
    for item in props.get("posts") or []:
        post = item.get("post") or item
        meta = post.get("metadata") or {}
        posts.append(
            {
                "post_id": post.get("id"),
                "title": meta.get("title"),
                "author": full_name(post.get("user")),
                "preview": (meta.get("content") or "")[:200],
                "url": f"{WEB}/{group}/{post.get('name')}",
            }
        )
    return {"posts": posts, "total": int(props.get("totalPosts") or len(posts))}
