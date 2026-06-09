"""ADK tools for the discussion->repo bridge brain."""

from app.services.workload_service import workload_service


def suggest_assignee(skills_or_area: str | None = None) -> dict:
    """Return the least-loaded suitable developer for new work assignment."""
    dev = workload_service.least_loaded()
    return {"suggested_assignee": dev, "reason": "lowest composite load score"}


def classify_actionable(thread_text: str) -> dict:
    """Classify whether a discussion thread implies a new task or bug that needs tracking.

    Returns confidence 0-1 and a suggested issue_type (bug | feature | task | none).
    Note: the Gemini agent does the actual classification via its reasoning; this tool
    provides a structured output schema for the result.
    """
    # The agent reasons over the text and produces this structure itself.
    # This function signature tells ADK the expected return shape.
    return {"actionable": True, "confidence": 0.0, "issue_type": "task"}


TOOLS = [suggest_assignee, classify_actionable]
