# Refusals and failures

`nuv new` refuses a name that cannot be a project and module name, refuses a target path that
exists, and reports a usage error for a bad option value. When a setup step fails after the
directory was created, `nuv` removes the directory unless `--keep-on-failure` was given. In each
case the exit code is non-zero and nothing that existed before changes.

## Sub-features

- `fail-name` refuses an invalid name with exit code `1` and creates nothing.
- `fail-exists` refuses an existing target with exit code `1` and leaves its content unchanged.
- `fail-usage` reports a bad `--python-version` or `--archetype` value with exit code `2`.
- `fail-sync-cleanup` removes the new directory when `uv sync` fails.
- `fail-sync-keep` keeps the new directory when `uv sync` fails and `--keep-on-failure` is set.

## How to get to it (user POV)

- Run `nuv new <invalid name>`.
- Run `nuv new <name>` where `./<name>` exists, or `nuv new <name> --at <existing path>`.
- Run `nuv new <name> --python-version <value that is not MAJOR.MINOR>` or `--archetype <unknown>`.
- Run `nuv new <name> --python-version <version that uv cannot find>`, with and without `--keep-on-failure`.

## Driving it with nuv-verify

Preconditions:

- The baseline in [README](./README.md) holds.
- The scratch directory has no `occupied`, `gone-tool`, or `kept-tool` entry.

- **Name with a space.** Run `nv nuv fail-name-space --expect 1 -- new "bad name"`. Stderr is `ERROR nuv.commands.new: Name cannot contain spaces.`
- **Empty name.** Run `nv nuv fail-name-empty --expect 1 -- new ""`. Stderr has `Name cannot be empty.`
- **Leading hyphen.** Run `nv nuv fail-name-hyphen --expect 1 -- new -- -x`. Stderr has `Name cannot start with a leading hyphen.`
- **Invalid character.** Run `nv nuv fail-name-chars --expect 1 -- new a.b`. Stderr has `Name contains invalid characters: 'a.b'`.
- **Path as a name.** First run `nv in fail-name-escape-pre --expect 1 -- test -e ../escape`. Exit code `1` shows that no `escape` entry exists beside the scratch directory. If it exits `0`, set `NUV_VERIFY_SCRATCH_ROOT` to an empty directory and start a new run. Then run `nv nuv fail-name-path --expect 1 -- new ../escape`. Stderr has `Name contains invalid characters: '../escape'`.
- **Trailing hyphen.** Run `nv nuv fail-name-edge --expect 1 -- new a-`. Stderr has `Name must start and end with a letter or digit.`
- **Keyword.** Run `nv nuv fail-name-keyword --expect 1 -- new class`. Stderr has `Name does not produce a valid Python module name: 'class'`.
- **Leading digit.** Run `nv nuv fail-name-digit --expect 1 -- new 1abc`. Stderr has `Name does not produce a valid Python module name: '1abc'`.
- **Nothing created.** Run `nv in fail-name-ls -- ls -A` and `nv in fail-name-escape --expect 1 -- test -e ../escape`. The listing has `.nuv-verify-run` and entries that other recipes of the same run made. It has none of `bad name`, `-x`, `a.b`, `a-`, `class`, or `1abc`. Exit code `1` of the second command shows that no `escape` directory exists beside the scratch directory.
- **Existing target.** Make a directory with content. Run `nv in fail-exists-setup -- sh -c 'mkdir occupied && echo keep > occupied/note.txt'`. Then run `nv nuv fail-exists --expect 1 -- new occupied`. Stderr has `Directory already exists: <scratch>/occupied`.
- **Existing `--at` target.** Run `nv nuv fail-at-exists --expect 1 -- new some-tool --at occupied`. Stderr has `Directory already exists: occupied`.
- **Content unchanged.** Run `nv tree fail-exists-tree occupied` and `nv in fail-exists-content -- cat occupied/note.txt`. The tree is `.` and `./note.txt`, and stdout is `keep`.
- **Bad version format.** Run `nv nuv fail-usage-pyver --expect 2 -- new x-tool --python-version 3.14.1`. Stderr has `Error: Invalid value for '--python-version': Python version must be MAJOR.MINOR (e.g. 3.14), got: '3.14.1'`.
- **Unknown archetype.** Run `nv nuv fail-usage-archetype --expect 2 -- new x-tool --archetype nope`. Stderr has `Error: Invalid value for '--archetype': 'nope' is not one of`.
- **Failed sync, cleanup.** Run `nv nuv fail-sync-cleanup --expect 1 -- new gone-tool --python-version 9.99`. Stderr has `No interpreter found for Python 9.99` from uv and ends with `ERROR nuv.commands.new: uv sync failed (exit 2)`. Then run `nv in fail-sync-cleanup-check --expect 1 -- test -e gone-tool`. Exit code `1` shows that the directory is gone.
- **Failed sync, keep.** Run `nv nuv fail-sync-keep --expect 1 -- new kept-tool --python-version 9.99 --keep-on-failure`. Stderr ends with `uv sync failed (exit 2)`. Then run `nv tree fail-sync-keep-tree kept-tool`. The tree has `pyproject.toml`, `main.py`, and `.python-version`, and has no `uv.lock`.
- **Proof.** Report the `.err` and `.exit` files of each refusal, `fail-name-ls.out`, `fail-name-escape.exit`, `fail-exists-tree.tree`, `fail-exists-content.out`, `fail-sync-cleanup-check.exit`, and `fail-sync-keep-tree.tree` from `.artifacts/verify-nuv/<run-id>/`.

## Gotchas

- Exit code `1` comes from `nuv` and exit code `2` comes from click usage errors. A refusal that changes from `1` to `2` or from `2` to `1` is a behavior change.
- A name that starts with `-` needs `--` before it, or click reads it as an option and exits `2`.
- `nuv new ""` reaches `nuv` with an empty name. A missing name argument is a different case: click exits `2` with `Missing argument 'NAME'`.
- Python `9.99` makes `uv sync` fail without a download. If uv ever ships a `9.99`, choose a different missing version.
- The failed-sync steps prove cleanup after a real `uv sync` failure only. Faults at other steps, and what happens to paths that existed before, are covered by the formal check in `.claude/skills/verify-run-new-safety/`.
- The existence check uses the path as the user gave it. The message shows an absolute path for `./<name>` and the given text for `--at`.
- `ls` hides dotfiles. A kept directory looks smaller in `ls` than it is. Use `nv tree`.
