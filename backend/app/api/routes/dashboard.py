"""Sprint Health Dashboard endpoints: PR review lag, deep work, estimation accuracy."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/pr-review-lag")
async def pr_review_lag():
    """Which PRs are stuck, how long, and who's the bottleneck.

    TODO: MetricsService.pr_review_lag() -> queries BigQuery view `pr_review_lag`.
    """
    raise NotImplementedError


@router.get("/deep-work")
async def deep_work():
    """Deep-work time vs meeting fragmentation per day of week.

    TODO: MetricsService.deep_work() -> BigQuery view `deep_work_blocks`.
    """
    raise NotImplementedError


@router.get("/estimation-accuracy")
async def estimation_accuracy():
    """How often tickets are over/underestimated by sprint.

    TODO: MetricsService.estimation_accuracy() -> BigQuery view `estimation_accuracy`.
    """
    raise NotImplementedError
