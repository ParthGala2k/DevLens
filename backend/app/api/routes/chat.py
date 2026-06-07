"""Chat endpoints: ask the agent, stream its reasoning + tool calls back via SSE."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def send_message():
    """Submit a chat message; returns a session/run id.

    TODO: ChatService.start_run(session_id, message) -> kicks off the ADK agent runner.
    """
    raise NotImplementedError


@router.get("/{session_id}/stream")
async def stream_chat(session_id: str):
    """SSE stream of normalized agent events for a run.

    Event types (see shared/contracts/agent-events.json):
      thinking | tool_call | tool_result | message

    TODO: subscribe to event bus "chat" channel for this session and yield SSE events.
    """
    raise NotImplementedError
