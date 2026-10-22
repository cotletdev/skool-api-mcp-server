"""Get poll results."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, api, find_post, group_name, person
from skool_api_mcp.skool.tools.vote_on_poll import options_of, poll_of

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "post_id": {"type": "string", "description": "post_id or slug of the post with the poll."},
        "voters": {"type": "boolean", "description": "Also list who voted for each answer, up to 30. Default: false."},
    },
    "required": ["group", "post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
    "your_vote": None,
    "options": [
        {
            "option": 1,
            "text": "Yes",
            "votes": 1,
            "voters": [
                {
                    "member_id": "5e1d7c2a9b8f4e3d6c0a1b2c3d4e5f60",
                    "name": "Ana Lopez",
                    "profile_url": "https://www.skool.com/@ana-lopez-4127",
                }
            ],
        }
    ],
}


@tool(
    name="get_poll_results",
    title="Get poll results",
    access="read",
    confirm=False,
    description="Answers and vote counts of a post's poll, optionally with who voted for what.",
    details=(
        "Returns the poll under a post: each answer with its number (what vote_on_poll takes), text and "
        "vote count, and your own vote. voters true adds up to 30 voters per answer, as the vote count "
        "opens in Skool."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/posts/{post_id}/poll",
    example_response=EXAMPLE_RESPONSE,
)
async def get_poll_results(ctx: ToolContext, args: dict[str, Any]) -> Any:
    post = await find_post(ctx, group_name(args["group"]), args["post_id"])
    poll_id, poll = poll_of(post)
    options = options_of(poll)
    if args.get("voters"):
        for item in options:
            if not item["votes"]:
                item["voters"] = []
                continue
            params = {"idx": item["option"] - 1, "offset": 0, "limit": 30}
            answer = await api(ctx, f"/polls/{poll_id}/option-users", params)
            item["voters"] = [person(user) for user in answer.get("users") or []]
    mine = int(poll.get("option_index", poll.get("optionIndex", -1)))
    return {"post_id": post.get("id"), "your_vote": mine + 1 if mine >= 0 else None, "options": options}
