---
name: ralph-workflows
description: Initialize, plan, run, inspect, and review resumable Ralph-style autonomous implementation loops with sequential chunks, persistent scratchpad memory, manifests, and idempotent post-sprint hooks. Use for `.ralph` orchestration or similar long-running coding-agent sprint systems.
---

# Ralph Workflows

Operate an autonomous implementation loop as a resumable state machine, not a one-shot prompt. Preserve negative knowledge, make progress machine-readable, and distinguish completed implementation chunks from completed review/documentation/test hooks.

## Route the Task

- New setup or reliability audit: [references/initialize.md](references/initialize.md)
- Turn a spec into dependent sprints: [references/spec-breakdown.md](references/spec-breakdown.md)
- Create or validate a sprint folder: [references/sprint.md](references/sprint.md)
- Design `chunks.json`: [references/chunks.md](references/chunks.md)
- Determine real completion: [references/status.md](references/status.md)
- Critically review a sprint: [references/review.md](references/review.md)

Read only the references needed for the requested operation.

## Shared Invariants

- Chunks are sequential, bounded, and have concrete acceptance criteria plus validation commands.
- Artifact paths are accurate because downstream hooks depend on them.
- Every sprint has persistent scratchpad memory; agents read it first and append decisions, dead ends, and discoveries before exiting.
- Manifests represent resumable phases and hook status explicitly.
- Review, documentation, and test hooks are idempotent and leave durable completion markers.
- Signals and interrupted exits reconcile state instead of silently losing completed work.
- A sprint is not complete merely because implementation chunks pass; required post-sprint hooks must also finish.

Adapt filenames when a repository uses an equivalent orchestration convention, but preserve these semantics.
