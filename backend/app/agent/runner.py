"""Agent session runner — streams normalized UI events onto the event bus."""

import logging
import uuid
from datetime import datetime, timezone

from app.agent.events import normalize
from app.events.bus import bus
from app.integrations.firestore_client import fs_client

log = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from app.agent.agent import build_agent
        _agent = build_agent()
    return _agent


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_session(session_id: str, message: str) -> str:
    """Run the agent for one user message, streaming events to the bus.

    Returns the run_id so the caller can link the SSE stream.
    """
    run_id = str(uuid.uuid4())
    agent = _get_agent()

    # Persist the user message.
    fs_client.add(f"chat_sessions/{session_id}/messages", {
        "role": "user",
        "text": message,
        "ts": _now(),
    })

    async def _stream() -> None:
        try:
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai import types as genai_types

            session_service = InMemorySessionService()
            runner = Runner(agent=agent, app_name="devlens", session_service=session_service)
            session = await session_service.create_session(app_name="devlens", user_id=session_id)

            user_content = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=message)],
            )

            async for adk_event in runner.run_async(
                user_id=session_id,
                session_id=session.id,
                new_message=user_content,
            ):
                ui_event = normalize(adk_event)
                if ui_event:
                    ui_event["session_id"] = session_id
                    ui_event["run_id"] = run_id
                    await bus.publish(f"chat:{session_id}", ui_event)

        except Exception as exc:
            log.warning("ADK runner failed: %s — using mock stream", exc)
            # Fallback: simulate a response using the mock agent.
            mock_agent = _get_agent()
            async for mock_event in mock_agent.run_async(None, message):
                ui_event = normalize(mock_event)
                if ui_event:
                    ui_event["session_id"] = session_id
                    ui_event["run_id"] = run_id
                    await bus.publish(f"chat:{session_id}", ui_event)

        # Mark run done.
        done_event = {
            "type": "done",
            "ts": _now(),
            "session_id": session_id,
            "run_id": run_id,
        }
        await bus.publish(f"chat:{session_id}", done_event)
        fs_client.set(f"agent_runs", run_id, {"session_id": session_id, "ts": _now(), "status": "done"})

    import asyncio
    asyncio.get_event_loop().create_task(_stream())
    return run_id
