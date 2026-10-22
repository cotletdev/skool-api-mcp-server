"""List posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import limit, page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, full_name, group_name, page_data

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "category": {"type": "string", "description": "Only posts whose category name contains this text."},
        "since": {
            "type": "string",
            "format": "date-time",
            "description": "Only posts created after this time (ISO 8601, UTC).",
        },
        "limit": {"type": "integer", "description": "1 to 30. Default: 20."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "posts": [
        {
            "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
            "slug": "week-12-challenge-ship-one-landing-page",
            "title": "Week 12 challenge: ship one landing page",
            "author": "Ana Lopez",
            "category": "Announcements",
            "likes": 23,
            "comments": 7,
            "pinned": True,
            "created_at": "2026-10-03T07:00:00.000000Z",
            "preview": "Post your link below by Sunday...",
            "url": "https://www.skool.com/yourgroup/week-12-challenge-ship-one-landing-page",
        }
    ],
    "next_cursor": "2",
}


@tool(
    name="list_posts",
    title="List posts",
    access="read",
    confirm=False,
    description="Posts in a group's feed, pinned first, then newest, with author, category, likes and comment count.",
    details=(
        "Lists one page of the group's feed as Skool shows it: pinned posts on top, then the newest. A page "
        "holds up to 30 posts; pass next_cursor back as cursor for older ones. category and since filter "
        "within the page, so a filtered page can come back short or empty while next_cursor still points "
        "further. preview is the first 200 characters; get_post takes post_id or slug and returns the "
        "full text with comments."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/posts",
    example_response=EXAMPLE_RESPONSE,
)
async def list_posts(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    page = page_cursor(args.get("cursor"))
    wanted = limit(args, 20, 30)
    props = await page_data(ctx, group, {"group": group, "p": page})
    labels = {
        label["id"]: (label.get("metadata") or {}).get("displayName", "")
        for label in (props.get("currentGroup") or {}).get("labels") or []
    }
    category = (args.get("category") or "").strip().lower()
    since = args.get("since")
    posts: list[dict[str, Any]] = []
    seen: set[object] = set()
    for tree in props.get("postTrees") or []:
        post = tree.get("post") or {}
        meta = post.get("metadata") or {}
        # The first page lists a pinned post twice: on top, then again where its date puts it.
        if post.get("id") in seen:
            continue
        seen.add(post.get("id"))
        label = labels.get(post.get("labelId") or "", "")
        if category and category not in label.lower():
            continue
        if since and (post.get("createdAt") or "") < since:
            continue
        posts.append(
            {
                "post_id": post.get("id"),
                "slug": post.get("name"),
                "title": meta.get("title"),
                "author": full_name(post.get("user")),
                "category": label,
                "likes": meta.get("upvotes", 0),
                "comments": meta.get("comments", 0),
                "pinned": bool(meta.get("pinned")),
                "created_at": post.get("createdAt"),
                "preview": (meta.get("content") or "")[:200],
                "url": f"{WEB}/{group}/{post.get('name')}",
            }
        )
    total = int(props.get("total") or 0)
    more = page * 30 < total
    return {"posts": posts[:wanted], "next_cursor": str(page + 1) if more else None}
