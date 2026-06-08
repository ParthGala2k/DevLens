"""ADK tools for the discussion->repo bridge brain.

The agent uses these to turn team discussion into proposed work:
  - detect whether a Slack/Jira thread implies an undone task or bug
  - draft a well-formed issue (title, description, labels) from the thread
  - suggest the least-loaded suitable assignee (reads workload_service)

These produce *proposals* (persisted for human approval), not direct GitLab writes — the actual
filing happens via gitlab_mcp tools once a human approves.
"""

# def is_actionable(thread_text: str) -> dict:
#     """Classify whether a discussion thread implies a new task/bug + confidence."""
#     ...
#
# def draft_issue(thread_text: str) -> dict:
#     """Draft {title, description, labels} from a thread."""
#     ...
#
# def suggest_assignee(skills_or_area: str | None = None) -> dict:
#     """Return the least-loaded suitable dev using developer_load metrics."""
#     ...

# TOOLS = [is_actionable, draft_issue, suggest_assignee]
TOOLS: list = []  # TODO: populate with bridge tool functions
