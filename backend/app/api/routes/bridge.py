"""Discussion -> Repo bridge endpoints: issue proposals + human approval."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.events.bus import bus
from app.services.bridge_service import bridge_service

router = APIRouter(prefix="/api/bridge", tags=["bridge"])


class ApproveRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    labels: list[str] | None = None
    suggested_assignee: str | None = None


@router.get("/proposals")
async def list_proposals(status: str | None = None) -> list[dict]:
    return bridge_service.list_proposals(status=status)


@router.get("/proposals/stream")
async def stream_proposals():
    async def _generate():
        for event in bus.recent("bridge"):
            yield f"data: {json.dumps(event)}\n\n"
        async for event in bus.subscribe("bridge"):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, body: ApproveRequest | None = None) -> dict:
    edits = body.model_dump(exclude_none=True) if body else None
    return await bridge_service.approve(proposal_id, edits)


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str) -> dict:
    return bridge_service.reject(proposal_id)
