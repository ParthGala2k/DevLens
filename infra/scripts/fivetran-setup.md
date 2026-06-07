# Fivetran setup (Phase 0/1)

1. Create a Fivetran account and a **destination** pointing at this GCP project's BigQuery.
2. Add four **connectors**, each into its own dataset:
   - GitHub  → dataset `github`
   - Jira    → dataset `jira`
   - Google Calendar → dataset `calendar`
   - PagerDuty → dataset `pagerduty`
3. Run an initial sync; confirm tables land in BigQuery.
4. Inspect the actual schemas and update `infra/bigquery/sql/*.sql` column/table names.
5. Note the **Fivetran MCP server** endpoint + API key/secret and group id → put in `.env`
   (`FIVETRAN_MCP_URL`, `FIVETRAN_API_KEY`, `FIVETRAN_API_SECRET`, `FIVETRAN_GROUP_ID`).

> Connectors have the longest lead time (initial syncs + OAuth). Start this first.
