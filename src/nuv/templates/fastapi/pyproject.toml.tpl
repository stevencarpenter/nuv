[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "fastapi>=0.135",
    "granian>=2.7",
    "orjson>=3.11",
    "pydantic>=2.12",
    "pydantic-settings>=2.13",
]

[project.scripts]
{name} = "main:main"

[dependency-groups]
dev = [
    "httpx>=0.28",
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7",
    "ruff>=0.15.6",
    "ty>=0.0.23",
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
