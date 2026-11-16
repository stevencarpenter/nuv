---
name: verify-run-new-safety
description: Check that `nuv new` (`run_new` in `src/nuv/commands/new.py`) cannot delete or change a path that existed before the command, cannot write outside its target, and cleans up or keeps a failed run as promised. The check runs the real code for every target pre-state, archetype, install mode, and a fault at every filesystem and subprocess step. Use it before and after any change to `run_new`, `resolve_target`, `scaffold_files`, a `_scaffold_*` function, `run_uv_sync`, `run_tool_install`, the failure cleanup (`shutil.rmtree`, `--keep-on-failure`), or `--at` handling.
---

# Verify the data safety of `nuv new`

`run_new` holds the only destructive call in this repo: `shutil.rmtree(target)` at
`src/nuv/commands/new.py:485`. Unit tests cover a few examples of the failure path with a mocked
`uv`. This check covers every case in a stated scope.

## The promise and the harm

**Property.** `nuv new` changes nothing that existed before it ran, writes only inside the
directory it creates, tells the truth about failure in its exit code, and after a failure
removes what it wrote, or keeps it when the user gave `--keep-on-failure`.

**Harm when it breaks.** A user loses files that `nuv` did not create, or gets files in a
directory they did not name, or sees success for a project that is incomplete.

The script checks five named properties. Each is one sentence in `PROPERTIES` in the script:

| Property | Statement |
| --- | --- |
| `NO-HARM` | A path that existed before the command still exists with the same type and content. |
| `CONTAINED` | The command creates paths only at the target, under it, or as missing parents of it. It creates nothing when the target path existed. |
| `HONEST-EXIT` | `run_new` returns `0` only when no step failed and the target did not exist before. |
| `KEEP` | With `keep_on_failure`, a failed run removes nothing that it wrote. |
| `CLEAN` | Without `keep_on_failure`, a failed run leaves no new path. |

## Does your change touch the verified code?

Coverage record. The check describes this code at sync commit **`e6b2e65`**.

| Code in `src/nuv/commands/new.py` | What the check depends on |
| --- | --- |
| `run_new` (line 452) | The order validate, `resolve_target`, `target.mkdir(parents=True)`, `created_target = True`, `scaffold_files`, `run_uv_sync`, `run_tool_install`. The `except (ValueError, RuntimeError, OSError)` clause and its `shutil.rmtree` condition. |
| `resolve_target` (line 445) | The refusal when the target path exists, for the default path and for `--at`. |
| `scaffold_files` (line 218) and every `_scaffold_*` function | Every `Path.mkdir` and `Path.write_text` call is one step. |
| `write_with_trailing_newline` (line 87), `render_template` (line 56) | Every `Path.write_text` and `Path.read_text` call is one step. |
| `run_uv_sync` (line 414), `run_tool_install` (line 426) | Every `shutil.which` and `subprocess.run` call is one step. |
| `ARCHETYPES`, `INSTALL_MODES` | The check enumerates both tuples. A new archetype or mode is included without an edit. |

To see whether the covered code changed since the sync commit:

```bash
git diff --stat e6b2e65 -- src/nuv/commands/new.py
```

Output means the code changed after the last confirmation. Run both commands below, then follow
"When a change is intended". A template change (`src/nuv/templates/`) needs only a rerun: the
check reads the real templates and takes the step list from the real run.

Not covered: `validate_name`, `validate_python_version`, and `src/nuv/cli.py`. See
"What the check does not cover".

## Run the check

Run both commands from the repo root. They need no network and they never start `uv` from
inside the check.

```bash
uv run --frozen python .claude/skills/verify-run-new-safety/check_run_new_safety.py
uv run --frozen python .claude/skills/verify-run-new-safety/check_run_new_safety.py --mutants
```

- The first command is the check. It took 48 seconds on an 18-core Mac and runs about
  24,000 cases. With one core it takes about 4 minutes.
- The second command proves that the check can fail. It applies five broken variants of
  `new.py` in memory, one for each property, and requires a new violation of that property from
  each. It takes about 3 seconds. It does not edit `new.py`.

The Python version comes from `.python-version` and `uv.lock`. The check uses only the standard
library.

Run the first command before you change the covered code, to see the starting state, and again
after the change. Run the second command after any edit to the check script or to the covered
code.

## Read the result

The last line is the result. Exit code `0` is `PASS`, exit code `1` is `FAIL`, and exit code `2`
means that `nuv` did not load from this checkout.

| Output | Meaning | Action |
| --- | --- | --- |
| `RESULT: PASS (no new violation, 2 known findings still present)` | The state at the sync commit. | None. |
| `<PROPERTY> NEW VIOLATION in N cases` | The code breaks a property in a case that the known findings do not explain. | See "A new violation". |
| `STALE known finding <id>` | No case shows that finding now. | Confirm that the change fixed it on purpose. Then remove the entry from `KNOWN_FINDINGS` in the script and from "Known findings" below. |
| `BASELINE the check itself is not valid` | A fault-free run failed, an injected fault did not fire, or the code created a path through a call that the check does not instrument. | See "A modeling error". |
| `MISSED <PROPERTY> mutant` (with `--mutants`) | The check no longer sees a broken variant. A `PASS` of that property means nothing. | Find what changed in the check or in the code path. Do not delete the mutant. |
| `STALE <PROPERTY> mutant` (with `--mutants`) | The text that the mutant replaces is not in `new.py` exactly once. | Update the `old` text in `MUTANTS` so that the variant breaks the same guard in the new code. Then rerun. |

Each violation prints a counterexample as steps in the words of the code:

```
  NO-HARM: existing paths were removed or changed: work/demo-app
    target pre-state: empty-dir, no --at
    run_new("demo-app", archetype="script", install_mode="editable", keep_on_failure=False)
    step 2: write_text(work/demo-app/.python-version) -> oserror
    run_new returned 1
```

Read it as: before the command, the target path held the named pre-state. `run_new` ran with
these arguments. Its second filesystem or subprocess step was that `write_text` call, and the
check made it raise `OSError`. `run_new` returned `1`. Afterward `work/demo-app`, which existed
before, was gone or different. Paths are relative to a temporary sandbox. `work` is the current
directory of the command and `outside` is a directory that only symlinks reach.

### A new violation

Treat it as a real bug until you show otherwise.

1. Read the counterexample and find the step in `new.py`.
2. Reproduce it by hand if it is not clear: make the pre-state in a scratch directory and run
   the command with the `verify-nuv` skill.
3. If your change caused it, fix your change. If the violation is in code that you did not
   change, report it to the user with the counterexample. Do not change product code to fix it
   unless the user asks.
4. Never add an entry to `KNOWN_FINDINGS`, weaken a statement in `PROPERTIES`, or remove a
   pre-state or a fault to get a `PASS`. A new known finding needs the user's decision.

### A modeling error

The check is wrong, not the code, in these cases:

- `BASELINE ... paths created by a call that the check does not instrument`. The code now writes
  with a call other than `Path.mkdir` or `Path.write_text` (for example `open`, `shutil.copy`,
  or `os.makedirs`). No fault is injected at that call. Add a wrapper for the new call in
  `instrumented()` and a fault list for it in `FAULTS`. Then rerun both commands.
- `BASELINE ... a fault-free run did not return 0`. `run_new` now needs something that the
  sandbox does not give, such as a new subprocess or a new argument. Update `run_case()` or the
  replaced `which` and `run` functions in `instrumented()`.
- A violation whose counterexample needs a step that cannot happen in the real code. Check the
  atomicity rules in "Scope" before you decide this. If the rule is wrong, fix the rule and state
  the change to the user.

## Known findings at the sync commit

The current code breaks `CLEAN` in two ways. The check reports both on every run. Neither one
loses user data. Product code was not changed.

- **`F1-new-parents-remain`** (1,962 cases). `nuv new demo-app --at deep/nested/demo-app` where
  `deep` does not exist. `target.mkdir(parents=True)` at `new.py:472` creates `deep` and
  `deep/nested`. A later step fails. `run_new` removes only `target` at `new.py:485`, so the
  empty directories `deep` and `deep/nested` remain. When the failure is in the `mkdir` of a
  parent, `created_target` is still false and nothing is removed.
- **`F2-uncaught-exception-keeps-target`** (4,536 cases). A step raises an exception that the
  `except` clause at `new.py:483` does not name, for example `KeyboardInterrupt` when the user
  presses Ctrl-C during `uv sync`, or `KeyError` from a bad placeholder in a template.
  `run_new` does not return. The partial target remains although `--keep-on-failure` was not
  given, and the next `nuv new` with the same name is refused with `Directory already exists`.

## Scope

A `PASS` covers exactly this enumeration, against the real `run_new` on a real temporary
filesystem:

- Every archetype in `ARCHETYPES` (6) and every mode in `INSTALL_MODES` (3).
- `keep_on_failure` false and true.
- Ten pre-states of the target path: absent, absent with two missing parents, absent under a
  symlinked parent, empty directory, directory with files, regular file, symlink to a directory,
  symlink to a file, dangling symlink, and a path whose parent is a regular file.
- Three ways to name the target: no `--at`, `--at` with an absolute path, and `--at` with a
  relative path.
- One fault-free run for each combination, and then one run for each step of that run and each
  fault for that step: `OSError`, `OSError` after half of the file was written, an exception
  type that `run_new` does not catch (`KeyError`), `uv` missing from `PATH`, a non-zero exit of
  `uv sync` or `uv tool install`, and `KeyboardInterrupt` at a subprocess step.

Atomicity rules. One step is one call of `Path.mkdir`, `Path.write_text`, `Path.read_text`,
`shutil.which`, or `subprocess.run`. A fault replaces the call, so the call has no effect,
except for the partial-write fault. `mkdir(parents=True)` shows as several steps because pathlib
calls `mkdir` once for each missing parent. At most one fault occurs in a run.

Assumptions. The project name is the fixed valid name `demo-app`. `uv` is replaced: a successful
`uv sync` and `uv tool install` write nothing. The sandbox holds a sibling file, a sibling
directory, and an outside directory, and every one of their paths is compared before and after
by type, content, inode, and modification time. A directory is compared by inode and mode only,
because a new child changes the modification time of an expected parent.

## What the check does not cover

- Name validation (`validate_name`). A name that passes validation but is unsafe as a path is
  outside this check.
- The click layer in `src/nuv/cli.py`, and exit codes of the `nuv` process.
- What the real `uv` writes. `uv tool install --editable` writes to the uv tool directories,
  which are outside the target by design. The `verify-nuv` skill drives the real `uv`.
- Two faults in one run, and a failure of `shutil.rmtree` itself. `rmtree` runs with
  `ignore_errors=True`, so a failed cleanup is silent.
- Another process that changes the directory during the run.
- An interrupt between two steps. `KeyboardInterrupt` is injected only at subprocess steps.
- Windows, hard links, special files, and permission changes.

## When a change is intended

1. Run both commands before the change and record the result.
2. Make the change. Run both commands again.
3. If a property should change (for example, a fix for `F1` or `F2`, or a new promise), change
   the statement in `PROPERTIES`, the `judge()` function, and the table above together. For a
   fixed finding, remove its entry from `KNOWN_FINDINGS` and from "Known findings". State the
   change to the user in plain words.
4. If the change adds a new kind of filesystem or subprocess call, add it to `instrumented()`
   and `FAULTS` as "A modeling error" describes.
5. If a guard moved or was renamed, update the matching `old` text in `MUTANTS`. Add a mutant
   for a new guard. Each mutant must be `CAUGHT`.
6. Update the line numbers in the coverage record.
7. Move the sync commit in this file forward only after both commands pass on the new commit and
   you confirmed that the coverage record and the atomicity rules describe the new code. Replace
   `e6b2e65` in the two places in this file with the new commit.

## Why this tool

The question is whether the code behaves for every input and failure point, not whether events
can happen in a bad order. No verifier for Python models filesystem side effects, and a TLA+
model would check a hand-written copy of `run_new`, not the code. The check therefore runs the
real function for every case in a bounded, stated scope. It needs only the pinned Python and
`uv`, which every developer of this repo has.
