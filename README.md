# DevLens

> **Developer Productivity Agent** — built for the **Google Cloud Rapid Agent Hackathon (Fivetran track)**.

Connect your team's tools once. **Fivetran** syncs the data into **BigQuery**, and a **Gemini 3**
agent (on **Google Cloud Agent Builder / ADK**) does two things:

1. **Bridges discussion → code.** When a Slack or Jira thread implies undone work, the agent drafts a
   GitLab issue (title, body, labels, suggested assignee) and — after a **human approves** — files it
   via the **GitLab MCP server**. No more manually turning conversations into tickets.
2. **Surfaces team blind spots & load.** MR review lag, deep-work vs meeting fragmentation, estimation
   accuracy, on-call noise — plus a **developer observability** layer: who's overloaded and who
   consistently delivers vs lags, so work is distributed fairly.

The dashboard streams the **agent's reasoning and every MCP call (Fivetran + GitLab) in real time**, so
the partner integration is visually obvious during the demo.

> **Two MCP servers, one story:** *Fivetran for cross-source history & observability, GitLab MCP for
> real-time action.* Both flow through the same activity tap, so both appear in the live MCP log.

---

## Architecture at a glance

```
GitLab / Jira / Slack / Calendar / PagerDuty
        │  (Fivetran connectors)
        ▼
     BigQuery  ──────────►  Gemini 3 Agent (ADK)  ──────►  FastAPI (SSE streams)  ──────►  Next.js dashboard
     (analytics)             ├─ BigQuery tools                ├─ /chat    (agent events)       ├─ Sprint Health
                             ├─ Fivetran MCP (sync)           ├─ /bridge  (issue proposals)    ├─ Team Workload + Reliability
                             ├─ GitLab MCP (action)           ├─ /team    (workload)           ├─ Proposal Queue (approve→file)
                             └─ bridge / analysis tools       ├─ /alerts  (proactive feed)     ├─ Chat
                                                              └─ /mcp-log (MCP activity)        └─ MCP Activity Log (Fivetran+GitLab)
        Firestore  ◄── app state: connectors, alerts, issue_proposals, chat history, agent runs
```

| Layer | Tech |
|---|---|
| Backend / API | Python 3.12 + FastAPI (async, SSE) |
| Agent | Google ADK + Gemini 3 (Vertex AI / Agent Builder) |
| Partner MCP (sync) | Fivetran MCP server |
| Second MCP (action) | GitLab MCP server |
| Analytics warehouse | BigQuery |
| App state | Firestore |
| Frontend | Next.js + TypeScript + Tailwind |
| Hosting | Cloud Run |

See [`docs/architecture.md`](docs/architecture.md) for the full design and roadmap.

---

## Repository layout

```
backend/    FastAPI app, ADK agent, services, integrations (BigQuery, Firestore, Fivetran + GitLab MCP)
frontend/   Next.js dashboard (data sync, sprint health, team observability, proposal queue, chat, MCP log)
shared/     contracts/ — JSON schemas shared between backend (pydantic) and frontend (TS)
infra/      BigQuery DDL/views, Firestore rules, Cloud Run deploy, setup scripts
docs/       architecture, data model, MCP integration, demo script
```

---

## Getting started (local)

> Prerequisites: Python 3.12, Node 20+, Docker, and (for live data) a GCP project + Fivetran account + a GitLab project.

```bash
cp .env.example .env          # fill in GCP project, dataset ids, Fivetran + GitLab MCP endpoints
make dev                      # backend + frontend + Firestore emulator via docker-compose
```

- Backend: http://localhost:8000  (docs at `/docs`)
- Frontend: http://localhost:3000

See `Makefile` for individual targets (`make backend`, `make frontend`, `make deploy`).

---

## Hackathon

- **Event:** Google Cloud Rapid Agent Hackathon
- **Track:** Fivetran (one project = one track = one prize; GitLab MCP strengthens the entry)
- **Deadline:** 2026-06-11 @ 2:00pm PDT
- **Required:** Google Cloud Agent Builder + Gemini 3 + Fivetran MCP server (partner integration)

> Source can be hosted on GitHub; the GitLab MCP integration operates on a GitLab project at runtime,
> independent of where this code lives.

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
