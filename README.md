# Skool API and MCP server, self-hosted

A **Skool API** and a **Skool MCP server** you run on your own computer, in Python, on the session of your own Google Chrome. All 69 Skool tools we run in production at [Cotlet](https://cotlet.dev/integrations/skool-api-mcp-server): members, membership requests, posts, comments, polls, Classroom, Calendar, group settings, Skool Chat and stats.

Skool has no public API and no official MCP server. This repo gives you both:

- **MCP server** for Claude Code, Claude Desktop, Cursor, Codex and any MCP client, over stdio or HTTP. [Setup](#mcp-server)
- **REST API** on `http://127.0.0.1:8787/api/v1/skool`, with OpenAPI docs at `/docs`. [Setup](#rest-api)
- **Python**: `call("list_members", group="yourgroup")`, plus 16 ready scripts in [`examples/`](examples/).

It is for technical people who want to run it themselves, **for noncommercial use only** ([license](#license)). If you want it running 24/7 on a server, kept working when Skool changes its site, for a team or a business, use the [hosted version at cotlet.dev](https://cotlet.dev/integrations/skool-api-mcp-server).

[![Skool MCP server](https://img.shields.io/badge/Skool%20MCP-69%20tools-6d4aef)](#all-69-tools)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-141318)](#requirements)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial-141318)](LICENSE)
[![MCP Badge](https://lobehub.com/badge/mcp/cotletdev-skool-api-mcp-server)](https://lobehub.com/mcp/cotletdev-skool-api-mcp-server)

```bash
uv tool install skool-api-mcp                  # or: pip install skool-api-mcp
skool-mcp connect                                  # reads your Skool session from Chrome
skool-mcp call list_groups
claude mcp add skool -- uvx --from skool-api-mcp skool-mcp mcp
```

## Contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Connect your Chrome](#connect-your-chrome)
- [MCP server](#mcp-server)
- [REST API](#rest-api)
- [Python and the example scripts](#python-and-the-example-scripts)
- [All 69 tools](#all-69-tools)
- [Configuration](#configuration)
- [Security and your Skool account](#security-and-your-skool-account)
- [Errors](#errors)
- [Self-hosted or hosted](#self-hosted-or-hosted)
- [FAQ](#faq)
- [License](#license)

## How it works

```text
AI agent (MCP) / script (REST, Python) ──▶ skool-mcp on your computer ──your Skool cookies──▶ skool.com
                                                  ▲
                         skool-mcp connect ───────┘ reads them once from your Chrome (DevTools Protocol)
```

1. You sign in to Skool in your own Chrome, the way you always do.
2. `skool-mcp connect` attaches to that Chrome through the Chrome DevTools Protocol, reads the skool.com cookies and saves them to `~/.config/skool-api-mcp/session.json`, readable by your user only. It never sees or stores your password.
3. Every tool call is a request to Skool's own web app endpoints (`api2.skool.com` and the page data of `www.skool.com`) with those cookies, sent with [curl_cffi](https://github.com/lexiforest/curl_cffi), which copies Chrome's TLS fingerprint. No headless browser runs.

Skool's session cookie lasts about a year. When Skool signs you out, the server reads the cookies from Chrome again, if Chrome is open with remote debugging on.

## Requirements

- Python 3.11 or newer.
- Google Chrome 144 or newer, signed in to Skool. Any Chrome or Chromium works with a [debugging port](#option-b-a-chrome-with-a-debugging-port).
- macOS, Linux or Windows.
- The Skool role a tool needs: membership requests need admin or moderator, stats and group settings need admin. Reading members, posts, courses and chat works with any role in groups you belong to.

## Install

From [PyPI](https://pypi.org/project/skool-api-mcp/):

```bash
uv tool install skool-api-mcp       # or: pipx install skool-api-mcp, or: pip install skool-api-mcp
skool-mcp --version
```

MCP clients can also run it with no install: `uvx --from skool-api-mcp skool-mcp mcp`.

From source:

```bash
git clone https://github.com/cotletdev/skool-api-mcp-server.git
cd skool-api-mcp-server
python3 -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -e .
skool-mcp --version
```

With [uv](https://docs.astral.sh/uv/): `uv venv && uv pip install -e .`, then `uv run skool-mcp ...`.

Setting it up with an AI agent (Claude Code, Codex, Cursor)? Open it in this folder and ask it to set up the repo: [`AGENTS.md`](AGENTS.md) tells it every step, and it asks you only for the steps in Chrome.

To update: `uv tool upgrade skool-api-mcp` (or `pip install -U skool-api-mcp`), from source `git pull && pip install -e .`. We copy every change of the hosted Skool tools into this repo.

## Connect your Chrome

### Option A: your everyday Chrome (recommended)

1. Open `chrome://inspect/#remote-debugging` in Chrome and switch **remote debugging** on. Chrome then accepts DevTools connections from programs on this computer, and asks you before each one.
2. Make sure you are signed in at [skool.com](https://www.skool.com).
3. Run:

   ```bash
   skool-mcp connect
   ```

4. Chrome asks whether to allow the connection. Click **Allow**.

```text
Saved 15 skool.com cookies to /Users/you/.config/skool-api-mcp/session.json
Signed in to Skool as Ana Lopez (ana-lopez-4127)
```

You can switch remote debugging off again afterwards. Leave it on if you want the server to pick up a new session by itself after Skool signs you out.

`connect` looks for Chrome's `DevToolsActivePort` file in the default profile folder. For Chrome Beta, Canary or a custom profile folder, pass `--profile-dir "<folder>"`.

### Option B: a Chrome with a debugging port

Chrome does not open a debugging port on your default profile, so start a separate one, sign in to Skool there once, and connect to it:

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-skool"
# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-skool"
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome-skool"

skool-mcp connect --cdp http://127.0.0.1:9222
```

`--cdp` also takes a `ws://` DevTools URL, for example of a Chrome on another machine reached over an SSH tunnel.

### Option C: paste the cookie by hand

For a server with no Chrome: in Chrome open DevTools on skool.com, **Application > Cookies > https://www.skool.com**, copy the value of `auth_token`, then:

```bash
skool-mcp connect --token          # paste it, input is hidden
# or, without a session file:
export SKOOL_AUTH_TOKEN=...
```

A pasted token is not refreshed on its own. Paste a new one when Skool signs you out.

Check the session at any time:

```bash
skool-mcp status
```

## MCP server

The MCP server lists every tool with its input schema, a description written for agents, and hints: read tools are marked read-only, and tools that post, message or delete are marked so your client asks before running them.

### Claude Code

```bash
claude mcp add skool -- uvx --from skool-api-mcp skool-mcp mcp
# read only:
claude mcp add skool -- uvx --from skool-api-mcp skool-mcp mcp --read-only
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "skool": {
      "command": "uvx",
      "args": ["--from", "skool-api-mcp", "skool-mcp", "mcp"]
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`, the same block as Claude Desktop. A ready copy is in [`mcp.json`](mcp.json).

### Codex

`~/.codex/config.toml`:

```toml
[mcp_servers.skool]
command = "uvx"
args = ["--from", "skool-api-mcp", "skool-mcp", "mcp"]
```

### Over HTTP

`skool-mcp serve` also serves MCP over streamable HTTP at `http://127.0.0.1:8787/mcp`, for clients that take a URL:

```bash
skool-mcp serve
claude mcp add --transport http skool http://127.0.0.1:8787/mcp
```

Then ask your agent things like:

> *Show me pending membership requests and approve the ones whose answers mention a business.*
>
> *Which posts from the last 7 days have no comments yet? Draft a reply for each.*
>
> *Create a Calendar event for Thursday 6pm CET with the Zoom link and pin an announcement about it.*
>
> *Tell me new members, churn and MRR for the last 30 days.*

## REST API

```bash
skool-mcp serve                    # http://127.0.0.1:8787, MCP at /mcp, docs at /docs
```

Each tool has its own route under `/api/v1/skool`, the same paths as the hosted API at cotlet.dev, so code written against one works with the other. Path parts and the query string are arguments, and a JSON body adds the rest.

```bash
curl 'http://127.0.0.1:8787/api/v1/skool/groups'
curl 'http://127.0.0.1:8787/api/v1/skool/groups/yourgroup/members?limit=30&role=admin'
curl -X POST http://127.0.0.1:8787/api/v1/skool/groups/yourgroup/posts \
  -H 'Content-Type: application/json' \
  -d '{"title": "Live call tonight", "body": "8pm CET, link in the Calendar.", "category": "Announcements"}'
```

Any tool by name, body as its arguments:

```bash
curl -X POST http://127.0.0.1:8787/api/v1/skool/tools/list_members -d '{"group": "yourgroup"}'
```

- `GET /api/v1/skool/tools`: every tool with its route, input schema and an example answer.
- `GET /docs`: interactive OpenAPI docs, `GET /openapi.json` the schema, for n8n, Postman or a generated client.
- Answers are JSON. Lists return `next_cursor`; pass it back as `cursor` for the next page.

The server listens on `127.0.0.1` only. To reach it from another device of yours, set a token, and every request then needs `Authorization: Bearer <token>`:

```bash
SKOOL_MCP_TOKEN=$(openssl rand -hex 24) skool-mcp serve --host 0.0.0.0
```

## Python and the example scripts

Straight from Python, no server needed:

```python
from skool_api_mcp import call
from skool_api_mcp.scripting import paginate, write_rows

groups = call("list_groups")["groups"]
members = list(paginate("list_members", {"group": "yourgroup", "joined_since": "2026-10-01"}, "members"))
write_rows(members, "members.csv")
call("create_post", group="yourgroup", category="Announcements", title="Week 12", body="Ship one landing page.")
```

Or one tool from the shell: `skool-mcp call list_posts group=yourgroup limit=10`, or with a JSON object.

Ready scripts in [`examples/`](examples/). Each prints JSON, takes `--out file.csv` or `--out file.json` where it makes sense, and `--help`:

| Script | What it does |
|---|---|
| [`list_groups.py`](examples/list_groups.py) | Your groups, with your role, member count and price. |
| [`export_members.py`](examples/export_members.py) | Members to CSV or JSON: name, role, level, points, join date, profile URL. `--role`, `--since`. |
| [`list_membership_requests.py`](examples/list_membership_requests.py) | Pending requests with each applicant's answers. |
| [`approve_membership_requests.py`](examples/approve_membership_requests.py) | Approves all pending requests, or those whose answers match `--match` keywords. `--dry-run` first. |
| [`decline_membership_request.py`](examples/decline_membership_request.py) | Declines one request. |
| [`welcome_new_members.py`](examples/welcome_new_members.py) | A welcome DM with your Start Here course link to everyone who joined in the last N days. |
| [`export_posts.py`](examples/export_posts.py) | Feed posts: title, author, category, likes, comments, date. `--category`, `--since`. |
| [`get_post.py`](examples/get_post.py) | One post with its body and the whole comment tree. |
| [`unanswered_posts.py`](examples/unanswered_posts.py) | Posts from the last N days with no comments yet. |
| [`create_post.py`](examples/create_post.py) | Publishes a post from `--body` or a Markdown file, `--pin` pins it. |
| [`comment_on_post.py`](examples/comment_on_post.py) | Comments on a post or replies under a comment. |
| [`pin_post.py`](examples/pin_post.py) | Pins or unpins a post on the feed or a Classroom page. |
| [`list_courses.py`](examples/list_courses.py) | Classroom courses with modules, unlock rule and URLs. |
| [`unread_messages.py`](examples/unread_messages.py) | Unread Skool Chat conversations with the full thread. |
| [`send_message.py`](examples/send_message.py) | A DM to one member. |
| [`group_stats.py`](examples/group_stats.py) | Total members, new joins, churn and MRR for 7, 30 or 90 days. |

```bash
python examples/export_members.py --group yourgroup --out members.csv
python examples/approve_membership_requests.py --group yourgroup --match business --dry-run
```

On a schedule, cron on your own computer works while it is on: `0 8 * * * cd ~/skool-api-mcp-server && .venv/bin/python examples/group_stats.py --group yourgroup`.

## All 69 tools

`group` is the URL name of a community: `yourgroup` for `skool.com/yourgroup`. `skool-mcp tools` prints this list, `skool-mcp tools --json` adds the input schemas.

### Groups and search

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_groups` | read | `GET /groups` | Skool groups of your account, with your role (or pending), member count and price. |
| `get_group` | read | `GET /groups/{group}` | A group's name, About text, privacy, price, counts, owner and membership questions. |
| `get_group_stats` | read | `GET /groups/{group}/stats` | Total, new and churned members and monthly recurring revenue for a period. Admins only. |
| `discover_groups` | read | `GET /groups/discover` | Search Skool's public directory of communities, with members, price and rating. |
| `search_group` | read | `GET /groups/{group}/search` | Search a group's posts, members or courses, as its search box does. |

### Posts

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_posts` | read | `GET /groups/{group}/posts` | Posts in a group's feed, pinned first, then newest, with author, category, likes and comment count. |
| `get_post` | read | `GET /groups/{group}/posts/{post_id}` | One post with its full text and comments, replies nested under their comment. |
| `create_post` | write | `POST /groups/{group}/posts` | Publish a post to the community feed in a category, as you. |
| `update_post` | write | `PATCH /groups/{group}/posts/{post_id}` | Change the title, text or category of a post you wrote, or any post as an admin. |
| `delete_post` | write | `DELETE /groups/{group}/posts/{post_id}` | Delete a post or a comment for good: yours, or anyone's as an admin. |

### Comments, likes, polls and moderation

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `comment_on_post` | write | `POST /groups/{group}/posts/{post_id}/comments` | Comment on a post, or reply to a comment, as you. |
| `like_post` | write | `PUT /groups/{group}/posts/{post_id}/like` | Like a post or a comment, or take the like back. |
| `list_post_likes` | read | `GET /groups/{group}/posts/{post_id}/likes` | Who liked a post or a comment. |
| `follow_post` | write | `PUT /groups/{group}/posts/{post_id}/follow` | Get notified of new comments on a post, or stop. |
| `pin_post` | write | `PUT /groups/{group}/posts/{post_id}/pin` | Pin a post to the top of the feed (up to 3) or to a Classroom page (up to 12). Admins only. |
| `pin_comment` | write | `PUT /groups/{group}/posts/{post_id}/comments/{comment_id}/pin` | Pin a comment to the top of a post's comments, or unpin it. |
| `set_post_comments` | write | `PUT /groups/{group}/posts/{post_id}/commenting` | Turn comments on a post off, or back on. |
| `vote_on_poll` | write | `PUT /groups/{group}/posts/{post_id}/poll/vote` | Vote in a post's poll, change your vote, or take it back. |
| `get_poll_results` | read | `GET /groups/{group}/posts/{post_id}/poll` | Answers and vote counts of a post's poll, optionally with who voted for what. |
| `list_reported_posts` | read | `GET /groups/{group}/posts/reported` | Posts members reported to the admins, waiting for review. Admins and moderators only. |

### Members

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_members` | read | `GET /groups/{group}/members` | Members of a group with role, level, points and join date, newest first; also banned or churned. |
| `search_members` | read | `GET /groups/{group}/members/search` | Find members of a group by name, as the @mention box does. |
| `get_member` | read | `GET /groups/{group}/members/{member_id}` | One member's profile in a group: name, bio, role, level, points and when they were last online. |
| `get_leaderboard` | read | `GET /groups/{group}/leaderboard` | The group's top 10 members by points for the last 7 days, 30 days or all time, and your rank. |
| `invite_members` | write | `POST /groups/{group}/invitations` | Email people an invitation that lets them straight into the group. Admins only. |
| `remove_member` | write | `DELETE /groups/{group}/memberships/{membership_id}` | Remove a member from the group, or lift a ban. Admins only. |
| `ban_member` | write | `POST /groups/{group}/memberships/{membership_id}/ban` | Ban a member from the group, optionally deleting their recent posts. Admins only. |
| `set_member_role` | write | `PUT /groups/{group}/memberships/{membership_id}/role` | Make a member an admin or moderator, or back to a member. Admins only. |

### Membership requests

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_membership_requests` | read | `GET /groups/{group}/membership-requests` | Pending requests to join, with each applicant's Membership Questions answers. Admins and moderators only. |
| `approve_membership_request` | write | `POST /groups/{group}/membership-requests/{request_id}/approve` | Let an applicant into the group. Your AutoDM, if set, goes out as usual. |
| `decline_membership_request` | write | `POST /groups/{group}/membership-requests/{request_id}/decline` | Decline an applicant's request to join. |

### Classroom

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_courses` | read | `GET /groups/{group}/courses` | Courses in the group's Classroom, open or locked for you, with the modules of open ones. |
| `get_course` | read | `GET /groups/{group}/courses/{course_id}` | One course with its lessons and folders in Classroom order; get_lesson reads a lesson. |
| `create_course` | write | `POST /groups/{group}/courses` | Add a course to the group's Classroom, as a draft or published. Admins only. |
| `set_course_published` | write | `PUT /groups/{group}/courses/{course_id}/published` | Publish a draft course to members, or turn it back into a draft. Admins only. |
| `get_lesson` | read | `GET /groups/{group}/courses/{course_id}/lessons/{lesson_id}` | One lesson's text and video link. |
| `create_lesson` | write | `POST /groups/{group}/courses/{course_id}/lessons` | Add a lesson at the end of a course, with text and a video link. Admins only. |
| `update_lesson` | write | `PATCH /groups/{group}/lessons/{lesson_id}` | Change a lesson's title, text or video link. Admins only. |
| `mark_lesson_complete` | write | `PUT /groups/{group}/lessons/{lesson_id}/completion` | Mark a lesson done in your own course progress, or undo it. |

### Calendar

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_events` | read | `GET /groups/{group}/events` | Events on a group's calendar in one month: title, time, place and who can join. |
| `get_event` | read | `GET /groups/{group}/events/{event_id}` | One calendar event with its full description, place and access. |
| `create_event` | write | `POST /groups/{group}/events` | Add an event to a group's calendar. Admins only. |
| `update_event` | write | `PATCH /groups/{group}/events/{event_id}` | Change a calendar event's title, time, place or access. Admins only. |
| `delete_event` | write | `DELETE /groups/{group}/events/{event_id}` | Delete a calendar event. Admins only. |

### Group settings (admins)

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_categories` | read | `GET /groups/{group}/categories` | The feed categories of a group: name, who can post, sort order, post count. |
| `create_category` | write | `POST /groups/{group}/categories` | Add a category to a group's feed. Admins only. |
| `update_category` | write | `PATCH /groups/{group}/categories/{category_id}` | Rename a category or change who can post in it and how it sorts. Admins only. |
| `delete_category` | write | `DELETE /groups/{group}/categories/{category_id}` | Delete a feed category and move its posts to another. Admins only. |
| `list_group_rules` | read | `GET /groups/{group}/rules` | The rules of a group, numbered as the group shows them. |
| `add_group_rule` | write | `POST /groups/{group}/rules` | Add a rule at the end of the group rules. Admins only. |
| `update_group_rule` | write | `PATCH /groups/{group}/rules/{number}` | Change the title or text of a group rule. Admins only. |
| `delete_group_rule` | write | `DELETE /groups/{group}/rules/{number}` | Delete a group rule. Admins only. |
| `list_group_links` | read | `GET /groups/{group}/links` | The links on a group's sidebar, numbered as the group shows them. |
| `add_group_link` | write | `POST /groups/{group}/links` | Add a link to the group's sidebar. Admins only. |
| `update_group_link` | write | `PATCH /groups/{group}/links/{number}` | Change the text or address of a sidebar link. Admins only. |
| `delete_group_link` | write | `DELETE /groups/{group}/links/{number}` | Remove a link from the group's sidebar. Admins only. |
| `add_membership_question` | write | `POST /groups/{group}/membership-questions` | Add a question people answer when they ask to join the group. Admins only. |
| `update_membership_question` | write | `PATCH /groups/{group}/membership-questions/{number}` | Change a membership question. Admins only. |
| `delete_membership_question` | write | `DELETE /groups/{group}/membership-questions/{number}` | Remove a membership question. Admins only. |
| `list_levels` | read | `GET /groups/{group}/levels` | The group's 9 levels with their custom titles and how many members reached each. |
| `rename_level` | write | `PATCH /groups/{group}/levels/{level}` | Give one of the group's 9 levels its own title. Admins only. |
| `update_group_about` | write | `PUT /groups/{group}/about` | Replace the text on the group's About page. Admins only. |
| `get_auto_dm` | read | `GET /groups/{group}/auto-dm` | The welcome message Skool sends every new member, and whether it is on. Admins only. |
| `set_auto_dm` | write | `PATCH /groups/{group}/auto-dm` | Change the welcome message new members get, or turn it on or off. Admins only. |

### Chat and notifications

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_conversations` | read | `GET /conversations` | Your Skool Chat inbox: who, unread count and last message preview. |
| `get_conversation` | read | `GET /conversations/{conversation_id}` | The latest messages of one Skool Chat conversation, oldest first. |
| `send_message` | write | `POST /members/{member_id}/messages` | Send a direct message in Skool Chat to a member, starting a conversation if needed. |
| `list_notifications` | read | `GET /notifications` | Your Skool notifications: new posts, comments, mentions, likes and approvals, newest first. |
| `mark_notifications_read` | write | `POST /notifications/read` | Mark all your notifications read, everywhere or in one group. |

Never built, on purpose: your Skool sign-in, email, password, name and profile settings, and anything that moves money (plans, payments, payouts, billing). Every request passes a guard that refuses those Skool paths.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `SKOOL_MCP_HOME` | `~/.config/skool-api-mcp` | Folder of `session.json`. |
| `SKOOL_AUTH_TOKEN` | | Skool `auth_token` cookie, instead of `skool-mcp connect`. |
| `SKOOL_PROXY` | | Proxy for every request to Skool, e.g. `http://user:pass@host:port`. |
| `SKOOL_MCP_READ_ONLY` | | `1` hides and refuses every tool that changes Skool (same as `--read-only`). |
| `SKOOL_MCP_TOKEN` | | Bearer token required by `serve`; needed to listen beyond `127.0.0.1`. |
| `SKOOL_MCP_HOST`, `SKOOL_MCP_PORT` | `127.0.0.1`, `8787` | Address of `serve`. |

## Security and your Skool account

- **Your password never reaches this code.** Only cookies are read, and only those of skool.com.
- **The session file is yours.** `session.json` is created with mode 0600. Anyone who has it can act as you on Skool, so keep it out of git and shared folders.
- **Local by default.** `serve` binds to `127.0.0.1` and refuses another address without `SKOOL_MCP_TOKEN`.
- **skool.com only.** Requests and redirects outside skool.com are refused.
- **Read-only mode.** `--read-only` or `SKOOL_MCP_READ_ONLY=1` exposes the 28 read tools only.
- **Actions reach real people.** Posts, comments, DMs, invitations and approvals go out under your name. MCP clients ask before running them; a script does not, so try it on a test group first.
- **Do not spam.** Mass DMs or invitations break Skool's rules and can get your account limited. You are responsible for what runs in your account.

## Errors

The REST API answers `{"error": "<code>", "message": "..."}`. The MCP server returns the same code and message as a tool error.

| Status | Code | What to do |
|---|---|---|
| 401 | `auth_required`, `auth_expired` | No session, or Skool signed you out. Sign in to Skool in Chrome and run `skool-mcp connect`. |
| 403 | `app_permission_denied` | Your Skool role cannot do this, e.g. stats as a member. |
| 403 | `scope_denied` | The server runs read-only. |
| 403 | `target_blocked` | Skool refused the request or showed a bot check. Open skool.com in Chrome once, then retry. |
| 409 | `captcha_required` | Skool asks for a CAPTCHA. Solve it in Chrome. |
| 422 | `invalid_input` | An argument is missing or wrong; the message names it. |
| 429 | `rate_limited` | Skool is limiting the account. Wait a few minutes. |
| 502 | `target_error` | Skool answered with an error, or changed its site. `git pull` for the latest tools, or [open an issue](https://github.com/cotletdev/skool-api-mcp-server/issues). |

## Self-hosted or hosted

| | This repo | [Cotlet, hosted](https://cotlet.dev/integrations/skool-api-mcp-server) |
|---|---|---|
| Tools | the same 69 | the same 69 |
| Runs | on your computer, while it is on | in the cloud, 24/7 |
| Skool session | your Chrome, cookies in a local file | your own Cloud Browser in the EU, profile encrypted with AES-256-GCM |
| When Skool changes its site | `git pull` once we have fixed it | fixed for you, every tool tested daily |
| Approvals | your MCP client asks per call | posts, DMs and approvals wait for your OK, switchable per tool |
| Works with | MCP clients on your machine, local scripts | Claude.ai and ChatGPT connectors, n8n, Make, Zapier, any HTTP client |
| Who may use it | you, for noncommercial use | teams, businesses, agencies |
| Price | free | free 7-day trial with 2,000 credits, no card; then one-time packs from $29 for 5,000 credits |

On the hosted version a successful call uses 20 to 30 credits (25 for most tools), failed calls are free, and the Cloud Browser uses 50 credits a day while it has an app enabled for agents. [Full pricing](https://cotlet.dev/pricing).

## FAQ

**Does Skool have an official API?**
No. Skool has no public API and no developer docs. The only official connection is the Zapier plugin on the Pro plan, which sends new paid members and Membership Questions answers out, invites a member and unlocks a course. It cannot list all members, approve requests, post, comment, send DMs or read stats. Details: [cotlet.dev/integrations/skool-api-mcp-server](https://cotlet.dev/integrations/skool-api-mcp-server).

**Is there a Skool MCP server for Claude, ChatGPT or Cursor?**
Yes, this one runs on your machine: `skool-mcp mcp` for Claude Code, Claude Desktop, Cursor and Codex. ChatGPT and Claude.ai connectors need a public HTTPS URL, which the [hosted Skool MCP server](https://cotlet.dev/integrations/skool-api-mcp-server) gives you.

**Is this a Skool scraper?**
It does what people want a scraper for (export members, posts and courses to CSV) but does not parse HTML in a headless browser. It calls the same JSON endpoints the Skool web app calls, in your own account.

**Can I export Skool members to CSV?**
Yes: `python examples/export_members.py --group yourgroup --out members.csv`. Every member with role, level, points, join date and profile URL, across all pages.

**Can I export members of a community I don't own?**
Only of groups your account belongs to, and only what Skool shows to your role.

**Do I need Skool's Pro plan or Zapier?**
No. A few Skool features are Pro only, for example some member roles; the tool says so when Skool refuses.

**Why does it need my Chrome?**
To read your Skool session without your password. Chrome is used once per sign-in, not for each call.

**What happens when Skool signs me out?**
Calls fail with `auth_expired`. With Chrome remote debugging on, the server reads the new cookies on the next call (click Allow when Chrome asks); otherwise run `skool-mcp connect` again.

**Can it run on a VPS or in Docker?**
Technically yes, with `SKOOL_AUTH_TOKEN`. Skool then sees your session from a datacenter IP, which looks less like you. For an always-on setup the hosted version keeps your session in your own Cloud Browser on a fixed IP.

**Will my Skool account get banned?**
Requests carry Chrome's fingerprint and go out one at a time, as you would click. Nobody can promise a platform never acts. Keep to your normal use and do not send bulk DMs.

**Can I use it at work or for my clients?**
No, the license allows noncommercial use only. For a team, a company or client work, use [Cotlet](https://cotlet.dev) or write to [contact@cotlet.dev](mailto:contact@cotlet.dev).

**Is it open source?**
The source is public, the license is not an open source license: noncommercial use only, no business use.

**A tool broke or I need another one.**
[Open an issue](https://github.com/cotletdev/skool-api-mcp-server/issues) with the tool name and the error message.

## License

[PolyForm Noncommercial License 1.0.0](LICENSE). In short:

- **Allowed:** noncommercial use: you, for your own personal purposes with your own Skool account, or a charity, school, public research or government body. Changing the code, and sharing it under the same license.
- **Not allowed:** any commercial use, your own business included; client work; selling or offering it, or a service built on it.

Versions up to 1.x of this repo (the scripts for the hosted API) stay MIT.

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev) ([@cotletdev](https://x.com/cotletdev)). Skool is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by Skool.
