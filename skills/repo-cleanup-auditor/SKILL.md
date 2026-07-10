---
name: repo-cleanup-auditor
description: Use when the user wants to clean up, declutter, reorganize, rename, or simplify a repository. Scans the whole repo and produces Potential/STRONG candidates for deletions, moves, and renames, then waits for explicit approval before changing files.
---

# Repo Cleanup Auditor

Use this skill for repo hygiene work where the first step should be a broad scan and a human approval checkpoint.

## Core Rule

Do not move, delete, or rename anything during the first pass. First produce a cleanup audit. Apply changes only after the user explicitly approves specific actions.

If the user already approved a specific cleanup action, you may execute that action, but still inspect references and validate afterward.

## First Pass: Repo Scan

Start at the repo root. If you are not sure which directory is the repo root, run `git rev-parse --show-toplevel`.

Inspect:

```bash
git status --short --untracked-files=all
rg --files
find . -maxdepth 3 -type d | sort
find . -maxdepth 4 -type f -empty | sort
```

Then use `rg` to check references before recommending a move, rename, or deletion. For large or binary-heavy repos, avoid exhaustive reads; sample names, manifests, READMEs, scripts, and tracked file lists first.

## Classification

Classify findings into exactly these sections, in this order.

### Potential Deletions

Possibly obsolete, generated, stale, duplicated, or confusing files where the evidence is not strong enough to delete without human judgment.

Use this table:

| ID | Path | Why suspicious | Evidence | Risk if deleted | Suggested action |
|---|---|---|---|---|---|

### STRONG Candidates for Deletion

High-confidence clutter: empty folders, `.DS_Store`, stale generated outputs, duplicate rollups, outdated snapshots, abandoned scratch files, local temp artifacts, superseded outputs with a clearer canonical copy, or files with no references and obvious generated naming.

Use this table:

| ID | Path | Why strong | Evidence | Risk if deleted | Exact delete command |
|---|---|---|---|---|---|

### Potential Moves

Files or folders that likely belong somewhere else, but where the destination needs human judgment.

Use this table:

| ID | Path | Current problem | Possible destination | Reason | Risk |
|---|---|---|---|---|---|

### STRONG Candidates for Moves

High-confidence moves where a better home is obvious from repo conventions, sibling folders, manifests, or naming.

Use this table:

| ID | Path | Proposed destination | Why strong | References needing updates | Exact move command |
|---|---|---|---|---|---|

### Potential Rename

Names that expose implementation details, confuse humans, or no longer match the artifact's purpose.

Use this table:

| ID | Path | Current name problem | Suggested name(s) | Audience impacted | References needing updates |
|---|---|---|---|---|---|

### STRONG Candidate for Rename

Names that are actively misleading, too code/methodology-heavy for human-facing artifacts, or inconsistent with nearby naming conventions.

Use this table:

| ID | Path | Proposed name | Why strong | References needing updates | Exact rename command |
|---|---|---|---|---|---|

If a section has no findings, write `None found`.

## Recommendation Standards

Promote a candidate to STRONG only when at least two of these are true:

- The file/folder is generated, duplicated, empty, or platform noise.
- The repo already has a clearer canonical location or naming pattern.
- `rg` finds no meaningful references, or only references that should be updated.
- The candidate is old relative to adjacent artifacts and no longer matches current docs.
- The artifact is large, confusing, or likely to cause operator error.
- Deleting or moving it has an obvious recovery path in git or from a reproducible script.

Keep a candidate as Potential when:

- It may be source data.
- It may be needed for audit, compliance, rollback, or historical context.
- It is referenced by scripts whose behavior you have not inspected.
- It is unclear whether the artifact is canonical or generated.

## Approval Step

After presenting the audit, stop. Ask the user which IDs to apply.

Accept feedback like:

- `Approve all STRONG candidates`
- `Approve deletions D1-D4 only`
- `Move M2, but use this destination instead`
- `Rename R1 to <name> instead`
- `Skip all potential candidates`

Do not infer approval for Potential items from approval of STRONG items.

## Apply Step

Only apply approved actions.

Use:

```bash
git mv <old> <new>
git rm <path>
```

For untracked files, use ordinary filesystem removal only after approval. Never use `git reset --hard`, `git clean`, or broad wildcard deletes unless the user explicitly asks for that exact destructive operation.

When applying a move or rename, update references in the same change:

- READMEs and docs
- scripts/constants
- manifests
- generated reports if they are meant to remain checked in
- risk notes or safety breadcrumbs

Prefer `apply_patch` for manual edits. Use structured parsers for structured files when practical.

## Validation

After applying approved changes, run the lightest validation that proves the cleanup is coherent:

```bash
rg "<old-path-or-name>"
git status --short --untracked-files=all
git diff --check
```

Also run one or more of these when relevant:

- compile changed scripts
- run focused tests
- verify row counts for moved CSVs
- compare checksums for moved data files
- check Git LFS handling for files moved into LFS-managed paths

## Final Report

Report concisely:

- Deleted
- Moved
- Renamed
- References updated
- Validation run
- Remaining unresolved cleanup candidates
- Whether changes are unstaged, staged, committed, or pushed

If no changes were applied because the user only asked for an audit, say that clearly.
