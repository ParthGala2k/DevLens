"""ADK tools backed by the Fivetran MCP server (the mandatory partner integration)."""

from app.services.connectors_service import connectors_service


async def sync_connector(connector: str) -> dict:
    """Trigger a Fivetran sync for a connector (github|jira|calendar)."""
    return await connectors_service.sync(connector)


async def connector_status(connector: str) -> dict:
    """Return the current Fivetran sync status and last sync time for a connector."""
    info = connectors_service.get(connector)
    return info or {"id": connector, "status": "unknown"}


def list_connectors() -> list[dict]:
    """List all Fivetran connectors and their current sync status."""
    return connectors_service.list()


TOOLS = [sync_connector, connector_status, list_connectors]
