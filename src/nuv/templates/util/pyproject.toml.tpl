[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
# Lean on purpose: click is the only runtime dependency. `uv add <pkg>` as the tool grows.
dependencies = [
    "click>=8.5.0",
]

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "ruff>=0.17.3",
    "ty>=0.0.92",
]

[tool.uv]
managed = true

[tool.uv.build-backend]
module-name = "{module_name}"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[build-system]
requires = ["uv_build>=0.13.6,<0.14.0"]
build-backend = "uv_build"
