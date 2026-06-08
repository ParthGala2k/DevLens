# Architecture — Sprint Mirror / DevLens

## Problem
Two recurring frictions on engineering teams:
1. **Discussion never becomes tracked work.** Decisions and bugs surface in Slack/Jira threads, and
   someone has to remember to hand-create the GitLab issue. Things fall through the cracks.
2. **Load and reliability are invisible.** Nobody has a clear, cross-source picture of who's
   overloaded, whose MRs are stuck, or who consistently delivers vs lags — so work piles unevenly.

The signals exist across GitLab, Jira, Slack, Calendar, and PagerDuty, but never joined in one place.

## Solution
A Gemini 3 agent reasons over all sources (synced by **Fivetran** into **BigQuery**) and:
- **Bridges discussion → repo:** drafts a GitLab issue from an actionable thread, suggests the
  least-loaded assignee, and files it via the **GitLab MCP server** *after a human approves*.
- **Surfaces blind spots + load:** MR review lag, deep work vs meetings, estimation accuracy, on-call
  noise, plus per-dev load and completion reliability.

The dashboard deliberately exposes the agent's reasoning and **every MCP call** (Fivetran + GitLab) in
real time — both a UX feature and clear evidence of the partner integration for judging.

Built for the **Google Cloud Rapid Agent Hackathon — Fivetran track** (due 2026-06-11).
**Two MCP servers, one story:** Fivetran for cross-source history & observability; GitLab MCP for
real-time action.

## System diagram
```
GitLab / Jira / Slack / Calendar / PagerDuty
        │  Fivetran connectors
        ▼
     BigQuery (raw + derived views: mr_review_lag, developer_load,
        │                          completion_reliability, actionable_threads, ...)
        ▼
   Gemini 3 Agent (Google ADK)
     ├─ BigQuery tools       ─┐
     ├─ Fivetran MCP (sync)   │ every MCP call → activity tap → event bus
     ├─ GitLab MCP (action)   │
     ├─ bridge tools          │
     └─ analysis tools        │
        │                     ▼
        ▼              FastAPI ── event bus ──► SSE: /chat, /alerts, /bridge, /mcp-log
   issue_proposals (Firestore)   (services + integrations)
        │                     │
        ▼                     ▼
   Next.js dashboard
     ├─ Data Sync Panel          ├─ Proposal Queue (approve → GitLab MCP files it)
     ├─ Sprint Health charts     ├─ Team Workload + Reliability
     ├─ Alert Feed               └─ MCP Activity Log (Fivetran + GitLab, live)
     └─ Chat (visible tool calls)

   Firestore: connectors, alerts, issue_proposals, chat_sessions, agent_runs
```

## Two core flows

### A. Discussion → repo bridge
```
Slack/Jira (Fivetran → BigQuery actionable_threads)
  → bridge_scanner (periodic; accepts Fivetran batch latency)
  → agent classifies actionable + drafts issue + suggests least-loaded assignee
  → Firestore issue_proposals (pending)  ──SSE──► Proposal Queue UI
  → human Approve (may edit)             ← human-in-the-loop by design
  → GitLab MCP create_issue + assign + label + link back to thread
```
Human approval builds trust, prevents duplicate/garbage issues, and is a strong demo beat. Optional
dedup via BigQuery `VECTOR_SEARCH` before proposing.

### B. Developer observability
- **Load score** (`developer_load`): open issues + points in flight + MRs awaiting review + on-call +
  meeting hours → Workload Heatmap, and feeds the bridge's assignee suggestion.
- **Reliability** (`completion_reliability`): assigned-vs-completed, cycle time, on-time %, churn per
  dev per sprint → Reliability Table.

## Layers (backend)
- **api/** — thin FastAPI controllers; no business logic.
- **services/** — business logic; reused by routes, the agent, and background jobs.
- **integrations/** — external I/O (BigQuery, Firestore, Fivetran MCP, GitLab MCP).
- **agent/** — ADK agent definition, tools, runner, event normalization.
- **events/** — in-process pub/sub fanned out to SSE channels.
- **jobs/** — `alert_scanner` (blind-spot alerts) + `bridge_scanner` (issue proposals).

## Key design decisions
1. **One activity tap, two MCP servers** (`integrations/mcp/activity_log.py`) — wraps every Fivetran
   and GitLab call so the judge-visible MCP log is automatic.
2. **Human-in-the-loop writes** — the agent proposes, a human approves, only then GitLab is written.
3. **One event bus, many streams** keeps real-time plumbing uniform (chat, alerts, bridge, mcp_log).
4. **Shared contracts** (`shared/contracts/*.json`) prevent backend/frontend drift.
5. **Firestore for app state, BigQuery for analytics** — transactional writes + real-time listeners on
   one side, heavy analytical queries on the other.
6. **Elasticsearch intentionally omitted** — BigQuery handles analytics; `VECTOR_SEARCH` covers
   semantic dedup if needed, without an extra system.

## Track strategy
One project competes in **one track and wins at most one prize** (hackathon rule). We compete on
**Fivetran**; **GitLab MCP** is a second integration that strengthens the entry, not a second prize.
Source code may live on GitHub — the GitLab MCP operates on a GitLab project at runtime.

## Roadmap (remaining)
| Phase | Focus |
|---|---|
| 1 | BigQuery views + MCP plumbing (Fivetran + GitLab clients) + BQ/Firestore clients |
| 2 | ADK agent + tools + bridge brain (classify/draft/assign) + event streaming |
| 3 | Backend API + SSE (connectors, dashboard, team, bridge, alerts, chat, mcp_log) |
| 4 | Frontend (sync, health, workload/reliability, proposal queue, chat, MCP log) |
| 5 | Proactive scanners (alerts + bridge), dedup, polish |
| 6 | Deploy to Cloud Run, demo video, Devpost submission |

See `CLAUDE.md` for conventions.
