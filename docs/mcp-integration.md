# MCP integration (Fivetran + GitHub)

DevLens uses **two** MCP servers. Fivetran is the mandatory track integration (sync); GitHub is the
action layer (writes). Both are wired through the same generic session + activity tap, so both appear
in the live MCP Activity Log.

## Shared plumbing
- `integrations/mcp/session.py` — generic MCP client session (connect, list_tools, call_tool).
- `integrations/mcp/activity_log.py` — the visibility layer. Wrap any call with
  `tap(action, server, connector=...)`, which publishes to the event bus `mcp_log` channel:
  ```
  { "server": "fivetran", "connector": "github", "action": "sync_connector", "status": "success", "ts": ... }
  { "server": "github",   "connector": null,     "action": "create_issue",   "status": "success", "ts": ... }
  ```
  Frontend `McpActivityLog` subscribes to `/api/mcp-log/stream` and renders these live, e.g.
  `[Fivetran MCP] → sync_connector(github) → success` / `[GitHub MCP] → create_issue → success`.

## 1. Fivetran MCP — sync layer  (`integrations/mcp/fivetran_client.py`)
Helpers: `sync_connector(connector)`, `connector_status(connector)`, `list_connectors()`.
Exposed to the agent via `agent/tools/fivetran_mcp.py`. Env: `FIVETRAN_MCP_URL`, `FIVETRAN_API_KEY`,
`FIVETRAN_API_SECRET`, `FIVETRAN_GROUP_ID`.

## 2. GitHub MCP — action layer  (`integrations/mcp/github_client.py`)
Helpers: `create_issue(...)`, `assign_issue(...)`, `add_labels(...)`, `list_issues(...)`.
Exposed to the agent via `agent/tools/github_mcp.py`. Env: `GITHUB_MCP_URL`, `GITHUB_TOKEN`
(PAT with `repo` scope), `GITHUB_REPO` (e.g. `itsRenuka22/stealth-labs-platform`).

## Where MCP calls originate
- **User-triggered sync:** "Sync Now" → `POST /api/connectors/{id}/sync` → Fivetran MCP.
- **Bridge action:** approving an issue proposal → `POST /api/bridge/proposals/{id}/approve` →
  GitHub MCP `create_issue` (gated on human approval — see `services/bridge_service.py`).
- **Agent-triggered:** the agent may call sync/status (Fivetran) or live issue reads (GitHub)
  mid-reasoning — visible in both the chat tool-call stream and the MCP log.
