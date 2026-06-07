"""Proactive Alert Feed endpoints: list past alerts + live SSE stream of new ones."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def list_alerts():
    """Return recent proactive alerts.

    TODO: AlertsService.list() -> Firestore `alerts` collection.
    """
    raise NotImplementedError


@router.get("/stream")
async def stream_alerts():
    """SSE stream of new alerts as the background scanner produces them.

    TODO: subscribe to event bus "alerts" channel and yield SSE events.
    """
    raise NotImplementedError
