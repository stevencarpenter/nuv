#!/usr/bin/env bash
# Drive the nuv CLI from this checkout in a scratch directory and record evidence.
# Usage: nuv-verify.sh <run-id> <init|doctor|nuv|in|tree|cleanup> ...   (see SKILL.md)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
RUN="${1:?usage: nuv-verify.sh <run-id> <init|doctor|nuv|in|tree|cleanup> ...}"
SUB="${2:?missing subcommand: init|doctor|nuv|in|tree|cleanup}"
shift 2
[[ "$RUN" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "run-id must match [A-Za-z0-9._-]+" >&2; exit 2; }

EVIDENCE="$REPO/.artifacts/verify-nuv/$RUN"
# The generated projects must use their own .venv, not the one of the calling shell.
unset VIRTUAL_ENV

load_scratch() {
    [[ -f "$EVIDENCE/scratch-path" ]] || { echo "run '$RUN' is not initialized: run init first" >&2; exit 2; }
    SCRATCH="$(cat "$EVIDENCE/scratch-path")"
    [[ -f "$SCRATCH/.nuv-verify-run" ]] || { echo "scratch directory is missing: $SCRATCH (run init with a new run-id)" >&2; exit 2; }
    # `--install editable` must not write to the real uv tool directories.
    export UV_TOOL_DIR="$SCRATCH/.uv-tools" UV_TOOL_BIN_DIR="$SCRATCH/.uv-bin"
}

# record <label> <expected-exit> <cwd> <cmd...>: run, save cmd/out/err/exit, compare the exit code.
record() {
    local label="$1" expect="$2" cwd="$3" code=0
    shift 3
    [[ "$label" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "label must match [A-Za-z0-9._-]+" >&2; exit 2; }
    printf 'cwd: %s\n$' "$cwd" >"$EVIDENCE/$label.cmd"
    printf ' %q' "$@" >>"$EVIDENCE/$label.cmd"
    printf '\n' >>"$EVIDENCE/$label.cmd"
    (cd "$cwd" && "$@") >"$EVIDENCE/$label.out" 2>"$EVIDENCE/$label.err" || code=$?
    echo "$code" >"$EVIDENCE/$label.exit"
    cat "$EVIDENCE/$label.cmd"
    echo "--- stdout"; cat "$EVIDENCE/$label.out"
    echo "--- stderr"; cat "$EVIDENCE/$label.err"
    echo "--- exit=$code expected=$expect evidence=$EVIDENCE/$label.{cmd,out,err,exit}"
    [[ "$code" == "$expect" ]]
}

# Parse: <label> [--expect N] [<dir>] -- <cmd...>
parse_run_args() {
    LABEL="${1:?missing label}"; shift
    EXPECT=0; DIR=""
    while [[ $# -gt 0 && "$1" != "--" ]]; do
        case "$1" in
            --expect) EXPECT="${2:?--expect needs a number}"; shift 2 ;;
            *) DIR="$1"; shift ;;
        esac
    done
    [[ "${1:-}" == "--" ]] || { echo "missing -- before the command" >&2; exit 2; }
    shift
    CMD=("$@")
}

case "$SUB" in
    init)
        [[ ! -e "$EVIDENCE" ]] || { echo "run '$RUN' already exists: $EVIDENCE (choose a new run-id)" >&2; exit 2; }
        (cd "$REPO" && uv sync --frozen)
        SCRATCH="$(mktemp -d "${NUV_VERIFY_SCRATCH_ROOT:-${TMPDIR:-/tmp}}/nuv-verify-$RUN.XXXXXX")"
        # Canonical path: doctor compares it with the `uv tool dir` output as text.
        SCRATCH="$(cd "$SCRATCH" && pwd -P)"
        touch "$SCRATCH/.nuv-verify-run"
        mkdir -p "$EVIDENCE"
        echo "$SCRATCH" >"$EVIDENCE/scratch-path"
        echo "evidence: $EVIDENCE"
        echo "scratch:  $SCRATCH"
        ;;
    doctor)
        load_scratch
        {
            echo "commit: $(git -C "$REPO" rev-parse --short HEAD)"
            echo "uncommitted files: $(git -C "$REPO" status --porcelain | wc -l | tr -d ' ')"
            echo "uv: $(uv --version)"
            echo "nuv module: $(uv run --project "$REPO" --frozen python -c 'import nuv; print(nuv.__file__)')"
            echo "nuv version: $(uv run --project "$REPO" --frozen python -c 'import importlib.metadata as m; print(m.version("nuv"))')"
            echo "scratch: $SCRATCH"
            echo "uv tool dir: $(uv tool dir)"
        } | tee "$EVIDENCE/doctor.txt"
        grep -q "^nuv module: $REPO/src/nuv/__init__.py$" "$EVIDENCE/doctor.txt" \
            || { echo "DOCTOR FAIL: nuv does not load from $REPO/src" >&2; exit 1; }
        grep -q "^uv tool dir: $SCRATCH/.uv-tools$" "$EVIDENCE/doctor.txt" \
            || { echo "DOCTOR FAIL: uv tool dir is not inside the scratch directory" >&2; exit 1; }
        echo "DOCTOR OK"
        ;;
    nuv)
        load_scratch
        parse_run_args "$@"
        record "$LABEL" "$EXPECT" "$SCRATCH/$DIR" uv run --project "$REPO" --frozen nuv ${CMD[@]+"${CMD[@]}"}
        ;;
    in)
        load_scratch
        parse_run_args "$@"
        record "$LABEL" "$EXPECT" "$SCRATCH/$DIR" "${CMD[@]}"
        ;;
    tree)
        load_scratch
        LABEL="${1:?missing label}"; DIR="${2:-}"
        (cd "$SCRATCH/$DIR" && find . \( -name .venv -o -name .uv-tools -o -name .uv-bin -o -name .nuv-verify-run \) -prune -o -print | sort) | tee "$EVIDENCE/$LABEL.tree"
        ;;
    cleanup)
        load_scratch
        rm -rf "$SCRATCH"
        echo "removed scratch: $SCRATCH"
        echo "evidence kept:   $EVIDENCE ($(find "$EVIDENCE" -type f | wc -l | tr -d ' ') files)"
        ;;
    *)
        echo "unknown subcommand: $SUB" >&2
        exit 2
        ;;
esac
