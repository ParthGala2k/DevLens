"""FastAPI application factory.

Mounts the API routers and wires CORS + lifespan. Keep this thin — route logic lives in
`app/api/routes/*` and business logic in `app/services/*`.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alerts, bridge, chat, connectors, dashboard, mcp_log, team
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: initialize shared clients (BigQuery, Firestore, MCP session, event bus)
    #       and the background alert scanner here; tear them down on shutdown.
    yield


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
        return {"status": "ok"}

    return app


app = create_app()
