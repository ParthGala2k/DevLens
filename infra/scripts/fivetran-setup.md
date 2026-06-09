# Fivetran setup (Phase 0/1)

1. Create a Fivetran account and a **destination** pointing at this GCP project's BigQuery.
2. Add five **connectors**, each into its own dataset:
   - GitHub → dataset `github`   (repo of record: PRs, issues — demo repo: itsRenuka22/stealth-labs-platform)
   - Jira → dataset `jira`       (demo project: SLS at sjsu-team-devlens.atlassian.net)
   - Slack → dataset `slack`     (team discussion — bridge input)
   - Google Calendar → dataset `calendar`
   - PagerDuty → dataset `pagerduty`
3. Run an initial sync; confirm tables land in BigQuery.
4. Inspect the actual schemas and update `infra/bigquery/sql/*.sql` column/table names.
5. Note the **Fivetran MCP server** endpoint + API key/secret and group id → put in `.env`
   (`FIVETRAN_MCP_URL`, `FIVETRAN_API_KEY`, `FIVETRAN_API_SECRET`, `FIVETRAN_GROUP_ID`).

## GitHub MCP (action layer — separate from Fivetran)
Fivetran *reads* GitHub history; the **GitHub MCP server** *writes* (creates issues from the
bridge). Configure separately in `.env`:
- `GITHUB_MCP_URL`, `GITHUB_TOKEN` (PAT with `repo` scope), `GITHUB_REPO` (e.g. `itsRenuka22/stealth-labs-platform`).

> Connectors have the longest lead time (initial syncs + OAuth). Start this first.
