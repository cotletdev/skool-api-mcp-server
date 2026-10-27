"""Videos in a group (recorded 25.10.2026): uploaded ones play from Mux under video.skool.com, linked ones are URLs.

A lesson page (`video`) and a post page (`postTree.videos`) give each uploaded video's `playbackId` and a signed
`playbackToken` (about a year) to every member who can open the page. The HLS playlist
`stream.video.skool.com/{playbackId}.m3u8?token=` lists Skool's auto captions as a subtitle track, and that
track is WebVTT in 30-second pieces. Skool's own "Copy transcript" reads `GET /videos/{id}/transcript-id`, but
that answers 401 to anyone but the uploader, and a 401 reads as signed out (bridge), so it is not used.
"""

from __future__ import annotations

import json
import re
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.skool.client import WEB, page_data
from skool_api_mcp.skool.courses import course_page

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

STREAM = "https://stream.video.skool.com"
# Pieces read in one call: the tool's timeout is 120 s and each piece is one paced request (about 2 s).
_BUDGET_S = 85.0
_MEDIA = re.compile(r"^#EXT-X-MEDIA:(.*)$", re.MULTILINE)
_ATTR = re.compile(r'([A-Z0-9-]+)=("[^"]*"|[^,]*)')
_CUE_TIME = re.compile(r"^(\d+:)?\d{2}:\d{2}\.\d{3} --> ")
_SCHOOL = re.compile(r"\b[Ss]chool\b")


def linked_videos(raw: Any) -> list[dict[str, Any]]:
    """`videoLinksData` of a post: YouTube, Vimeo, Loom or Wistia links typed into it."""
    try:
        items = json.loads(raw) if isinstance(raw, str) else raw
    except ValueError:
        return []
    return [
        {"video_url": item["url"], "duration_s": round(item["len_ms"] / 1000) if item.get("len_ms") else None}
        for item in items or []
        if isinstance(item, dict) and item.get("url")
    ]


def uploaded_ids(raw: Any) -> list[str]:
    """`videoIds` of a post: comma-separated ids of videos uploaded to Skool."""
    return [part.strip() for part in str(raw or "").split(",") if part.strip()]


async def playback(ctx: ToolContext, group: str, args: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """The uploaded video's Mux record and the page it is on, from the lesson or the post that holds it."""
    video_id = args["video_id"].strip()
    if args.get("post_id"):
        post_id = args["post_id"].strip()
        props = await page_data(ctx, f"{group}/{post_id}", {"group": group, "postName": post_id})
        tree = props.get("postTree") or {}
        post = tree.get("post") or {}
        if not post:
            raise ToolError("Skool has no such post in this group.", ErrorCode.TARGET_ERROR)
        videos = tree.get("videos") or []
        page = f"{WEB}/{group}/{post.get('name') or post_id}"
    elif args.get("course_id") and args.get("lesson_id"):
        props = await course_page(ctx, group, args["course_id"], args["lesson_id"].strip())
        videos = [props["video"]] if props.get("video") else []
        page = f"{WEB}/{group}/classroom/{props['course']['course'].get('name')}?md={args['lesson_id'].strip()}"
    else:
        raise ToolError("Give post_id, or course_id and lesson_id, from list_videos.", ErrorCode.INVALID_INPUT)
    for video in videos:
        if video.get("id") == video_id:
            if video.get("status") not in (None, "ready") or not video.get("playbackId"):
                raise ToolError("Skool is still processing this video; try again later.", ErrorCode.TARGET_ERROR)
            return video, page
    raise ToolError(
        "That page has no uploaded video with this video_id. Linked videos (YouTube and others) have no "
        "transcript on Skool.",
        ErrorCode.TARGET_ERROR,
    )


def _tracks(master: str, base: str) -> list[dict[str, str]]:
    tracks = []
    for line in _MEDIA.findall(master):
        attrs = {key: value.strip('"') for key, value in _ATTR.findall(line)}
        if attrs.get("TYPE") == "SUBTITLES" and attrs.get("URI"):
            tracks.append(
                {
                    "language": attrs.get("LANGUAGE", ""),
                    "name": attrs.get("NAME", ""),
                    "uri": urljoin(base, attrs["URI"]),
                }
            )
    return tracks


def _pieces(playlist: str, base: str) -> list[tuple[float, str]]:
    """(start in seconds, URL) of every WebVTT piece."""
    pieces, start, length = [], 0.0, 0.0
    for line in playlist.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF:"):
            length = float(line[len("#EXTINF:") :].split(",")[0] or 0)
        elif line and not line.startswith("#"):
            pieces.append((start, urljoin(base, line)))
            start += length
    return pieces


def _cues(vtt: str) -> list[tuple[str, str]]:
    """(cue number, text) of a WebVTT piece; a cue cut by a piece boundary repeats in the next one."""
    cues = []
    for block in vtt.replace("\r\n", "\n").split("\n\n"):
        lines = [line for line in block.strip().split("\n") if line]
        timing = next((n for n, line in enumerate(lines) if _CUE_TIME.match(line)), None)
        if timing is None:
            continue
        key = lines[timing - 1] if timing else lines[timing]
        text = " ".join(lines[timing + 1 :]).strip()
        if text:
            cues.append((key, text))
    return cues


def clock(seconds: float) -> str:
    whole = int(seconds)
    hours, rest = divmod(whole, 3600)
    return f"{hours}:{rest // 60:02d}:{rest % 60:02d}" if hours else f"{rest // 60:02d}:{rest % 60:02d}"


async def _text(ctx: ToolContext, url: str, what: str) -> str:
    response = await ctx.call("GET", url, headers={"referer": f"{WEB}/", "origin": WEB})
    if response.status == 404:
        raise ToolError(f"Skool has no {what} for this video.", ErrorCode.TARGET_ERROR)
    if response.status >= 400:
        raise ToolError(f"Skool refused the {what} ({response.status}).", ErrorCode.TARGET_ERROR)
    return response.text


async def transcript(
    ctx: ToolContext, video: dict[str, Any], *, language: str | None, start_s: float
) -> dict[str, Any]:
    """Caption text from start_s on, in 30-second segments, until the time budget runs out."""
    master_url = f"{STREAM}/{video['playbackId']}.m3u8?token={video.get('playbackToken', '')}"
    tracks = _tracks(await _text(ctx, master_url, "video playlist"), master_url)
    if not tracks:
        raise ToolError("Skool has no captions for this video (no speech, or not made yet).", ErrorCode.TARGET_ERROR)
    wanted = (language or "").strip().lower()
    track = next((t for t in tracks if wanted and t["language"].lower().startswith(wanted)), None)
    if wanted and not track:
        have = ", ".join(t["language"] for t in tracks)
        raise ToolError(f"No captions in '{language}'; this video has: {have}.", ErrorCode.INVALID_INPUT)
    track = track or tracks[0]
    pieces = [p for p in _pieces(await _text(ctx, track["uri"], "caption list"), track["uri"]) if p[0] + 30 > start_s]
    deadline = time.monotonic() + _BUDGET_S
    seen: set[str] = set()
    segments: list[dict[str, str]] = []
    next_start: float | None = None
    for start, url in pieces:
        if time.monotonic() > deadline:
            next_start = start
            break
        fresh = []
        for key, text in _cues(await _text(ctx, url, "captions")):
            if key not in seen:
                seen.add(key)
                fresh.append(text)
        if fresh:
            # Skool's "Copy transcript" makes the same fix: speech recognition hears "school".
            segments.append({"at": clock(start), "text": _SCHOOL.sub("Skool", " ".join(fresh))})
    duration = video.get("duration")
    return {
        "language": track["language"],
        "languages": [t["language"] for t in tracks],
        "duration": clock(duration / 1000) if duration else None,
        "segments": segments,
        "next_start_minute": int(next_start // 60) if next_start is not None else None,
    }
