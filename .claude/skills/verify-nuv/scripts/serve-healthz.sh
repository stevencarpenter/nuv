#!/usr/bin/env bash
# Start a generated fastapi project on 127.0.0.1:<port>, print GET /healthz, then stop the server.
# Run it with the generated project as the current directory. Usage: serve-healthz.sh <port>
set -euo pipefail
PORT="${1:?usage: serve-healthz.sh <port>}"

uv run --frozen python main.py --host 127.0.0.1 --port "$PORT" >serve.log 2>&1 &
pid=$!
# Stop only the server that this script started.
trap 'kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null || true; echo "--- serve.log"; cat serve.log' EXIT

for _ in $(seq 1 50); do
    if curl -fsS "http://127.0.0.1:$PORT/healthz" 2>/dev/null; then
        echo
        exit 0
    fi
    sleep 0.2
done
echo "no answer from /healthz on port $PORT after 10 s" >&2
exit 1
