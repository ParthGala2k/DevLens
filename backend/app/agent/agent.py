"""Root ADK agent definition (Gemini 3).

Composes the agent's instructions + model + tools. Tools are thin wrappers in `tools/` that
ultimately call `services/` and `integrations/`.
"""

# from google.adk.agents import Agent
# from app.config import settings
# from app.agent.tools import bigquery_tools, fivetran_mcp, analysis_tools


def build_agent():
    """Construct and return the root DevLens agent.

    TODO:
      root_agent = Agent(
          name="devlens",
          model=settings.gemini_model,
          instruction=<system prompt from prompts/>,
          tools=[*bigquery_tools.TOOLS, *fivetran_mcp.TOOLS, *analysis_tools.TOOLS],
      )
      return root_agent
    """
    raise NotImplementedError
