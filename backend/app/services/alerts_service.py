"""Proactive alert generation + persistence.

Combines rule-based scans with agent synthesis to produce human-readable alerts,
persists to Firestore `alerts`, and publishes to the event bus "alerts" channel.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.events.bus import bus
from app.integrations.firestore_client import fs_client
from app.services.metrics_service import metrics_service

log = logging.getLogger(__name__)

_DEMO_ALERTS = [
    {
        "id": "alert-demo-001",
        "severity": "warning",
        "title": "alice has 3 PRs awaiting review for 5+ days",
        "detail": "PR #42 (Add OAuth middleware) has been open 7.2 days with no reviewer assigned. This blocks the auth refactor milestone.",
        "source": "github",
        "evidence": [{"pr": 42, "days_open": 7.2}, {"pr": 37, "days_open": 5.0}],
        "created_at": "2026-06-08T09:00:00Z",
    },
    {
        "id": "alert-demo-002",
        "severity": "warning",
        "title": "bob is in meetings 22h this week — deep-work time critically low",
        "detail": "bob has only 1.5h of uninterrupted work blocks this week vs 22h in meetings. Sprint velocity risk.",
        "source": "calendar",
        "evidence": [{"developer": "bob", "meeting_hours": 22.0, "deep_work_hours": 1.5}],
        "created_at": "2026-06-08T09:01:00Z",
    },
    {
        "id": "alert-demo-003",
        "severity": "critical",
        "title": "alice absorbed 80% of on-call incidents last 30 days",
        "detail": "alice handled 12 of 16 PagerDuty incidents (75%). This on-call skew correlates with her low sprint completion ratio (0.67).",
        "source": "cross",
        "evidence": [{"developer": "alice", "incidents": 12, "total": 16}],
        "created_at": "2026-06-08T09:02:00Z",
    },
    {
        "id": "alert-demo-004",
        "severity": "info",
        "title": "SLS-47 jira ticket has no linked GitHub issue",
        "detail": "SLS-47 (Instrument API latency) was accepted in sprint planning but has no corresponding GitHub issue. Likely fell through the cracks.",
        "source": "jira",
        "evidence": [{"jira_key": "SLS-47", "sprint": "SLS-Sprint-4"}],
        "created_at": "2026-06-08T09:03:00Z",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertsService:
    def _seed_demo_if_empty(self) -> None:
        existing = fs_client.get_all("alerts")
        if not existing:
            for a in _DEMO_ALERTS:
                fs_client.set("alerts", a["id"], a)

    def get_all(self, limit: int = 50) -> list[dict]:
        self._seed_demo_if_empty()
        alerts = fs_client.get_all("alerts")
        return sorted(alerts, key=lambda a: a.get("created_at", ""), reverse=True)[:limit]

    async def create(self, alert: dict) -> dict:
        alert.setdefault("id", str(uuid.uuid4()))
        alert.setdefault("created_at", _now())
        fs_client.set("alerts", alert["id"], alert)
        await bus.publish("alerts", alert)
        return alert

    async def scan(self) -> list[dict]:
        """Rule-based scan over metrics to auto-generate alerts."""
        created = []

        lag = metrics_service.pr_review_lag()
        stale = [r for r in lag if r.get("days_open", 0) >= 5]
        if stale:
            for row in stale[:3]:
                alert = {
                    "severity": "warning",
                    "title": f"PR #{row['pr_number']} open {row['days_open']:.1f} days without review",
                    "detail": f'"{row["title"]}" by {row["author"]} needs a reviewer.',
                    "source": "github",
                    "evidence": [row],
                }
                created.append(await self.create(alert))

        return created


alerts_service = AlertsService()
