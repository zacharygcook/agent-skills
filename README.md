# Agent Skills

[![Validate skills](https://github.com/zacharygcook/agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/zacharygcook/agent-skills/actions/workflows/validate.yml)
[![Install with npx](https://img.shields.io/badge/install%20with-npx-334155?logo=npm&logoColor=white)](#install)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)

Practical, evidence-first workflows for coding agents: safer repository changes, trustworthy tests
and reviews, and controlled long-running work.

## Install

Install the collection in the current project:

```bash
npx skills add zacharygcook/agent-skills
```

Or install one workflow:

```bash
npx skills add zacharygcook/agent-skills@agent-readiness-scoring
```

Add `-g` to install globally.

## Start here

### Set up this system

```text
$setup-agent-skills on my system
```

It inspects your machine and repository, finds available coding agents and prerequisites, then
recommends a small relevant set. It asks before installing anything. Optionally add one or two
preferences, such as “for this repo” or “for Codex.”

### Audit this repository

```text
$agent-readiness-scoring audit this repo and suggest improvements
```

It produces a read-only, evidence-backed assessment and the highest-value next improvements.

### Set readiness preferences

```text
$agent-readiness-scoring walk me through setting up my preferences
```

It helps tailor repository preferences without overwriting an existing file.

## Skills shipped with this package

Browse [all 23 skills](skills/), or start with one of these groups:

- **Repository readiness** — [`setup-agent-skills`](skills/setup-agent-skills),
  [`agent-readiness-scoring`](skills/agent-readiness-scoring), and
  [`repo-cleanup-auditor`](skills/repo-cleanup-auditor).
- **Build, test, and review** — [`local-web-e2e`](skills/local-web-e2e),
  [`expand-test-coverage`](skills/expand-test-coverage), [`code-review`](skills/code-review), and
  [`handle-automated-code-review`](skills/handle-automated-code-review).
- **Long-running and risky work** — [`ralph-loop`](skills/ralph-loop),
  [`ralph-sprint`](skills/ralph-sprint), [`ralph-status`](skills/ralph-status),
  [`ralph-review`](skills/ralph-review), and [`staged-script-rollout`](skills/staged-script-rollout).
- **Codebase health and artifacts** — [`ban-type-assertions`](skills/ban-type-assertions),
  [`fix-knip-unused-exports`](skills/fix-knip-unused-exports),
  [`ui-css-performance`](skills/ui-css-performance),
  [`perplexity-research`](skills/perplexity-research), and
  [`mermaid-diagrams`](skills/mermaid-diagrams).

## Ralph loop

For long-running autonomous implementation work:

```text
ralph-loop → ralph-sprint → ralph-status → ralph-review
```

## The readiness loop

`agent-readiness-scoring` audits a repository with concrete evidence, chooses one high-value gap,
builds a durable capability, then validates and rescores the result.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/agent-readiness-loop-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/agent-readiness-loop-light.svg">
  <img alt="The agent readiness loop: audit the repository, capture evidence, choose one gap, implement durable capability, validate and rescore, then repeat until the target is reached." src="assets/agent-readiness-loop-light.svg">
</picture>

## License

Released under the [MIT License](LICENSE).
