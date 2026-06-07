# Data model

## BigQuery (analytics)
Fivetran lands raw connector data into per-source datasets; we build derived views in
`devlens_metrics`.

| Source dataset | Example raw tables (confirm against real Fivetran schema) |
|---|---|
| `github` | pull_request, review, requested_reviewer, commit |
| `jira` | issue, changelog, sprint, worklog |
| `calendar` | event, attendee |
| `pagerduty` | incident, service, log_entry |

Derived views (`infra/bigquery/sql/`): `pr_review_lag`, `deep_work_blocks`,
`estimation_accuracy`, `oncall_noise`.

## Firestore (app state)
| Collection | Doc shape |
|---|---|
| `connectors/{id}` | `{ status, last_sync_at }` |
| `alerts/{id}` | see `shared/contracts/alert.json` |
| `chat_sessions/{id}/messages/{msgId}` | `{ role, text, ts }` |
| `agent_runs/{id}` | `{ session_id, events[], created_at }` |

## Streamed event shapes
Defined once in `shared/contracts/`: `agent-events.json`, `mcp-event.json`, `alert.json`.
