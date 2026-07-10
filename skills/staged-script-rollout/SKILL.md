---
name: staged-script-rollout
description: "Use ONLY when the user explicitly asks to roll out, stage, ramp, dry-run/live-run, or operate a script that writes to live data, shared Postgres mirrors, or external systems. Do NOT use for ordinary code edits, reviews, tests, pipeline investigation, bug fixes, script design, or merely noticing that a script could touch live systems."
---

# Staged Script Rollout

## Activation Gate

Use this skill only when BOTH conditions are true:

1. The task is about actively operating or planning the rollout of a script through staged execution.
2. The user makes that rollout intent explicit with language such as:
   - "roll this out"
   - "stage the rollout"
   - "run the dry run, then a limited live run"
   - "take this through dry run / live run"
   - "ramp this script"
   - "operate this script against production"
   - "run this live safely"

If those conditions are not both true, do not use this skill.

Permission to make live calls is not enough. A user saying "you may run live
ZoomInfo/Firecrawl/API calls," "run a small E2E test," or "smoke test the
pipeline" is still not a staged-script-rollout request unless they explicitly
ask for staged rollout/ramp sequencing.

## Non-Triggers

Do not use this skill for:

- Implementing a new script unless the user explicitly asks to roll it out now.
- Revising an existing script unless the user explicitly asks to run or stage it now.
- Code review.
- General pipeline investigation.
- Test writing or test fixing.
- CI debugging.
- Refactoring.
- Adding safety checks, dry-run flags, audit output, or rollback support.
- Reading docs or explaining how a script works.
- Running ordinary local validation commands such as Ruff, pytest, or schema checks.
- Running a bounded E2E smoke test or pipeline probe.
- Debugging a failed live run after the fact.
- Noticing that a script touches HubSpot, PhoneBurner, Postgres, Firecrawl, ZoomInfo, or another external system.

For those tasks, follow the normal repo instructions and only mention staged rollout as an optional next step if it is directly useful.

## Intended Use

When explicitly activated, use this skill for scripts that can mutate:
- HubSpot
- PhoneBurner
- shared Postgres mirrors
- other external systems or production-like state

The skill is about execution sequencing and operator commands, not general script development.

## Operator Rollout Order

Default rollout sequence:

1. Full dry run
- Run the full script in dry-run mode first.
- Use this to catch bugs, inspect artifacts, and judge whether the output is good enough.
- If the dry-run output is weak or unclear, improve the script before any live run.

2. Very limited real run
- After the dry run looks nominal, do a very small live run.
- Limit by the smallest practical scope: one rep, one territory, one object, one page, one batch, one session limit, etc.
- Expect spot-checking and potential rollback after this step.
- Treat this step as mandatory for materially changed live-write code paths. Dry runs do not exercise write-only failures such as association endpoints, permission gaps, archived-target behavior, or partial-write cleanup.
- If the user asks to skip straight from dry run to a broad live run, push back clearly and recommend the smallest practical live slice first.
- Only skip the limited-live step when the user explicitly accepts the elevated risk after that warning, or when the script's natural unit of work truly cannot be scoped smaller without making the run less representative or less safe.

3. Larger but still scoped real run
- Expand to a meaningful but not full production slice.
- This should still be small enough that rollback or repair is realistic if the results are wrong.

4. Full real run
- Only after the prior live scopes look correct.
- Expect heavy spot checks after completion.

## Required Engineering Biases

- Dry-run must be the default for any script that touches live data or shared production-like state.
- If a script does not support a safe dry-run, fix that before recommending usage.
- Prefer a dedicated audit/end-state verification script when the primary script is complex.
- Prefer a dedicated rollback/reversion script when the primary script can cause broad or hard-to-undo changes.
- If audit or rollback scripts do not exist yet, be ready to create them.

## Command Style

When giving commands to the operator:
- Use one-line commands.
- Prefer the repo-native command wrapper when one exists, especially `just`
  recipes. Use `source .venv/bin/activate && python3 ...` only when there is no
  maintained wrapper for the script.
- Keep commands as simple as possible, but no simpler.
- Prefer sensible defaults in the script over requiring many runtime flags.
- If too many flags are needed to operate safely, recommend rewriting the script defaults or CLI.

## Default Command Pattern

When proposing commands, prefer this shape:

- Dry run
- Very limited real run
- Scoped real run
- Full real run
- Audit command(s)
- Rollback command(s), if they exist

Do not jump straight to the full live command unless the user explicitly asks for that.

## UX Heuristics

- If a "limit" flag exists, use it for the very limited real run.
- If a natural scope flag exists, prefer that over a numeric limit for the scoped real run.
- If the script mutates a shared mirror, treat it like a production write.
- If the dry-run output is not human-auditable, improve the output before recommending a live run.
- For live-writing scripts, prefer commands in this order even when the user wants speed: dry run, limited live, scoped live, full live. Explain that some failures appear only after the first successful write.

## Escalation Rule

If a script is hard to operate safely because of weak defaults, confusing flags, poor dry-run fidelity, or missing audit/rollback support, do not paper over that with a long command. Fix the script or propose the fix first.
