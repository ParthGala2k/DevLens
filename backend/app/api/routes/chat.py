"""Chat endpoints: ask the agent, stream its reasoning + tool calls back via SSE."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.events.bus import bus
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post("")
async def send_message(body: ChatRequest) -> dict:
    return await chat_service.start_run(body.session_id, body.message)


@router.get("/{session_id}/stream")
async def stream_chat(session_id: str):
    async def _generate():
        async for event in bus.subscribe(f"chat:{session_id}"):
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") == "done":
                break

    return StreamingResponse(_generate(), media_type="text/event-stream")


@router.get("/{session_id}/history")
async def chat_history(session_id: str) -> list[dict]:
    return chat_service.history(session_id)
