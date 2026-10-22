"""Pin post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import group_info, group_name, require_admin, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."},
        "post_id": {"type": "string", "description": "post_id from list_posts (not the slug)."},
        "pinned": {"type": "boolean", "description": "false unpins. Default: true."},
        "course_page_id": {"type": "string", "description": "Pin to this Classroom page instead of the feed."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06", "pinned": True, "location": "feed"}


@tool(
    name="pin_post",
    title="Pin post",
    access="write",
    confirm=False,
    description="Pin a post to the top of the feed (up to 3) or to a Classroom page (up to 12). Admins only.",
    details=(
        "Pins a post to the top of the feed, where Skool allows up to 3 pinned posts, or to a Classroom "
        "page, which allows up to 12. Set pinned to false to unpin. Admins only. pin_post runs without "
        "asking first: pinning sends nothing to anyone and is undone with one call."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/pin",
    example_response=EXAMPLE_RESPONSE,
)
async def pin_post(ctx: ToolContext, args: dict[str, Any]) -> Any:
    require_admin(await group_info(ctx, group_name(args["group"])))
    pinned = args.get("pinned", True)
    module = args.get("course_page_id")
    post = args["post_id"]
    if module:
        action = "pin-module" if pinned else "unpin-module"
        await write(ctx, "POST", f"/posts/{post}/{action}", params={"module": module} if pinned else None)
    else:
        await write(ctx, "POST", f"/posts/{post}/{'pin' if pinned else 'unpin'}")
    return {"post_id": post, "pinned": pinned, "location": "classroom" if module else "feed"}
