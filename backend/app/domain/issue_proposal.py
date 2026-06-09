"""IssueProposal domain model — a drafted GitHub issue awaiting human approval."""

from pydantic import BaseModel


class IssueProposal(BaseModel):
    id: str
    status: str                     # pending | filed | dismissed
    source: str                     # slack | jira
    source_ref: str                 # thread/issue id + permalink
    title: str
    description: str
    labels: list[str] = []
    suggested_assignee: str | None = None
    confidence: float = 0.0
    github_issue_url: str | None = None
    created_at: str
