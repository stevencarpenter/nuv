[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "polars>=1",
    "duckdb>=1",
    "deltalake>=0.20",
    "pydantic-settings>=2",
    "click>=8",
]

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
notebooks = [
    "marimo>=0.10",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov=main --cov={module_name} --cov-report=term-missing --cov-fail-under=90"

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