---
name: write-public-readme
description: Write or substantially revise a polished public-facing repository README. Use for open-source launches, public GitHub repositories, first-time user onboarding, installation and quick-start redesign, command documentation, project positioning, or README reviews where clarity, trust, and adoption matter.
---

# Write Public README

Treat the README as the product's front door. Optimize for a capable stranger deciding whether to
trust, install, and use the project—not for maintainers who already know its internals.

## Build the story in reader order

1. Inspect the repository, current README, license, package metadata, real commands, and screenshots.
2. Identify the audience, primary outcome, maturity, and shortest verified path to first value.
3. Lead with the project name, one concrete sentence, and a compact mental model or screenshot only
   when it materially improves understanding.
4. Put installation and the human quick start before architecture, implementation details, or
   exhaustive reference material.
5. Explain the distinctive workflows and benefits with evidence from the repository.
6. End with automation/reference commands, deeper documentation, contribution guidance, license,
   and credits as applicable.

## Make installation feel obvious

- Show the smallest supported path that actually works in a clean repository.
- Prefer one command per line and commands that fit a normal mobile-width GitHub code block.
- Do not expose package-layout details, redundant selectors, forced confirmation flags, interpreter
  spelling, manual file copies, or lifecycle glue when the product can automate them.
- Do not make humans read the automation interface to get started. Put fully explicit flags and
  machine-oriented variants in a small section near the end.
- If the honest command is ugly, improve the installer or CLI instead of cosmetically explaining it.
- Verify version behavior before adding `@latest`, pins, `-y`, or similar ceremony.

## Keep the README public-facing

- Write in plain, confident language. Remove internal history, private context, machine-specific
  paths, score-chasing rationale, apologies, and implementation archaeology.
- Prefer a few strong sections over a complete inventory. Link deeper docs rather than duplicating
  them.
- Use badges sparingly: build health, package/version, and license should communicate real trust.
- Use tables only for genuine comparison or exact mappings; avoid wide tables and horizontally
  scrolling command blocks.
- Keep examples realistic and copy/paste-ready. Separate shell commands from explanatory comments
  when comments make copying awkward.
- State access limitations, supported platforms, maturity, and destructive behavior plainly.

## Human and automation surfaces

Show short human commands first, modeled after durable tools such as Git:

```text
tool init
tool status
tool run
tool resume
tool upgrade
```

Move long noninteractive equivalents to an `Automation`, `CI`, or `Reference` section near the end.
Do not let the existence of scripts or agents lower the quality bar for the human interface.

## Validate before finishing

- Run every install and quick-start command in a disposable or clean repository when safe.
- Verify links, referenced files, package names, default version behavior, and authentication notes.
- Inspect GitHub rendering or a faithful preview at narrow width; remove side-scrolling onboarding.
- Confirm the README does not promise defaults, automation, compatibility, or safety the code lacks.
- Re-read only the first screen and installation flow: a new user should know what this is, why it is
  useful, and what to do next without reading the rest.
