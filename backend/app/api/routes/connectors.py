"""Data Sync Panel endpoints: connector status + trigger Fivetran MCP sync."""

from fastapi import APIRouter

from app.services.connectors_service import connectors_service

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


@router.get("")
async def list_connectors() -> list[dict]:
    return connectors_service.list()


@router.post("/{connector}/sync")
async def sync_now(connector: str) -> dict:
    return await connectors_service.sync(connector)
