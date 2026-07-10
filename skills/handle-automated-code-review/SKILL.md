---
name: handle-automated-code-review
description: Triage findings from automated or AI code-review systems, verify them against current code, and either present a human-gated action plan or auto-fix only narrowly safe correctness issues. Use for review bots, synthetic review PRs, or unattended self-heal workflows.
---

# Handle Automated Code Review

Automated review is evidence, not authority. Verify every meaningful claim against the current target branch and choose one operating mode explicitly.

## Mode A: Human-Gated Review

Use by default when the user asks to inspect or review findings.

1. Read PR metadata, diff, review submissions, inline comments, and thread state.
2. Cluster findings into **act on**, **maybe**, and **no action**.
3. Verify each against current code, tests, docs, and commit order.
4. Present a concise recommendation with exact implementation scope.
5. Stop before edits, commits, comments, thread resolution, or PR closure.
6. After approval, implement only the selected fixes, validate proportionately, and leave an audit trail.

“Review these comments” is not permission to implement them. An initial request that explicitly says fix/apply/address them is permission for scoped implementation.

## Mode B: Narrow Automatic Repair

Use only when the user or an established repository workflow explicitly authorizes unattended fixes.

Auto-fix only high-confidence, behavior-preserving correctness defects with a bounded patch and deterministic validation, such as:

- clear null/undefined handling;
- migration rollback symmetry;
- missing authorization on an equivalent route;
- obvious stale-request/polling cleanup;
- atomicity defects with an established repository pattern;
- simple resource cleanup or incorrect conditionals.

Escalate instead of auto-fixing anything involving product policy, ranking, funnels, eligibility, parsing tradeoffs, pricing/cost behavior, privacy retention, schema redesign, dependency/platform changes, ambiguous intent, or broad architecture.

## Judgment Rules

- Ignore synthetic split artifacts when the real commit sequence/current branch is correct.
- Treat style and memoization suggestions as optional unless they fix measured behavior.
- Match tests to risk; do not build a large regression suite for a trivial obvious fix.
- Treat auth, data loss, queue atomicity, migrations, and concurrency seriously.
- Do not merge synthetic review PRs whose purpose is only to carry comments.
- Respect concurrent work and stage only scoped files.

## Closeout

When authorized to act on a synthetic review PR, record commits, actioned and skipped findings, validation commands, and why it is being closed rather than merged. Do not resolve threads or close/merge external state beyond the user's authorization.
