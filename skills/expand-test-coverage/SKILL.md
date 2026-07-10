---
name: expand-test-coverage
description: Add meaningful tests for changed or recently committed code, run focused and full suites, and fix real implementation defects exposed by those tests. Use when asked to add tests, improve coverage, test new code, or make sure a change is well tested.
---

# Expand Test Coverage

Add tests that increase confidence in reachable behavior, not just coverage percentages.

## Establish Scope

1. Prefer the user-named files, PR, branch, or commit.
2. Otherwise inspect `git status`, `git diff`, and `git diff --cached`.
3. If the tree is clean, inspect the latest relevant commit.
4. Read each changed file in full plus adjacent contracts and existing tests.

Before writing tests, identify the public behavior, critical invariants, error paths, state transitions, integration boundaries, and realistic edge cases. Follow the repository's existing framework, fixtures, naming, and command conventions.

## Select Valuable Cases

Prioritize:

- critical happy paths and business invariants;
- realistic validation, authorization, not-found, and provider failures;
- boundary values and malformed external data;
- important state transitions and retry/idempotency behavior;
- regression cases for confirmed bugs;
- integration behavior where mocks would hide the risk.

Avoid tests that only restate implementation details, assert framework behavior, exercise unreachable branches, or preserve dead code. If a branch has no production path, simplify or delete it instead of inventing a test.

## Iterate

1. Write a small coherent batch.
2. Run the narrowest relevant test command immediately.
3. Diagnose every failure before editing.
4. Fix production code when the test reveals a real defect; fix the test when its premise or setup is wrong.
5. Repeat until the planned behavior passes.
6. Run the broader affected suite, then the full suite when proportionate and practical.

Never weaken an assertion, over-mock a boundary, or change expected behavior merely to turn the suite green. When intent is ambiguous, use docs, call sites, and existing tests as evidence and report the uncertainty.

## Handoff

Report:

- behavior covered and tests added;
- implementation bugs found and fixed;
- focused and full commands run with results;
- anything not run and why;
- remaining meaningful gaps, not raw uncovered-line counts.
