"""Data Sync Panel endpoints: connector status + trigger Fivetran MCP sync."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


@router.get("")
async def list_connectors():
    """Return all connected sources with last sync time + status.

    TODO: delegate to ConnectorsService (reads Firestore `connectors`).
    """
    raise NotImplementedError


@router.post("/{connector}/sync")
async def sync_now(connector: str):
    """Trigger a Fivetran MCP sync for a connector ("Sync Now" button).

    TODO: call ConnectorsService.sync(connector) -> Fivetran MCP `sync_connector`.
          The MCP activity tap publishes the call to the mcp_log SSE stream automatically.
    """
    raise NotImplementedError
