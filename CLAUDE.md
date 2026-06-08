# CLAUDE.md — Project Guide for Claude Code

This file orients any Claude Code session working in this repo. Keep it current as the project evolves.

## What this is

**DevLens** — a developer-productivity agent for the **Google Cloud Rapid Agent
Hackathon (Fivetran track)**, due **2026-06-11 @ 2:00pm PDT**.

A Gemini 3 agent (Google ADK / Agent Builder) works over team data that **Fivetran** syncs into
**BigQuery** (GitLab, Jira, Slack, Google Calendar, PagerDuty). It does two things:

1. **Discussion → repo bridge:** detects when a Slack/Jira thread implies undone work, drafts a GitLab
   issue, and — after **human approval** — files it via the **GitLab MCP server**.
2. **Developer observability:** per-dev load score + completion reliability, plus the classic blind
   spots (MR review lag, deep work vs meetings, estimation accuracy, on-call noise).

The Next.js dashboard streams the agent's reasoning and every MCP call (Fivetran + GitLab) live.
Full design + roadmap: `docs/architecture.md`.

## Stack

- **Backend:** Python 3.12, FastAPI (async, Server-Sent Events for streaming).
- **Agent:** Google ADK + Gemini 3 (Vertex AI / Agent Builder).
- **MCP servers:** Fivetran (sync — mandatory track integration) + GitLab (action — file issues).
- **Analytics warehouse:** BigQuery (Fivetran sync target).
- **App state:** Firestore (alerts, issue proposals, chat history, connector status, agent runs).
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind; Recharts for charts.
- **Hosting:** Cloud Run (backend + frontend).

**Data sources (Fivetran → BigQuery):** GitLab, Jira, Slack, Calendar, PagerDuty.

## Repository layout

```
backend/app/
  api/routes/      thin HTTP controllers (connectors, dashboard, team, bridge, alerts, chat, mcp_log)
  api/schemas/     pydantic request/response DTOs
  agent/           ADK agent: agent.py, runner.py, events.py, prompts/,
                   tools/ (bigquery_tools, fivetran_mcp, gitlab_mcp, bridge_tools, analysis_tools)
  services/        business logic — agent & jobs call these, NOT routes
                   (metrics, workload, bridge, alerts, chat, connectors)
  integrations/    external I/O: bigquery_client, firestore_client,
                   mcp/ (session, activity_log, fivetran_client, gitlab_client)
  domain/          entities (alert, metric, connector, chat, issue_proposal, developer)
  events/bus.py    in-process pub/sub fanned out to SSE channels
  jobs/            background tasks (alert_scanner, bridge_scanner)
frontend/src/
  app/             Next.js App Router pages
  components/      data-sync, dashboard, team, bridge, alerts, chat, mcp-log, ui
  features/        per-feature hooks + client logic
  lib/             api-client, sse, types
shared/contracts/  JSON schemas shared by backend (pydantic) + frontend (TS)
infra/             bigquery/ (DDL + metric views), firestore/, cloudrun/, scripts/
docs/              architecture, data-model, data-pipeline (bring-up runbook), mcp-integration, demo-script
```

## Architectural conventions

- **Layering:** `api` (thin) → `services` (logic) → `integrations` (I/O). Never call integrations
  directly from routes; never put business logic in routes. The agent and jobs reuse `services`.
- **Events are first-class:** one `events/bus.py` fans out to SSE channels (chat, alerts, bridge,
  mcp_log). `integrations/mcp/activity_log.py` wraps every MCP call (Fivetran **and** GitLab) so the
  UI MCP log is automatic — do not hand-instrument individual MCP calls. Use
  `tap(action, server="fivetran"|"gitlab", connector=...)`.
- **Human-in-the-loop for writes:** the agent *proposes* GitLab issues into `issue_proposals`; a human
  approves before `gitlab_client.create_issue` runs. Don't auto-file.
- **Contracts shared:** event/DTO shapes are defined once in `shared/contracts/*.json`. Backend
  pydantic models and frontend TS types both derive from these — keep them in sync.
- **Secrets:** never hardcode. Config comes from env via `backend/app/config.py` (pydantic-settings).
  See `.env.example` for the full list of variables.

## Git conventions

- **Commit under your own git identity.** Each contributor sets their own `user.name` / `user.email`
  via *local* git config (`git config user.email "you@example.com"`) — never hardcode anyone's personal
  email in committed files. (Personal overrides can go in the gitignored `CLAUDE.local.md`.)
- **Do NOT add a `Co-Authored-By: Claude ...` trailer** (or any AI co-author line) to commit messages.

## Common commands

```bash
make dev        # backend + frontend + Firestore emulator (docker-compose)
make backend    # run FastAPI locally (uvicorn)
make frontend   # run Next.js dev server
make test       # backend pytest
make deploy     # build + deploy both services to Cloud Run
```

## Status

Skeleton scaffolded; extended for the discussion→repo bridge + developer observability + GitLab MCP.
Modules are documented stubs awaiting implementation — see the phased roadmap in `docs/architecture.md`.
Credentials (GCP project, Fivetran account + connectors, Fivetran MCP endpoint, GitLab MCP endpoint +
token) are required before Phase 1 (real data + MCP plumbing).
