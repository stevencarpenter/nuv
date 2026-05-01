#!/usr/bin/env -S just --justfile

default: check

# Run everything in order: lint, test, build
all: lint test build

check: lint test

install:
    cd {{justfile_directory()}} && uv tool install .

# Run linter (ruff check + format)
lint:
    uv run ruff check --fix
    uv run ruff format

# Run all tests
test:
    uv run pytest

# Run the CLI
run *args:
    uv run nuv {{args}}

# Remove build artifacts
clean:
    rm -rf dist/ .coverage htmlcov/ __pycache__

# Build the package
build:
    uv build
