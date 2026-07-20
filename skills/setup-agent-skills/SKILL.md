---
name: setup-agent-skills
description: Inspect a computer and software repository, detect installed coding agents and tool prerequisites, recommend relevant skills or outcome-based packs with evidence, and safely vendor selected skills through the upstream Skills CLI. Use for first-time onboarding, repository-local skill setup, prerequisite diagnosis, agent discovery, installation planning, or refreshing skills after a toolchain change.
---

# Set Up Agent Skills

Act as a post-install concierge. Diagnose first, recommend a small repository-specific flight plan,
and use the upstream Skills CLI for installation instead of reimplementing its agent path registry.

## Run the read-only doctor

From any directory, point the bundled standard-library Python tool at the target repository:

```bash
python3 <skill-dir>/scripts/doctor.py --repo <repository>
```

Use `--format json` when another tool or agent will consume the result. Add one or more `--pack`
options when the user names an outcome; run `--list-packs` to see pack IDs. Use repeated `--skill`
and `--agent` options for an exact installation plan. The doctor never reads secret values and does
not change the machine or repository unless `--install --yes` and an explicit agent target are set.

## Onboarding workflow

1. Run the doctor before asking broad setup questions.
2. Present detected agents with confidence, repository signals with evidence, relevant skills, and
   missing conditional prerequisites.
3. Explain why each recommended skill fits. Do not recommend a skill only because it exists.
4. Default to project-local vendoring under `.agents/skills/` for reproducible team behavior. Use
   global scope only when the user explicitly wants personal defaults across repositories.
5. Ask for approval on the exact skill set, scope, and agent targets before installation.
6. After approval, either run the printed `npx skills@latest add ...` command or rerun the doctor with
   `--install --yes`. The doctor delegates actual placement and lockfile behavior to the Skills CLI.
7. Rerun the doctor, verify the installed set, and offer one immediate first win—normally a read-only
   `$agent-readiness` audit.

## Interpret prerequisite states

- **Ready:** required capabilities are present.
- **Ready with fallbacks:** the skill works, but an optional renderer, CLI, or richer output is absent.
- **Needs provider:** an external provider/MCP capability is not discoverable; do not invent results.
- **Needs setup:** a genuinely required local capability is missing.
- **Not applicable:** repository evidence does not currently match the skill unless the user selected
  a pack explicitly.

Never install system packages, create accounts, add secrets, connect providers, or mutate external
settings merely because the doctor found a gap. Give platform-appropriate guidance and request the
authority required for the next action.

## Detection discipline

- Treat an active-agent environment signal, executable, and configuration directory as separate
  evidence. A non-interactive shell can hide a real executable from `PATH`; a stale directory can
  outlive an uninstall.
- Report confidence and evidence instead of converting weak signals into certainty.
- Inspect known manifests, filenames, and configuration—not `.env` contents, credential stores,
  arbitrary home-directory files, or source data.
- Keep machine-specific findings in local output. Do not write detected paths into vendored skills.

## Installation and repository policy

The generated command uses `zacharygcook/agent-skills`, explicit skill names, copy mode, selected
agents when provided, and project scope unless `--global-scope` is requested. `--install` requires
`--yes` so an agent cannot turn a diagnostic run into a write accidentally.

Offer—but do not silently make—these follow-up repository changes:

- commit `.agents/skills/` and `skills-lock.json` when the team wants fully vendored reproducibility;
- add one concise `AGENTS.md` pointer to the vendored directory;
- initialize `AGENT_READINESS_PREFERENCES.md` through the readiness skill.

Read [references/catalog.json](references/catalog.json) only when changing packs, applicability
signals, prerequisite rules, or recommendation priority.
