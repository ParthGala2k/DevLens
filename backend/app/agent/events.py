"""Normalize ADK agent events into the UI event schema.

Target shape (see shared/contracts/agent-events.json):
    {"type": "thinking" | "tool_call" | "tool_result" | "message", "data": {...}, "ts": ...}

Keeping this mapping in one place means the frontend has a stable contract regardless of
ADK's internal event representation.
"""


def normalize(adk_event):
    """Map a single ADK event to a UI event dict (or None to skip).

    TODO: branch on the ADK event kind (model thought, function call, function response,
          final text) and return the corresponding UI event.
    """
    raise NotImplementedError
