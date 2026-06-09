"""Developer observability endpoints: workload + completion reliability."""

from fastapi import APIRouter

from app.services.workload_service import workload_service

router = APIRouter(prefix="/api/team", tags=["team"])


@router.get("/workload")
async def workload() -> list[dict]:
    return workload_service.load()


@router.get("/reliability")
async def reliability() -> list[dict]:
    return workload_service.reliability()
