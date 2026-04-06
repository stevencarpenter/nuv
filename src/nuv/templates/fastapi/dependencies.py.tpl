"""Shared FastAPI dependencies."""

from fastapi import Request

from {module_name}.config import Settings


async def get_settings(request: Request) -> Settings:
    return request.app.state.settings
