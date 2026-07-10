# Initialize or Audit a Ralph Loop

Use when setting up `.ralph/` for a new project or auditing an existing setup.

## Required checks

1. Ensure the equivalent core structure exists:
- `.ralph/loop.sh`
- `.ralph/hooks/post-sprint.sh`
- `.ralph/hooks/review.sh`
- `.ralph/hooks/document.sh`
- `.ralph/hooks/test.sh`
- `.ralph/prompts/*.md`

2. Ensure hardened loop behavior is present:
- completion reconciliation on exit/signals
- orchestration log file per run
- completion detection from both `RALPH_COMPLETE` and `chunks.json` pass state

3. Ensure manifest schema supports resumability:
- `phase`: `running|chunks_done|hooks_done`
- `hooks.review|documentation|tests` statuses

4. Ensure post-sprint idempotency:
- marker files in sprint dirs: `.hook-review.done`, `.hook-documentation.done`, `.hook-tests.done`

5. Ensure `SCRATCHPAD.md` is treated as persistent sprint memory:
- prompts tell agents to read it first and append before finishing.
