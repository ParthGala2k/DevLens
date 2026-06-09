"""Discussion -> Repo bridge orchestration.

Lifecycle: scan → propose → human approves → GitHub MCP files the issue.
The agent proposes; a human approves; only then do we write to GitHub.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.events.bus import bus
from app.integrations.firestore_client import fs_client
from app.integrations.mcp.github_client import GitHubMcpClient
from app.services.workload_service import workload_service

log = logging.getLogger(__name__)

_github = GitHubMcpClient()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_DEMO_PROPOSALS = [
    {
        "id": "prop-demo-001",
        "status": "pending",
        "source": "slack",
        "source_ref": "#dev-alerts thread 2026-06-07",
        "title": "Add retry logic for GitHub webhook delivery failures",
        "description": (
            "**Context:** Thread in #dev-alerts discusses webhook delivery failures under load.\n\n"
            "Users report intermittent 5xx responses from GitHub's webhook endpoint during peak CI.\n\n"
            "**Proposed fix:** Implement exponential backoff with jitter for webhook delivery attempts.\n"
            "Max 5 retries, 30s cap."
        ),
        "labels": ["bug", "reliability"],
        "suggested_assignee": "carol",
        "confidence": 0.91,
        "github_issue_url": None,
        "created_at": "2026-06-07T15:23:00Z",
    },
    {
        "id": "prop-demo-002",
        "status": "pending",
        "source": "jira",
        "source_ref": "SLS-47",
        "title": "SLS-47: Instrument API latency for P95 alerting",
        "description": (
            "**Context:** Jira ticket SLS-47 was never moved to a GitHub issue.\n\n"
            "The team agreed to add OpenTelemetry spans for all API routes and wire a P95 alert.\n"
            "This is blocked by the logging refactor in SLS-42 which shipped last sprint."
        ),
        "labels": ["observability", "enhancement"],
        "suggested_assignee": "dave",
        "confidence": 0.87,
        "github_issue_url": None,
        "created_at": "2026-06-08T08:10:00Z",
    },
]


class BridgeService:
    def _seed_demo_if_empty(self) -> None:
        existing = fs_client.get_all("issue_proposals")
        if not existing:
            for p in _DEMO_PROPOSALS:
                fs_client.set("issue_proposals", p["id"], p)

    def list_proposals(self, status: str | None = None) -> list[dict]:
        self._seed_demo_if_empty()
        all_props = fs_client.get_all("issue_proposals")
        if status:
            return [p for p in all_props if p.get("status") == status]
        return sorted(all_props, key=lambda p: p.get("created_at", ""), reverse=True)

    async def approve(self, proposal_id: str, edits: dict | None = None) -> dict:
        proposal = fs_client.get("issue_proposals", proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal.get("status") != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal['status']}")

        title = (edits or {}).get("title", proposal["title"])
        description = (edits or {}).get("description", proposal["description"])
        labels = (edits or {}).get("labels", proposal.get("labels", []))
        assignee = (edits or {}).get("suggested_assignee", proposal.get("suggested_assignee"))

        issue = await _github.create_issue(
            title=title,
            description=description,
            labels=labels,
            assignee=assignee,
        )

        issue_url = issue.get("html_url") or issue.get("url") or ""
        fs_client.update("issue_proposals", proposal_id, {
            "status": "filed",
            "github_issue_url": issue_url,
            "filed_at": _now(),
        })

        updated = {**proposal, "status": "filed", "github_issue_url": issue_url}
        await bus.publish("bridge", {"type": "proposal_filed", "proposal": updated})
        return updated

    def reject(self, proposal_id: str) -> dict:
        proposal = fs_client.get("issue_proposals", proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        fs_client.update("issue_proposals", proposal_id, {"status": "dismissed"})
        updated = {**proposal, "status": "dismissed"}
        return updated


bridge_service = BridgeService()
