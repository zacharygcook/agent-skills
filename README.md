# Agent Skills

A curated collection of practical skills for coding agents. These packages turn recurring engineering judgment into explicit, reviewable workflows that can travel between repositories and agent clients.

The collection currently contains 17 skills covering repository readiness, testing, code review, browser E2E, safe live-script rollouts, Postgres queues, documentation artifacts, autonomous coding loops, diagrams, research, and codebase hygiene.

The flagship is `agent-readiness-scoring`: a transparent 82-criterion audit and remediation system designed to make repositories safer and more effective for coding agents without rewarding score-only theater.

## Collection

| Area | Skills |
| --- | --- |
| Agent operations | `agent-readiness-scoring`, `ralph-workflows`, `repo-cleanup-auditor`, `staged-script-rollout` |
| Review and testing | `code-review`, `handle-automated-code-review`, `triage-stale-pull-requests`, `expand-test-coverage`, `good-test-bad-test`, `local-web-e2e` |
| TypeScript/frontend | `ban-type-assertions`, `fix-knip-unused-exports`, `ui-css-performance` |
| Data and communication | `postgres-queue-health`, `local-html-pdf-reports`, `mermaid-diagrams`, `perplexity-research` |

Every package has a `SKILL.md`; richer packages may include `references/`, `scripts/`, `assets/`, or `agents/openai.yaml` metadata.

## Install

Copy or symlink a skill into a client-supported discovery directory:

```bash
ln -s "$PWD/skills/agent-readiness-scoring" ~/.agents/skills/agent-readiness-scoring
```

Repository-specific installations can vendor the same folder under `<repo>/.agents/skills/`. Check your agent client's documentation for additional discovery paths.

## Validate

```bash
python3 scripts/validate_skills.py
python3 scripts/build_inventory.py --check
PYTHONDONTWRITEBYTECODE=1 python3 skills/agent-readiness-scoring/scripts/test_readiness.py -v
gitleaks dir --redact=100 --no-banner .
```

## Design Principles

- Preserve hard-won operating judgment, not project names or machine setup.
- Prefer narrowly triggered skills with explicit safety and authorization boundaries.
- Keep core instructions concise and move specialized detail into references.
- Delete or consolidate overlapping skills rather than growing an indiscriminate catalog.
- Treat source-repository visibility as provenance, not an automatic publication decision.

See [inventory/collection.md](inventory/collection.md) for provenance and curation notes.

## License

Released under the [MIT License](LICENSE).
