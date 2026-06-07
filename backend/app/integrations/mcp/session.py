"""Generic MCP session/transport management.

Establishes and holds an MCP client session (stdio or HTTP/SSE transport) and exposes
list_tools() / call_tool(). The Fivetran-specific wrapper builds on this.
"""

# from mcp import ClientSession


class McpSession:
    """TODO: connect(url/transport), list_tools(), call_tool(name, args)."""
