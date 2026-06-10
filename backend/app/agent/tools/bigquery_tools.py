"""ADK tools that let the agent query sprint metrics from BigQuery."""

from app.services.metrics_service import metrics_service
from app.services.workload_service import workload_service


def query_pr_review_lag() -> list[dict]:
    """Return GitHub PRs stuck awaiting review, sorted by days open descending."""
    rows = metrics_service.pr_review_lag()
    return sorted(rows, key=lambda r: r.get("days_open", 0), reverse=True)


def query_deep_work() -> list[dict]:
    """Return deep-work hours vs meeting hours per developer per day."""
    return metrics_service.deep_work()


def query_estimation_accuracy() -> list[dict]:
    """Return story-point estimation accuracy by sprint and developer."""
    return metrics_service.estimation_accuracy()


def query_developer_load() -> list[dict]:
    """Return per-developer composite load score (issues + points + PRs + on-call + meetings)."""
    return workload_service.load()


def query_completion_reliability() -> list[dict]:
    """Return per-developer per-sprint completion ratio, cycle time, and on-time rate."""
    return workload_service.reliability()


TOOLS = [
    query_pr_review_lag,
    query_deep_work,
    query_estimation_accuracy,
    query_developer_load,
    query_completion_reliability,
]
