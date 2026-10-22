"""Search group."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, full_name, group_name, page_data, person

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "query": {"type": "string", "description": "Words to look for."},
        "type": {
            "type": "string",
            "enum": ["posts", "members", "courses"],
            "description": "posts (default), members or courses.",
        },
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": ["group", "query"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "type": "posts",
    "total": 3,
    "results": [
        {
            "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
            "title": "Week 12 challenge: ship one landing page",
            "author": "Ana Lopez",
            "preview": "Post your link below by Sunday...",
            "url": "https://www.skool.com/yourgroup/week-12-challenge-ship-one-landing-page",
        }
    ],
    "next_cursor": None,
}


@tool(
    name="search_group",
    title="Search group",
    access="read",
    confirm=False,
    description="Search a group's posts, members or courses, as its search box does.",
    details=(
        "Runs the group's search box: posts (titles and text, with author and a preview), members (by "
        "name) or courses. Posts come 30 to a page; pass next_cursor back as cursor. Results are what "
        "this account can see."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/search",
    example_response=EXAMPLE_RESPONSE,
)
async def search_group(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    kind = args.get("type") or "posts"
    page = page_cursor(args.get("cursor"))
    params = {"group": group, "q": args["query"].strip(), "t": kind, "p": page}
    props = await page_data(ctx, f"{group}/-/search", params)
    if kind == "members":
        # Member results are memberships with the person inside.
        results = [person(member.get("user")) for member in props.get("members") or []]
        total = props.get("totalMembers") or len(results)
    elif kind == "courses":
        results = [
            {
                "course_id": course.get("name"),
                "title": (course.get("metadata") or {}).get("title"),
                "url": f"{WEB}/{group}/classroom/{course.get('name')}",
            }
            for course in props.get("courses") or []
        ]
        total = props.get("totalCourses") or len(results)
    else:
        results = []
        for tree in props.get("postTrees") or []:
            post = tree.get("post") or {}
            meta = post.get("metadata") or {}
            results.append(
                {
                    "post_id": post.get("id"),
                    "title": meta.get("title"),
                    "author": full_name(post.get("user")),
                    "preview": (meta.get("content") or "")[:200],
                    "url": f"{WEB}/{group}/{post.get('name')}",
                }
            )
        total = props.get("totalPosts") or len(results)
    more = kind == "posts" and page < int(props.get("totalPostPages") or 1)
    return {"type": kind, "total": total, "results": results, "next_cursor": str(page + 1) if more else None}
