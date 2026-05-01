[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "pyspark>=4.1.1,<5",
]

[project.scripts]
{name} = "main:main"

[dependency-groups]
dev = [
    "chispa>=0.12.0",
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.12",
    "ty>=0.0.33",
]
notebooks = [
    "jupyterlab>=4.5.7",
    "marimo>=0.23.4",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov=main --cov={module_name} --cov-report=term-missing --cov-fail-under=100"

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
include = ["main.py", "_logging.py"]

[build-system]
requires = ["hatchling>=1.29.0"]
build-backend = "hatchling.build"
