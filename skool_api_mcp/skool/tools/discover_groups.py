"""Discover groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.helpers import json_field, page_cursor
from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, page_data, price_label

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Words to look for. Left out: the top groups."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "groups": [
        {
            "group": "evelyn",
            "name": "Grow With Evelyn",
            "description": "Meta ads and marketing for coaches and creators.",
            "members": 3511,
            "price": "$29/month",
            "rating": 5.0,
            "reviews": 124,
            "url": "https://www.skool.com/evelyn",
        }
    ],
    "next_cursor": "2",
}


@tool(
    name="discover_groups",
    title="Discover groups",
    access="read",
    confirm=False,
    description="Search Skool's public directory of communities, with members, price and rating.",
    details=(
        "Searches skool.com/discovery, the public list of communities, as its search box does: URL name, "
        "title, description, member count, price and review rating. 30 to a page; pass next_cursor back "
        "as cursor. Private groups that hide from discovery are not listed."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/discover",
    example_response=EXAMPLE_RESPONSE,
)
async def discover_groups(ctx: ToolContext, args: dict[str, Any]) -> Any:
    page = page_cursor(args.get("cursor"))
    params: dict[str, Any] = {"p": page}
    if args.get("query"):
        params["q"] = args["query"].strip()
    props = await page_data(ctx, "discovery", params)
    groups = []
    for row in props.get("groups") or []:
        group = row.get("group") or row
        meta = group.get("metadata") or {}
        price = json_field(meta.get("displayPrice")) or {}
        groups.append(
            {
                "group": group.get("name"),
                "name": meta.get("displayName"),
                "description": meta.get("description") or "",
                "members": meta.get("totalMembers"),
                "price": price_label({"displayPrice": price, "recurringInterval": price.get("recurring_interval")}),
                "rating": float(meta["reviewAverageRating"]) if meta.get("reviewAverageRating") else None,
                "reviews": meta.get("reviewCount", 0),
                "url": f"{WEB}/{group.get('name')}",
            }
        )
    return {"groups": groups, "next_cursor": str(page + 1) if props.get("hasMore") else None}
