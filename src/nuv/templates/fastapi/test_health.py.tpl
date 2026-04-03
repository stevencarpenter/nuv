import logging
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from {module_name}._logging import configure
from {module_name}.app import create_app, lifespan
from {module_name}.config import Settings
from {module_name}.dependencies import get_settings


# --- Main ---


def test_main_starts_granian():
    from main import main

    with patch("main.Granian") as mock_cls:
        mock_server = MagicMock()
        mock_cls.return_value = mock_server
        result = main([])
    assert result == 0
    mock_server.serve.assert_called_once()


# --- App ---


def test_create_app_has_healthz():
    app = create_app()
    paths = [route.path for route in app.routes]
    assert "/healthz" in paths


def test_create_app_uses_custom_settings():
    settings = Settings(app_name="custom")
    app = create_app(settings)
    assert app.state.settings.app_name == "custom"


async def test_lifespan_runs():
    app = create_app()
    async with lifespan(app):
        pass


# --- Health ---


async def test_healthz_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {{"status": "ok"}}


# --- Config ---


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.app_name == "{name}"
    assert settings.debug is False
    assert settings.log_level == "WARNING"


# --- Dependencies ---


async def test_get_settings_returns_app_settings() -> None:
    settings = Settings(app_name="dep-test")
    app = create_app(settings)
    mock_request = MagicMock()
    mock_request.app = app
    result = await get_settings(mock_request)
    assert result.app_name == "dep-test"


# --- Logging ---


def test_configure_sets_level() -> None:
    configure("DEBUG")
    assert logging.getLogger().level == logging.DEBUG
