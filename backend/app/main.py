"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alerts, bridge, chat, connectors, dashboard, mcp_log, team
from app.config import settings

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("DevLens starting — project=%s model=%s", settings.google_cloud_project, settings.gemini_model)
    # Warm up singletons eagerly so the first request isn't slow.
    from app.integrations.bigquery_client import bq_client  # noqa: F401
    from app.integrations.firestore_client import fs_client  # noqa: F401
    from app.integrations.mcp.activity_log import recent_calls  # noqa: F401
    yield
    log.info("DevLens shutting down")


def create_app() -> FastAPI:
    app = FastAPI(title="DevLens API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(connectors.router)
    app.include_router(dashboard.router)
    app.include_router(team.router)
    app.include_router(bridge.router)
    app.include_router(alerts.router)
    app.include_router(chat.router)
    app.include_router(mcp_log.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "project": settings.google_cloud_project}

    return app


app = create_app()
