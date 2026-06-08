"""GitLab MCP client wrapper — the action layer.

While Fivetran syncs GitLab *history* into BigQuery, the GitLab MCP server performs *actions*:
creating, assigning, and labeling issues from the discussion->repo bridge, plus live reads when
fresher-than-sync data is needed.

Every call routes through the activity tap (activity_log.py) so GitLab calls appear in the live
MCP Activity Log alongside Fivetran calls.
"""

from app.config import settings
from app.integrations.mcp.activity_log import tap
from app.integrations.mcp.session import McpSession


class GitLabMcpClient:
    """Typed helpers over the GitLab MCP server.

    Construct against settings.gitlab_mcp_url (auth via settings.gitlab_token). Each method wraps
    its MCP call with tap(server="gitlab", action=..., connector="gitlab").
    """

    def __init__(self, session: McpSession | None = None) -> None:
        self._session = session
        # TODO: lazily connect McpSession to settings.gitlab_mcp_url with the token header.

    async def create_issue(
        self,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        """Create a GitLab issue (default project = settings.gitlab_project_id).

        TODO: with tap("create_issue", server="gitlab"):
                  return await session.call_tool("create_issue", {...})
        """
        raise NotImplementedError

    async def assign_issue(self, issue_iid: int, assignee: str, project_id: str | None = None) -> dict:
        """Assign an existing issue. TODO: tap + session.call_tool('assign_issue', ...)."""
        raise NotImplementedError

    async def add_label(self, issue_iid: int, labels: list[str], project_id: str | None = None) -> dict:
        """Add labels to an issue. TODO: tap + session.call_tool('add_label', ...)."""
        raise NotImplementedError

    async def list_issues(self, project_id: str | None = None, state: str = "opened") -> list[dict]:
        """List issues (live read). TODO: tap + session.call_tool('list_issues', ...)."""
        raise NotImplementedError
