from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from {module_name}.app import create_app
from {module_name}.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(app_name="{name}", debug=True)


@pytest.fixture
async def client(settings: Settings) -> AsyncIterator[AsyncClient]:
    app = create_app(settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
