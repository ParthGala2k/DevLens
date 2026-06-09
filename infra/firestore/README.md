# Firestore — app state

Collections:

- `connectors/{id}` — `{status, last_sync_at}` for github/jira/slack/calendar/pagerduty
- `alerts/{id}` — proactive alerts (see `shared/contracts/alert.json`)
- `issue_proposals/{id}` — discussion→repo bridge approval queue (see `shared/contracts/issue-proposal.json`)
- `chat_sessions/{id}/messages/{msgId}` — chat history
- `agent_runs/{id}` — cached agent reasoning traces (incl. MCP/tool calls)

Local dev uses the Firestore emulator (`docker-compose.yml`, `FIRESTORE_EMULATOR_HOST`).
Writes are performed only by the backend service account; `firestore.rules` reflects that.
