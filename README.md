# DevLens

> **Developer Productivity Agent** — built for the **Google Cloud Rapid Agent Hackathon (Fivetran track)**, submitted 2026-06-11.

Connect your team's tools once. **Fivetran** syncs the data into **BigQuery**, and a **Gemini** agent (Google ADK / Vertex AI) does two things:

1. **Bridges discussion → code.** When a Jira thread implies undone work, the agent drafts a GitHub issue (title, body, suggested assignee) and — after a **human approves** — files it via the **GitHub MCP server**. No more manually turning conversations into tickets.
2. **Surfaces team blind spots & load.** PR review lag, deep-work vs meeting fragmentation, estimation accuracy, sprint completion prediction — plus a developer observability layer: who's overloaded and who consistently delivers vs lags.

The dashboard streams the **agent's reasoning and every MCP call (Fivetran + GitHub) in real time**, so the partner integration is visually obvious during the demo.

> **Two MCP servers, one story:** Fivetran for cross-source history & observability; GitHub MCP for real-time action. Both flow through the same activity tap and both appear in the live MCP log.

---

## Live deployment

| Service | URL |
|---|---|
| **Dashboard (submit this)** | https://devlens-frontend-942383800159.us-central1.run.app |
| **Backend API** | https://devlens-backend-942383800159.us-central1.run.app |
| Health check | https://devlens-backend-942383800159.us-central1.run.app/health |

GCP project: `dev-blindspot-agent` · Region: `us-central1`

---

## What's on the dashboard

| Panel | Data source | Notes |
|---|---|---|
| Sprint timeline banner | Jira `sprint` table | Active sprint name, start/end dates |
| Sprint completion prediction | Jira issues + story points | One-sentence forecast: velocity × days remaining → predicted % |
| Agent Insights | BigQuery scans on load | Proactive alerts: open PRs, meeting overload, workload spikes |
| Chat (Ask DevLens) | Live agent + BigQuery | Suggestion chips on first load; markdown-rendered streaming responses; visible tool calls |
| MCP Activity Log | Fivetran + GitHub MCP calls | Live feed; pulsing counter in the header |
| PR Review Lag | `pr_review_lag` view | Horizontal bar chart, green → amber → red by age |
| Deep Work Blocks | `deep_work_blocks` view | Calendar-aware coding-time analysis |
| Estimation Accuracy | `estimation_accuracy` view | Story-point promises vs delivery |
| Workload Heatmap | `developer_load` view | Per-developer load score |
| Reliability Table | `completion_reliability` view | Per-developer on-time delivery rate |
| Issue Proposal Queue | Firestore `issue_proposals` | Human-in-the-loop: Approve → GitHub MCP `create_issue` |
| Data Sources | Fivetran REST API | Connector status + "Sync Now" triggers |

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI (async), Server-Sent Events |
| Agent | Google ADK + Gemini (Vertex AI); data-driven mock agent fallback when Vertex AI is unavailable |
| MCP — sync (mandatory) | Fivetran MCP → REST API fallback |
| MCP — action | GitHub MCP → REST API fallback |
| Analytics | BigQuery (Fivetran sync target + `devlens_metrics` derived views) |
| App state | Firestore (alerts, issue proposals, chat sessions, connector status) |
| Frontend | Next.js 15 (App Router) + TypeScript + Tailwind CSS + Recharts |
| Hosting | Google Cloud Run (two services) |

---

## Data sources (Fivetran → BigQuery)

Three connectors are active and synced for this submission:

| Connector | BigQuery dataset | What it powers |
|---|---|---|
| GitHub (`itsRenuka22/stealth-labs-platform`) | `github` | PR review lag, workload, reliability |
| Jira (project `SLS`, sjsu-team-devlens.atlassian.net) | `jira` | Sprint health, estimation accuracy, bridge |
| Google Calendar | `google_calendar` | Deep work blocks, meeting overload alerts |

Derived metric views (`devlens_metrics` dataset): `pr_review_lag`, `developer_load`, `completion_reliability`, `deep_work_blocks`, `estimation_accuracy`, `actionable_threads`.

Apply/update views: `make bq-views`

---

## MCP integrations

All MCP calls go through a single activity tap in `backend/app/integrations/mcp/activity_log.py`. Every call — whether Fivetran sync or GitHub action — is automatically published to the `mcp_log` SSE channel, so the live log in the dashboard requires zero per-call instrumentation.

**Fivetran MCP** (`integrations/mcp/fivetran_client.py`)
- Tools: `sync_connector`, `connector_status`, `list_connectors`
- Triggered by user-initiated "Sync Now" and by the agent mid-reasoning
- Falls back to Fivetran REST API when no local MCP server is running (checked via `FIVETRAN_MCP_URL`)

**GitHub MCP** (`integrations/mcp/github_client.py`)
- Tools: `create_issue`, `assign_issue`, `add_labels`, `list_issues`
- Triggered **only** after a human approves a proposal in the Proposal Queue — never auto-filed
- Falls back to GitHub REST API

Live log events rendered in the dashboard:
```
[Fivetran MCP] → sync_connector(github)  → success
[GitHub MCP]   → create_issue            → success
```

---

## Architecture

```
GitHub / Jira / Google Calendar
        │  Fivetran connectors
        ▼
     BigQuery  (raw datasets)
        │
        ▼  devlens_metrics views
   Gemini Agent (Google ADK)
     ├─ bigquery_tools      ─┐
     ├─ fivetran_mcp (sync)  │  every call → activity_log.tap() → event bus
     ├─ github_mcp (action)  │
     ├─ bridge_tools         │
     └─ analysis_tools       │
        │                    ▼
        ▼              FastAPI  ──SSE──►  /api/chat/run/{run_id}/stream
   Firestore                  ──SSE──►  /api/alerts/stream
   (issue_proposals,          ──SSE──►  /api/bridge/stream
    alerts, sessions)         ──SSE──►  /api/mcp-log/stream
        │
        ▼
   Next.js Dashboard
     ├─ Sprint timeline + prediction
     ├─ Agent Insights (proactive alerts, live)
     ├─ Chat (markdown + tool calls + suggestion chips)
     ├─ MCP Activity Log + header call counter
     ├─ Sprint Health (PR lag bar chart, deep work, estimation)
     ├─ Workload Heatmap + Reliability Table
     ├─ Issue Proposal Queue (human approval → GitHub MCP)
     └─ Data Sources (Fivetran status + sync trigger)
```

### Key design decisions

| Decision | Reason |
|---|---|
| **One activity tap, two MCP servers** | `activity_log.tap()` wraps every Fivetran and GitHub call; the judge-visible MCP log is automatic |
| **Human-in-the-loop writes** | Agent proposes GitHub issues into Firestore; a human approves before `create_issue` runs |
| **Per-run SSE channels** (`chat:{run_id}`) | Prevents stale ring-buffer replay when a user asks a second question in the same session |
| **BigQuery type sanitisation at source** | `bigquery_client._sanitize()` converts `datetime`, `date`, `Decimal` to JSON-safe types so all downstream code gets clean dicts |
| **Mock agent fallback** | When Vertex AI / Gemini is not configured, a data-driven mock agent answers all queries from live BigQuery data — the UI remains fully functional |
| **Build-time `NEXT_PUBLIC_API_BASE_URL`** | Next.js inlines `NEXT_PUBLIC_*` vars into the client bundle at `next build`; the frontend image must be built locally with the backend URL injected as a Docker `--build-arg` |

---

## Repository layout

```
backend/app/
  api/routes/          thin HTTP controllers
                       (connectors, dashboard, team, bridge, alerts, chat, mcp_log)
  api/schemas/         Pydantic request/response DTOs
  agent/               ADK agent definition, runner, event normalizer
                       tools/ (bigquery_tools, fivetran_mcp, github_mcp, bridge_tools, analysis_tools)
  services/            business logic reused by routes, agent, and background jobs
                       (metrics, workload, bridge, alerts, chat, connectors)
  integrations/        external I/O
                       bigquery_client, firestore_client
                       mcp/ (session, activity_log, fivetran_client, github_client)
  domain/              entities (alert, metric, connector, chat, issue_proposal, developer)
  events/bus.py        in-process pub/sub → SSE channels (ring buffer + replay)
  jobs/                alert_scanner, bridge_scanner

frontend/src/
  app/                 Next.js App Router pages (dashboard at /, chat at /chat)
  components/
    alerts/            InsightCards (agent-generated proactive alerts)
    bridge/            ProposalQueue (human approval UI)
    chat/              ChatWindow (streaming, markdown, suggestion chips)
    dashboard/         SprintHealthDashboard (PR lag bar chart, deep work, estimation)
    data-sync/         DataSyncPanel (connector status + sync trigger)
    mcp-log/           McpActivityLog, McpCounter
    sprint/            SprintBanner, SprintPrediction
    team/              WorkloadHeatmap, ReliabilityTable
    ui/                Card
  lib/                 api-client, sse, types

shared/contracts/      JSON schemas — backend Pydantic models and frontend TS types both derive from these
infra/
  bigquery/sql/        metric view definitions (pr_review_lag, developer_load, etc.)
  bigquery/apply_views.py
  cloudrun/            deployment notes
docs/                  architecture, data-model, data-pipeline (runbook), mcp-integration, demo-script
```

---

## Local development

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (for Firestore emulator)
- A GCP project with BigQuery datasets already populated by Fivetran

### Setup

```bash
git clone <repo-url>
cd DevLens

# Copy env template and fill in all values
cp .env.example .env

# Backend
cd backend && pip install -e ".[dev]" && cd ..

# Frontend
cd frontend && npm install && cd ..

# Apply BigQuery metric views (first time or after SQL changes)
make bq-views
```

### Run

```bash
make dev        # backend + frontend + Firestore emulator (docker-compose)
make backend    # FastAPI only  (uvicorn --reload, port 8000)
make frontend   # Next.js only  (port 3000)
make test       # backend pytest
make lint       # ruff + eslint
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in `.env` when running the frontend locally.

---

## Environment variables

See [`.env.example`](.env.example) for the full list with descriptions.

| Variable | Example | Description |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | `dev-blindspot-agent` | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex AI region |
| `GOOGLE_GENAI_USE_VERTEXAI` | `1` | `1` = Vertex AI, `0` = AI Studio key |
| `GEMINI_MODEL` | `gemini-3-pro` | Model ID passed to ADK |
| `BIGQUERY_PROJECT` | `dev-blindspot-agent` | BigQuery project (usually same as GCP project) |
| `BIGQUERY_DATASET_GITHUB` | `github` | Raw GitHub tables (Fivetran-managed) |
| `BIGQUERY_DATASET_JIRA` | `jira` | Raw Jira tables (Fivetran-managed) |
| `BIGQUERY_DATASET_CALENDAR` | `google_calendar` | Raw Calendar tables (Fivetran-managed) |
| `BIGQUERY_DATASET_METRICS` | `devlens_metrics` | Our derived metric views |
| `FIRESTORE_PROJECT` | `dev-blindspot-agent` | Firestore project |
| `FIRESTORE_DATABASE` | `(default)` | Firestore database name |
| `FIVETRAN_API_KEY` | `...` | Fivetran API key |
| `FIVETRAN_API_SECRET` | `...` | Fivetran API secret |
| `FIVETRAN_GROUP_ID` | `eating_radiance` | Fivetran destination group ID |
| `FIVETRAN_MCP_URL` | *(empty on Cloud Run)* | Set to `http://localhost:3000` when running the MCP server locally |
| `GITHUB_TOKEN` | `ghp_...` | PAT with `repo` scope |
| `GITHUB_REPO` | `itsRenuka22/stealth-labs-platform` | Demo repo (owner/repo) |
| `GITHUB_MCP_URL` | *(empty on Cloud Run)* | Set to `http://localhost:8082` when running GitHub MCP locally |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins for CORS |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend URL baked into the client bundle at build time |

> On Cloud Run, `GOOGLE_APPLICATION_CREDENTIALS` is **not needed** — the runtime service account provides ADC automatically. Do not set it.

> `NEXT_PUBLIC_API_BASE_URL` is a Next.js **build-time** variable. It is inlined into the client JavaScript bundle during `next build`. Passing it as a runtime Cloud Run env var has no effect. See the deployment section below.

---

## Deployment

### 1. Authenticate gcloud

```bash
gcloud auth login
gcloud config set project dev-blindspot-agent
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### 2. Deploy backend

The backend has no build-time variable requirements. Use `--source` (Cloud Build builds the Dockerfile):

```bash
# Write all env vars to a YAML file — handles special chars (colons, commas in URLs) safely
cat > /tmp/backend-envvars.yaml << 'EOF'
GOOGLE_CLOUD_PROJECT: "dev-blindspot-agent"
GOOGLE_CLOUD_LOCATION: "us-central1"
GOOGLE_GENAI_USE_VERTEXAI: "1"
GEMINI_MODEL: "gemini-3-pro"
BIGQUERY_PROJECT: "dev-blindspot-agent"
BIGQUERY_DATASET_GITHUB: "github"
BIGQUERY_DATASET_JIRA: "jira"
BIGQUERY_DATASET_CALENDAR: "google_calendar"
BIGQUERY_DATASET_METRICS: "devlens_metrics"
FIRESTORE_PROJECT: "dev-blindspot-agent"
FIRESTORE_DATABASE: "(default)"
FIVETRAN_API_KEY: "<your-key>"
FIVETRAN_API_SECRET: "<your-secret>"
FIVETRAN_GROUP_ID: "<your-group-id>"
GITHUB_TOKEN: "<your-github-pat>"
GITHUB_REPO: "itsRenuka22/stealth-labs-platform"
CORS_ORIGINS: "https://<frontend-cloud-run-url>"
EOF

gcloud run deploy devlens-backend \
  --source ./backend \
  --region us-central1 \
  --env-vars-file /tmp/backend-envvars.yaml \
  --allow-unauthenticated \
  --memory 1Gi \
  --quiet
```

Note the deployed **Service URL** (e.g. `https://devlens-backend-XXXXXXXX-uc.a.run.app`).

> **Important:** `--env-vars-file` replaces all env vars on the service. Always pass the complete set when updating.

### 3. Build and deploy frontend (local Docker build required)

`NEXT_PUBLIC_API_BASE_URL` is baked into the client JS bundle by Next.js at build time. It cannot be overridden at runtime. The image must be built locally with `--build-arg`:

```bash
BACKEND_URL="https://devlens-backend-XXXXXXXX-uc.a.run.app"
PROJECT="dev-blindspot-agent"
IMAGE="us-central1-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/devlens-frontend:latest"

# Authenticate Docker to Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
# If docker-credential-gcloud is not in PATH, use the token approach:
# gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

# Build with backend URL baked in
docker build \
  --build-arg NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" \
  -t "$IMAGE" \
  ./frontend

# Push and deploy
docker push "$IMAGE"
gcloud run deploy devlens-frontend \
  --image "$IMAGE" \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --quiet
```

### 4. Update backend CORS after frontend deploys

Once you have the frontend URL, update `CORS_ORIGINS` in the backend YAML and re-apply:

```bash
# Update CORS_ORIGINS line in /tmp/backend-envvars.yaml, then:
gcloud run services update devlens-backend \
  --region us-central1 \
  --env-vars-file /tmp/backend-envvars.yaml \
  --quiet
```

### What the root URL shows

FastAPI has no route defined at `/` — visiting the backend root returns `{"detail": "Not Found"}`. This is expected. Use `/health` to verify the service is up, or `/docs` for the OpenAPI explorer.

---

## Key files

| File | Purpose |
|---|---|
| `backend/app/agent/agent.py` | ADK agent construction + data-driven mock agent fallback |
| `backend/app/agent/runner.py` | Executes a query, publishes events to `chat:{run_id}` SSE channel |
| `backend/app/integrations/mcp/activity_log.py` | Universal MCP call tap — both Fivetran and GitHub calls go through here |
| `backend/app/integrations/bigquery_client.py` | BQ query wrapper; `_sanitize()` converts datetime/Decimal to JSON-safe types |
| `backend/app/services/alerts_service.py` | Proactive insight scanner: open PRs, meeting overload, workload spikes |
| `backend/app/api/routes/dashboard.py` | Sprint prediction endpoint (velocity-based forecast from Jira story points) |
| `backend/app/api/routes/chat.py` | `GET /api/chat/run/{run_id}/stream` — per-run SSE channel |
| `backend/app/events/bus.py` | In-process pub/sub with ring buffer + `subscribe_with_replay()` |
| `frontend/src/components/chat/ChatWindow.tsx` | Streaming chat: react-markdown, remark-gfm, suggestion chips |
| `frontend/src/components/dashboard/SprintHealthDashboard.tsx` | PR lag bar chart (Recharts + Cell per-bar colour) |
| `frontend/src/components/sprint/SprintPrediction.tsx` | One-sentence sprint forecast banner |
| `frontend/src/components/mcp-log/McpCounter.tsx` | Live MCP call counter in header (SSE-incremented) |
| `frontend/src/lib/api-client.ts` | Fetch wrapper; BASE = `NEXT_PUBLIC_API_BASE_URL` (build-time) |
| `frontend/next.config.js` | Next.js config: `output: "standalone"` for the Cloud Run Docker image |
| `frontend/Dockerfile` | Multi-stage build; accepts `NEXT_PUBLIC_API_BASE_URL` as `ARG` |
| `infra/bigquery/sql/` | Metric view SQL definitions |
| `infra/bigquery/apply_views.py` | Script to create/replace all views in `devlens_metrics` |
| `shared/contracts/*.json` | JSON schemas keeping backend Pydantic models and frontend TS types in sync |

---

## Demo script (3 minutes)

1. **Hook (0:00–0:20)** — Show the dashboard. Call out the three live Fivetran connectors (GitHub, Jira, Calendar) in the Data Sources panel and the live MCP counter in the header.
2. **Live sync (0:20–0:45)** — Click **Sync Now** on a connector. The MCP Activity Log scrolls: `[Fivetran MCP] → sync_connector(github) → success`. The counter increments.
3. **Sprint health (0:45–1:10)** — Show the PR lag bar chart (four real PRs, colour-coded), the sprint completion prediction banner, and the Agent Insights cards.
4. **Proposal Queue (1:10–1:50)** — Open a pending issue proposal. The agent read a Jira thread and drafted a GitHub issue with a suggested assignee. Click **Approve** → `[GitHub MCP] → create_issue → success`. The real issue appears in `stealth-labs-platform`.
5. **Chat (1:50–2:40)** — Ask "Who's the bottleneck this sprint?" The agent streams tool calls (BigQuery queries visible as teal pills) and returns a markdown-formatted answer.
6. **Close (2:40–3:00)** — Recap: two MCP servers, real Fivetran data, human-in-the-loop writes, all on Google Cloud.

---

## Hackathon details

- **Event:** Google Cloud Rapid Agent Hackathon
- **Track:** Fivetran (one project = one track)
- **Deadline:** 2026-06-11 @ 2:00pm PDT
- **Demo repo:** `itsRenuka22/stealth-labs-platform` (GitHub)
- **Jira project:** `SLS` (sjsu-team-devlens.atlassian.net)
- **Team:** Mrunal Kotkar, Parth Gala, Renuka Rajpure

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
