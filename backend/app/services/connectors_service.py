"""Connector status + sync orchestration (framework-agnostic business logic).

Reads/writes connector status in Firestore and triggers Fivetran syncs via the MCP client.
Called by routes (api/routes/connectors.py) and agent tools (agent/tools/fivetran_mcp.py).
"""


class ConnectorsService:
    """TODO: list(), get(connector), sync(connector)."""
