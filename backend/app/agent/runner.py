"""Agent session runner.

Runs the ADK agent for a chat session and yields normalized UI events (via events.py)
onto the event bus so the frontend can stream the agent's reasoning + tool calls live.
"""


async def run_session(session_id: str, message: str):
    """Run the agent for one user message, streaming events.

    TODO:
      - get/create an ADK session for `session_id`
      - iterate the runner's event stream
      - map each ADK event -> UI event via agent.events.normalize()
      - publish to event bus "chat" channel
      - persist the run to Firestore `agent_runs` and message to `chat_sessions`
    """
    raise NotImplementedError
