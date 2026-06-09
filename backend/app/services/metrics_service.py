"""Sprint-health metrics over BigQuery (PR review lag, deep work, estimation accuracy)."""

import logging

from app.integrations.bigquery_client import bq_client

log = logging.getLogger(__name__)

CONNECTORS = ["github", "jira", "slack", "calendar", "pagerduty"]


class MetricsService:
    def pr_review_lag(self) -> list[dict]:
        """PRs open > 1 day that need a review, from the derived view."""
        rows = bq_client.query_view("pr_review_lag")
        if rows:
            return rows
        # Demo fallback when BigQuery views aren't ready yet.
        return [
            {"pr_number": 42, "title": "Add OAuth middleware", "author": "alice",
             "opened_at": "2026-06-01T10:00:00Z", "days_open": 7.2},
            {"pr_number": 37, "title": "Fix rate limiter bug", "author": "bob",
             "opened_at": "2026-06-03T14:00:00Z", "days_open": 5.0},
            {"pr_number": 55, "title": "Migrate to PostgreSQL 16", "author": "carol",
             "opened_at": "2026-06-05T09:00:00Z", "days_open": 3.1},
        ]

    def deep_work(self) -> list[dict]:
        """Deep-work hours vs meeting hours per developer per day."""
        rows = bq_client.query_view("deep_work_blocks")
        if rows:
            return rows
        return [
            {"date": "2026-06-06", "developer": "alice", "deep_work_hours": 4.5, "meeting_hours": 2.0},
            {"date": "2026-06-06", "developer": "bob", "deep_work_hours": 2.0, "meeting_hours": 5.5},
            {"date": "2026-06-06", "developer": "carol", "deep_work_hours": 6.0, "meeting_hours": 1.0},
            {"date": "2026-06-07", "developer": "alice", "deep_work_hours": 3.0, "meeting_hours": 3.5},
            {"date": "2026-06-07", "developer": "bob", "deep_work_hours": 1.5, "meeting_hours": 6.0},
            {"date": "2026-06-07", "developer": "carol", "deep_work_hours": 5.0, "meeting_hours": 1.5},
        ]

    def estimation_accuracy(self) -> list[dict]:
        """Story-point estimation accuracy by sprint and developer."""
        rows = bq_client.query_view("estimation_accuracy")
        if rows:
            return rows
        return [
            {"sprint": "SLS-Sprint-3", "developer": "alice", "estimated_points": 13, "completed_points": 11, "accuracy_ratio": 0.85},
            {"sprint": "SLS-Sprint-3", "developer": "bob", "estimated_points": 8, "completed_points": 10, "accuracy_ratio": 1.25},
            {"sprint": "SLS-Sprint-3", "developer": "carol", "estimated_points": 5, "completed_points": 5, "accuracy_ratio": 1.0},
            {"sprint": "SLS-Sprint-4", "developer": "alice", "estimated_points": 10, "completed_points": 9, "accuracy_ratio": 0.9},
            {"sprint": "SLS-Sprint-4", "developer": "bob", "estimated_points": 13, "completed_points": 8, "accuracy_ratio": 0.62},
            {"sprint": "SLS-Sprint-4", "developer": "carol", "estimated_points": 8, "completed_points": 8, "accuracy_ratio": 1.0},
        ]

    def oncall_noise(self) -> list[dict]:
        """On-call incident volume per developer (from PagerDuty)."""
        rows = bq_client.query_view("oncall_noise")
        if rows:
            return rows
        return [
            {"developer": "alice", "incidents": 12, "period": "last_30_days"},
            {"developer": "bob", "incidents": 3, "period": "last_30_days"},
            {"developer": "carol", "incidents": 1, "period": "last_30_days"},
        ]


metrics_service = MetricsService()
