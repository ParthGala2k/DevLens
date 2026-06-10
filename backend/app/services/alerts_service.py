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
from app.services.workload_service import workload_service

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertsService:
    def get_all(self, limit: int = 50) -> list[dict]:
        alerts = fs_client.get_all("alerts")
        return sorted(alerts, key=lambda a: a.get("created_at", ""), reverse=True)[:limit]

    async def create(self, alert: dict) -> dict:
        alert.setdefault("id", str(uuid.uuid4()))
        alert.setdefault("created_at", _now())
        fs_client.set("alerts", alert["id"], alert)
        await bus.publish("alerts", alert)
        return alert

    async def scan(self) -> list[dict]:
        """Rule-based scan over real BigQuery metrics to auto-generate alerts."""
        created = []

        # ── PR review lag: flag any open PR (review bottleneck is immediate risk) ──
        lag = metrics_service.pr_review_lag()
        if lag:
            lag_sorted = sorted(lag, key=lambda r: r.get("days_open", 0), reverse=True)
            top = lag_sorted[0]
            detail = (
                f'"{top["title"]}" by {top["author"]} has been open '
                f'{top["days_open"]:.1f} day(s) with no review. '
                f'{len(lag_sorted)} PR(s) total are awaiting review.'
            )
            created.append(await self.create({
                "severity": "warning" if top.get("days_open", 0) >= 3 else "info",
                "title": f"PR #{top['pr_number']} waiting for review — {top['days_open']:.1f} day(s)",
                "detail": detail,
                "source": "github",
                "evidence": lag_sorted[:3],
            }))

        # ── Deep work: flag developers with high meeting load ──────────────────
        dw = metrics_service.deep_work()
        if dw:
            by_dev: dict = {}
            for r in dw:
                d = r["developer"]
                by_dev.setdefault(d, {"deep": 0.0, "meet": 0.0, "days": 0})
                by_dev[d]["deep"] += r.get("deep_work_hours", 0)
                by_dev[d]["meet"] += r.get("meeting_hours", 0)
                by_dev[d]["days"] += 1

            for dev, v in by_dev.items():
                avg_meet = v["meet"] / v["days"]
                avg_deep = v["deep"] / v["days"]
                if avg_meet > avg_deep:
                    created.append(await self.create({
                        "severity": "warning",
                        "title": f"{dev} spends more time in meetings than coding",
                        "detail": (
                            f"Avg {avg_meet:.1f}h/day in meetings vs "
                            f"{avg_deep:.1f}h/day of focused coding time. "
                            f"High meeting load reduces sprint throughput."
                        ),
                        "source": "calendar",
                        "evidence": [{"developer": dev, "avg_meeting_hours": round(avg_meet, 1), "avg_deep_work_hours": round(avg_deep, 1)}],
                    }))

        # ── Workload: flag the most overloaded developer ───────────────────────
        load = workload_service.load()
        if load:
            top = max(load, key=lambda r: r.get("load_score", 0))
            if top.get("load_score", 0) >= 50:
                created.append(await self.create({
                    "severity": "critical" if top["load_score"] >= 80 else "warning",
                    "title": f"{top['developer']} has the highest workload on the team",
                    "detail": (
                        f"Load score {top['load_score']:.0f}/100 — "
                        f"{top['open_issues']} open issues, "
                        f"{top['story_points_in_flight']} story points in flight, "
                        f"{top.get('prs_awaiting_review', 0)} PRs to review. "
                        f"Consider redistributing tickets before assigning more."
                    ),
                    "source": "jira",
                    "evidence": [top],
                }))

        return created


alerts_service = AlertsService()
