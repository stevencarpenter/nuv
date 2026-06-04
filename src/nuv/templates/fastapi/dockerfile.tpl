FROM {uv_docker_image} AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project --frozen

COPY . .
RUN uv sync --no-dev --frozen

FROM {python_docker_image}

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["granian", "--interface", "asgi", "{module_name}.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
