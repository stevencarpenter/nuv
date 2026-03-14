[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "fastapi>=0.115",
    "granian>=2",
    "orjson>=3",
    "pydantic-settings>=2",
]

[project.scripts]
{name} = "main:main"

[dependency-groups]
dev = [
    "httpx>=0.28",
    "pytest>=9",
    "pytest-asyncio>=0.25",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov=main --cov={module_name} --cov-report=term-missing --cov-fail-under=100"
asyncio_mode = "auto"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[tool.hatch.build.targets.wheel]
packages = ["src/{module_name}"]
include = ["main.py"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
