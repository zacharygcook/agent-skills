---
name: triage-stale-pull-requests
description: Evaluate an old or explicitly stale pull request against current default-branch behavior, product plans, code quality, and architecture. Use for backlog cleanup and close, salvage, refresh, or merge recommendations; do not close or modify a PR without authorization.
---

# Triage Stale Pull Requests

Decide whether a stale PR should be closed, salvaged, refreshed, or kept as a merge candidate. Age is a prompt to re-evaluate assumptions, not proof the work is bad.

## Gather Evidence

- PR age, metadata, base/head refs, diff, files, checks, comments, and mergeability.
- Current default branch and repository instructions.
- Current vision, goals, milestones, architecture, and domain docs.
- Commit history and searches for equivalent capabilities already landed.

Fetch and inspect the PR without switching the active working tree when possible. Treat unrelated dirty files as other work and do not alter them.

## Score 1–5 on Four Dimensions

1. **Remaining capability gap** — 1 means current code already solves it better; 5 means the gap remains.
2. **Current plan alignment** — 1 means misaligned or harmful; 5 means directly supports current priorities.
3. **Code quality / bug risk** — 1 means serious defects or CI risk; 5 means clean, tested, idiomatic, and low risk.
4. **Architecture fit** — 1 means assumptions conflict with current architecture; 5 means minimal adaptation.

Total the score out of 20, but do not let arithmetic replace judgment. A small valuable idea inside an obsolete implementation may deserve salvage even when the PR should close.

## Recommendation

Choose one:

- close as redundant or obsolete;
- close after preserving specific ideas or follow-up work;
- refresh/refactor against current default branch;
- keep for merge after named fixes;
- merge candidate.

Explain each dimension, exact reusable parts, current equivalents, and concrete follow-up. Distinguish “same general capability landed” from identical code.

If asked to comment, begin with the score and recommendation, remain direct but respectful, and state what should or should not be pulled forward. Only comment, close, edit, or merge when explicitly authorized.
