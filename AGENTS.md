# AGENTS.md

You are an AI agent in a clone of this repo. It is a self-hosted Skool API and MCP server: 69 tools that work in the user's own Skool account, through the session of their own Google Chrome. Your usual job is one of three: set it up for the user, use its tools for them, or change its code. Human docs: `README.md`.

## Before you start

- The license allows noncommercial use only (PolyForm Noncommercial 1.0.0, `LICENSE`). If the user is setting this up for a company, a team or clients, say so and point to the hosted version at https://cotlet.dev/integrations/skool-api-mcp-server. Do not continue the setup for that use.
- Every tool acts as the user on Skool. Tools with access `write` post, comment, message, invite, approve or change a group, and real people see the result.

## Set it up for the user

Do the steps yourself. Ask the user only for what needs their hands in Chrome.

1. Check Python: `python3 --version` must be 3.11 or newer.
2. Install in the repo root:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -e .
   .venv/bin/skool-mcp --version
   ```

   On Windows the path is `.venv\Scripts\skool-mcp`. With uv: `uv venv && uv pip install -e .`.
3. Ask the user to do two things in Chrome. You cannot open `chrome://` pages for them.
   - Open `chrome://inspect/#remote-debugging` and switch remote debugging on.
   - Be signed in at https://www.skool.com.
4. Run `.venv/bin/skool-mcp connect`. Tell the user to click **Allow** when Chrome asks about the connection. Success prints `Signed in to Skool as <name>`.
5. Check: `.venv/bin/skool-mcp status`, then `.venv/bin/skool-mcp call list_groups`.
6. Add the MCP server to the user's client. Use the absolute path of `.venv/bin/skool-mcp`:
   - Claude Code: `claude mcp add skool -- <abs path>/.venv/bin/skool-mcp mcp`
   - Claude Desktop, Cursor, Codex: the config blocks in `README.md`, section "MCP server".
   - Add `--read-only` after `mcp` if the user only wants to read.
   The client loads new MCP servers on its next start. Tell the user.

If step 4 fails:

| Message | What to do |
|---|---|
| `Chrome remote debugging is off` | Step 3 is not done, or Chrome is Beta, Canary or a custom profile: pass `--profile-dir "<profile folder>"`. |
| `Could not connect to Chrome` | The user did not click Allow, or Chrome is closed. Run `connect` again. |
| `This Chrome is not signed in to Skool` | The user signs in at skool.com in that Chrome, then run `connect` again. |
| No Chrome on this machine (a server) | The user copies the `auth_token` cookie from Chrome DevTools (Application, Cookies, https://www.skool.com) and runs `skool-mcp connect --token` themselves. Never ask them to paste the token into the chat. |

## Use the tools

- With the MCP server added, call its tools. Without it: `.venv/bin/skool-mcp call <tool> key=value ...`, or one JSON object as the argument.
- `.venv/bin/skool-mcp tools` lists every tool with access and route. `tools --json` adds the input schemas.
- Start with `list_groups`. Its `group` values (the URL name, `yourgroup` for skool.com/yourgroup) are what most tools take.
- Lists return `next_cursor`. Pass it back as `cursor` for the next page.
- Before a `write` tool, show the user what you will send and to whom, and get their OK. Never send the same message to many members in a loop.
- For a script or a cron job, use `skool_api_mcp.scripting` (`call`, `paginate`, `write_rows`) and the scripts in `examples/` as models.
- For a REST API (n8n, other languages): `.venv/bin/skool-mcp serve`, routes under `http://127.0.0.1:8787/api/v1/skool`, docs at `/docs`.

Errors come as `<code>: <message>`. `auth_expired` means Skool signed the session out: the user signs in again in Chrome and you run `connect`. `app_permission_denied` means the user's Skool role is too low for that tool. More codes: `README.md`, section "Errors".

## Keep secrets out

- `~/.config/skool-api-mcp/session.json` and `SKOOL_AUTH_TOKEN` give full access to the user's Skool account. Never print, log, commit or copy their content.
- `serve` listens on 127.0.0.1. Never start it on another address without `SKOOL_MCP_TOKEN`.

## Change the code

| Path | What | Edit? |
|---|---|---|
| `skool_api_mcp/skool/` | the Skool tools, one file per tool in `tools/`, shared request code in `client.py` | Yes for a local fix, but the next `git pull` brings our version of these files. Report the bug at https://github.com/cotletdev/skool-api-mcp-server/issues |
| `skool_api_mcp/app.py` | app name, domains, session cookie, REST prefix | Rarely |
| `skool_api_mcp/core/` | `@tool` declaration, errors, the HTTP client with the session (`context.py`) | Yes |
| `skool_api_mcp/session.py` | reading cookies from Chrome over CDP, the session file | Yes |
| `skool_api_mcp/runner.py`, `api.py`, `mcp_server.py`, `cli.py` | tool registry, REST API, MCP server, command line | Yes |
| `examples/` | scripts for common jobs | Yes |

A new tool is a new file in `skool_api_mcp/skool/tools/` with a `@tool(...)` declaration (name, access, input schema, `route`). The registry finds it, and the REST API, the MCP server and the CLI show it without other changes.

There is no test suite. After a change, run `.venv/bin/skool-mcp tools` and one read tool against the user's account.
