# Initialize or Audit a Ralph Loop

Use when setting up `.ralph/` for a new project or auditing an existing setup.

## Required checks

1. Ensure the equivalent core structure exists:

   - `.ralph/loop.sh`
   - `.ralph/status.sh`
   - `.ralph/lib/ralph-common.sh`
   - `.ralph/hooks/post-sprint.sh`
   - `.ralph/hooks/review.sh`
   - `.ralph/hooks/document.sh`
   - `.ralph/hooks/test.sh`
   - `.ralph/prompts/*.md`

2. Ensure hardened loop behavior is present:

   - completion reconciliation on exit/signals
   - orchestration log file per run
   - heartbeat and structured event logs
   - stale hook state and lock recovery
   - post-result stall recovery without a wall-clock cap on legitimate long runs
   - completion detection from scoped markers plus `chunks.json` pass-state deltas

3. Ensure manifest schema supports resumability:

   - `phase`: `running|chunks_done|hooks_done`
   - `hooks.review|documentation|tests` statuses

4. Ensure post-sprint idempotency:

   - marker files in sprint dirs: `.hook-review.done`, `.hook-documentation.done`, `.hook-tests.done`
   - disabled hooks are explicitly `skipped`, never mislabeled as executed

5. Ensure `SCRATCHPAD.md` is treated as persistent sprint memory:

   - prompts tell agents to read it first and append before finishing.

6. Ensure safety and portability:

   - unattended execution remains disarmed until explicitly approved
   - broad auto-commit is disabled
   - project-specific test/E2E commands live in `config.env`, not the runtime
   - `bash`, `git`, `jq`, and Python 3 are present
