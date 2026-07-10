---
name: good-test-bad-test
description: Classify proposed tests as valuable behavior tests, harmful implementation tests, or temporary proof/TDD tests. Use before writing, expanding, reviewing, or deleting tests, especially during coverage work or when a test would keep questionable code alive.
---

# Good Test, Bad Test

Optimize for production confidence and maintainability, not raw coverage.

## Required Classification

Before adding a test:

1. Name the behavior or branch.
2. Name the real production workflow that reaches it.
3. Classify the test as `good`, `bad`, or `temporary proof/TDD`.
4. Choose whether to test, simplify production code, delete dead code, or temporarily prove a hypothesis.

## Good Tests

Good tests protect behavior users or operators depend on:

- public contracts, domain rules, and critical state transitions;
- realistic external data and failure modes;
- regressions for bugs likely to recur;
- auth, data integrity, idempotency, retry, and concurrency invariants;
- integration seams where a unit mock would conceal risk.

They should survive reasonable refactors because they assert outcomes rather than private choreography.

## Bad Tests

Do not add tests whose main effect is to:

- pin private helper calls, internal ordering, or incidental object shape;
- exercise unreachable defensive branches;
- preserve stale exports, obsolete commands, placeholder providers, or speculative abstractions;
- mock so much that the behavior under test cannot fail realistically;
- restate framework or library behavior;
- inflate line or branch coverage without protecting an invariant.

If production cannot reach a branch, prefer deleting or simplifying it. If it is an intentional placeholder, keep it small and document why coverage is deferred.

## Temporary Proof/TDD Tests

Temporary tests may recreate a bug, test a narrow hypothesis, or drive an unsettled implementation. Before handoff, either convert them into durable behavior tests or delete them. Keep one only when the user explicitly approves the maintenance cost and the reason is documented.

## Coverage Triage

For each uncovered branch, ask in order:

1. Can a real workflow reach it?
2. Does it protect meaningful behavior?
3. Can it be tested through a public boundary?
4. Would deleting or simplifying the code be safer?

Report the classification and reasoning when the answer is not obvious.
