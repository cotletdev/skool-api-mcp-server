"""Get video transcript."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, group_name
from skool_api_mcp.skool.courses import COURSE_PROP
from skool_api_mcp.skool.videos import playback, transcript

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "video_id": {"type": "string", "description": "video_id from list_videos (uploaded videos only)."},
        "course_id": {**COURSE_PROP, "description": "For a lesson video: course_id from list_videos."},
        "lesson_id": {"type": "string", "description": "For a lesson video: lesson_id from list_videos."},
        "post_id": {"type": "string", "description": "For a post video: post_id from list_videos."},
        "language": {
            "type": "string",
            "description": "Caption language code, e.g. 'en'. Default: the video's first caption track.",
        },
        "start_minute": {
            "type": "integer",
            "minimum": 0,
            "description": "Minute to start from; pass next_start_minute of the previous answer to go on.",
        },
    },
    "required": ["group", "video_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "video_id": "6346fd01e61b48dcb0440b85f29af859",
    "page_url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e?md=4585d17f546b4ff48ae6058ad34761d9",
    "language": "en",
    "languages": ["en"],
    "duration": "25:14",
    "segments": [
        {"at": "00:00", "text": "Welcome to the course. Today we cover the one thing you sell."},
        {"at": "00:30", "text": "Write it down in one line before you build anything else."},
    ],
    "next_start_minute": 22,
}


@tool(
    name="get_video_transcript",
    title="Get video transcript",
    access="read",
    confirm=False,
    description="The spoken text of a video uploaded to a lesson or post, from Skool's captions.",
    details=(
        "Returns what is said in a video uploaded to Skool, as Skool's automatic captions, in 30-second "
        "segments with their start time. Give the video_id and where it is (course_id and lesson_id, or "
        "post_id), as list_videos returns them. One call reads about 20 minutes of video; when "
        "next_start_minute is not null, call again with it as start_minute for the rest (the first "
        "segment may repeat the last one). Linked YouTube, Vimeo, Loom or Wistia videos have no "
        "transcript here. Only videos this account can watch."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/videos/{video_id}/transcript",
    timeout_s=120,
    example_response=EXAMPLE_RESPONSE,
)
async def get_video_transcript(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    video, page = await playback(ctx, group, args)
    text = await transcript(ctx, video, language=args.get("language"), start_s=60.0 * args.get("start_minute", 0))
    return {"video_id": video["id"], "page_url": page, **text}
