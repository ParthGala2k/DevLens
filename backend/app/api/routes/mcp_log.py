"""MCP Activity Log endpoint — the judge-visible live feed of every Fivetran MCP call.

Powered by integrations/mcp/activity_log.py, which taps every MCP call and publishes it to
the event bus "mcp_log" channel. This route just fans those out over SSE.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/mcp-log", tags=["mcp"])


@router.get("/stream")
async def stream_mcp_log():
    """SSE stream of MCP calls, e.g. {connector, action, status, ts, payload}.

    TODO: subscribe to event bus "mcp_log" channel and yield SSE events.
    """
    raise NotImplementedError


@router.get("")
async def recent_mcp_calls():
    """Return the most recent MCP calls (for initial render / refresh).

    TODO: read from an in-memory ring buffer in activity_log, or Firestore `agent_runs`.
    """
    raise NotImplementedError
