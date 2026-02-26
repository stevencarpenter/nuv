[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov=main --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]
