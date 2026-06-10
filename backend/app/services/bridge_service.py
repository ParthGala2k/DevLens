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


class BridgeService:
    def list_proposals(self, status: str | None = None) -> list[dict]:
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
