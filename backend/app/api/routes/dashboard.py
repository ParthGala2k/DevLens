"""Sprint Health Dashboard endpoints: PR review lag, deep work, estimation accuracy."""

from fastapi import APIRouter

from app.services.metrics_service import metrics_service

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
