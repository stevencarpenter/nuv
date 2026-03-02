[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "pyspark>=4,<5",
]

[project.scripts]
{name} = "main:main"

[dependency-groups]
dev = [
    "chispa>=0.11",
    "pytest>=9",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
notebooks = [
    "jupyterlab>=4",
    "marimo>=0.10",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov={module_name} --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
