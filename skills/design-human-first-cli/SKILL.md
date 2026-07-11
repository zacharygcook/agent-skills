---
name: design-human-first-cli
description: Design, implement, or review a human-first command-line interface and developer workflow. Use when commands are long, flag-heavy, difficult to discover, require manual setup glue, expose implementation paths, need interactive onboarding, mix human and automation concerns, or create avoidable developer-experience friction.
---

# Design Human-First CLI

Treat commands as product UI. Start with the interaction a human should remember, then do the
engineering required to make that interaction real.

## Design the target surface first

Write the ideal everyday vocabulary before editing implementation:

```text
tool init
tool status
tool validate
tool run
tool resume
tool upgrade
```

Prefer short, stable verbs; consistent grammar; obvious help; and commands that fit comfortably in a
terminal. A user should not need repository archaeology or shell history to operate the tool.

## Separate humans from automation

- Human commands should be short, interactive, discoverable, and safe to rerun.
- Agent/CI commands may expose explicit flags, paths, structured output, and noninteractive controls.
- Keep the complete automation interface documented, but do not make it the main onboarding path.
- Provide `--json`, exit codes, or equivalent machine contracts without degrading human output.

## Remove unnecessary flags

- Detect facts the system can know: repository root, sole package/skill, installed harnesses,
  existing configuration, platform, and available prerequisites.
- Ask interactively for genuine operator choices: provider/harness, model, budgets, destructive
  behavior, validation commands, and ambiguous targets.
- Do not invent defaults for consequential choices merely to avoid a prompt.
- Do not ask users to repeat intent already expressed by invoking the command.
- Preserve explicit flags for automation and for users who want to bypass prompts.

## Automate setup glue

- Make initialization and upgrades idempotent and preservation-first.
- Create or augment configuration without overwriting existing user content.
- Hide internal package paths, interpreter selection, file copies, symlinks, migrations, and adapter
  wiring behind the installer.
- Use a small bootstrap package or launcher when an upstream package manager cannot perform required
  lifecycle work; do not document manual glue as though it were a polished installation.
- Detect prerequisites and fail with the shortest actionable next step. Do not silently install
  system-wide dependencies or mutate external state without authorization.

## Make failures teach the workflow

An error should name the missing decision and the next useful command. Avoid messages that expose an
empty variable, recommend a legacy escape hatch, or force users to infer whether they should run
`init`, `upgrade`, or edit a file manually.

Good setup should:

- recognize an existing installation;
- enter a safe upgrade/configuration path;
- preserve state;
- collect all missing choices in one coherent journey;
- summarize the resulting configuration; and
- stop before autonomous or destructive execution unless the user explicitly started it.

## Dogfood without insider help

1. Start in a disposable repository with only the public documentation.
2. Use a person or agent without implementation context.
3. Record every guess, side-scroll, unexplained prerequisite, redundant flag, and manual file edit.
4. Fix the product surface, not merely the documentation.
5. Test new installs, existing installs, repeated runs, upgrades, missing prerequisites, cancellation,
   narrow terminals, and noninteractive automation.
6. Add regression tests for the exact ergonomic contract: short recipes exist, hidden defaults do
   not, bootstrap is idempotent, existing files survive, and documented commands really execute.

## Completion standard

- The first useful human command is memorable and short.
- `tool` or `tool help` reveals the everyday command set.
- Normal operation does not require internal paths or copied boilerplate.
- Automation remains fully expressive and deterministic.
- README examples lead with human commands and move full flags near the end.
- The clean-room path has been executed, not merely reasoned about.
