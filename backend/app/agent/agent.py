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
    """Stand-in used when google-adk isn't importable or Vertex AI isn't configured.

    Responses are built entirely from live BigQuery data via the service layer.
    Returns an empty/no-data message when BigQuery has no rows for a metric.
    """

    name = "devlens-mock"

    async def run_async(self, session_id: str, message: str):
        import re
        from app.services.metrics_service import metrics_service
        from app.services.workload_service import workload_service

        msg = message.lower()

        def has(words: list[str]) -> bool:
            """Whole-word match — prevents 'pr' matching inside 'sprint'."""
            return any(re.search(r'\b' + re.escape(w) + r'\b', msg) for w in words)

        # ── Route by topic — most specific first ──────────────────────────────
        if has(["sprint", "reliability", "completion", "velocity"]):
            rel = workload_service.reliability()
            if not rel:
                text = "No sprint completion data is available yet. Check back after the next Fivetran sync."
            else:
                current = [r for r in rel if "3" in r.get("sprint", "") or "active" in r.get("sprint", "").lower()]
                rows = current or rel
                text = "## Sprint Completion Reliability\n\n"
                for r in sorted(rows, key=lambda x: x.get("completion_ratio", 0)):
                    pct = int(r.get("completion_ratio", 0) * 100)
                    icon = "✓" if pct >= 100 else "⚠" if pct >= 75 else "✗"
                    text += (
                        f"- {icon} **{r['developer']}** ({r.get('sprint', '—')}): "
                        f"{r.get('completed', 0)}/{r.get('assigned', 0)} tickets completed ({pct}%), "
                        f"avg {r.get('avg_cycle_time_days', 0):.1f} days per ticket\n"
                    )

        elif has(["overload", "load", "busy", "capacity", "workload", "who is most"]):
            load = workload_service.load()
            if not load:
                text = "No workload data is available yet. Check back after the next Fivetran sync."
            else:
                top = max(load, key=lambda r: r.get("load_score", 0))
                least = min(load, key=lambda r: r.get("load_score", 0))
                text = (
                    f"## Team Workload\n\n"
                    f"**{top['developer']}** currently has the highest load — "
                    f"**{top['load_score']:.0f}/100** load score, "
                    f"{top['open_issues']} open issues, "
                    f"{top['story_points_in_flight']} story points in flight, "
                    f"and {top.get('prs_awaiting_review', 0)} PRs waiting for their review.\n\n"
                    f"**{least['developer']}** has the most capacity right now ({least['load_score']:.0f}/100) "
                    f"and would be the best person to assign new work to."
                )

        elif has(["pull request", "review lag", "pr lag", "bottleneck", "waiting for review", "prs", "pr review"]) or \
             (has(["lag"]) and not has(["sprint"])):
            lag = metrics_service.pr_review_lag()
            if not lag:
                text = "No open pull requests awaiting review were found."
            else:
                lag_sorted = sorted(lag, key=lambda r: r.get("days_open", 0), reverse=True)
                top = lag_sorted[0]
                critical = sum(1 for r in lag_sorted if r.get("days_open", 0) >= 5)
                text = (
                    f"## PR Review Lag\n\n"
                    f"There are **{len(lag_sorted)} open pull requests** waiting for review.\n\n"
                    f"The longest-waiting is **PR #{top['pr_number']}** — "
                    f"*{top['title']}* by {top['author']}, "
                    f"open for **{top['days_open']:.1f} days** with no reviewer assigned."
                )
                if critical:
                    text += f"\n\n{critical} PR(s) have been waiting more than 5 days — these are blocking their authors from moving forward."
                if len(lag_sorted) > 1:
                    text += "\n\n**All open PRs:**\n"
                    for r in lag_sorted:
                        text += f"- PR #{r['pr_number']}: *{r['title']}* by {r['author']} — {r['days_open']:.1f}d\n"

        elif has(["estimation", "estimate", "accuracy", "story point", "underestimate"]):
            est = metrics_service.estimation_accuracy()
            if not est:
                text = "No estimation accuracy data is available yet. Check back after the next Fivetran sync."
            else:
                worst = min(est, key=lambda r: r.get("accuracy_ratio", 1))
                text = (
                    f"## Estimation Accuracy\n\n"
                    f"**{worst['developer']}** had the biggest gap this sprint — "
                    f"completed **{worst.get('completed_points', 0)} points** out of "
                    f"**{worst.get('estimated_points', 0)} estimated** "
                    f"(ratio: {worst['accuracy_ratio']:.2f}).\n\n"
                    f"A ratio below 1.0 means the team under-delivered vs their commitment. "
                    f"Above 1.0 means they over-delivered."
                )

        elif has(["deep work", "focus", "focus time", "meeting", "calendar", "interrupt", "block"]):
            dw = metrics_service.deep_work()
            if not dw:
                text = "No calendar or deep work data is available yet. Check back after the next Fivetran sync."
            else:
                by_dev: dict = {}
                for r in dw:
                    d = r["developer"]
                    by_dev.setdefault(d, {"deep": 0.0, "meet": 0.0, "days": 0})
                    by_dev[d]["deep"] += r.get("deep_work_hours", 0)
                    by_dev[d]["meet"] += r.get("meeting_hours", 0)
                    by_dev[d]["days"] += 1
                avgs = {d: {"deep": v["deep"] / v["days"], "meet": v["meet"] / v["days"]} for d, v in by_dev.items()}
                worst_dev = min(avgs.items(), key=lambda kv: kv[1]["deep"])
                best_dev = max(avgs.items(), key=lambda kv: kv[1]["deep"])
                text = (
                    f"## Deep Work vs Meetings\n\n"
                    f"**{worst_dev[0]}** has the least uninterrupted coding time — "
                    f"averaging **{worst_dev[1]['deep']:.1f}h/day** of focused work "
                    f"against **{worst_dev[1]['meet']:.1f}h/day** in meetings.\n\n"
                    f"**{best_dev[0]}** has the most focus time at {best_dev[1]['deep']:.1f}h/day. "
                    f"High meeting load is a common cause of missed sprint commitments."
                )

        elif has(["assign", "who should", "next ticket", "give to"]):
            load = workload_service.load()
            if not load:
                text = "No workload data is available yet to make an assignment recommendation."
            else:
                least = min(load, key=lambda r: r.get("load_score", 999))
                most = max(load, key=lambda r: r.get("load_score", 0))
                text = (
                    f"## Assignment Recommendation\n\n"
                    f"Based on current workload, assign the next ticket to **{least['developer']}** — "
                    f"they have a load score of {least['load_score']:.0f}/100 with "
                    f"{least['open_issues']} open issues and {least['story_points_in_flight']} points in flight.\n\n"
                    f"Hold off on giving more to **{most['developer']}** for now — "
                    f"their load score is {most['load_score']:.0f}/100."
                )

        elif any(k in msg for k in ("sync", "fivetran", "data")):
            text = (
                "## Data Sync Status\n\n"
                "Fivetran syncs GitHub, Jira, and Google Calendar into BigQuery on a regular schedule.\n\n"
                "- **GitHub** — open issues, pull requests, commit activity\n"
                "- **Jira** — sprint tickets, story points, assignees\n"
                "- **Google Calendar** — meeting hours per developer\n\n"
                "Use the **Data Sources** panel to check last sync times or trigger a manual refresh."
            )

        else:
            text = (
                "I'm DevLens — a Gemini-powered agent that analyses your team's GitHub, Jira, "
                "and Google Calendar data to surface productivity insights.\n\n"
                "Here are some things you can ask me:\n"
                "- Who is most overloaded right now?\n"
                "- Which PRs have been waiting for review the longest?\n"
                "- How is estimation accuracy trending this sprint?\n"
                "- How much deep work time is the team getting?\n"
                "- Who should I assign the next ticket to?\n"
                "- Show me sprint completion reliability\n\n"
                "What would you like to know?"
            )

        yield _MockEvent(text)


class _MockEvent:
    def __init__(self, text: str) -> None:
        self._text = text

    def is_final_response(self) -> bool:
        return True

    @property
    def content(self):
        return _MockContent(self._text)


class _MockContent:
    def __init__(self, text: str) -> None:
        self.role = "model"
        p = _MockPart(text)
        self.parts = [p]


class _MockPart:
    def __init__(self, text: str) -> None:
        self.text = text
        self.function_call = None
        self.function_response = None
