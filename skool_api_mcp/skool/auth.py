"""Who is signed in: Skool's own answer for the account (api2.skool.com/self), for "Signed in as ..."."""

from __future__ import annotations

from typing import TYPE_CHECKING

from skool_api_mcp.core.errors import AuthExpiredError
from skool_api_mcp.skool.client import API, WEB, full_name

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext


async def whoami(ctx: ToolContext) -> str | None:
    """None only when Skool says signed out; any other failure raises (detection tries again later)."""
    try:
        response = await ctx.call("GET", f"{API}/self", headers={"referer": f"{WEB}/", "origin": WEB})
    except AuthExpiredError:
        return None
    if response.status != 200:
        return None
    me = response.json()
    name = full_name(me)
    return f"{name} ({me['name']})" if name and me.get("name") else name or None
