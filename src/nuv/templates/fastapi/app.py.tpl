"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from {module_name}.config import Settings
from {module_name}.routes import register_routes


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = Settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    app.state.settings = settings
    register_routes(app)
    return app
