# Fivetran MCP integration

The Fivetran MCP server is our mandatory partner integration. It is wired in two places and made
visible in one.

## 1. Transport — `integrations/mcp/session.py`
Generic MCP client session (connect, list_tools, call_tool). Transport + endpoint come from
`.env` (`FIVETRAN_MCP_URL`, credentials).

## 2. Fivetran wrapper — `integrations/mcp/fivetran_client.py`
Typed helpers: `sync_connector(connector)`, `connector_status(connector)`,
`list_connectors()`. These are also exposed to the agent as ADK tools
(`agent/tools/fivetran_mcp.py`).

## 3. Activity tap — `integrations/mcp/activity_log.py`  ← the visibility layer
Every MCP call is wrapped by `tap()`, which publishes structured events to the event bus
`mcp_log` channel:
```
{ "connector": "github", "action": "sync_connector", "status": "start",   "ts": ... }
{ "connector": "github", "action": "sync_connector", "status": "success", "ts": ... }
```
The frontend `McpActivityLog` subscribes to `/api/mcp-log/stream` and renders these live, e.g.:
```
[Fivetran MCP] → sync_connector(github) → success
```

## Where MCP calls originate
- **User-triggered:** the "Sync Now" button → `POST /api/connectors/{id}/sync`.
- **Agent-triggered:** the agent decides data is stale and calls the Fivetran sync/status tools
  mid-reasoning — visible in both the chat tool-call stream and the MCP log.
