"""Connector status + sync orchestration."""

import logging
from datetime import datetime, timezone

from app.integrations.firestore_client import fs_client
from app.integrations.mcp.fivetran_client import FivetranMcpClient

log = logging.getLogger(__name__)

_fivetran = FivetranMcpClient()

_CONNECTOR_IDS = ["github", "jira", "slack", "calendar", "pagerduty"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConnectorsService:
    def _default_connectors(self) -> list[dict]:
        return [
            {"id": c, "status": "unknown", "last_sync_at": None}
            for c in _CONNECTOR_IDS
        ]

    def _seed_if_empty(self) -> None:
        existing = fs_client.get_all("connectors")
        if not existing:
            for c in self._default_connectors():
                fs_client.set("connectors", c["id"], c)

    def list(self) -> list[dict]:
        self._seed_if_empty()
        stored = {c["id"]: c for c in fs_client.get_all("connectors")}
        result = []
        for cid in _CONNECTOR_IDS:
            result.append(stored.get(cid, {"id": cid, "status": "unknown", "last_sync_at": None}))
        return result

    def get(self, connector_id: str) -> dict | None:
        return fs_client.get("connectors", connector_id)

    async def sync(self, connector_id: str) -> dict:
        try:
            result = await _fivetran.sync_connector(connector_id)
            status = "syncing"
        except Exception as exc:
            log.warning("Fivetran sync failed for %s: %s", connector_id, exc)
            result = {"error": str(exc)}
            status = "error"

        fs_client.update("connectors", connector_id, {
            "status": status,
            "last_sync_at": _now(),
        })
        return {"connector": connector_id, "status": status, **result}


connectors_service = ConnectorsService()
