"""Get post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, api, full_name, group_name, page_data

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "post_id": {"type": "string", "description": "post_id or slug from list_posts."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "title": "Week 12 challenge: ship one landing page",
    "body": "Post your link below by Sunday. Best three get a live review on Thursday's call.",
    "author": {"member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60", "name": "Jordan Price"},
    "comments": [
        {
            "comment_id": "c74e82a622174d37b81d9e9e562e53c2",
            "author": "Ana Lopez",
            "body": "Here's mine: ana.dev/launch",
            "likes": 3,
            "replies": [
                {
                    "comment_id": "2f0c13b74daa4a2eb9dadf61d74c6bab",
                    "author": "Jordan Price",
                    "body": "Love the headline!",
                    "likes": 0,
                    "replies": [],
                }
            ],
        }
    ],
    "url": "https://www.skool.com/yourgroup/week-12-challenge-ship-one-landing-page",
}


@tool(
    name="get_post",
    title="Get post",
    access="read",
    confirm=False,
    description="One post with its full text and comments, replies nested under their comment.",
    details=(
        "Returns one post by post_id or slug: title, full text, author and up to 25 comments with their "
        "replies nested under them. Images and files attached to the post are not returned; links typed "
        "in the text are. Use comment_id as parent_comment_id of comment_on_post to reply."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/posts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    post_id = args["post_id"].strip()
    # The post page answers to the post id as well as to its slug; comments come from the app's API.
    props = await page_data(ctx, f"{group}/{post_id}", {"group": group, "postName": post_id})
    post = (props.get("postTree") or {}).get("post") or {}
    if not post:
        raise ToolError("Skool has no such post in this group.", ErrorCode.TARGET_ERROR)
    meta = post.get("metadata") or {}
    params = {"group-id": post.get("groupId"), "limit": 25, "tail": "true"}
    tree = (await api(ctx, f"/posts/{post.get('id')}/comments", params)).get("post_tree") or {}

    def comment(node: dict[str, Any]) -> dict[str, Any]:
        item = node.get("post") or {}
        item_meta = item.get("metadata") or {}
        return {
            "comment_id": item.get("id"),
            "author": full_name(item.get("user")),
            "body": item_meta.get("content", ""),
            "likes": item_meta.get("upvotes", 0),
            "replies": [comment(child) for child in node.get("children") or []],
        }

    return {
        "post_id": post.get("id") or post_id,
        "title": meta.get("title"),
        "body": meta.get("content", ""),
        "author": {"member_id": (post.get("user") or {}).get("id"), "name": full_name(post.get("user"))},
        "comments": [comment(child) for child in tree.get("children") or []],
        "url": f"{WEB}/{group}/{post.get('name')}" if post.get("name") else None,
    }
