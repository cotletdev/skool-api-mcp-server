"""Everything the server knows about Skool outside `skool/`: names, domains and the session cookie.

The rest of the package reads these values and never names the app itself.
"""

from __future__ import annotations

NAME = "Skool"
SLUG = "skool"
# The command and the prefix of every environment variable (SKOOL_AUTH_TOKEN, SKOOL_MCP_TOKEN ...).
CLI = "skool-mcp"
ENV = "SKOOL"
# Requests may reach only these hosts and their subdomains. Their cookies are read from Chrome.
DOMAINS = ("skool.com",)
# Present only while signed in. The first is the cookie a pasted token sets.
SESSION_COOKIES = ("auth_token",)
COOKIE_DOMAIN = ".skool.com"
LOGIN_URL = "https://www.skool.com/login"
# A final URL with one of these means the app signed the session out.
LOGGED_OUT_MARKERS = ("/login",)
# REST routes live under this path, the same as on cotlet.dev.
API_PREFIX = "/api/v1/skool"
# Prepended to the MCP server's instructions: where an agent starts.
AGENT_START = "Start with list_groups: its `group` values are what every other tool takes."
