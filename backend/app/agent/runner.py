"""Agent session runner — streams normalized UI events onto the event bus."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.agent.events import normalize
from app.events.bus import bus
from app.integrations.firestore_client import fs_client

log = logging.getLogger(__name__)

_agent = None
_mock = None


def _get_agent():
    global _agent
    if _agent is None:
        from app.agent.agent import build_agent
        _agent = build_agent()
    return _agent


def _get_mock():
    """Always returns a _MockAgent — used as the guaranteed fallback."""
    global _mock
    if _mock is None:
        from app.agent.agent import _MockAgent
        _mock = _MockAgent()
    return _mock


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_session(session_id: str, message: str) -> str:
    """Run the agent for one user message, streaming events to the bus.

    Returns the run_id immediately. The actual agent run is a background task.
    """
    run_id = str(uuid.uuid4())
    agent = _get_agent()

    fs_client.add(f"chat_sessions/{session_id}/messages", {
        "role": "user",
        "text": message,
        "ts": _now(),
    })

    async def _stream() -> None:
        # Small yield so the HTTP response reaches the client and the SSE
        # subscriber registers before we start publishing events.
        await asyncio.sleep(0)

        ran_ok = False
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
                    await bus.publish(f"chat:{run_id}", ui_event)

            ran_ok = True

        except Exception as exc:
            log.warning("ADK runner failed for session %s: %s", session_id, exc)

        if not ran_ok:
            # Use the explicit mock (never the real ADK agent) as fallback.
            mock = _get_mock()
            async for mock_event in mock.run_async(session_id, message):
                ui_event = normalize(mock_event)
                if ui_event:
                    ui_event["session_id"] = session_id
                    ui_event["run_id"] = run_id
                    await bus.publish(f"chat:{run_id}", ui_event)

        done_event = {
            "type": "done",
            "ts": _now(),
            "session_id": session_id,
            "run_id": run_id,
        }
        await bus.publish(f"chat:{run_id}", done_event)
        fs_client.set("agent_runs", run_id, {"session_id": session_id, "ts": _now(), "status": "done"})

    asyncio.get_event_loop().create_task(_stream())
    return run_id
