"""GitHub MCP client wrapper — the action layer.

Creates, assigns, and labels GitHub issues from the discussion->repo bridge.
Every call routes through the activity tap so GitHub calls appear in the MCP Activity Log.
"""

import logging

from app.config import settings
from app.integrations.mcp.activity_log import tap
from app.integrations.mcp.session import McpSession

log = logging.getLogger(__name__)


class GitHubMcpClient:
    def __init__(self, session: McpSession | None = None) -> None:
        self._session = session

    def _get_session(self) -> McpSession:
        if self._session is None:
            self._session = McpSession(
                url=settings.github_mcp_url,
                headers={"Authorization": f"Bearer {settings.github_token}"},
            )
        return self._session

    def _parse_repo(self, repo: str | None) -> tuple[str, str]:
        r = repo or settings.github_repo
        owner, name = r.split("/", 1)
        return owner, name

    async def create_issue(
        self,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee: str | None = None,
        repo: str | None = None,
    ) -> dict:
        owner, name = self._parse_repo(repo)
        args: dict = {"owner": owner, "repo": name, "title": title, "body": description}
        if labels:
            args["labels"] = labels
        if assignee:
            args["assignees"] = [assignee]

        async with tap("create_issue", server="github", connector="github", payload={"title": title}):
            return await self._get_session().call_tool("create_issue", args)

    async def assign_issue(self, issue_number: int, assignee: str, repo: str | None = None) -> dict:
        owner, name = self._parse_repo(repo)
        async with tap("assign_issue", server="github", connector="github"):
            return await self._get_session().call_tool("add_issue_assignees", {
                "owner": owner, "repo": name,
                "issue_number": issue_number,
                "assignees": [assignee],
            })

    async def add_labels(self, issue_number: int, labels: list[str], repo: str | None = None) -> dict:
        owner, name = self._parse_repo(repo)
        async with tap("add_labels", server="github", connector="github"):
            return await self._get_session().call_tool("add_issue_labels", {
                "owner": owner, "repo": name,
                "issue_number": issue_number,
                "labels": labels,
            })

    async def list_issues(self, repo: str | None = None, state: str = "open") -> list[dict]:
        owner, name = self._parse_repo(repo)
        async with tap("list_issues", server="github", connector="github"):
            result = await self._get_session().call_tool("list_issues", {
                "owner": owner, "repo": name, "state": state,
            })
            return result if isinstance(result, list) else result.get("issues", [])
