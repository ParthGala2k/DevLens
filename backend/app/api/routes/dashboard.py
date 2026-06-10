"""Sprint Health Dashboard endpoints: PR review lag, deep work, estimation accuracy, sprints."""

import logging

from fastapi import APIRouter

from app.services.metrics_service import metrics_service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/pr-review-lag")
async def pr_review_lag() -> list[dict]:
    return metrics_service.pr_review_lag()


@router.get("/deep-work")
async def deep_work() -> list[dict]:
    return metrics_service.deep_work()


@router.get("/estimation-accuracy")
async def estimation_accuracy() -> list[dict]:
    return metrics_service.estimation_accuracy()


@router.get("/sprint-prediction")
async def sprint_prediction() -> dict:
    """Velocity-based completion forecast for the active sprint.

    Uses real Jira issue status + story points from BigQuery.
    Sprint progress is measured against the sprint's own start/end dates so the
    maths work correctly regardless of when the query runs.
    """
    try:
        from app.integrations.bigquery_client import bq_client
        from app.config import settings
        P = settings.bigquery_project
        J = settings.bigquery_dataset_jira

        rows = bq_client.query(f"""
            WITH sprint AS (
              SELECT
                name,
                CAST(start_date AS DATE) AS start_date,
                CAST(end_date   AS DATE) AS end_date,
                DATE_DIFF(CAST(end_date AS DATE), CAST(start_date AS DATE), DAY) AS total_days
              FROM `{P}.{J}.sprint`
              WHERE state = 'active'
              LIMIT 1
            ),
            story_points AS (
              SELECT issue_id, CAST(value AS FLOAT64) AS pts
              FROM `{P}.{J}.issue_field_history`
              WHERE field_id = 'customfield_10016' AND is_active = TRUE AND value IS NOT NULL
            ),
            issues AS (
              SELECT
                i.id,
                sc.name AS status_category,
                IFNULL(sp.pts, 0) AS pts
              FROM `{P}.{J}.issue` i
              JOIN `{P}.{J}.status_category` sc ON sc.id = i.status_category
              LEFT JOIN story_points sp ON sp.issue_id = i.id
              WHERE (i._fivetran_deleted IS FALSE OR i._fivetran_deleted IS NULL)
            )
            SELECT
              s.name                                                      AS sprint_name,
              s.start_date,
              s.end_date,
              s.total_days,
              -- Clamp "today" to the sprint window so velocity maths are always valid
              DATE_DIFF(
                LEAST(GREATEST(CURRENT_DATE(), s.start_date), s.end_date),
                s.start_date, DAY
              )                                                            AS days_elapsed,
              DATE_DIFF(s.end_date,
                LEAST(GREATEST(CURRENT_DATE(), s.start_date), s.end_date),
                DAY
              )                                                            AS days_remaining,
              COUNTIF(iss.status_category = 'Done')                       AS done_count,
              COUNT(*)                                                     AS total_count,
              SUM(CASE WHEN iss.status_category = 'Done' THEN iss.pts ELSE 0 END)  AS done_pts,
              SUM(iss.pts)                                                 AS total_pts
            FROM sprint s, issues iss
            GROUP BY s.name, s.start_date, s.end_date, s.total_days
        """)

        if not rows:
            return {}

        r = rows[0]
        total_pts    = r["total_pts"] or 0
        done_pts     = r["done_pts"] or 0
        days_elapsed = max(r["days_elapsed"] or 1, 1)
        days_remaining = max(r["days_remaining"] or 0, 0)
        total_days   = r["total_days"] or 1

        velocity_per_day = done_pts / days_elapsed
        projected_pts    = min(done_pts + velocity_per_day * days_remaining, total_pts)
        predicted_pct    = round((projected_pts / total_pts * 100) if total_pts else 0)
        current_pct      = round((done_pts / total_pts * 100) if total_pts else 0)

        return {
            "sprint_name":     r["sprint_name"],
            "end_date":        str(r["end_date"])[:10],
            "days_remaining":  days_remaining,
            "total_days":      total_days,
            "done_pts":        int(done_pts),
            "total_pts":       int(total_pts),
            "done_count":      r["done_count"],
            "total_count":     r["total_count"],
            "current_pct":     current_pct,
            "predicted_pct":   predicted_pct,
            "velocity_per_day": round(velocity_per_day, 1),
        }
    except Exception as exc:
        log.warning("Sprint prediction failed: %s", exc)
        return {}


@router.get("/sprints")
async def sprints() -> list[dict]:
    """Return sprint list from Jira BigQuery. Returns empty list if unavailable."""
    try:
        from app.integrations.bigquery_client import bq_client
        from app.config import settings
        rows = bq_client.query(
            f"SELECT id, name, state, start_date, end_date "
            f"FROM `{settings.bigquery_project}.{settings.bigquery_dataset_jira}.sprint` "
            f"ORDER BY start_date LIMIT 20"
        )
        result = []
        for r in rows:
            result.append({
                "id": str(r.get("id", "")),
                "name": r.get("name", ""),
                "state": (r.get("state") or "future").lower(),
                "start_date": str(r["start_date"])[:10] if r.get("start_date") else None,
                "end_date": str(r["end_date"])[:10] if r.get("end_date") else None,
            })
        return result
    except Exception as exc:
        log.warning("Sprint BQ query failed: %s", exc)
        return []
