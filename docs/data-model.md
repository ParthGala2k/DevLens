# Data model

## BigQuery (analytics)
Fivetran lands raw connector data into per-source datasets; we build derived views in
`devlens_metrics`.

| Source dataset | Example raw tables (confirm against real Fivetran schema) |
|---|---|
| `github` | pull_request, pull_request_review, issue, commit, repository |
| `jira` | issue, comment, changelog, sprint, worklog |
| `slack` | message, channel |
| `calendar` | event, attendee |
| `pagerduty` | incident, service, log_entry |

Derived views (`infra/bigquery/sql/`):
`pr_review_lag`, `deep_work_blocks`, `estimation_accuracy`, `oncall_noise`,
`developer_load`, `completion_reliability`, `actionable_threads`.

## Firestore (app state)
| Collection | Doc shape |
|---|---|
| `connectors/{id}` | `{ status, last_sync_at }` (github/jira/slack/calendar/pagerduty) |
| `alerts/{id}` | see `shared/contracts/alert.json` |
| `issue_proposals/{id}` | see `shared/contracts/issue-proposal.json` (bridge approval queue) |
| `chat_sessions/{id}/messages/{msgId}` | `{ role, text, ts }` |
| `agent_runs/{id}` | `{ session_id, events[], created_at }` |

## Streamed / shared shapes
Defined once in `shared/contracts/`: `agent-events.json`, `mcp-event.json` (now includes a `server`
field: fivetran | github), `alert.json`, `issue-proposal.json`, `workload.json`.
