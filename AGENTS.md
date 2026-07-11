# Agent Skills Repository

This repository contains a small, public-facing collection of generally useful coding-agent skills.

- Keep installable packages under `skills/<skill-name>/` with a required `SKILL.md`.
- Keep YAML frontmatter limited to `name` and `description`; the name must match the directory.
- Put client-specific discovery metadata under `agents/`, detailed guidance under `references/`, deterministic helpers under `scripts/`, and reusable templates under `assets/`.
- Keep skills agent-neutral unless a workflow inherently depends on a named tool or protocol.
- Do not add project names, personal machine paths, credentials, private operating data, vendor-bundled skills, or former-company material.
- Consolidate overlaps and avoid packages that merely duplicate a major platform's maintained tooling.
- Preserve explicit authorization gates for destructive, live, publishing, and external-state actions.
- Update `inventory/skills.json` after changing a package.
- Treat `agent-readiness-scoring` and `ralph-workflows` as generated flagship packages. Change their canonical standalone repositories, then use `python3 scripts/sync_flagship_skills.py update --skill <name> --source-root <path> --apply`; never hand-edit their collection copies.
- Keep `flagship-skills.lock.json` committed. CI must reject package drift, untracked deletions/additions, and fingerprint mismatches.
- Validate with `python3 scripts/validate_skills.py`, `python3 scripts/build_inventory.py --check`, `python3 scripts/sync_flagship_skills.py check`, flagship tests, and Gitleaks.
- Do not create a remote, publish, or make this repository public until the owner explicitly approves the review artifact.
