# Sprint Mirror / DevLens

> **Developer Productivity Blind Spot Agent** — built for the **Google Cloud Rapid Agent Hackathon (Fivetran track)**.

Connect GitHub, Jira, Google Calendar, and PagerDuty once. **Fivetran** syncs the data into
**BigQuery**, and a **Gemini 3** agent (on **Google Cloud Agent Builder / ADK**) proactively surfaces
your developer-productivity blind spots through a live web dashboard:

- *"PR #247 has been waiting for review for 4 days — same person blocked you last sprint too."*
- *"You have 3 tickets this sprint you've historically underestimated by 2x."*
- *"Tuesday had 6 meetings back to back — you had zero deep-work blocks."*

The dashboard shows the **agent reasoning and every Fivetran MCP call in real time**, so the partner
integration is visually obvious during the demo.

---

## Architecture at a glance

```
GitHub / Jira / Calendar / PagerDuty
        │  (Fivetran connectors)
        ▼
     BigQuery  ──────────►  Gemini 3 Agent (ADK)  ──────►  FastAPI (SSE streams)  ──────►  Next.js dashboard
     (analytics)             ├─ BigQuery tools                ├─ /chat   (agent events)        ├─ Sprint Health
                             ├─ Fivetran MCP tools            ├─ /alerts (proactive feed)      ├─ Alert Feed
                             └─ analysis tools                ├─ /mcp-log (MCP activity)       ├─ Chat
        Firestore  ◄─────────────────────────────────────────┘  app state                     └─ MCP Activity Log
        (alerts, chat history, connector status, agent runs)
```

| Layer | Tech |
|---|---|
| Backend / API | Python 3.12 + FastAPI (async, SSE) |
| Agent | Google ADK + Gemini 3 (Vertex AI / Agent Builder) |
| Partner MCP | Fivetran MCP server |
| Analytics warehouse | BigQuery |
| App state | Firestore |
| Frontend | Next.js + TypeScript + Tailwind |
| Hosting | Cloud Run |

See [`docs/architecture.md`](docs/architecture.md) for the full design and roadmap.

---

## Repository layout

```
backend/    FastAPI app, ADK agent, services, integrations (BigQuery, Firestore, Fivetran MCP)
frontend/   Next.js dashboard (data sync, sprint health, alerts, chat, MCP activity log)
shared/     contracts/ — JSON schemas shared between backend (pydantic) and frontend (TS)
infra/      BigQuery DDL/views, Firestore rules, Cloud Run deploy, setup scripts
docs/       architecture, data model, MCP integration, demo script
```

---

## Getting started (local)

> Prerequisites: Python 3.12, Node 20+, Docker, and (for live data) a GCP project + Fivetran account.

```bash
cp .env.example .env          # fill in GCP project, dataset ids, Fivetran MCP endpoint
make dev                      # backend + frontend + Firestore emulator via docker-compose
```

- Backend: http://localhost:8000  (docs at `/docs`)
- Frontend: http://localhost:3000

See `Makefile` for individual targets (`make backend`, `make frontend`, `make deploy`).

---

## Hackathon

- **Event:** Google Cloud Rapid Agent Hackathon
- **Track:** Fivetran
- **Deadline:** 2026-06-11 @ 2:00pm PDT
- **Required:** Google Cloud Agent Builder + Gemini 3 + Fivetran MCP server (partner integration)

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
