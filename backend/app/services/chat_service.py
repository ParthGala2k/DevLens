"""Chat orchestration: manage sessions, kick off agent runs, persist history."""

import logging
import uuid
from datetime import datetime, timezone

from app.integrations.firestore_client import fs_client

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChatService:
    async def start_run(self, session_id: str | None, message: str) -> dict:
        """Start an agent run. Returns {session_id, run_id}."""
        if not session_id:
            session_id = str(uuid.uuid4())

        from app.agent.runner import run_session
        run_id = await run_session(session_id, message)
        return {"session_id": session_id, "run_id": run_id}

    def history(self, session_id: str) -> list[dict]:
        """Retrieve chat history for a session from Firestore."""
        try:
            docs = fs_client.get_all(f"chat_sessions/{session_id}/messages")
            return sorted(docs, key=lambda m: m.get("ts", ""))
        except Exception as exc:
            log.warning("Failed to fetch chat history for %s: %s", session_id, exc)
            return []


chat_service = ChatService()
