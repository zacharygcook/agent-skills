# Collection Notes

## Scope

This repository contains 18 generally useful skills: 17 engineering workflows selected from personal reusable packages and project-derived work, plus a repository-aware onboarding concierge. Project-specific originals remain in their source repositories; this collection contains generalized extractions.

The source search covered personal agent discovery directories, selected software repositories, duplicate worktrees, and two personal workstations. Exact duplicates and stale variants were collapsed.

## Curation Rules

- A private source repository does not make an otherwise safe skill private.
- A public source does not prove ownership or redistribution rights.
- Exclude vendor-installed, marketplace, plugin-cache, bundled-system, and externally authored packages.
- Exclude former-company material, secrets, account identifiers, machine paths, and project-only procedures.
- Prefer one strong workflow over several slightly different copies.
- Generalize project-derived judgment while leaving concrete commands and domain rules in the source project.

## Consolidations

- Six Ralph packages became `ralph-workflows`, with operation-specific references.
- Two Mermaid packages became `mermaid-diagrams`.
- Two local dashboard/browser suites became `local-web-e2e`.
- Two stale-PR rubrics became `triage-stale-pull-requests`.
- Human-gated and unattended review-bot workflows became two modes in `handle-automated-code-review`.
- Project queue guidance was folded into `postgres-queue-health`.

## Onboarding

`setup-agent-skills` wraps the upstream Skills CLI rather than duplicating its agent-path registry. A
dependency-free Python doctor detects agent footprints, repository signals, installed scope, and
conditional prerequisites; recommends evidence-backed outcome packs; and requires exact skill,
scope, and agent approval before project or global installation.

## Notable Provenance

`repo-cleanup-auditor` originated from a personal workflow design specifying six candidate categories and approval before mutation. Generator-added company/license metadata was removed; the collection is released under the repository-level MIT License.

`github-issues-gh-cli` was a custom local workflow, not an official GitHub package, but was excluded because it was too setup-specific and insufficiently differentiated from maintained platform tooling.

The collection intentionally excludes OS maintenance, cloud CLI wrappers, project workers, design-system-only instructions, and skills owned by external authors or vendors.
