"""Discussion -> Repo bridge endpoints: issue proposals + human approval.

The agent drafts issues from Slack/Jira threads into Firestore `issue_proposals`; these endpoints
let the UI list them, stream new ones, and approve/reject. Approval is what triggers the GitLab MCP
write — nothing is filed without a human.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/bridge", tags=["bridge"])


@router.get("/proposals")
async def list_proposals():
    """List pending (and recent) issue proposals.

    TODO: BridgeService.list_proposals() -> Firestore `issue_proposals`.
    """
    raise NotImplementedError


@router.get("/proposals/stream")
async def stream_proposals():
    """SSE stream of new proposals as the bridge scanner produces them.

    TODO: subscribe to event bus "bridge" channel and yield SSE events.
    """
    raise NotImplementedError


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str):
    """Approve (optionally with edits) -> file the issue via GitLab MCP.

    TODO: BridgeService.approve(proposal_id, edits) -> GitLabMcpClient.create_issue + assign + label.
    """
    raise NotImplementedError


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str):
    """Dismiss a proposal. TODO: BridgeService.reject(proposal_id)."""
    raise NotImplementedError
