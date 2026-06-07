"""ADK tools that let the agent query sprint metrics from BigQuery.

Each tool is a plain function with a typed signature + docstring (ADK uses these as the tool
schema). Tools delegate to MetricsService / BigQueryClient — they do not embed SQL strings of
their own beyond referencing the derived views.
"""

# def query_pr_review_lag(sprint: str | None = None) -> list[dict]:
#     """Return stuck PRs and their review wait times. ..."""
#     ...

# TOOLS = [query_pr_review_lag, query_deep_work, query_estimation_accuracy]
TOOLS: list = []  # TODO: populate with tool functions
