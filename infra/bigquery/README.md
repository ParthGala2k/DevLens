# BigQuery — datasets & derived views

Fivetran lands raw connector data into per-source datasets (`github`, `jira`, `calendar`,
`pagerduty`). We build **derived metric views** in `${BIGQUERY_DATASET_METRICS}` (default
`devlens_metrics`) that the agent + dashboard query.

| View | Powers |
|---|---|
| `pr_review_lag` | Dashboard PR review lag; blocked-PR alerts |
| `deep_work_blocks` | Deep work vs meeting fragmentation |
| `estimation_accuracy` | Ticket over/underestimation per sprint |
| `oncall_noise` | On-call noise trends (PagerDuty) |

The `.sql` files use `${VAR}` placeholders matching `.env`. Apply with `make bq-views` (TODO:
substitutes vars and runs `bq query --use_legacy_sql=false`). Column/table names are placeholders
until the real Fivetran schemas are confirmed (Phase 1).
