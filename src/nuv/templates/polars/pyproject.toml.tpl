[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "polars>=1.41.2",
    "pyarrow>=24.0.0",
    "duckdb>=1.5.3",
    "deltalake>=1.6.0",
    "pydantic-settings>=2.14.1",
    "click>=8.4.1",
]

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.15",
    "ty>=0.0.43",
]
notebooks = [
    "marimo>=0.23.8",
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

[tool.ruff.lint.per-file-ignores]
"notebooks/*.py" = ["B018"]

[tool.ty.src]
exclude = ["notebooks"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[tool.hatch.build.targets.wheel]
packages = ["src/{module_name}"]
include = ["main.py"]

[build-system]
requires = ["hatchling>=1.29.0"]
build-backend = "hatchling.build"
