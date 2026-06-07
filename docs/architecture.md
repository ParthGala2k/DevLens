# Architecture — Sprint Mirror / DevLens

## Problem
Engineers lack visibility into their own productivity blind spots: PRs that quietly sit waiting
for review, sprints stuffed with historically underestimated tickets, and days fragmented into
back-to-back meetings with no deep-work time. The signals exist across GitHub, Jira, Calendar, and
PagerDuty — but never in one place, and never proactively surfaced.

## Solution
A Gemini 3 agent reasons over all four sources (synced by **Fivetran** into **BigQuery**) and
proactively surfaces blind spots through a web dashboard. The dashboard deliberately exposes the
agent's reasoning and **every Fivetran MCP call** in real time — both as a UX feature and as clear
evidence of the partner integration for hackathon judging.

Built for the **Google Cloud Rapid Agent Hackathon — Fivetran track** (due 2026-06-11).

## System diagram
```
GitHub / Jira / Calendar / PagerDuty
        │  Fivetran connectors
        ▼
     BigQuery (raw + derived metric views)
        │
        ▼
   Gemini 3 Agent (Google ADK)
     ├─ BigQuery tools      ─┐
     ├─ Fivetran MCP tools   │ every MCP call → activity tap → event bus
     └─ analysis tools       │
        │                    │
        ▼                    ▼
   FastAPI backend ── event bus ──► SSE: /chat, /alerts, /mcp-log
        │  (services + integrations)
        ▼
   Next.js dashboard
     ├─ Data Sync Panel        ├─ Alert Feed
     ├─ Sprint Health charts    ├─ Chat (visible tool calls)
     └─ MCP Activity Log (live)

   Firestore: connectors, alerts, chat_sessions, agent_runs
```

## Layers (backend)
- **api/** — thin FastAPI controllers; no business logic.
- **services/** — business logic; reused by routes, the agent, and background jobs.
- **integrations/** — external I/O (BigQuery, Firestore, Fivetran MCP).
- **agent/** — ADK agent definition, tools, runner, event normalization.
- **events/** — in-process pub/sub fanned out to three SSE channels.
- **jobs/** — periodic proactive alert scanner.

## Key design decisions
1. **MCP activity tap** (`integrations/mcp/activity_log.py`) wraps every MCP call, so the
   judge-visible MCP log is automatic — never hand-instrumented per call.
2. **One event bus, three streams** keeps real-time plumbing uniform across chat, alerts, MCP log.
3. **Shared contracts** (`shared/contracts/*.json`) prevent backend/frontend drift.
4. **Firestore for app state, BigQuery for analytics** — transactional writes + real-time
   listeners on one side, heavy analytical queries on the other.

## Roadmap (5-day sprint)
| Phase | Focus |
|---|---|
| 0a | Scaffold skeleton (done) |
| 0 | GCP + Fivetran connectors + deploy pipeline |
| 1 | BigQuery metric views + MCP plumbing + clients |
| 2 | ADK agent + tools + event streaming |
| 3 | Backend API + SSE |
| 4 | Frontend dashboard + chat + MCP log |
| 5 | Proactive alerts, polish, demo video, Devpost submission |

See the full plan in the planning file and `CLAUDE.md` for conventions.
