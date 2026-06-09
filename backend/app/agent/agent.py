"""Root ADK agent definition (Gemini 3).

Composes the DevLens agent with all tools. Falls back to a mock agent when
google-adk isn't available or Vertex AI isn't configured, so the API layer
can still run for UI development.
"""

import logging
from pathlib import Path

from app.config import settings

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system.md").read_text()


def build_agent():
    """Construct and return the root DevLens agent."""
    from app.agent.tools import bigquery_tools, fivetran_mcp, github_mcp, bridge_tools, analysis_tools

    try:
        from google.adk.agents import Agent

        agent = Agent(
            name="devlens",
            model=settings.gemini_model,
            instruction=_SYSTEM_PROMPT,
            tools=[
                *bigquery_tools.TOOLS,
                *fivetran_mcp.TOOLS,
                *github_mcp.TOOLS,
                *bridge_tools.TOOLS,
                *analysis_tools.TOOLS,
            ],
        )
        log.info("ADK agent built with model %s", settings.gemini_model)
        return agent
    except Exception as exc:
        log.warning("ADK unavailable (%s) — using mock agent", exc)
        return _MockAgent()


class _MockAgent:
    """Minimal stand-in used when google-adk isn't importable or configured."""

    name = "devlens-mock"

    async def run_async(self, session, new_message):
        yield _MockEvent(f"[mock agent] Received: {new_message}")


class _MockEvent:
    def __init__(self, text: str) -> None:
        self._text = text

    def is_final_response(self) -> bool:
        return True

    class _Content:
        def __init__(self, text: str) -> None:
            self.role = "model"

            class _Part:
                pass

            p = _Part()
            p.text = text
            p.function_call = None
            p.function_response = None
            self.parts = [p]

    @property
    def content(self):
        return self._Content(self._text)
