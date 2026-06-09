"""Normalize ADK agent events into the UI event schema (shared/contracts/agent-events.json).

Event types: thinking | tool_call | tool_result | message
"""

from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(adk_event) -> dict | None:
    """Map a single ADK event to a UI event dict (None to skip)."""
    try:
        # google-adk event API (subject to change between versions)
        if hasattr(adk_event, "content") and adk_event.content:
            content = adk_event.content
            if hasattr(content, "parts"):
                for part in content.parts:
                    # Function call (tool invocation)
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        return {
                            "type": "tool_call",
                            "ts": _now(),
                            "data": {
                                "name": getattr(fc, "name", "unknown"),
                                "args": dict(getattr(fc, "args", {})),
                            },
                        }
                    # Function response (tool result)
                    if hasattr(part, "function_response") and part.function_response:
                        fr = part.function_response
                        return {
                            "type": "tool_result",
                            "ts": _now(),
                            "data": {
                                "name": getattr(fr, "name", "unknown"),
                                "result": getattr(fr, "response", {}),
                            },
                        }
                    # Text output
                    if hasattr(part, "text") and part.text:
                        # Heuristic: model thoughts vs final answer
                        role = getattr(content, "role", "model")
                        event_type = "thinking" if role == "model" and not adk_event.is_final_response() else "message"
                        return {
                            "type": event_type,
                            "ts": _now(),
                            "data": {"text": part.text},
                        }
        return None
    except Exception:
        return None
