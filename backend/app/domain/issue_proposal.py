"""IssueProposal domain model — a drafted GitLab issue awaiting human approval.

Mirror shared/contracts/issue-proposal.json.
"""

# from pydantic import BaseModel
#
# class IssueProposal(BaseModel):
#     id: str
#     status: str                 # pending | filed | dismissed
#     source: str                 # slack | jira
#     source_ref: str             # thread/issue id + permalink back to the discussion
#     title: str                  # drafted issue title
#     description: str            # drafted issue body
#     labels: list[str]
#     suggested_assignee: str | None
#     confidence: float           # how sure the agent is this is actionable
#     gitlab_issue_url: str | None  # set once filed
#     created_at: str
