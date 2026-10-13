# Skool API and MCP Server

**Skool API** for Python scripts and a hosted **Skool MCP server** for Claude, ChatGPT, Cursor, Codex and n8n. Export Skool members to CSV, approve membership requests, export and publish posts, read and send Skool Chat DMs and pull members, churn and MRR stats from your own Skool community.

Skool has no public API and no official MCP server. This repo gives you both, on top of the **hosted Skool API by [Cotlet](https://cotlet.dev/integrations/skool-api-mcp-server)**: you sign in to Skool once in your browser, Cotlet keeps the session working, and your AI agent (over MCP) or the Python scripts here (over the REST API) work in your account with one API key.

- **Skool MCP server:** `https://cotlet.dev/mcp/v1`, 15 Skool tools for your AI agent. [Setup](#skool-mcp-server-for-claude-chatgpt-cursor-and-codex)
- **Skool API:** `https://cotlet.dev/api/v1/skool/{endpoint}`, plus 16 ready Python scripts, one file per job, standard library only. [Scripts](#scripts)

[![Skool API docs](https://img.shields.io/badge/Skool%20API-docs-6d4aef)](https://cotlet.dev/docs/api/skool)
[![Skool MCP server](https://img.shields.io/badge/Skool%20MCP%20server-cotlet.dev%2Fmcp%2Fv1-6d4aef)](https://cotlet.dev/docs/mcp)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-141318)](#requirements)
[![No dependencies](https://img.shields.io/badge/dependencies-none-141318)](#requirements)
[![License: MIT](https://img.shields.io/badge/license-MIT-141318)](LICENSE)

```bash
# Skool MCP server for your AI agent (Claude Code)
claude mcp add --transport http cotlet https://cotlet.dev/mcp/v1 \
  --header "Authorization: Bearer $COTLET_API_KEY"

# Skool API from Python
git clone https://github.com/cotletdev/skool-api-mcp-server.git && cd skool-api-mcp-server
export COTLET_API_KEY=cotlet_...          # https://cotlet.dev/app/signup?app=skool
python export_members.py --group yourgroup --out members.csv
```

## Contents

- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Scripts](#scripts)
- [Skool MCP server for Claude, ChatGPT, Cursor and Codex](#skool-mcp-server-for-claude-chatgpt-cursor-and-codex)
- [Run it on a schedule: cron, GitHub Actions, n8n, Make, Zapier](#run-it-on-a-schedule)
- [Skool API endpoints](#skool-api-endpoints)
- [FAQ](#faq)
- [Pricing](#pricing)
- [Security and your Skool account](#security-and-your-skool-account)

## How it works

```text
your script / AI agent ──HTTPS──▶ Cotlet Skool API ──your session──▶ skool.com (your account)
```

1. **Get an API key.** [Request access at cotlet.dev](https://cotlet.dev/app/signup?app=skool) with Skool selected. Each request is reviewed and the key arrives by email. Every account starts with a free 7-day trial and 5,000 credits, no card needed.
2. **Connect Skool once.** In the Cotlet console, open the Skool connect page and sign in to Skool the way you always do, including 2FA. Cotlet keeps the session, never your password.
3. **Run the scripts.** Each one is a plain `POST https://cotlet.dev/api/v1/skool/{endpoint}` with your key. When Skool changes its site, Cotlet fixes the integration; these scripts keep working unchanged.

Without a key, or before your access is active, the API answers `403` with a link to request access.

## Quick start

### Requirements

- Python 3.9 or newer. No `pip install`: the scripts use only the standard library.
- A Cotlet API key with Skool connected.
- An admin or moderator role in the group for membership requests, and admin for stats and pinning. Members, posts, courses and DMs work with any role in groups you belong to.

### Setup

```bash
git clone https://github.com/cotletdev/skool-api-mcp-server.git
cd skool-api-mcp-server
cp .env.example .env          # paste your key into .env, or:
export COTLET_API_KEY=cotlet_...
```

### First calls

```bash
python list_groups.py                                   # your groups and the --group value of each
python export_members.py --group yourgroup --out members.csv
python list_membership_requests.py --group yourgroup
python group_stats.py --group yourgroup --period 30d
```

`--group` is the URL name of the community: `yourgroup` for `skool.com/yourgroup`.

## Scripts

Every script prints JSON by default. Add `--out file.csv` or `--out file.json` to save it. Run any script with `--help` for all options.

### Members and membership requests

| Script | What it does |
|---|---|
| [`list_groups.py`](list_groups.py) | Lists every Skool group you belong to, with your role, member count and price. |
| [`export_members.py`](export_members.py) | Exports members to CSV or JSON: name, role, level, points, join date, profile URL. Filter by `--role` or `--since`. Follows pagination for you. |
| [`list_membership_requests.py`](list_membership_requests.py) | Pending requests to join, with each applicant's Membership Questions answers. |
| [`approve_membership_requests.py`](approve_membership_requests.py) | Approves all pending requests, or only those whose answers contain your `--match` keywords. `--dry-run` shows who would get in. |
| [`decline_membership_request.py`](decline_membership_request.py) | Declines one request. |
| [`welcome_new_members.py`](welcome_new_members.py) | Sends everyone who joined in the last N days a personal welcome DM with your Start Here course link. |

### Posts and comments

| Script | What it does |
|---|---|
| [`export_posts.py`](export_posts.py) | Exports feed posts: title, author, category, likes, comment count, date. Filter by `--category` or `--since`. |
| [`get_post.py`](get_post.py) | One post with its full body, attachments and the whole comment tree. |
| [`unanswered_posts.py`](unanswered_posts.py) | Posts from the last N days with no comments yet. |
| [`create_post.py`](create_post.py) | Publishes a post in a category, from `--body` or a Markdown file, and pins it with `--pin`. |
| [`comment_on_post.py`](comment_on_post.py) | Comments on a post or replies under a comment. |
| [`pin_post.py`](pin_post.py) | Pins or unpins a post on the feed or a Classroom page. |

### Classroom, chat and stats

| Script | What it does |
|---|---|
| [`list_courses.py`](list_courses.py) | Classroom courses with modules, unlock rule (open, level or paid) and URLs. |
| [`unread_messages.py`](unread_messages.py) | Your unread Skool Chat conversations with the full thread. |
| [`send_message.py`](send_message.py) | Sends a DM to one member. |
| [`group_stats.py`](group_stats.py) | Total members, new joins, churn and MRR for 7, 30 or 90 days. |

### Write your own

[`cotlet_client.py`](cotlet_client.py) is 150 lines and has everything: auth, pagination, rate-limit retries, confirmations and CSV export.

```python
from cotlet_client import call, paginate

for member in paginate("list_members", {"group": "yourgroup", "joined_since": "2026-10-01"}, "members"):
    print(member["name"], member["level"])

call("create_post", {"group": "yourgroup", "category": "Announcements",
                     "title": "Live call tonight", "body": "8pm CET, link in the Calendar."})
```

### Confirmations for actions that reach people

Approving, declining, posting, commenting and sending DMs go out under your name. By default each of these calls waits for your OK: the script prints a link, you approve it in the browser, and the script continues. For unattended runs (cron, GitHub Actions), switch confirmation off for the tools you choose in the Cotlet dashboard, for example only for `approve_membership_request`. Pinning runs without asking.

## Skool MCP server for Claude, ChatGPT, Cursor and Codex

The same Skool API is a hosted Skool MCP server, so your AI agent can do all of this in plain words. Nothing to install or run: one URL, same key. A ready config is in [`mcp.json`](mcp.json).

```bash
# Claude Code
claude mcp add --transport http cotlet https://cotlet.dev/mcp/v1 \
  --header "Authorization: Bearer $COTLET_API_KEY"
```

```json
// Cursor: ~/.cursor/mcp.json
{
  "mcpServers": {
    "cotlet": {
      "url": "https://cotlet.dev/mcp/v1",
      "headers": { "Authorization": "Bearer ${env:COTLET_API_KEY}" }
    }
  }
}
```

```toml
# Codex: ~/.codex/config.toml
[mcp_servers.cotlet]
url = "https://cotlet.dev/mcp/v1"
bearer_token_env_var = "COTLET_API_KEY"
```

Claude Desktop and ChatGPT: add a custom connector with the URL `https://cotlet.dev/mcp/v1`. Setup for every client: [cotlet.dev/docs/mcp](https://cotlet.dev/docs/mcp).

Then ask:

> *Show me pending membership requests and approve the ones whose answers mention a business.*
>
> *Which posts from the last 7 days have no comments yet? Draft a reply for each.*
>
> *Send a welcome DM with the Start Here course link to everyone who joined this week.*
>
> *Every Monday, tell me new members, churn and MRR for last week.*

Tools show up as `skool_list_members`, `skool_approve_membership_request` and so on.

## Run it on a schedule

| Where | How |
|---|---|
| **cron** | `0 8 * * * cd ~/skool-api-mcp-server && python3 approve_membership_requests.py --group yourgroup --match business` |
| **GitHub Actions** | Fork this repo, add the `COTLET_API_KEY` secret, set your group in [`.github/workflows/skool-daily.yml`](.github/workflows/skool-daily.yml) and uncomment the schedule. |
| **n8n** | MCP Client node with `https://cotlet.dev/mcp/v1`, or an HTTP Request node: `POST https://cotlet.dev/api/v1/skool/{endpoint}` with `Authorization: Bearer <key>`. Trigger: Schedule. |
| **Make** | HTTP module, same URL, header and JSON body. Scenario schedule. |
| **Zapier** | Webhooks by Zapier (POST), same URL, header and body. Schedule by Zapier trigger. |
| **Your AI agent** | A scheduled agent run, for example a Claude Code routine, with the MCP server above. |

Cotlet runs in the cloud, so scheduled jobs keep working while your computer is off.

## Skool API endpoints

Base URL `https://cotlet.dev/api/v1/skool`. Every endpoint is a `POST` with a JSON body. Full parameters and example responses: [cotlet.dev/docs/api/skool](https://cotlet.dev/docs/api/skool).

| Endpoint | Access | Description |
|---|---|---|
| `list_groups` | read | Skool groups you belong to, with your role and member count. |
| `list_members` | read | Members with name, role, level and join date, newest first. |
| `list_membership_requests` | read | Pending requests with Membership Questions answers. Admins and moderators. |
| `list_posts` | read | Feed posts, newest first, with author, category, likes and comment count. |
| `get_post` | read | Full post with body, attachments and comment tree. |
| `list_courses` | read | Classroom courses with modules, unlock rule and URL. |
| `list_conversations` | read | Skool Chat inbox: who, unread count, last message. |
| `get_conversation` | read | Messages in one conversation, oldest first. |
| `get_group_stats` | read | Total, new and churned members and MRR. Admins. |
| `approve_membership_request` | write, confirm | Let an applicant in. Your AutoDM goes out as usual. |
| `decline_membership_request` | write, confirm | Decline a request. |
| `create_post` | write, confirm | Publish a post in a category, as you. |
| `comment_on_post` | write, confirm | Comment or reply, as you. |
| `send_message` | write, confirm | DM a member in Skool Chat. |
| `pin_post` | write | Pin to the feed (up to 3) or a Classroom page (up to 12). Admins. |

Raw call, any language:

```bash
curl -X POST https://cotlet.dev/api/v1/skool/list_members \
  -H "Authorization: Bearer $COTLET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"group": "yourgroup", "limit": 100}'
```

### Errors

| Status | Code | What to do |
|---|---|---|
| 403 | `api_key_required`, `access_not_granted` | Set `COTLET_API_KEY`, or [request access to Skool](https://cotlet.dev/app/signup?app=skool). |
| 409 | `AUTH_REQUIRED`, `AUTH_EXPIRED` | Skool is not connected or the session expired. Open the link in the error and sign in again. |
| 409 | `CAPTCHA_REQUIRED`, `MFA_REQUIRED` | Skool asked for a check only you can pass. Finish it on the connect page. |
| 403 | `SCOPE_DENIED` | You connected Skool read-only. Allow write access in the dashboard. |
| 402 | `insufficient_credits` | Credits ran out. Wait for next month's or move to a bigger size. |
| 429 | `rate_limited` | The client waits for `Retry-After` and retries by itself. |
| 503 | `TARGET_BLOCKED` | Skool changed something; the endpoint is paused until it is fixed. Credits are refunded. |

## FAQ

**Does Skool have an official API?**
No. Skool has no public API and no developer docs. The only official connection is the Zapier plugin on the Pro plan, which can send new paid members and Membership Questions answers out, invite a member and unlock a course. It cannot list all members, approve requests, post, comment, send DMs or read stats. Details and sources: [cotlet.dev/integrations/skool-api-mcp-server](https://cotlet.dev/integrations/skool-api-mcp-server).

**Is this a Skool scraper?**
It does what people usually want a scraper for (export members, posts and courses to CSV) but works differently: the scripts call a hosted API that acts in your own Skool account with your own session. There is no headless browser on your machine, no `auth_token` cookie to copy from DevTools and nothing to fix when Skool updates its site.

**Can I export Skool members to CSV?**
Yes: `python export_members.py --group yourgroup --out members.csv`. You get every member with role, level, points, join date and profile URL, across all pages.

**Can I export members of a community I don't own?**
Only of groups your account belongs to, and only what Skool shows to your role. The scripts act as you; they do not reach data you could not see in the browser.

**Do I need Skool's Pro plan or Zapier?**
No. Cotlet does not use the Zapier plugin. Approving requests needs an admin or moderator role and stats need an admin, the same as in the Skool admin panel.

**Do I have to copy cookies or my Skool password into a config file?**
No. You sign in to Skool once in your browser on the Cotlet connect page, with 2FA if you use it. Cotlet stores only the session, encrypted, and never your password. Your scripts only ever hold the Cotlet API key.

**What happens when my Skool session expires?**
The call returns `AUTH_EXPIRED` with a link. Open it, sign in to Skool again, and rerun the script.

**Can these scripts approve every pending membership request automatically?**
Yes. `approve_membership_requests.py --all`, or `--match` with keywords from your Membership Questions. For a daily unattended run, switch confirmation off for `approve_membership_request` in the Cotlet dashboard and schedule the script with cron or GitHub Actions.

**Can I send DMs to all my Skool members?**
You can DM members one by one, for example a welcome message to new members with `welcome_new_members.py`. Messages go out under your name, wait for your OK by default, and calls are paced like a person, not blasted. Do not use it for spam: it breaks Skool's rules and Cotlet's [acceptable use policy](https://cotlet.dev/acceptable-use).

**Will my Skool account get banned?**
Calls are human-paced and use one isolated session per user. Nobody can promise a platform will never act, but Cotlet keeps the risk low and refuses abusive use. You stay responsible for following Skool's terms.

**Is this legal?**
You automate your own Skool account with your own login, to do what you could do by hand. Cotlet is unofficial and not affiliated with Skool, does not solve CAPTCHAs or bypass MFA, and pauses an integration within 24 hours if the platform objects.

**What about free members and free trials?**
`list_members` returns every member of the group, paid or free, unlike Skool's Zapier triggers, which fire only for paid members.

**Can I use it with n8n, Make or Zapier?**
Yes. Use the MCP Client node in n8n, or an HTTP request in any of them: `POST https://cotlet.dev/api/v1/skool/{endpoint}` with your key. See [Run it on a schedule](#run-it-on-a-schedule).

**Is there a Skool MCP server? Can I use it with Claude, ChatGPT or Cursor?**
Yes. Add the hosted Skool MCP server `https://cotlet.dev/mcp/v1`. See [Skool MCP server setup](#skool-mcp-server-for-claude-chatgpt-cursor-and-codex).

**How is this different from open-source Skool MCP servers or Apify actors?**
Open-source Skool MCP servers run on your computer with your session cookie in a local file, and stop working when Skool changes until someone fixes them. Apify actors bill per run on Apify. Cotlet is hosted, tested daily, keeps your session in an encrypted EU vault, gives you both a REST API and an MCP server with one key, and refunds credits for failed calls. If you would rather run and fix your own code, an open-source server may suit you better.

**What does it cost?**
See [Pricing](#pricing). Failed calls are free.

**Which Python version?**
3.9 or newer. No dependencies.

**My Skool community is not working / I need another endpoint.**
Email [contact@cotlet.dev](mailto:contact@cotlet.dev) with the `X-Request-Id` from the error, or [open an issue](https://github.com/cotletdev/skool-api-mcp-server/issues).

## Pricing

Free 7-day trial with 5,000 credits, no card needed. Then one plan for every app Cotlet supports, Skool included:

| Size | Price | Credits / month |
|---|---|---|
| Solo | $29/mo | 3,000 |
| Pro | $99/mo | 12,000 |
| Agency | $299/mo | 40,000 |

Each successful call uses credits for the work it takes; failed calls cost nothing. Each month's credits stay valid for 3 months. Nothing is charged until your access is active. [Full pricing](https://cotlet.dev/pricing).

## Security and your Skool account

- **No password stored.** You sign in to Skool yourself; Cotlet keeps only the session, encrypted with AES-256 in an EU vault.
- **Scoped access.** Connect Skool read-only, or read and write.
- **Your OK first.** Posts, comments, DMs and approvals wait for your confirmation unless you switch that off per tool.
- **Revoke in one click.** Disconnect Skool in the dashboard and the session is deleted.
- **No data kept.** Results pass through to your script and are not stored.
- **Never:** CAPTCHA solving, MFA bypass, spam.

More: [cotlet.dev/security](https://cotlet.dev/security).

## Links

- Skool API and MCP server: [cotlet.dev/integrations/skool-api-mcp-server](https://cotlet.dev/integrations/skool-api-mcp-server)
- Skool API reference: [cotlet.dev/docs/api/skool](https://cotlet.dev/docs/api/skool)
- Skool use cases: [auto-approve membership requests](https://cotlet.dev/integrations/skool-api-mcp-server/auto-approve-membership-requests), [weekly posts](https://cotlet.dev/integrations/skool-api-mcp-server/schedule-weekly-posts), [reply to unanswered posts](https://cotlet.dev/integrations/skool-api-mcp-server/reply-to-unanswered-posts), [answer Skool Chat](https://cotlet.dev/integrations/skool-api-mcp-server/answer-skool-chat-messages), [welcome new members](https://cotlet.dev/integrations/skool-api-mcp-server/welcome-new-members), [MRR and churn report](https://cotlet.dev/integrations/skool-api-mcp-server/weekly-mrr-churn-report)
- All apps without an API on Cotlet: [cotlet.dev/integrations](https://cotlet.dev/integrations)
- About Cotlet: [github.com/cotletdev/cotlet](https://github.com/cotletdev/cotlet)
- Cotlet on X: [@cotletdev](https://x.com/cotletdev)

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev). Skool is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by Skool. Scripts are MIT licensed; using the hosted API requires a Cotlet account and is subject to the [Cotlet terms](https://cotlet.dev/terms).
