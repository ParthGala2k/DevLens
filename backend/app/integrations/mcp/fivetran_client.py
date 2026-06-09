"""Fivetran MCP client wrapper (the mandatory partner integration).

Exposes typed helpers: sync_connector(), connector_status(), list_connectors().
Every call routes through the activity tap so it appears in the live MCP Activity Log.
"""

import logging

from app.config import settings
from app.integrations.mcp.activity_log import tap
from app.integrations.mcp.session import McpSession

log = logging.getLogger(__name__)


class FivetranMcpClient:
    def __init__(self, session: McpSession | None = None) -> None:
        self._session = session

    def _get_session(self) -> McpSession:
        if self._session is None:
            import base64
            token = base64.b64encode(
                f"{settings.fivetran_api_key}:{settings.fivetran_api_secret}".encode()
            ).decode()
            self._session = McpSession(
                url=settings.fivetran_mcp_url,
                headers={"Authorization": f"Basic {token}"},
            )
        return self._session

    async def list_connectors(self) -> list[dict]:
        async with tap("list_connectors", server="fivetran"):
            session = self._get_session()
            result = await session.call_tool("list_connectors", {
                "group_id": settings.fivetran_group_id,
            })
            return result.get("connectors", result if isinstance(result, list) else [])

    async def connector_status(self, connector: str) -> dict:
        async with tap("connector_status", server="fivetran", connector=connector):
            session = self._get_session()
            return await session.call_tool("get_connector_details", {
                "connector_id": connector,
            })

    async def sync_connector(self, connector: str) -> dict:
        async with tap("sync_connector", server="fivetran", connector=connector):
            session = self._get_session()
            return await session.call_tool("trigger_sync", {
                "connector_id": connector,
                "force": True,
            })
