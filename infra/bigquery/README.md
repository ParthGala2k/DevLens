# BigQuery — datasets & derived views

Fivetran lands raw connector data into per-source datasets (`github`, `jira`, `slack`, `calendar`,
`pagerduty`). We build **derived views** in `${BIGQUERY_DATASET_METRICS}` (default `devlens_metrics`)
that the agent + dashboard query.

| View | Powers |
|---|---|
| `pr_review_lag` | Dashboard PR review lag; blocked-PR alerts |
| `deep_work_blocks` | Deep work vs meeting fragmentation |
| `estimation_accuracy` | Ticket over/underestimation per sprint |
| `oncall_noise` | On-call noise trends (PagerDuty) |
| `developer_load` | Per-dev load score (Workload Heatmap + bridge assignee suggestion) |
| `completion_reliability` | Per-dev completion reliability (Reliability Table) |
| `actionable_threads` | Slack/Jira threads that may imply work (discussion→repo bridge input) |

The `.sql` files use `${VAR}` placeholders matching `.env`. Apply with `make bq-views` (TODO:
substitutes vars and runs `bq query --use_legacy_sql=false`). Column/table names are placeholders
until the real Fivetran schemas are confirmed (Phase 1).
