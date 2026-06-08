# Data Pipeline & Bring-Up Runbook

How DevLens gets its data: from source tools → Fivetran → BigQuery → derived views → agent +
dashboard. Use this to divide work and bring the data layer up smoothly.

```
Source APIs → Fivetran connectors → raw datasets (Fivetran-managed schema)
                                      → devlens_metrics views (we design)
                                         → agent BigQuery tools + dashboard
```

---

## 1. Division of labor

| Owner | Responsibility |
|---|---|
| **Demo-data teammate** | Create the **GitLab project on gitlab.com** (NOT GitHub) and populate realistic activity. Hand over: project ID/path, a **personal access token (`api` scope)** for the GitLab MCP, and confirm Fivetran can reach it. |
| **Data/infra owner** | Fivetran account + BigQuery destination + connectors; the derived BigQuery views in `devlens_metrics`. |
| **Narrative owner** | Seed matching **Jira + Slack** demo data so a Slack/Jira thread maps to a GitLab issue (the bridge story). |

> **Code repo vs demo repo:** our source code lives on GitHub (`ParthGala2k/DevLens`). The **demo
> GitLab project** is separate and must be on GitLab, because both the Fivetran GitLab connector
> (reads history) and the GitLab MCP (creates issues) target it.

---

## 2. Fivetran → BigQuery setup

1. Create the Fivetran account.
2. Create a **BigQuery destination** in Fivetran → point at the GCP project. Fivetran's service
   account needs **BigQuery Data Editor + Job User**. Choose **one region** (e.g. `US`) and use it
   everywhere (destination + all datasets must match).
3. Add each **connector** and set its destination dataset:
   - GitLab → `gitlab`
   - Jira → `jira`
   - Slack → `slack`
   - Google Calendar → `calendar`
   - PagerDuty → `pagerduty`
4. Run the initial sync — **Fivetran auto-creates the tables**. Set frequency to the lowest available
   (~15 min) for the demo.
5. Capture the **Fivetran MCP** endpoint + API key/secret + group id → `.env`
   (`FIVETRAN_MCP_URL`, `FIVETRAN_API_KEY`, `FIVETRAN_API_SECRET`, `FIVETRAN_GROUP_ID`).
6. Capture **GitLab MCP** details → `.env` (`GITLAB_MCP_URL`, `GITLAB_TOKEN`, `GITLAB_PROJECT_ID`).

Confirm each connector exists in Fivetran's catalog when you start (versions vary).

---

## 3. The "indexing" reality (BigQuery)

- **Fivetran owns the raw schema** — it mirrors each source API into tables, handles incremental sync
  + schema drift, and adds `_fivetran_synced` / `_fivetran_deleted` columns. We **inspect** it after
  the first sync; we don't design it.
- **BigQuery has no traditional indexes.** Performance comes from **partitioning** (by date) +
  **clustering** (by key columns). At demo scale this is irrelevant — do not optimize.
- **Our layer = derived views** in `devlens_metrics` that join/transform raw tables into exactly what
  the agent + dashboard consume. These schemas are ours (see `infra/bigquery/sql/`).

---

## 4. Schemas

### Raw (Fivetran-managed — representative; confirm exact names after first sync)

| Dataset | Key tables (approx.) |
|---|---|
| `gitlab` | `merge_request` (iid, project_id, author_id, state, created_at, merged_at), `note`/`merge_request_note` (reviews/comments), `issue`, `pipeline`, `user`, `project`, `label` |
| `jira` | `issue` (key, status, assignee, **story_points** custom field, sprint, created, resolved), `comment`, `changelog`, `sprint`, `user` |
| `slack` | `message` (channel_id, user_id, text, ts, thread_ts, permalink), `channel`, `user` |
| `calendar` | `event` (id, summary, start, end, organizer), `attendee` |
| `pagerduty` | `incident` (service_id, created_at, resolved_at, urgency), `service`, `log_entry` |

### Derived (ours, in `devlens_metrics` — see `infra/bigquery/sql/`)

`mr_review_lag`, `deep_work_blocks`, `estimation_accuracy`, `oncall_noise`,
`developer_load`, `completion_reliability`, `actionable_threads`.
(Output shapes mirrored in `shared/contracts/workload.json`.)

> After the first sync, update the `${...}` placeholders and column/table names in the view SQL to
> match the real Fivetran schema.

---

## 5. Cross-source identity (decide before writing views)

A developer appears as `author_id` (GitLab), `assignee` (Jira), `user_id` (Slack), and an email
(Calendar). Per-dev load/reliability needs these unified.

**Recommended for the demo:** key on **email** where available, or keep a tiny seed mapping table
(canonical developer → per-source ids). This is the detail most likely to bite the observability
layer — settle it early.

---

## 6. Bring-up order (don't block on all five)

1. **GitLab + Jira + Slack** first — they drive the bridge and the headline demo.
2. **Calendar + PagerDuty** next — observability polish (deep work, on-call noise).

Build and test the views + agent against the first three while the rest sync.

---

## Status checklist

- [ ] GitLab demo project created + populated (teammate) → project id + PAT shared
- [ ] Jira + Slack demo data seeded (matching thread → issue)
- [ ] Fivetran account + BigQuery destination (single region)
- [ ] Connectors added (gitlab, jira, slack, calendar, pagerduty) + initial sync done
- [ ] Fivetran MCP + GitLab MCP creds in `.env`
- [ ] Raw schemas inspected; view SQL placeholders updated
- [ ] Identity mapping decided (email vs seed table)
- [ ] `devlens_metrics` views applied (`make bq-views`)
