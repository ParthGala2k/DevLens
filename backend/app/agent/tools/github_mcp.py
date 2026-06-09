"""ADK tools backed by the GitHub MCP server (the action layer).

Issue creation is gated behind human approval (see bridge_service.approve).
The agent uses list_issues for dedup checking before proposing.
"""

from app.integrations.mcp.github_client import GitHubMcpClient

_client = GitHubMcpClient()


async def list_issues(state: str = "open") -> list[dict]:
    """List GitHub issues for the configured repo (live read, for dedup before proposing)."""
    return await _client.list_issues(state=state)


async def create_issue(title: str, description: str, labels: list[str] | None = None,
                       assignee: str | None = None) -> dict:
    """Create a GitHub issue. Only call after receiving human approval via the bridge flow."""
    return await _client.create_issue(title=title, description=description,
                                      labels=labels, assignee=assignee)


TOOLS = [list_issues, create_issue]
