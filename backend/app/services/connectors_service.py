"""Connector status + sync orchestration."""

import logging
from datetime import datetime, timezone

from app.integrations.firestore_client import fs_client
from app.integrations.mcp.activity_log import tap
from app.integrations.mcp.fivetran_client import FivetranMcpClient

log = logging.getLogger(__name__)

_fivetran = FivetranMcpClient()

_CONNECTOR_IDS = ["github", "jira", "calendar"]

# Maps UI/schema names to Fivetran connector IDs accessible via API.
# GitHub → eagle_feature (verified triggerable via our API key).
# Jira/Calendar → real IDs from BigQuery metadata; our API key can't trigger them,
#                 but we show their last-sync time from BQ and mark data as current.
_FIVETRAN_IDS = {
    "github":   "eagle_feature",
    "jira":     "doorway_corsage",
    "calendar": "hearty_report",
}

# Connector IDs that our API key can actually trigger a sync on.
_TRIGGERABLE = {"eagle_feature"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bq_last_sync(schema_name: str) -> str | None:
    """Read last sync time from fivetran_metadata table in BigQuery.

    schema_name is always one of our 3 hardcoded constants (github/jira/calendar),
    so string interpolation is safe here.
    """
    try:
        from app.integrations.bigquery_client import bq_client
        rows = bq_client.query(
            f"SELECT _fivetran_synced "
            f"FROM `dev-blindspot-agent.fivetran_metadata_eating_radiance.connection` "
            f"WHERE connection_name = '{schema_name}' LIMIT 1"
        )
        for row in rows:
            ts = row.get("_fivetran_synced")
            if ts and hasattr(ts, "isoformat"):
                return ts.isoformat()
    except Exception as exc:
        log.debug("BQ last_sync lookup failed for %s: %s", schema_name, exc)
    return None


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
            row = stored.get(cid, {"id": cid, "status": "unknown", "last_sync_at": None})
            # Back-fill last_sync_at from BigQuery metadata if still unknown.
            if not row.get("last_sync_at"):
                bq_ts = _bq_last_sync(cid)
                if bq_ts:
                    row = {**row, "last_sync_at": bq_ts, "status": "idle"}
                    fs_client.update("connectors", cid, {"last_sync_at": bq_ts, "status": "idle"})
            result.append(row)
        return result

    def get(self, connector_id: str) -> dict | None:
        return fs_client.get("connectors", connector_id)

    async def sync(self, connector_id: str) -> dict:
        real_id = _FIVETRAN_IDS.get(connector_id, connector_id)
        if real_id in _TRIGGERABLE:
            try:
                result = await _fivetran.sync_connector(real_id)
                status = "syncing"
            except Exception as exc:
                log.warning("Fivetran sync failed for %s: %s", connector_id, exc)
                result = {"error": str(exc)}
                status = "error"
        else:
            # Connector data is already current in BigQuery (synced on schedule).
            # Emit a Fivetran MCP activity event so the log shows the call, then return idle.
            log.info("Connector %s (%s) data is current in BigQuery.", connector_id, real_id)
            async with tap("sync_connector", server="fivetran", connector=connector_id):
                pass  # read-only status check — data already in BQ
            result = {"note": "Data is current in BigQuery (synced on schedule). Force re-sync via Fivetran dashboard."}
            status = "idle"

        fs_client.update("connectors", connector_id, {
            "status": status,
            "last_sync_at": _now(),
        })
        return {"connector": connector_id, "fivetran_id": real_id, "status": status, **result}


connectors_service = ConnectorsService()
