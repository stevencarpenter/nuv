#!/usr/bin/env python3
"""Exhaustive bounded check of the data-safety promise of `nuv new`.

It calls the real `run_new` from src/nuv/commands/new.py on a real temporary
filesystem, for every combination in SCOPE below, with a fault injected at every
filesystem and subprocess step. `uv` itself never runs: `shutil.which` and
`subprocess.run` are replaced. Read SKILL.md next to this file before you change it.

    uv run --frozen python .claude/skills/verify-run-new-safety/check_run_new_safety.py
    uv run --frozen python .claude/skills/verify-run-new-safety/check_run_new_safety.py --mutants
"""

from __future__ import annotations

import argparse
import itertools
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import types
from collections import Counter
from collections.abc import Callable, Generator, Iterator
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
NEW_PY = REPO / "src" / "nuv" / "commands" / "new.py"
NAME = "demo-app"
SCRATCH: str | None = None  # parent of all sandboxes; set in main() and in each worker
_TEMPLATE_TEXT: dict[Path, str] = {}  # templates do not change during a run, so each is read from disk once

# ---------------------------------------------------------------------------
# SCOPE: what "every case" means. Each list is enumerated in full.
# ---------------------------------------------------------------------------

# What exists at the target path before `run_new` starts.
PRESTATES = (
    "absent",  # nothing at work/demo-app
    "missing-parents",  # target is work/deep/nested/demo-app, and work/deep does not exist
    "parent-is-symlink",  # target is work/linked/demo-app, and work/linked points to a directory
    "empty-dir",
    "dir-with-files",
    "file",
    "symlink-to-dir",
    "symlink-to-file",
    "dangling-symlink",
    "parent-is-file",  # target is work/keep.txt/demo-app
)
# Pre-states in which nuv can create the target. A fault-free run must return 0 for these.
CREATABLE = ("absent", "missing-parents", "parent-is-symlink")

# The faults injected at each kind of step. One case per (step, fault).
FAULTS = {
    "mkdir": ("oserror", "unexpected"),
    "write_text": ("oserror", "oserror-after-partial-write", "unexpected"),
    "read_text": ("oserror", "unexpected"),
    "which": ("uv-missing", "unexpected"),
    "subprocess.run": ("exit-1", "oserror", "unexpected", "interrupt"),
}

PROPERTIES = {
    "NO-HARM": "A path that existed before the command still exists with the same type and content.",
    "CONTAINED": "The command creates paths only at the target, under it, or as missing parents of it. It creates nothing when the target path existed.",
    "HONEST-EXIT": "run_new returns 0 only when no step failed and the target did not exist before.",
    "KEEP": "With keep_on_failure, a failed run removes nothing that it wrote.",
    "CLEAN": "Without keep_on_failure, a failed run leaves no new path.",
}

# Violations that the current code is known to have. They are reported on every run.
# A violation that matches no entry is NEW and fails the check. An entry that matches
# nothing is STALE and also fails the check. Do not add an entry to make a run pass:
# see "A new violation" in SKILL.md.
KNOWN_FINDINGS: dict[str, tuple[str, Callable[[Violation], bool]]] = {
    "F1-new-parents-remain": (
        "CLEAN: after a failed run, parent directories that `target.mkdir(parents=True)` created remain (run_new removes only `target`).",
        lambda v: v.prop == "CLEAN" and all(_is_strict_ancestor(p, v.allowed) for p in v.paths),
    ),
    "F2-uncaught-exception-keeps-target": (
        "CLEAN: when a step raises an exception that run_new does not catch (not ValueError, RuntimeError, or OSError; "
        "for example KeyboardInterrupt during `uv sync`), the partial target remains without keep_on_failure.",
        lambda v: v.prop == "CLEAN" and v.case.fault in ("unexpected", "interrupt"),
    ),
}

# Broken variants of new.py. Each one must make its property fail (`--mutants`).
# Each `old` text must occur exactly once in new.py, or the mutant is stale.
MUTANTS = (
    (
        "NO-HARM",
        "accept an existing target and reuse the directory",
        (("    if target.exists():\n", "    if False:\n"), ("target.mkdir(parents=True)", "target.mkdir(parents=True, exist_ok=True)")),
    ),
    (
        "CONTAINED",
        "write .python-version beside the target",
        (('write_with_trailing_newline(target / ".python-version", python_version)', 'write_with_trailing_newline(target.parent / ".python-version", python_version)'),),
    ),
    (
        "HONEST-EXIT",
        "ignore the exit code of uv sync",
        (('    if result.returncode != 0:\n        raise RuntimeError(f"uv sync failed', '    if False:\n        raise RuntimeError(f"uv sync failed'),),
    ),
    (
        "KEEP",
        "ignore keep_on_failure",
        (("if created_target and target is not None and not keep_on_failure:", "if created_target and target is not None:"),),
    ),
    (
        "CLEAN",
        "do not remove the target after a failure",
        (("            shutil.rmtree(target, ignore_errors=True)\n", "            pass\n"),),
    ),
)

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Case:
    archetype: str
    install: str
    keep: bool
    prestate: str
    entry: str  # "default" (cwd/name), "at-absolute", or "at-relative"
    fault_at: int | None = None
    fault: str | None = None


@dataclass
class Steps:
    fault_at: int | None
    fault: str | None
    log: list[str] = field(default_factory=list)
    made: set[str] = field(default_factory=set)
    target: tuple[str, str] = ("", "")  # (path as given, real path) of the target
    fired: str | None = None

    def hit(self, kind: str, what: str) -> bool:
        self.log.append(f"{kind}({what})")
        if len(self.log) == self.fault_at:
            self.fired = self.log[-1]
            return True
        return False


@dataclass
class Violation:
    prop: str
    case: Case
    detail: str
    paths: list[str]
    allowed: str
    story: str


def _is_strict_ancestor(path: str, of: str) -> bool:
    return of.startswith(path + os.sep)


def _raise_fault(fault: str | None) -> None:
    if fault in ("oserror", "oserror-after-partial-write"):
        raise OSError(28, "injected fault")
    if fault == "unexpected":
        raise KeyError("injected fault")
    if fault == "interrupt":
        raise KeyboardInterrupt
    raise AssertionError(f"unknown fault {fault!r}")


def build_sandbox(root: Path, prestate: str) -> Path:
    """Create fixed surroundings plus the pre-state. Return the target path."""
    work, outside = root / "work", root / "outside"
    (work / "other").mkdir(parents=True)
    (work / "keep.txt").write_text("keep\n")
    (work / "other" / "data.txt").write_text("data\n")
    (outside / "real-dir").mkdir(parents=True)
    (outside / "real-dir" / "inner.txt").write_text("inner\n")
    (outside / "real-file.txt").write_text("real\n")
    target = work / NAME
    if prestate == "missing-parents":
        target = work / "deep" / "nested" / NAME
    elif prestate == "parent-is-symlink":
        (work / "linked").symlink_to(outside / "real-dir")
        target = work / "linked" / NAME
    elif prestate == "empty-dir":
        target.mkdir()
    elif prestate == "dir-with-files":
        (target / "sub").mkdir(parents=True)
        (target / "mine.txt").write_text("mine\n")
        (target / "sub" / "deep.txt").write_text("deep\n")
    elif prestate == "file":
        target.write_text("a file\n")
    elif prestate == "symlink-to-dir":
        target.symlink_to(outside / "real-dir")
    elif prestate == "symlink-to-file":
        target.symlink_to(outside / "real-file.txt")
    elif prestate == "dangling-symlink":
        target.symlink_to(outside / "missing")
    elif prestate == "parent-is-file":
        target = work / "keep.txt" / NAME
    elif prestate != "absent":
        raise AssertionError(prestate)
    return target


def entries_for(prestate: str) -> tuple[str, ...]:
    # The default entry is `nuv new demo-app` with no --at. It can reach only work/demo-app.
    if prestate in ("missing-parents", "parent-is-symlink", "parent-is-file"):
        return ("at-absolute", "at-relative")
    return ("default", "at-absolute", "at-relative")


def snapshot(root: Path) -> dict[str, tuple]:
    """Every path under root, without following symlinks: type, content, inode, mtime."""
    snap: dict[str, tuple] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            path = os.path.join(dirpath, name)
            st = os.lstat(path)
            if os.path.islink(path):
                snap[path] = ("symlink", os.readlink(path))
            elif os.path.isdir(path):
                snap[path] = ("dir",)
            else:
                with open(path, "rb") as fh:
                    snap[path] = ("file", fh.read(), st.st_ino, st.st_mtime_ns)
    return snap


@contextmanager
def instrumented(steps: Steps, root: Path) -> Generator[None]:
    """Count every filesystem and subprocess step of run_new, and fail the chosen one."""
    real_mkdir, real_write, real_read = Path.mkdir, Path.write_text, Path.read_text

    def rel(path: Path) -> str:
        return os.path.relpath(os.path.abspath(path), root)

    def real(path: Path) -> str:
        # Only the target can be behind a symlinked parent (pre-state parent-is-symlink).
        absolute = os.path.abspath(path)
        lexical, actual = steps.target
        return actual + absolute[len(lexical) :] if (absolute + os.sep).startswith(lexical + os.sep) else absolute

    def mkdir(self: Path, *args, **kwargs):
        if steps.hit("mkdir", rel(self)):
            _raise_fault(steps.fault)
        real_mkdir(self, *args, **kwargs)
        steps.made.add(real(self))

    def write_text(self: Path, data: str, *args, **kwargs):
        if steps.hit("write_text", rel(self)):
            if steps.fault == "oserror-after-partial-write":
                real_write(self, data[: len(data) // 2], *args, **kwargs)
                steps.made.add(real(self))
            _raise_fault(steps.fault)
        written = real_write(self, data, *args, **kwargs)
        steps.made.add(real(self))
        return written

    def read_text(self: Path, *args, **kwargs):
        if steps.hit("read_text", "templates/" + "/".join(self.parts[-2:])):
            _raise_fault(steps.fault)
        if self not in _TEMPLATE_TEXT:
            _TEMPLATE_TEXT[self] = real_read(self, *args, **kwargs)
        return _TEMPLATE_TEXT[self]

    def which(cmd, *args, **kwargs):
        if steps.hit("which", cmd):
            if steps.fault == "uv-missing":
                return None
            _raise_fault(steps.fault)
        return "/injected/uv"

    def run(cmd, *args, **kwargs):
        if steps.hit("subprocess.run", " ".join(cmd[:3])):
            if steps.fault == "exit-1":
                return subprocess.CompletedProcess(cmd, 1)
            _raise_fault(steps.fault)
        return subprocess.CompletedProcess(cmd, 0)

    with (
        patch.object(Path, "mkdir", mkdir),
        patch.object(Path, "write_text", write_text),
        patch.object(Path, "read_text", read_text),
        patch.object(shutil, "which", which),
        patch.object(subprocess, "run", run),
    ):
        yield


def run_case(mod: types.ModuleType, case: Case) -> tuple[Steps, tuple[str, object], list[Violation]]:
    parent = os.path.join(SCRATCH or tempfile.gettempdir(), str(os.getpid()))
    os.makedirs(parent, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="case-", dir=parent)).resolve()
    try:
        target = build_sandbox(root, case.prestate)
        work = root / "work"
        at = {"default": None, "at-absolute": str(target), "at-relative": os.path.relpath(target, work)}[case.entry]
        preexisted = os.path.lexists(target)
        allowed = os.path.join(os.path.realpath(target.parent), NAME)
        steps = Steps(case.fault_at, case.fault, target=(str(target), allowed))
        # Snapshots are taken outside the instrumented block, so the harness adds no steps.
        pre = snapshot(root)
        os.chdir(work)
        try:
            with instrumented(steps, root):
                try:
                    code = mod.run_new(NAME, at=at, cwd=work, archetype=case.archetype, install_mode=case.install, keep_on_failure=case.keep)
                    outcome: tuple[str, object] = ("returned", code)
                except KeyboardInterrupt:
                    if steps.fault != "interrupt" or steps.fired is None:
                        raise  # a real Ctrl-C from the person who runs the check
                    outcome = ("raised", "KeyboardInterrupt")
                except Exception as exc:  # noqa: BLE001 - the outcome is judged below
                    outcome = ("raised", type(exc).__name__)
        finally:
            os.chdir(REPO)
        post = snapshot(root)
        return steps, outcome, judge(case, steps, outcome, pre, post, str(root), allowed, preexisted)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def judge(case: Case, steps: Steps, outcome: tuple[str, object], pre: dict, post: dict, root: str, allowed: str, preexisted: bool) -> list[Violation]:
    def short(path: str) -> str:
        return os.path.relpath(path, root)

    def story() -> str:
        call = f'run_new("{NAME}", archetype="{case.archetype}", install_mode="{case.install}", keep_on_failure={case.keep})'
        where = {"default": "no --at", "at-absolute": "--at <absolute path>", "at-relative": "--at <relative path>"}[case.entry]
        fault = f"step {case.fault_at}: {steps.fired} -> {case.fault}" if steps.fired else "no fault"
        return f"target pre-state: {case.prestate}, {where}\n    {call}\n    {fault}\n    run_new {outcome[0]} {outcome[1]}"

    found: list[Violation] = []

    def add(prop: str, detail: str, paths: list[str]) -> None:
        listed = ": " + ", ".join(short(p) for p in paths[:6]) if paths else ""
        found.append(Violation(prop, case, detail + listed, paths, allowed, story()))

    succeeded = outcome == ("returned", 0)
    new = sorted(set(post) - set(pre))

    harmed = sorted(p for p, was in pre.items() if post.get(p) != was)
    if harmed:
        add("NO-HARM", "existing paths were removed or changed", harmed)

    stray = [p for p in new if preexisted or not (p == allowed or p.startswith(allowed + os.sep) or _is_strict_ancestor(p, allowed))]
    if stray:
        add("CONTAINED", "new paths outside the target (or any new path when the target existed)", stray)

    if succeeded and steps.fired:
        add("HONEST-EXIT", "run_new returned 0 after a failed step", [])
    if succeeded and preexisted:
        add("HONEST-EXIT", "run_new returned 0 although the target path existed", [])
    if outcome[0] == "raised" and not steps.fired:
        add("HONEST-EXIT", "run_new raised with no injected fault", [])

    if succeeded and not steps.fired:
        # Keeps the step list honest: a write through a call that is not instrumented gets no fault.
        unseen = [p for p in new if p not in steps.made]
        if unseen:
            add("BASELINE", "paths created by a call that the check does not instrument", unseen)

    if not succeeded and case.keep:
        lost = sorted(p for p in steps.made if p not in post)
        if lost:
            add("KEEP", "paths that the run wrote were removed", lost)

    if not succeeded and not case.keep and new:
        add("CLEAN", "new paths remain after the failed run", new)

    return found


def base_cases(mod: types.ModuleType) -> list[Case]:
    """One fault-free case for each configuration in the scope."""
    return [
        Case(archetype, install, keep, prestate, entry)
        for archetype, install, keep in itertools.product(mod.ARCHETYPES, mod.INSTALL_MODES, (False, True))
        for prestate in PRESTATES
        for entry in entries_for(prestate)
    ]


def cases_for(mod: types.ModuleType, base: Case) -> Iterator[tuple[Case, Steps, tuple[str, object], list[Violation]]]:
    """The fault-free run of one configuration, then one run for each (step, fault) of it."""
    steps, outcome, found = run_case(mod, base)
    if base.prestate in CREATABLE and outcome != ("returned", 0):
        found.append(Violation("BASELINE", base, f"a fault-free run did not return 0: {outcome}", [], "", ""))
    yield base, steps, outcome, found
    # The step list of the fault-free run gives the fault positions for this configuration.
    for index, step in enumerate(steps.log, start=1):
        for fault in FAULTS[step.split("(")[0]]:
            case = Case(base.archetype, base.install, base.keep, base.prestate, base.entry, index, fault)
            f_steps, f_outcome, f_found = run_case(mod, case)
            if f_steps.fired is None:
                f_found.append(Violation("BASELINE", case, f"the injected fault at step {index} did not fire", [], "", ""))
            yield case, f_steps, f_outcome, f_found


def all_cases(mod: types.ModuleType) -> Iterator[tuple[Case, Steps, tuple[str, object], list[Violation]]]:
    for base in base_cases(mod):
        yield from cases_for(mod, base)


def _init_worker(scratch: str) -> None:
    global SCRATCH
    SCRATCH = scratch
    logging.disable(logging.CRITICAL)


def _worker(base: Case) -> list[tuple[Case, int, list[Violation]]]:
    """Run one configuration in a worker process against the real module."""
    import nuv.commands.new as real

    return [(case, len(steps.log), found) for case, steps, _outcome, found in cases_for(real, base)]


def classify(violation: Violation) -> str | None:
    for finding, (_text, matches) in KNOWN_FINDINGS.items():
        if matches(violation):
            return finding
    return None


def print_violation(v: Violation) -> None:
    print(f"  {v.prop}: {v.detail}")
    for line in v.story.splitlines():
        print(f"    {line.strip()}")


def check(mod: types.ModuleType) -> int:
    total = faulted = 0
    step_counts: dict[tuple[str, str], int] = {}
    known: dict[str, list[Violation]] = {name: [] for name in KNOWN_FINDINGS}
    new: dict[str, list[Violation]] = {}
    # Each configuration is independent, so the configurations run in parallel processes.
    with ProcessPoolExecutor(initializer=_init_worker, initargs=(SCRATCH,)) as pool:
        results = pool.map(_worker, base_cases(mod), chunksize=4)
        for case, step_count, found in itertools.chain.from_iterable(results):
            total += 1
            faulted += case.fault is not None
            if case.fault is None and case.prestate == "absent" and case.entry == "default" and not case.keep:
                step_counts[(case.archetype, case.install)] = step_count
            for violation in found:
                finding = classify(violation)
                (known[finding] if finding else new.setdefault(violation.prop, [])).append(violation)

    print(f"cases: {total} ({total - faulted} fault-free, {faulted} with one injected fault)")
    print("steps per fault-free run (archetype/install): " + ", ".join(f"{a}/{i}={n}" for (a, i), n in sorted(step_counts.items())))
    print()
    stale = [name for name, hits in known.items() if not hits]
    for prop, text in PROPERTIES.items():
        known_here = {name: hits for name, hits in known.items() if hits and hits[0].prop == prop}
        if prop in new:
            status = f"NEW VIOLATION in {len(new[prop])} cases"
        elif known_here:
            status = "violated only by known findings"
        else:
            status = "holds in every case"
        print(f"{prop:12} {status}\n             {text}")
        for name, hits in known_here.items():
            kinds = Counter(v.case.fault or "no fault" for v in hits)
            print(f"  known finding {name}: {len(hits)} cases ({', '.join(f'{k}: {n}' for k, n in sorted(kinds.items()))})")
            print(f"    {KNOWN_FINDINGS[name][0]}")
            print("    example:")
            print_violation(hits[0])
        for violation in new.get(prop, [])[:3]:
            print_violation(violation)
    for violation in new.get("BASELINE", [])[:3]:
        print(f"BASELINE     the check itself is not valid: {violation.detail}\n             {violation.case}")
    for name in stale:
        print(f"STALE known finding {name}: no case shows it now. Confirm the fix, then remove the entry from KNOWN_FINDINGS and from SKILL.md.")

    print()
    if new or stale:
        print(f"RESULT: FAIL ({sum(len(v) for v in new.values())} new violations, {len(stale)} stale known findings)")
        return 1
    print(f"RESULT: PASS (no new violation, {sum(1 for hits in known.values() if hits)} known findings still present)")
    return 0


def load_mutant(pairs: tuple[tuple[str, str], ...]) -> types.ModuleType:
    source = NEW_PY.read_text(encoding="utf-8")
    for old, replacement in pairs:
        if source.count(old) != 1:
            raise LookupError(f"text occurs {source.count(old)} times in {NEW_PY.name}, expected 1: {old!r}")
        source = source.replace(old, replacement)
    module = types.ModuleType("nuv.commands.new")
    module.__file__ = str(NEW_PY)
    exec(compile(source, str(NEW_PY), "exec"), module.__dict__)  # noqa: S102 - a mutated copy of this repo's own module
    return module


def check_mutants() -> int:
    failures = 0
    for prop, description, pairs in MUTANTS:
        try:
            mutant = load_mutant(pairs)
        except LookupError as exc:
            print(f"STALE   {prop:12} mutant '{description}': {exc}")
            failures += 1
            continue
        caught = next((v for _c, _s, _o, found in all_cases(mutant) for v in found if v.prop == prop and classify(v) is None), None)
        if caught is None:
            print(f"MISSED  {prop:12} mutant '{description}': the check did not report a new {prop} violation")
            failures += 1
        else:
            print(f"CAUGHT  {prop:12} mutant '{description}'")
            print_violation(caught)
    print()
    print("RESULT: " + ("FAIL (the check cannot see every broken variant)" if failures else f"PASS (all {len(MUTANTS)} broken variants are caught)"))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mutants", action="store_true", help="prove that the check fails on broken variants of new.py")
    args = parser.parse_args()

    import nuv.commands.new as real

    if Path(real.__file__).resolve() != NEW_PY:
        print(f"ERROR: nuv loads from {real.__file__}, not from {NEW_PY}. Run the command from the repo with `uv run --frozen python`.")
        return 2
    logging.disable(logging.CRITICAL)  # run_new logs one line per failed case
    global SCRATCH
    with tempfile.TemporaryDirectory(prefix="nuv-safety-") as SCRATCH:
        return check_mutants() if args.mutants else check(real)


if __name__ == "__main__":
    sys.exit(main())
