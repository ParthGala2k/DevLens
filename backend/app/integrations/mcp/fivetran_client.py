"""Fivetran MCP client wrapper (the partner integration).

Exposes typed helpers over the Fivetran MCP server — e.g. sync_connector(), connector_status(),
list_connectors(). Every call goes through the activity tap (activity_log.py) so it appears in
the live MCP Activity Log.
"""

# from app.config import settings
# from app.integrations.mcp.session import McpSession
# from app.integrations.mcp.activity_log import tap


class FivetranMcpClient:
    """TODO: wrap McpSession against settings.fivetran_mcp_url; decorate calls with
    tap(action, server="fivetran", connector=...)."""
