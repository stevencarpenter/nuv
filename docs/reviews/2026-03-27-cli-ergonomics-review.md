# CLI Ergonomics Review (2026-03-27)

## Scope

Assess the command-line ergonomics of `nuv` for its intentional UV-only, opinionated product direction, with suggestions to reduce confusion and improve day-to-day usage.

## Overall assessment

`nuv` already has strong CLI ergonomics for its intended audience:

- `nuv new <name>` is an excellent golden path.
- `--install command-only` aligns with intentional, explicit tool installation.
- Argument choices and validation provide clear guardrails and reduce user footguns.

The core UX is good; most improvements are clarity-focused rather than architectural.

## Key confusion points

1. **README drift vs implementation**
   - `fastapi` exists in code and tests, but README still lists it as “coming soon.”
   - This creates immediate trust friction.

2. **Success feedback can be too quiet at defaults**
   - Important completion guidance is logged at `INFO`/`WARNING` levels.
   - With default `--log-level WARNING`, users can miss useful “what happened” context.

3. **`--install` semantics are correct but cognitively heavy**
   - `editable` / `none` / `command-only` is flexible, but users may hesitate on intent.

4. **No short aliases for high-frequency flags**
   - Repeated usage benefits from faster input (`-a`, `-t`, `-p` style shortcuts).

## Recommended improvements (priority)

1. **Fix docs/behavior drift first (highest priority)**
   - Remove “fastapi coming soon.”
   - Add concrete `fastapi` usage and generated structure examples.
   - Ensure docs reflect current defaults (`--install command-only`).

2. **Make post-create output deterministic and explicit**
   - Always print a concise success summary to stdout:
     - target path
     - archetype
     - Python version
     - install-mode result
     - next command(s)

3. **Clarify `--install` help text around intent**
   - Keep behavior unchanged, improve wording:
     - `command-only` = recommended; prints install command
     - `editable` = installs now
     - `none` = skip install action and guidance

4. **Add short aliases for frequent flags**
   - Suggested mappings:
     - `--archetype` / `-t`
     - `--at` / `-o` (or `-d`)
     - `--python-version` / `-p`

5. **Add intent-first examples to README**
   - “I want a FastAPI API quickly”
   - “I want scaffolding only (no install action)”
   - “I want editable install immediately”

## Product-direction recommendation

For a UV-only strategy with rare new archetypes, prioritize:

- command clarity,
- output clarity,
- and docs/runtime-message consistency.

Avoid adding plugin-system complexity until archetype growth truly demands it.

## Scorecard

- Generated structure: `9/10`
- Tool usage/defaults: `9.5/10`
- CLI ergonomics for target audience: `8.5/10`
- Long-term extensibility without abstraction changes: `6.5/10`

## Bottom line

`nuv` is already a high-quality, opinionated generator with strong defaults and a fast path. The highest-value improvements now are reducing user confusion through tighter docs/behavior alignment and more explicit success feedback.
