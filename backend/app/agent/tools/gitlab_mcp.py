"""ADK tools backed by the GitLab MCP server (the action layer).

These wrap integrations/mcp/gitlab_client.py so the agent can take action on the repo — chiefly
filing issues that come out of the discussion->repo bridge. Every call routes through the activity
tap, so GitLab invocations show up in the live MCP Activity Log alongside Fivetran calls.

Note: issue creation is normally gated behind human approval (see services/bridge_service.py); the
agent *proposes*, a human *approves*, then the approved proposal calls create_issue.
"""

# def create_issue(title: str, description: str, labels: list[str] | None = None,
#                  assignee: str | None = None) -> dict:
#     """Create a GitLab issue in the configured project."""
#     ...
#
# def list_issues(state: str = "opened") -> list[dict]:
#     """List GitLab issues (live read), e.g. for dedup before proposing a new one."""
#     ...

# TOOLS = [create_issue, list_issues, assign_issue, add_label]
TOOLS: list = []  # TODO: populate with GitLab MCP-backed tool functions
