# Shared contracts

JSON Schemas that are the **single source of truth** for data shapes crossing the
backend↔frontend boundary. When you change a schema here, update both:

- backend pydantic models in `backend/app/domain/` and `backend/app/api/schemas/`
- frontend TS types in `frontend/src/lib/types.ts`

| Schema | Used by |
|---|---|
| `agent-events.json` | `/api/chat/{id}/stream` SSE — agent reasoning + tool calls |
| `mcp-event.json` | `/api/mcp-log/stream` SSE — live MCP calls (Fivetran + GitHub) |
| `alert.json` | `/api/alerts` + `/api/alerts/stream` — proactive alert feed |
| `issue-proposal.json` | `/api/bridge/proposals` (+ stream) — discussion→repo approval queue |
| `workload.json` | `/api/team/workload` + `/api/team/reliability` — developer observability |
