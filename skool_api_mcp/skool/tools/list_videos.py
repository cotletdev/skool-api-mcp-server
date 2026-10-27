"""List videos."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import GROUP_PROP, WEB, group_name, page_data
from skool_api_mcp.skool.videos import linked_videos, uploaded_ids

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": GROUP_PROP,
        "where": {
            "type": "string",
            "enum": ["all", "classroom", "posts"],
            "description": "Classroom lessons, feed posts, or both (default).",
        },
        "post_pages": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Feed pages to scan for post videos, newest first, 30 posts each. Default 1.",
        },
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "videos": [
        {
            "source": "lesson",
            "title": "1. The big picture",
            "video_id": "6346fd01e61b48dcb0440b85f29af859",
            "video_url": None,
            "duration_s": None,
            "transcript": True,
            "course_id": "4b1c2d3e",
            "course": "Start Here",
            "lesson_id": "4585d17f546b4ff48ae6058ad34761d9",
            "url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e?md=4585d17f546b4ff48ae6058ad34761d9",
        },
        {
            "source": "post",
            "title": "Week 12 call recording",
            "video_id": None,
            "video_url": "https://www.youtube.com/watch?v=abc123",
            "duration_s": 1834,
            "transcript": False,
            "post_id": "a3f9c2e1b7d84c06a3f9c2e1b7d84c06",
            "url": "https://www.skool.com/yourgroup/week-12-call-recording",
        },
    ],
    "locked_courses": ["Advanced Funnels"],
}


@tool(
    name="list_videos",
    title="List videos",
    access="read",
    confirm=False,
    description="Videos in the group's Classroom lessons and feed posts, uploaded or linked.",
    details=(
        "Lists the videos this account can watch: one per Classroom lesson with a video, in course "
        "order, and the videos in the newest feed posts (post_pages pages of 30). An uploaded video has "
        "a video_id and transcript true: pass it with its course_id and lesson_id, or post_id, to "
        "get_video_transcript. A linked one (YouTube, Vimeo, Loom, Wistia) has only video_url. Locked "
        "courses are named in locked_courses, without their videos."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/videos",
    timeout_s=120,
    example_response=EXAMPLE_RESPONSE,
)
async def list_videos(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    where = args.get("where", "all")
    videos: list[dict[str, Any]] = []
    locked: list[str] = []
    if where in ("all", "classroom"):
        props = await page_data(ctx, f"{group}/classroom", {"group": group})
        for course in props.get("allCourses") or []:
            meta = course.get("metadata") or {}
            if not meta.get("hasAccess"):
                locked.append(meta.get("title", ""))
                continue
            name = course.get("name")
            # The classroom list has no lessons; the course page has every lesson's video fields.
            page = await page_data(ctx, f"{group}/classroom/{name}", {"group": group, "course": name})
            units = (page.get("course") or {}).get("children") or []
            videos.extend(_lessons(group, name, meta.get("title", ""), units))
    if where in ("all", "posts"):
        seen: set[str | None] = set()
        for number in range(1, args.get("post_pages", 1) + 1):
            props = await page_data(ctx, group, {"group": group, "p": number})
            trees = props.get("postTrees") or []
            for tree in trees:
                post = tree.get("post") or {}
                # Pinned posts head every page.
                if post.get("id") not in seen:
                    seen.add(post.get("id"))
                    videos.extend(_post(group, post))
            if len(trees) < 30:
                break
    return {"videos": videos, "locked_courses": locked}


def _lessons(group: str, course: str, title: str, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for node in nodes:
        unit = node.get("course") or {}
        meta = unit.get("metadata") or {}
        if unit.get("unitType") == "module" and (meta.get("videoId") or meta.get("videoLink")):
            length = meta.get("videoLenMs")
            found.append(
                {
                    "source": "lesson",
                    "title": meta.get("title", ""),
                    "video_id": meta.get("videoId") or None,
                    "video_url": None if meta.get("videoId") else meta.get("videoLink"),
                    "duration_s": round(length / 1000) if length else None,
                    "transcript": bool(meta.get("videoId")),
                    "course_id": course,
                    "course": title,
                    "lesson_id": unit.get("id"),
                    "url": f"{WEB}/{group}/classroom/{course}?md={unit.get('id')}",
                }
            )
        found.extend(_lessons(group, course, title, node.get("children") or []))
    return found


def _post(group: str, post: dict[str, Any]) -> list[dict[str, Any]]:
    meta = post.get("metadata") or {}
    common = {"post_id": post.get("id"), "url": f"{WEB}/{group}/{post.get('name')}"}
    title = meta.get("title", "")
    uploaded = [
        {
            "source": "post",
            "title": title,
            "video_id": video_id,
            "video_url": None,
            "duration_s": None,
            "transcript": True,
            **common,
        }
        for video_id in uploaded_ids(meta.get("videoIds"))
    ]
    linked = [
        {"source": "post", "title": title, "video_id": None, **link, "transcript": False, **common}
        for link in linked_videos(meta.get("videoLinksData"))
    ]
    return uploaded + linked
