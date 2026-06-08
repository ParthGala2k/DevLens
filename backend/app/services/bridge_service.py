"""Discussion -> Repo bridge orchestration.

Lifecycle:
  1. scan(): read `actionable_threads` (BigQuery) for Slack/Jira threads that look like undone work.
  2. For each, use the agent (bridge_tools) to draft an issue + suggest the least-loaded assignee
     (via WorkloadService), optionally dedup-checking existing issues.
  3. Persist an IssueProposal to Firestore `issue_proposals` (status=pending) and publish to the
     event bus so the Proposal Queue UI updates live.
  4. approve(proposal_id): file the issue via GitLabMcpClient.create_issue (+ assign + label + link
     back to the source thread), mark the proposal filed.
  5. reject(proposal_id): mark dismissed.

Human-in-the-loop by design: the agent proposes, a human approves, only then do we write to GitLab.
"""


class BridgeService:
    """TODO: scan(), list_proposals(), approve(proposal_id, edits=None), reject(proposal_id)."""
