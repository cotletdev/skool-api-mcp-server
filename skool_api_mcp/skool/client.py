"""Skool web requests recorded in the spike (16.10.2026).

Two sources, both with the account's own cookies (`auth_token`):
- `www.skool.com/_next/data/{build_id}/...json`: the JSON each page of the web app loads (posts, members,
  classroom, about). The build id changes with every Skool deploy; it is read from any page's HTML and
  kept for an hour, and a 404 on the data URL means a new deploy (read it again once).
- `api2.skool.com`: the app's API for the signed-in user (self, groups, chat, comments).
Answers keep Skool's ids; times are ISO 8601. Cursors are page numbers (Skool pages by number).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qsl, urlsplit

from skool_api_mcp.core.errors import ErrorCode, ToolError
from skool_api_mcp.core.helpers import json_field

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

WEB = "https://www.skool.com"
API = "https://api2.skool.com"
_BUILD_KEY = "build-id"
_BUILD_RE = re.compile(r'"buildId":"([^"]+)"')
_GROUP_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")


def group_name(value: str) -> str:
    name = value.strip().lower().removeprefix("https://").removeprefix("www.skool.com/").strip("/").split("/")[0]
    if not _GROUP_RE.match(name):
        raise ToolError("group must be the group's URL name, e.g. 'yourgroup'.", ErrorCode.INVALID_INPUT)
    return name


async def _build_id(ctx: ToolContext, fresh: bool = False) -> str:
    if not fresh and (cached := await ctx.cache_get(_BUILD_KEY)):
        return cached
    page = await ctx.call("GET", f"{WEB}/discovery", headers={"accept": "text/html"})
    match = _BUILD_RE.search(page.text)
    if not match:
        raise ToolError("Skool changed its page format.", ErrorCode.TARGET_ERROR)
    await ctx.cache_set(_BUILD_KEY, match.group(1), ttl_s=3600)
    return match.group(1)


async def page_data(ctx: ToolContext, path: str, params: dict[str, Any], *, follow: bool = True) -> dict[str, Any]:
    """`pageProps` of one web app page, e.g. path "yourgroup/-/members" with {"group": "yourgroup", "p": 2}.

    A redirect inside the group (a course opens on its first module) is followed once.
    """
    headers = {"x-nextjs-data": "1", "referer": f"{WEB}/{path.split('/')[0]}"}
    for attempt in (0, 1):
        build = await _build_id(ctx, fresh=attempt == 1)
        response = await ctx.call("GET", f"{WEB}/_next/data/{build}/{path}.json", params=params, headers=headers)
        if response.status == 404 and attempt == 0:
            continue
        if response.status == 404:
            raise ToolError("Skool has no such group or page, or this account cannot see it.", ErrorCode.TARGET_ERROR)
        props = response.json().get("pageProps") or {}
        if props.get("__N_REDIRECT"):
            target = str(props["__N_REDIRECT"])
            if "/login" in target:
                raise ToolError("Skool signed this account out.", ErrorCode.AUTH_EXPIRED)
            location = urlsplit(target)
            if follow and location.path.lstrip("/").startswith(path.split("/")[0] + "/"):
                query = {**params, **dict(parse_qsl(location.query))}
                return await page_data(ctx, location.path.lstrip("/"), query, follow=False)
            raise ToolError("This account has no access to that group page.", ErrorCode.APP_PERMISSION_DENIED)
        return props
    raise ToolError("Skool did not answer.", ErrorCode.TARGET_ERROR)


# Never a tool : the account's own sign-in, email, password, name and settings, and anything that
# moves money (plans, payments, payouts, billing). Every api2 request goes through `_guard`, so a tool cannot
# reach them by mistake.
_NEVER = re.compile(
    r"^/(auth/|billing/|payments/|affiliates/|self/(?!groups$|chat-channels$|notifications$)|users/[^/]+/"
    r"(update-name|metadata/))|payout|payment|invoice|subscription|refund|dispute|membership-product"
)

# Skool's own refusal texts that need a plain answer; anything else gets the status code.
_REFUSALS = {
    "not_allowed_for_hobby_plan": "Skool allows this only for groups on the Pro plan.",
    "cannot update to same role": "The member already has that role.",
    "member is banned": "The member is banned; remove_member unbans them first.",
    "cannot mark private course": "Skool keeps progress only in published courses.",
    "same state": "same state",
}


def _guard(path: str) -> None:
    if _NEVER.search(path):
        raise ToolError("This server does not change Skool account or payment settings.", ErrorCode.INVALID_INPUT)


def _refused(response: Any, what: str) -> ToolError:
    text = response.text.strip().strip('"')
    for key, message in _REFUSALS.items():
        if key in text:
            return ToolError(message, ErrorCode.TARGET_ERROR)
    if response.status == 422:
        try:
            field = (response.json().get("fields") or [{}])[0]
        except ValueError:
            field = {}
        if field.get("user") and field.get("error"):
            return ToolError(f"Skool: {field['error']}.", ErrorCode.INVALID_INPUT)
    return ToolError(f"Skool refused the {what} ({response.status}).", ErrorCode.TARGET_ERROR)


async def api(
    ctx: ToolContext, path: str, params: dict[str, Any] | None = None, *, method: str = "GET", body: Any = None
) -> Any:
    """A read through api2; a few reads are POSTs (member search)."""
    _guard(path)
    headers = {"referer": f"{WEB}/", "origin": WEB}
    response = await ctx.call(method, f"{API}{path}", params=params, json=body, headers=headers)
    if response.status == 404:
        raise ToolError("Skool has no such item, or this account cannot see it.", ErrorCode.TARGET_ERROR)
    if response.status >= 400:
        raise _refused(response, "request")
    return response.json() if response.text.strip() else {}


async def write(
    ctx: ToolContext, method: str, path: str, *, params: dict[str, Any] | None = None, body: Any = None
) -> Any:
    """A change through api2 (posts, comments, pins, roles, chat).

    A bare 403 (Skool's answer to a non-admin) never gets here: the joining layer treats it as a block.
    Admin-only tools check the account's role first (`require_admin`).
    """
    _guard(path)
    headers = {"referer": f"{WEB}/", "origin": WEB}
    response = await ctx.call(method, f"{API}{path}", params=params, json=body, headers=headers)
    if response.status == 404:
        raise ToolError("Skool has no such item, or this account cannot see it.", ErrorCode.TARGET_ERROR)
    if response.status == 429:
        raise ToolError("Skool is limiting this account; try again in a few minutes.", ErrorCode.RATE_LIMITED)
    if response.status >= 400:
        raise _refused(response, "change")
    return response.json() if response.text.strip() else {}


async def group_info(ctx: ToolContext, group: str) -> dict[str, Any]:
    """Skool's id of the group and its categories (name -> label id), from the feed page."""
    props = await page_data(ctx, group, {"group": group})
    current = props.get("currentGroup") or {}
    if not current.get("id"):
        raise ToolError("Skool has no such group, or this account cannot see it.", ErrorCode.TARGET_ERROR)
    labels = {
        (label.get("metadata") or {}).get("displayName", ""): label["id"] for label in current.get("labels") or []
    }
    return {"id": current["id"], "labels": labels, "role": _member_role(props)}


def _member_role(props: dict[str, Any]) -> str:
    me = props.get("self") or {}
    member = me.get("member") or (props.get("currentGroup") or {}).get("member") or {}
    return str(member.get("role") or "")


def require_admin(info: dict[str, Any], *, moderators: bool = False) -> None:
    allowed = {"group-admin", "admin", "owner"} | ({"group-moderator", "moderator"} if moderators else set())
    if info["role"] not in allowed:
        who = "admins and moderators" if moderators else "admins"
        raise ToolError(f"Only group {who} can do this; this account is not one.", ErrorCode.APP_PERMISSION_DENIED)


def full_name(user: dict[str, Any] | None) -> str:
    user = user or {}
    first = user.get("firstName") or user.get("first_name") or ""
    last = user.get("lastName") or user.get("last_name") or ""
    return f"{first} {last}".strip() or user.get("name") or ""


def price_label(metadata: dict[str, Any]) -> str:
    price = json_field(metadata.get("displayPrice") or metadata.get("display_price"))
    if not isinstance(price, dict) or not price.get("amount"):
        return "free"
    interval = metadata.get("recurringInterval") or metadata.get("recurring_interval") or ""
    amount = price["amount"] / 100
    label = f"${amount:g}" if str(price.get("currency", "usd")).lower() == "usd" else f"{amount:g} {price['currency']}"
    return f"{label}/{interval}" if interval else label


_ROLES = {
    "group-admin": "admin",
    "admin": "admin",
    "owner": "admin",
    "group-moderator": "moderator",
    "moderator": "moderator",
    "pending": "pending",
    "banned": "banned",
}


def role_name(raw: str | None) -> str:
    """Skool's member role as admin, moderator, member, banned, or pending while a request to join waits."""
    return _ROLES.get(raw or "", "member")


GROUP_PROP: dict[str, Any] = {
    "type": "string",
    "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup.",
}


async def find_post(ctx: ToolContext, group: str, post_id: str) -> dict[str, Any]:
    """One post of the group as its page shows it (by post_id or slug): metadata holds poll, upvotes, myVote."""
    props = await page_data(ctx, f"{group}/{post_id.strip()}", {"group": group, "postName": post_id.strip()})
    post = (props.get("postTree") or {}).get("post") or {}
    if not post:
        raise ToolError("Skool has no such post in this group.", ErrorCode.TARGET_ERROR)
    return post


async def require_author_or_moderator(ctx: ToolContext, group: str, post_id: str) -> None:
    """Skool answers 401 (read as signed out) when a member edits or deletes someone else's post.

    Admins and moderators pass; a member passes on their own post. A comment has no page of its own, so a
    member's comment id goes through and Skool decides.
    """
    info = await group_info(ctx, group)
    if info["role"] in {"group-admin", "admin", "owner", "group-moderator", "moderator"}:
        return
    try:
        post = await find_post(ctx, group, post_id)
    except ToolError:
        return
    me = (await api(ctx, "/self")).get("id")
    if (post.get("user") or {}).get("id", post.get("userId")) != me:
        raise ToolError(
            "Only the author, admins and moderators can do this to a post.", ErrorCode.APP_PERMISSION_DENIED
        )


def person(user: dict[str, Any] | None) -> dict[str, Any]:
    """A Skool user as the tools return one: id, name and profile link, never an email."""
    user = user or {}
    return {"member_id": user.get("id"), "name": full_name(user), "profile_url": f"{WEB}/@{user.get('name')}"}
