# Create or Validate a Sprint

Use when creating a new sprint under `.ralph/sprints/`.

## Required sprint files

- `README.md`
- `IMPLEMENTATION_PLAN.md`
- `relevant-specs.md`
- `chunks.json`
- `prompt.md`
- `SCRATCHPAD.md`

## Non-negotiables

1. `SCRATCHPAD.md` is mandatory memory across context resets.
2. `prompt.md` must instruct: read scratchpad first, append learnings before exit.
3. Harnesses run from the repository or orchestration root. `prompt.md` must use explicit
   root-relative sprint paths such as `.ralph/sprints/<sprint-name>/SCRATCHPAD.md`,
   `.ralph/sprints/<sprint-name>/IMPLEMENTATION_PLAN.md`, and
   `.ralph/sprints/<sprint-name>/chunks.json`; bare sprint filenames are ambiguous.
4. `chunks.json` must include accurate `artifacts`; review/doc/test hooks depend on them.
5. Sprint should be resumable: avoid assumptions that require uninterrupted execution.
6. Configure a fast chunk gate and a comprehensive final sprint gate; do not rely only on agent-reported validation.
