---
name: code-review
description: Perform an evidence-backed adversarial review of a diff, commit, branch, pull request, or named files. Use only when the user explicitly requests a fresh code review or findings on implementation quality; do not use merely to fix CI or act on existing review comments.
---

# Code Review

Find real correctness, security, reliability, product, performance, and maintainability risks. Do not implement fixes unless the user also asks for them.

## Review Posture

- Assume bugs may exist, but prove claims from code, tests, docs, or deterministic output.
- Review system outcomes and repository invariants, not syntax alone.
- Separate definite findings from open questions and speculative risks.
- Prefer one root-cause finding over several overlapping symptoms.
- Do not pad the report when no issue exists.

## Priorities

- **P0:** catastrophic security, data loss, outage, or broken core workflow; must not ship.
- **P1:** serious definite correctness, privacy, auth, reliability, migration, or integration bug.
- **P2:** normal actionable bug, edge case, test gap, performance risk, API/data-model issue, or maintainability problem.
- **P3:** low-risk inconsistency or polish worth addressing.

Use the lowest priority that honestly matches both impact and confidence.

## Workflow

1. Read repository instructions and docs relevant to the changed domain.
2. Establish the exact target and intent from status, commits, PR text, issues, and tests.
3. Read changed files plus nearby code that owns contracts and invariants.
4. Run focused repository-native checks without mutating code.
5. Inspect auth, data handling, migrations, concurrency, external costs, dependencies, queries, UI states, and operability as applicable.
6. Review manually after tool output; scanners are evidence, not conclusions.
7. Return findings first with tight file/line references and concrete remediation.

Never run destructive resets, live provider calls, production migrations, or write-mode formatting during a read-only review without explicit authorization.

## Deterministic Evidence

Choose proportional checks: formatting check mode, lint, typecheck, focused tests, contract/schema tests, build/bundle analysis, dependency inspection, and existing complexity tooling. Report exact commands and outcomes.

For complexity, report exact cyclomatic/cognitive scores only when tooling supplies them. Treat functions over 10 as prompts for manual inspection, not automatic bugs. State limitations instead of fabricating scores.

## Output

1. **Big picture** — whether the direction fits the intended outcome.
2. **Findings** — ordered P0 through P3; include title, location, behavior, impact, and recommendation.
3. **Checks run** — commands, results, complexity evidence, and skipped checks.
4. **Recommendations** — blockers first, then follow-ups.
5. **Open questions / residual risk** — only when useful.

If no findings survive verification, say so plainly while still reporting checks and residual risk.
