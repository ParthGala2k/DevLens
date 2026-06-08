"""MCP activity tap — the single point that makes every MCP call judge-visible.

Wrap any MCP call with `tap()` (or use it as a decorator). Works for BOTH MCP servers
(Fivetran sync + GitLab action). On each call it publishes a structured event to the event bus
"mcp_log" channel:

    {"server": "fivetran|gitlab", "connector": ..., "action": ...,
     "status": "start|success|error", "ts": ..., "payload": ...}

It also keeps a small in-memory ring buffer of recent calls for initial render.
"""

# from app.events.bus import bus


def tap(action: str, server: str, connector: str | None = None):
    """Context manager / decorator that emits start + success/error MCP events.

    Args:
        action: MCP tool name (e.g. "sync_connector", "create_issue").
        server: which MCP server — "fivetran" or "gitlab".
        connector: optional data source the action concerns (gitlab/jira/slack/...).

    TODO: publish "start" before the call and "success"/"error" after, to bus channel
          "mcp_log"; append to the ring buffer.
    """
    raise NotImplementedError
