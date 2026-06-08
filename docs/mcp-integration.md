# MCP integration (Fivetran + GitLab)

DevLens uses **two** MCP servers. Fivetran is the mandatory track integration (sync); GitLab is the
action layer (writes). Both are wired through the same generic session + activity tap, so both appear
in the live MCP Activity Log.

## Shared plumbing
- `integrations/mcp/session.py` — generic MCP client session (connect, list_tools, call_tool).
- `integrations/mcp/activity_log.py` — the visibility layer. Wrap any call with
  `tap(action, server, connector=...)`, which publishes to the event bus `mcp_log` channel:
  ```
  { "server": "fivetran", "connector": "gitlab", "action": "sync_connector", "status": "success", "ts": ... }
  { "server": "gitlab",   "connector": null,     "action": "create_issue",   "status": "success", "ts": ... }
  ```
  Frontend `McpActivityLog` subscribes to `/api/mcp-log/stream` and renders these live, e.g.
  `[Fivetran MCP] → sync_connector(gitlab) → success` / `[GitLab MCP] → create_issue → success`.

## 1. Fivetran MCP — sync layer  (`integrations/mcp/fivetran_client.py`)
Helpers: `sync_connector(connector)`, `connector_status(connector)`, `list_connectors()`.
Exposed to the agent via `agent/tools/fivetran_mcp.py`. Env: `FIVETRAN_MCP_URL`, `FIVETRAN_API_KEY`,
`FIVETRAN_API_SECRET`, `FIVETRAN_GROUP_ID`.

## 2. GitLab MCP — action layer  (`integrations/mcp/gitlab_client.py`)
Helpers: `create_issue(...)`, `assign_issue(...)`, `add_label(...)`, `list_issues(...)`.
Exposed to the agent via `agent/tools/gitlab_mcp.py`. Env: `GITLAB_MCP_URL`, `GITLAB_TOKEN`
(PAT with `api` scope), `GITLAB_PROJECT_ID`.

## Where MCP calls originate
- **User-triggered sync:** "Sync Now" → `POST /api/connectors/{id}/sync` → Fivetran MCP.
- **Bridge action:** approving an issue proposal → `POST /api/bridge/proposals/{id}/approve` →
  GitLab MCP `create_issue` (gated on human approval — see `services/bridge_service.py`).
- **Agent-triggered:** the agent may call sync/status (Fivetran) or live issue reads (GitLab)
  mid-reasoning — visible in both the chat tool-call stream and the MCP log.
