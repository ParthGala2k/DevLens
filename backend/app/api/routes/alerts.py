"""Proactive Alert Feed endpoints: list past alerts + live SSE stream."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.events.bus import bus
from app.services.alerts_service import alerts_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def list_alerts() -> list[dict]:
    alerts = alerts_service.get_all()
    if not alerts:
        # No alerts in Firestore yet — run the rule-based scan now so the UI
        # shows real insights from the first page load.
        alerts = await alerts_service.scan()
    return alerts


@router.get("/stream")
async def stream_alerts():
    async def _generate():
        # Replay recent alerts for initial render.
        for event in bus.recent("alerts"):
            yield f"data: {json.dumps(event)}\n\n"
        # Then stream live.
        async for event in bus.subscribe("alerts"):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
