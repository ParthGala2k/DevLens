"""MCP Activity Log endpoint — judge-visible live feed of every Fivetran + GitHub MCP call."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.events.bus import bus
from app.integrations.mcp.activity_log import recent_calls

router = APIRouter(prefix="/api/mcp-log", tags=["mcp"])


@router.get("")
async def recent_mcp_calls(n: int = 50) -> list[dict]:
    return recent_calls(n)


@router.get("/count")
async def mcp_call_count() -> dict:
    """Count of completed MCP calls today (success + error, excluding start events)."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    count = sum(
        1 for e in recent_calls(100)
        if e.get("status") in ("success", "error") and e.get("ts", "").startswith(today)
    )
    return {"count": count}


@router.get("/stream")
async def stream_mcp_log():
    async def _generate():
        for event in recent_calls(20):
            yield f"data: {json.dumps(event)}\n\n"
        async for event in bus.subscribe("mcp_log"):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
