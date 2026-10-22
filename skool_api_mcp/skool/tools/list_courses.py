"""List courses."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skool_api_mcp.core.tools import tool
from skool_api_mcp.skool.client import WEB, group_name, page_data

if TYPE_CHECKING:
    from skool_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "group": {"type": "string", "description": "Group URL name, e.g. 'yourgroup' for skool.com/yourgroup."}
    },
    "required": ["group"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "courses": [
        {
            "course_id": "4b1c2d3e",
            "title": "Start Here",
            "unlock": "open",
            "modules": [
                {
                    "lesson_id": "6a7b8c9d0e1f4a2b3c4d5e6f7a8b9c0d",
                    "title": "Welcome",
                    "url": "https://www.skool.com/yourgroup/classroom/4b1c2d3e?md=6a7b8c9d0e1f4a2b3c4d5e6f7a8b9c0d",
                },
            ],
        },
        {"course_id": "9f8e7d6c", "title": "Advanced Funnels", "unlock": "locked", "modules": []},
    ]
}


@tool(
    name="list_courses",
    title="List courses",
    access="read",
    confirm=False,
    description="Courses in the group's Classroom, open or locked for you, with the modules of open ones.",
    details=(
        "Lists the courses of the group's Classroom in its order. unlock is open when your account can "
        "open the course and locked otherwise (a level, a purchase or a time lock; Skool does not say "
        "which here). Open courses list their modules in order with links; locked ones have none. "
        "Use the module links in welcome messages."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /groups/{group}/courses",
    timeout_s=110,
    example_response=EXAMPLE_RESPONSE,
)
async def list_courses(ctx: ToolContext, args: dict[str, Any]) -> Any:
    group = group_name(args["group"])
    props = await page_data(ctx, f"{group}/classroom", {"group": group})
    courses = []
    for course in props.get("allCourses") or []:
        meta = course.get("metadata") or {}
        name = course.get("name")
        modules: list[dict[str, str]] = []
        if meta.get("hasAccess"):
            # One request per course: the classroom list has no modules, the course page has them in order.
            page = await page_data(ctx, f"{group}/classroom/{name}", {"group": group, "course": name})
            modules = _modules(group, name, (page.get("course") or {}).get("children") or [])
        courses.append(
            {
                "course_id": name,
                "title": meta.get("title"),
                "unlock": "open" if meta.get("hasAccess") else "locked",
                "modules": modules,
            }
        )
    return {"courses": courses}


def _modules(group: str, course: str, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sets hold modules; both come back flat, in the classroom's order."""
    found: list[dict[str, Any]] = []
    for node in nodes:
        unit = node.get("course") or {}
        if unit.get("unitType") == "module":
            title = (unit.get("metadata") or {}).get("title", "")
            url = f"{WEB}/{group}/classroom/{course}?md={unit.get('id')}"
            found.append({"lesson_id": unit.get("id"), "title": title, "url": url})
        found.extend(_modules(group, course, node.get("children") or []))
    return found
