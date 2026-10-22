"""Vote on poll."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.helpers import json_field
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, find_post, group_name, write

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id or slug of the post with the poll."},
        "option": {
            "type": "integer",
            "minimum": 0,
            "description": "Answer number, 1 for the first. 0 takes your vote back.",
        },
    },
    "required": ["group", "post_id", "option"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "your_vote": 1,
    "options": [{"option": 1, "text": "Yes", "votes": 12}, {"option": 2, "text": "No", "votes": 3}],
}


def poll_of(post: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    meta = post.get("metadata") or {}
    poll = json_field(meta.get("pollData") or meta.get("poll_data"))
    if not meta.get("poll") or not isinstance(poll, dict):
        raise ToolError("This post has no poll.", ErrorCode.INVALID_INPUT)
    return meta["poll"], poll


def options_of(poll: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"option": number, "text": entry.get("text"), "votes": entry.get("count", 0)}
        for number, entry in enumerate(poll.get("entries") or [], start=1)
    ]


@tool(
    name="vote_on_poll",
    title="Vote on poll",
    access="write",
    confirm=False,
    description="Vote in a post's poll, change your vote, or take it back.",
    details=(
        "Votes for one answer of the poll under a post, as clicking it does. If you already voted the vote "
        "moves to the new answer; option 0 takes it back. Returns the counts after your vote. Your vote "
        "is visible to the post's readers. Runs without asking first: undone with one call."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /groups/{group}/posts/{post_id}/poll/vote",
    example_response=EXAMPLE_RESPONSE,
)
async def vote_on_poll(ctx: ToolContext, args: dict[str, Any]) -> Any:
    post = await find_post(ctx, group_name(args["group"]), args["post_id"])
    poll_id, poll = poll_of(post)
    option = args.get("option") or 0
    if option == 0:
        answer = await write(ctx, "POST", f"/polls/{poll_id}/cancel-vote")
    else:
        if not 1 <= option <= len(poll.get("entries") or []):
            raise ToolError(f"The poll has answers 1 to {len(poll.get('entries') or [])}.", ErrorCode.INVALID_INPUT)
        action = "vote" if int(poll.get("option_index", -1)) < 0 else "change-vote"
        answer = await write(ctx, "POST", f"/polls/{poll_id}/{action}", params={"idx": option - 1})
    return {"post_id": post.get("id"), "your_vote": option or None, "options": options_of(answer)}
