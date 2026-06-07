# CLAUDE.md — Project Guide for Claude Code

This file orients any Claude Code session working in this repo. Keep it current as the project evolves.

## What this is

**Sprint Mirror / DevLens** — a Developer Productivity Blind Spot Agent for the **Google Cloud Rapid
Agent Hackathon (Fivetran track)**, due **2026-06-11 @ 2:00pm PDT**.

A Gemini 3 agent (Google ADK / Agent Builder) analyzes developer data that **Fivetran** syncs into
**BigQuery** (GitHub, Jira, Google Calendar, PagerDuty), and surfaces productivity blind spots through
a Next.js dashboard that shows agent reasoning + every Fivetran MCP call in real time.

The full design and roadmap live in `docs/architecture.md`.

## Stack

- **Backend:** Python 3.12, FastAPI (async, Server-Sent Events for streaming).
- **Agent:** Google ADK + Gemini 3 (Vertex AI / Agent Builder).
- **Partner MCP:** Fivetran MCP server (mandatory hackathon integration).
- **Analytics warehouse:** BigQuery (Fivetran sync target).
- **App state:** Firestore (alerts, chat history, connector status, agent run cache).
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind; Recharts for charts.
- **Hosting:** Cloud Run (backend + frontend).

## Repository layout

```
backend/app/
  api/routes/      thin HTTP controllers (connectors, dashboard, alerts, chat, mcp_log)
  api/schemas/     pydantic request/response DTOs
  agent/           ADK agent: agent.py, runner.py, events.py, tools/, prompts/
  services/        business logic — agent & jobs call these, NOT routes
  integrations/    external I/O: bigquery_client, firestore_client, mcp/
  domain/          entities (alert, metric, connector, chat)
  events/bus.py    in-process pub/sub fanned out to SSE channels
  jobs/            background tasks (alert_scanner)
frontend/src/
  app/             Next.js App Router pages
  components/      data-sync, dashboard, alerts, chat, mcp-log, ui
  features/        per-feature hooks + client logic
  lib/             api-client, sse, types
shared/contracts/  JSON schemas shared by backend (pydantic) + frontend (TS)
infra/             bigquery/ (DDL + metric views), firestore/, cloudrun/, scripts/
docs/              architecture, data-model, mcp-integration, demo-script
```

## Architectural conventions

- **Layering:** `api` (thin) → `services` (logic) → `integrations` (I/O). Never call integrations
  directly from routes; never put business logic in routes. The agent and jobs reuse `services`.
- **Events are first-class:** one `events/bus.py` fans out to three SSE channels (chat, alerts,
  mcp_log). `integrations/mcp/activity_log.py` wraps every MCP call so the UI MCP log is automatic —
  do not hand-instrument individual MCP calls.
- **Contracts shared:** event/DTO shapes are defined once in `shared/contracts/*.json`. Backend
  pydantic models and frontend TS types both derive from these — keep them in sync.
- **Secrets:** never hardcode. Config comes from env via `backend/app/config.py` (pydantic-settings).
  See `.env.example` for the full list of variables.

## Common commands

```bash
make dev        # backend + frontend + Firestore emulator (docker-compose)
make backend    # run FastAPI locally (uvicorn)
make frontend   # run Next.js dev server
make test       # backend pytest
make deploy     # build + deploy both services to Cloud Run
```

## Status

Skeleton scaffolded (Phase 0a). Modules are stubs awaiting implementation — see the phased roadmap in
`docs/architecture.md`. Credentials (GCP project, Fivetran account + connectors, Fivetran MCP endpoint)
are required before Phase 1 (real data + MCP plumbing).
