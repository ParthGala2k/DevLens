"""Chat orchestration: manage sessions, kick off agent runs, persist history.

Bridges the chat routes and the ADK agent runner; stores messages in Firestore
`chat_sessions/{id}/messages`.
"""


class ChatService:
    """TODO: start_run(session_id, message), history(session_id)."""
