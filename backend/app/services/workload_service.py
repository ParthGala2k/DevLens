"""Developer observability: load + completion reliability (over BigQuery)."""

import logging

from app.integrations.bigquery_client import bq_client

log = logging.getLogger(__name__)

_DEMO_LOAD = [
    {"developer": "alice", "open_issues": 8, "story_points_in_flight": 21.0,
     "prs_awaiting_review": 3, "on_call": True, "meeting_hours": 14.0, "load_score": 87.0},
    {"developer": "bob", "open_issues": 3, "story_points_in_flight": 8.0,
     "prs_awaiting_review": 1, "on_call": False, "meeting_hours": 22.0, "load_score": 62.0},
    {"developer": "carol", "open_issues": 5, "story_points_in_flight": 13.0,
     "prs_awaiting_review": 2, "on_call": False, "meeting_hours": 6.0, "load_score": 45.0},
    {"developer": "dave", "open_issues": 2, "story_points_in_flight": 5.0,
     "prs_awaiting_review": 0, "on_call": False, "meeting_hours": 8.0, "load_score": 28.0},
]

_DEMO_RELIABILITY = [
    {"developer": "alice", "sprint": "SLS-Sprint-3", "assigned": 5, "completed": 4,
     "completion_ratio": 0.8, "avg_cycle_time_days": 3.2, "on_time_ratio": 0.75, "churn": 1},
    {"developer": "bob", "sprint": "SLS-Sprint-3", "assigned": 4, "completed": 5,
     "completion_ratio": 1.25, "avg_cycle_time_days": 2.1, "on_time_ratio": 1.0, "churn": 0},
    {"developer": "carol", "sprint": "SLS-Sprint-3", "assigned": 3, "completed": 3,
     "completion_ratio": 1.0, "avg_cycle_time_days": 1.8, "on_time_ratio": 1.0, "churn": 0},
    {"developer": "alice", "sprint": "SLS-Sprint-4", "assigned": 6, "completed": 4,
     "completion_ratio": 0.67, "avg_cycle_time_days": 4.5, "on_time_ratio": 0.6, "churn": 2},
    {"developer": "bob", "sprint": "SLS-Sprint-4", "assigned": 4, "completed": 3,
     "completion_ratio": 0.75, "avg_cycle_time_days": 3.0, "on_time_ratio": 0.75, "churn": 1},
    {"developer": "carol", "sprint": "SLS-Sprint-4", "assigned": 4, "completed": 4,
     "completion_ratio": 1.0, "avg_cycle_time_days": 2.0, "on_time_ratio": 1.0, "churn": 0},
]


class WorkloadService:
    def load(self) -> list[dict]:
        rows = bq_client.query_view("developer_load")
        return rows if rows else _DEMO_LOAD

    def reliability(self) -> list[dict]:
        rows = bq_client.query_view("completion_reliability")
        return rows if rows else _DEMO_RELIABILITY

    def least_loaded(self, candidates: list[str] | None = None) -> str | None:
        """Return the least-loaded developer from candidates (or all devs)."""
        all_load = self.load()
        if candidates:
            all_load = [r for r in all_load if r.get("developer") in candidates]
        if not all_load:
            return None
        return min(all_load, key=lambda r: r.get("load_score", 999)).get("developer")


workload_service = WorkloadService()
