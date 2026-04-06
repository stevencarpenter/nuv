FROM ghcr.io/astral-sh/uv:python{python_version}-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project --frozen

COPY . .
RUN uv sync --no-dev --frozen

FROM python:{python_version}-slim-bookworm

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["granian", "--interface", "asgi", "{module_name}.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
