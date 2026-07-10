# Agent Skills

[![Validate skills](https://github.com/zacharygcook/agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/zacharygcook/agent-skills/actions/workflows/validate.yml)
[![Install with skills.sh](https://img.shields.io/badge/install-skills.sh-ff2b88?logo=npm&logoColor=white)](#install-in-30-seconds)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)

Seventeen practical workflows for coding agents that need to do real engineering: make a repository
agent-ready, run trustworthy E2E tests, operate long autonomous loops, review code, improve test
coverage, diagnose Postgres queues, and ship risky scripts without losing control.

I built these skills to capture the engineering judgment I want agents to apply repeatedly—not just
prompts that produce a plausible answer once. Each skill defines when it should activate, what a
good outcome looks like, and the checks or artifacts that make the work reviewable.

## The flagship: make a repository ready for agents

Most repositories were designed around knowledge that lives in a maintainer's head: which commands
are safe, where the real architecture is documented, how tests are selected, what production
operations require approval, and how an automated change proves it worked.

[`agent-readiness-scoring`](skills/agent-readiness-scoring) turns that fuzzy problem into a repeatable
workflow:

- Audit a repository against a transparent 82-criterion rubric.
- Require concrete source, configuration, or command evidence for every passing judgment.
- Produce a fair **owned score** and a **Factory-compatible score** from the same assessment.
- Respect repository-specific preferences without allowing documentation to impersonate tooling.
- Select one valuable gap, implement a durable fix, validate it, rescore, and repeat.
- Improve toward Level 5 or a target percentage one criterion-sized commit at a time.

The loop is intentionally simple:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/agent-readiness-loop-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/agent-readiness-loop-light.svg">
  <img alt="The agent readiness loop: audit the repository, capture evidence, choose one gap, implement durable capability, validate and rescore, then repeat until the target is reached." src="assets/agent-readiness-loop-light.svg">
</picture>

*Diagram source: [`assets/agent-readiness-loop.mmd`](assets/agent-readiness-loop.mmd).*

It is useful as a one-time health check, but the more interesting workflow is continuous improvement:
give an agent a target, let it work through the highest-value readiness gaps, and keep every decision
auditable.

## Install in 30 seconds

From the repository where you want to use the skills:

```bash
npx skills@latest add zacharygcook/agent-skills
```

Choose the skills and coding agents when prompted. To install only the flagship:

```bash
npx skills@latest add zacharygcook/agent-skills --skill agent-readiness-scoring
```

To make installed skills available globally instead of only in the current project, add `--global`.

## Quick start

Ask your coding agent for a read-only readiness audit:

```text
Use $agent-readiness-scoring to audit this repository. Produce an evidence-backed report, show both
the owned and Factory-compatible scores, and recommend the highest-value next improvement.
```

Or initialize a repository policy and start an improvement loop:

```text
Use $agent-readiness-scoring to initialize AGENT_READINESS_PREFERENCES.md, then help me tailor it to
this repository. Audit the repo and improve one readiness criterion at a time until it reaches Level
5. Validate and rescore every fix, and make one focused commit per criterion.
```

The skill includes a deterministic scoring engine, the full rubric, an assessment schema, preference
templates, and remediation guidance. Reports are generated as Markdown and JSON so humans and later
agent runs can inspect the same evidence.

## What the collection is about

### Agent-ready repositories and durable autonomous work

- [`agent-readiness-scoring`](skills/agent-readiness-scoring) — Audit and iteratively improve how
  safely and effectively coding agents can work in a repository.
- [`ralph-workflows`](skills/ralph-workflows) — Build resumable Ralph-style implementation loops with
  sequential chunks, persistent scratchpad memory, manifests, and post-sprint hooks.
- [`repo-cleanup-auditor`](skills/repo-cleanup-auditor) — Scan an entire repository for evidence-backed
  deletion, move, and rename candidates, then wait for approval before changing anything.
- [`staged-script-rollout`](skills/staged-script-rollout) — Take a live-writing script through dry run,
  limited live execution, audit, ramp-up, and rollback instead of jumping straight to production.

### Testing and review that produce real confidence

- [`local-web-e2e`](skills/local-web-e2e) — Design and debug local browser suites with isolated ports,
  disposable data, deterministic seeds, readiness checks, traces, and state restoration.
- [`good-test-bad-test`](skills/good-test-bad-test) — Separate valuable behavior tests from coverage
  theater, implementation-detail tests, and temporary proof/TDD tests.
- [`expand-test-coverage`](skills/expand-test-coverage) — Add meaningful coverage for changed code and
  fix real implementation defects exposed by the new tests.
- [`code-review`](skills/code-review) — Perform an adversarial, evidence-backed review with prioritized
  findings, deterministic checks, and explicit residual risk.
- [`handle-automated-code-review`](skills/handle-automated-code-review) — Verify AI review-bot findings,
  then use either human-gated triage or a deliberately narrow automatic-repair mode.
- [`triage-stale-pull-requests`](skills/triage-stale-pull-requests) — Decide whether an old PR should be
  closed, salvaged, refreshed, or merged based on today's plans and architecture.

### Codebase health and operational depth

- [`ban-type-assertions`](skills/ban-type-assertions) — Replace TypeScript `as` casts with runtime
  validation, compiler-verified narrowing, or better API design.
- [`fix-knip-unused-exports`](skills/fix-knip-unused-exports) — Resolve unused-export findings without
  hiding dead code behind suppressions, dummy imports, or speculative public APIs.
- [`ui-css-performance`](skills/ui-css-performance) — Keep UI source, Tailwind scanning, emitted CSS,
  and frontend dependencies small, reachable, and measured.
- [`postgres-queue-health`](skills/postgres-queue-health) — Diagnose Postgres queue slowdowns involving
  MVCC dead tuples, vacuum lag, claim indexes, long transactions, and retention.

### Research, diagrams, and reviewable artifacts

- [`perplexity-research`](skills/perplexity-research) — Run current, citation-backed research with
  primary-source standards and clear separation between confirmed facts and inference.
- [`mermaid-diagrams`](skills/mermaid-diagrams) — Create, render, and verify the smallest useful
  architecture, sequence, state, schema, timeline, or tradeoff diagram.
- [`local-html-pdf-reports`](skills/local-html-pdf-reports) — Turn research, plans, and run results into
  polished Markdown, self-contained HTML, PDF, and visually verified page images.

## Compose the workflows

The skills are small enough to use alone and opinionated enough to compose:

```text
agent-readiness-scoring
  → local-web-e2e
  → expand-test-coverage
  → code-review
```

```text
ralph-workflows
  → good-test-bad-test
  → handle-automated-code-review
  → staged-script-rollout
```

The first chain turns a readiness finding into tested, reviewed repository capability. The second
keeps long-running implementation work resumable, grounded in useful tests, and controlled when it
eventually touches live state.

## What is inside a skill?

Every installable package has a `SKILL.md` containing the activation description and core workflow.
Skills may also include:

- `scripts/` for deterministic tools;
- `references/` for detailed rubrics, variants, and domain knowledge;
- `assets/` for templates copied into a repository; and
- `agents/` for client-specific discovery metadata.

The collection is intentionally curated. Overlapping workflows are consolidated, project-specific
details stay in their source repositories, and a skill has to preserve useful judgment—not merely
add another folder to the catalog.

## Manual installation

If you prefer to manage discovery paths yourself, clone the repository and copy or symlink individual
folders from `skills/` into your agent's personal skills directory or the repository's
`.agents/skills/` directory.

```bash
git clone https://github.com/zacharygcook/agent-skills.git
ln -s "$PWD/agent-skills/skills/agent-readiness-scoring" ~/.agents/skills/agent-readiness-scoring
```

## Validate the collection

```bash
python3 scripts/validate_skills.py
python3 scripts/build_inventory.py --check
PYTHONDONTWRITEBYTECODE=1 python3 skills/agent-readiness-scoring/scripts/test_readiness.py -v
gitleaks dir --redact=100 --no-banner .
```

See [`inventory/collection.md`](inventory/collection.md) for the collection's provenance and curation
rules.

## License

Released under the [MIT License](LICENSE).
