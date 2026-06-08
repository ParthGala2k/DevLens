"""Developer observability endpoints: workload + completion reliability."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/team", tags=["team"])


@router.get("/workload")
async def workload():
    """Per-developer load score for the workload heatmap.

    TODO: WorkloadService.load() -> BigQuery view `developer_load`.
    """
    raise NotImplementedError


@router.get("/reliability")
async def reliability():
    """Per-developer, per-sprint completion reliability for the reliability table.

    TODO: WorkloadService.reliability() -> BigQuery view `completion_reliability`.
    """
    raise NotImplementedError
