# DevLens

> **Developer Productivity Agent** — built for the **Google Cloud Rapid Agent Hackathon (Fivetran track)**.

Connect your team's tools once. **Fivetran** syncs the data into **BigQuery**, and a **Gemini 3**
agent (Google ADK / Vertex AI) does two things:

1. **Bridges discussion → code.** When a Slack or Jira thread implies undone work, the agent drafts a
   GitHub issue (title, body, labels, suggested assignee) and — after a **human approves** — files it
   via the **GitHub MCP server**. No more manually turning conversations into tickets.
2. **Surfaces team blind spots & load.** PR review lag, deep-work vs meeting fragmentation, estimation
   accuracy, on-call noise — plus a **developer observability** layer: who's overloaded and who
   consistently delivers vs lags, so work is distributed fairly.

The dashboard streams the **agent's reasoning and every MCP call (Fivetran + GitHub) in real time**, so
the partner integration is visually obvious during the demo.

> **Two MCP servers, one story:** *Fivetran for cross-source history & observability, GitHub MCP for
> real-time action.* Both flow through the same activity tap — both appear in the live MCP log.

---

## Architecture

```
GitHub / Jira / Slack / Calendar / PagerDuty
        │  (Fivetran connectors)
        ▼
     BigQuery  ──────────►  Gemini 3 Agent (ADK)  ──────►  FastAPI (SSE)  ──────►  Next.js dashboard
     (analytics)             ├─ BigQuery tools                ├─ /chat                 ├─ Data Sync Panel
                             ├─ Fivetran MCP (sync)           ├─ /bridge               ├─ Sprint Health charts
                             ├─ GitHub MCP (action)           ├─ /alerts               ├─ Team Workload + Reliability
                             └─ bridge / analysis tools       └─ /mcp-log              ├─ Proposal Queue
                                                                                        ├─ Alert Feed
        Firestore  ◄── app state (connectors, alerts, issue_proposals, chat history)   ├─ Chat
                                                                                        └─ MCP Activity Log
```

| Layer | Tech |
|---|---|
| Backend / API | Python 3.12 + FastAPI (async, Server-Sent Events) |
| Agent | Google ADK + Gemini 3 (Vertex AI) |
| Partner MCP — sync | Fivetran MCP server (`https://mcp.fivetran.com/mcp`) |
| Second MCP — action | GitHub MCP server (Docker, `ghcr.io/github/github-mcp-server`) |
| Analytics warehouse | BigQuery (Fivetran sync target) |
| App state | Firestore (+ local emulator for dev) |
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + Recharts |
| Hosting | Cloud Run |

---

## Repository layout

```
backend/app/
  api/routes/        thin HTTP controllers (connectors, dashboard, team, bridge, alerts, chat, mcp_log)
  agent/             ADK agent definition, runner, event normalizer, tools/
  services/          business logic (metrics, workload, bridge, alerts, chat, connectors)
  integrations/      external I/O — bigquery_client, firestore_client, mcp/ (session, activity_log,
                     fivetran_client, github_client)
  events/bus.py      in-process pub/sub → SSE channels
  domain/            pydantic models (alert, metric, connector, issue_proposal, developer)
frontend/src/
  app/               Next.js App Router pages (dashboard, chat)
  components/        data-sync, dashboard, team, bridge, alerts, chat, mcp-log, ui
  lib/               api-client, sse, types
shared/contracts/    JSON schemas shared by backend (pydantic) and frontend (TypeScript)
infra/               bigquery/ (DDL + metric views), cloudrun/, scripts/
docs/                architecture, data-model, data-pipeline (runbook), mcp-integration
```

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker Desktop | latest | runs the full local stack |
| Python | 3.12 | backend (if running outside Docker) |
| Node.js | 20+ | frontend (if running outside Docker) |
| GCP project | — | Vertex AI, BigQuery, Firestore |
| Fivetran account | — | connectors → BigQuery |
| GitHub PAT | `repo` scope | GitHub MCP server |

---

## Local setup

### 1. Clone and configure

```bash
git clone <repo-url>
cd DevLens
cp .env.example .env
```

Edit `.env` and fill in every value (see the table below).

### 2. Place your GCP service account key

Download a JSON key for your GCP service account and save it as:

```
DevLens/
├── service-account.json    ← here, next to docker-compose.yml
├── .env
├── docker-compose.yml
└── ...
```

`.env` should reference it as:

```
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

### 3. Start the GitHub MCP server

```powershell
docker run -d --name github-mcp -p 8082:8082 `
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_pat> `
  ghcr.io/github/github-mcp-server http --port 8082
```

Then set in `.env`:

```
GITHUB_MCP_URL=http://host.docker.internal:8082
GITHUB_TOKEN=<your_github_pat>
```

### 4. Start the full stack

```bash
docker compose up
```

| Service | URL |
|---|---|
| Frontend dashboard | http://localhost:3000 |
| Backend API + docs | http://localhost:8000 / http://localhost:8000/docs |
| Firestore emulator | http://localhost:8080 |

The app loads with **demo data immediately** — no Fivetran sync required to see the UI working.

---

## Environment variables

| Variable | Example | Description |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | `my-project-id` | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex AI region |
| `GOOGLE_APPLICATION_CREDENTIALS` | `./service-account.json` | Path to GCP service account key |
| `GOOGLE_GENAI_USE_VERTEXAI` | `1` | Use Vertex AI (1) vs AI Studio (0) |
| `GEMINI_MODEL` | `gemini-3-pro` | Gemini model ID |
| `BIGQUERY_PROJECT` | `my-project-id` | BQ project (usually same as GCP project) |
| `BIGQUERY_DATASET_METRICS` | `devlens_metrics` | Dataset for derived metric views |
| `FIRESTORE_PROJECT` | `my-project-id` | Firestore project |
| `FIVETRAN_MCP_URL` | `https://mcp.fivetran.com/mcp` | Fivetran MCP endpoint |
| `FIVETRAN_API_KEY` | `...` | Fivetran API key |
| `FIVETRAN_API_SECRET` | `...` | Fivetran API secret |
| `FIVETRAN_GROUP_ID` | `...` | Fivetran destination group ID (from dashboard URL) |
| `GITHUB_MCP_URL` | `http://host.docker.internal:8082` | GitHub MCP server URL |
| `GITHUB_TOKEN` | `ghp_...` | GitHub PAT with `repo` scope |
| `GITHUB_REPO` | `itsRenuka22/stealth-labs-platform` | Demo repo (owner/repo) |

> **Finding `FIVETRAN_GROUP_ID`:** Fivetran dashboard → Destinations → click your destination → copy the ID from the URL, or call `GET https://api.fivetran.com/v1/groups` with Basic auth.

---

## Fivetran → BigQuery setup

1. Create a **BigQuery destination** in Fivetran → point at your GCP project (single region, e.g. `US`).
2. Add connectors and set destination datasets:

| Connector | Dataset |
|---|---|
| GitHub (`itsRenuka22/stealth-labs-platform`) | `github` |
| Jira (project key: `SLS`) | `jira` |
| Slack | `slack` |
| Google Calendar | `calendar` |
| PagerDuty | `pagerduty` |

3. Trigger initial sync — Fivetran auto-creates all tables.
4. Apply the derived metric views:

```bash
make bq-views
```

5. Update `BIGQUERY_DATASET_*` values in `.env` to match.

---

## Running without Docker

**Backend:**

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## How the demo story works

1. Fivetran syncs GitHub, Jira, Slack, Calendar, PagerDuty into BigQuery.
2. The agent reads BigQuery views and surfaces blind spots on the dashboard.
3. It detects a Slack/Jira thread that implies undone work → drafts a GitHub issue → adds it to the **Proposal Queue**.
4. A human reviews the proposal (can edit title, assignee, labels) and clicks **Approve**.
5. The agent calls the GitHub MCP server → issue is filed in `itsRenuka22/stealth-labs-platform`.
6. Every Fivetran and GitHub MCP call appears live in the **MCP Activity Log** panel — the judge-visible integration evidence.

---

## Makefile targets

```bash
make dev        # docker compose up (backend + frontend + Firestore emulator)
make backend    # uvicorn dev server only
make frontend   # Next.js dev server only
make test       # backend pytest
make lint       # ruff (backend) + eslint (frontend)
make bq-views   # apply BigQuery metric views
make deploy     # Cloud Run deploy (backend + frontend)
```

---

## Hackathon

- **Event:** Google Cloud Rapid Agent Hackathon
- **Track:** Fivetran (one project = one track)
- **Deadline:** 2026-06-11 @ 2:00pm PDT
- **Required integrations:** Google Cloud ADK + Gemini 3 + Fivetran MCP (partner) + GitHub MCP (action)
- **Demo repo:** `itsRenuka22/stealth-labs-platform`
- **Jira project:** `SLS` (sjsu-team-devlens.atlassian.net)

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
