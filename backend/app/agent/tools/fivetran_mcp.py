"""ADK tools backed by the Fivetran MCP server (the mandatory partner integration).

These wrap the MCP client in integrations/mcp/fivetran_client.py. Every call routes through the
activity tap, so invocations show up in the live MCP Activity Log automatically.
"""

# def sync_connector(connector: str) -> dict:
#     """Trigger a Fivetran sync for a connector (gitlab|jira|slack|calendar|pagerduty)."""
#     ...

# def connector_status(connector: str) -> dict:
#     """Return the current Fivetran sync status / last sync time."""
#     ...

# TOOLS = [sync_connector, connector_status]
TOOLS: list = []  # TODO: populate with MCP-backed tool functions
