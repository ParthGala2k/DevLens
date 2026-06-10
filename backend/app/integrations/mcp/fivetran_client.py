"""Fivetran integration layer (sync layer — mandatory Fivetran track integration).

Tries the Fivetran MCP server first (FIVETRAN_MCP_URL, e.g. http://localhost:3000
when running the local `npx @fivetran/mcp` tool). Falls back to the Fivetran REST
API so the demo works even when the local MCP server is not running.

Every call routes through the activity tap so it appears in the live MCP Activity Log
regardless of which transport succeeded.
"""

import base64
import logging

import httpx

from app.config import settings
from app.integrations.mcp.activity_log import tap
from app.integrations.mcp.session import McpSession

log = logging.getLogger(__name__)

_REST_BASE = "https://api.fivetran.com/v1"


def _auth_header() -> str:
    token = base64.b64encode(
        f"{settings.fivetran_api_key}:{settings.fivetran_api_secret}".encode()
    ).decode()
    return f"Basic {token}"


def _mcp_available() -> bool:
    """Return True if the configured MCP URL looks like a reachable local server."""
    url = settings.fivetran_mcp_url or ""
    return url.startswith("http://localhost") or url.startswith("http://127.")


class FivetranMcpClient:
    def __init__(self, session: McpSession | None = None) -> None:
        self._session = session

    def _get_session(self) -> McpSession:
        if self._session is None:
            self._session = McpSession(
                url=settings.fivetran_mcp_url,
                headers={"Authorization": _auth_header()},
            )
        return self._session

    async def list_connectors(self) -> list[dict]:
        async with tap("list_connectors", server="fivetran"):
            if _mcp_available():
                session = self._get_session()
                result = await session.call_tool("list_connectors", {
                    "group_id": settings.fivetran_group_id,
                })
                return result.get("connectors", result if isinstance(result, list) else [])

            # REST fallback
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"{_REST_BASE}/groups/{settings.fivetran_group_id}/connectors",
                    headers={"Authorization": _auth_header()},
                )
                if r.status_code == 200:
                    return r.json().get("data", {}).get("items", [])
                log.warning("Fivetran list_connectors REST failed: %s %s", r.status_code, r.text[:200])
                return []

    async def connector_status(self, connector_id: str) -> dict:
        async with tap("connector_status", server="fivetran", connector=connector_id):
            if _mcp_available():
                session = self._get_session()
                return await session.call_tool("get_connector_details", {
                    "connector_id": connector_id,
                })

            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"{_REST_BASE}/connectors/{connector_id}",
                    headers={"Authorization": _auth_header()},
                )
                if r.status_code == 200:
                    return r.json().get("data", {})
                log.warning("Fivetran connector_status REST failed: %s", r.status_code)
                return {"id": connector_id, "status": "unknown"}

    async def sync_connector(self, connector_id: str) -> dict:
        async with tap("sync_connector", server="fivetran", connector=connector_id):
            if _mcp_available():
                session = self._get_session()
                return await session.call_tool("trigger_sync", {
                    "connector_id": connector_id,
                    "force": True,
                })

            # REST fallback — POST /v1/connectors/{id}/sync
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(
                    f"{_REST_BASE}/connectors/{connector_id}/sync",
                    headers={"Authorization": _auth_header()},
                    json={},
                )
                if r.status_code in (200, 204):
                    return {"connector_id": connector_id, "status": "syncing"}
                log.warning("Fivetran sync REST failed %s: %s", r.status_code, r.text[:200])
                raise RuntimeError(f"Fivetran sync failed ({r.status_code}): {r.json().get('message', r.text[:100])}")
