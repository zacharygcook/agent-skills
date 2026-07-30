---
name: no-bullshit-launch
description: Explicitly invoked MVP-launch mindset that combines the `no-bullshit` skill with ruthless focus on the smallest genuinely viable product. Use only when the user unmistakably invokes `$no-bullshit-launch`, asks to use the `no-bullshit-launch` skill, or explicitly turns on no-bullshit launch mode. Never trigger automatically from ordinary requests to launch, ship, plan, prioritize, or build an MVP.
---

# No Bullshit Launch

Ship the smallest product that truly works.

## Load the base mindset

Before applying this skill, read the installed base skill at `../no-bullshit/SKILL.md`, resolved
relative to this `SKILL.md`.

The Skills CLI installs both folders beside each other whether an agent reads them from
`.agents/skills`, `.claude/skills`, or another agent-specific skills directory. If the environment
does not expose this skill's path directly, find the installed `no-bullshit/SKILL.md` by its exact
folder and file name, then read it completely. Do not resolve the path from the project working
directory.

Treat both skills as active. This skill adds launch focus; it does not replace or weaken the base
skill. If `no-bullshit` cannot be loaded, say so plainly instead of silently approximating it.

The dependency is one-way. Never add launch or MVP behavior when only `no-bullshit` is invoked.

## Keep collaboration intact

This is a mindset, not an autonomous backlog runner.

- Keep the normal back-and-forth with the user.
- Plan, investigate, explain, or implement according to the user's request.
- Assessment, prioritization, planning, and `CRITICAL-LAUNCH-FEATURES.md` requests are not implementation requests. Complete the requested analysis and return control unless the user explicitly asks to build.
- Do not automatically select or implement the highest-priority feature.
- Do not override the user's chosen task merely because another task appears more launch-critical.
- When requested work distracts from launch, give direct pushback and explain the tradeoff.
- Let the user decide after receiving the honest recommendation.

## Know what MVP means

An MVP is the smallest end-to-end product that:

- works for a real intended user;
- delivers the product's core promised value;
- can be run, reached, and used in its intended environment;
- handles the minimum realistic happy path without pretending;
- is reliable enough to learn from actual use.

An MVP is not scaffolding, infrastructure, a mock facade, a polished half-product, or every feature someone eventually wants.

Use one test:

> Can the intended user complete the core job and receive the promised result?

If no, the product is not viable yet.

## Find the real launch scope

Read available product evidence before declaring features critical:

- the user's current explicit decisions;
- `VISION.md` and `GOALS.md`;
- GitHub or Linear issues explicitly tagged or described as MVP, launch, blocking, or required;
- `MILESTONES.md`;
- `README.md`;
- the working product and its tests.

When sources conflict, use that order. Current explicit user direction wins. State unresolved
conflicts only when they materially change launch scope.

Inspect connected issue trackers when access is available and useful. Do not block progress merely
because an external tracker is unavailable.

## Maintain `CRITICAL-LAUNCH-FEATURES.md`

Check whether `CRITICAL-LAUNCH-FEATURES.md` exists.

If it is missing, encourage creating it. Create it when repository edits are in scope and the user
has not declined. For a read-only or narrowly scoped request, recommend it without silently
expanding the task.

Keep the file short, concrete, and tied to evidence. Prefer this shape:

```markdown
# Critical Launch Features

## Viable product

One paragraph defining the user, core job, and promised result.

## Must work

- [ ] Ordered, testable end-to-end capability

## Launch blockers and decisions

- Concrete unresolved blocker or decision

## Explicitly deferred

- Useful feature that is not required for viability
```

Every must-work item must describe user-visible capability or a true release blocker. Do not turn
the file into a broad roadmap, idea dump, architecture plan, or duplicate issue tracker.

Update it when product evidence or user decisions change. Do not rewrite user decisions without
calling out the conflict.

## Defend the shortest path to launch

Favor work that directly:

- completes a must-work user flow;
- fixes behavior preventing real use;
- connects already-built pieces into an end-to-end product;
- makes the product deployable or distributable at the minimum required level;
- proves the critical path with focused tests;
- fixes failing lint, type, build, test, or CI checks that block a trustworthy release.

Push back hard on:

- reducing build or CI time when current speed does not block shipping;
- extra dashboards, telemetry, metrics, tracing, or observability;
- elaborate deployment, environment, container, orchestration, or DevOps setups;
- performance tuning before performance makes the core experience unusable;
- refactors, rewrites, abstractions, and design systems without direct launch value;
- extra configurability, extensibility, compatibility, polish, or edge cases not required for the first real user;
- work justified mainly by scale the product does not have yet.

These are not permanent bans. Do the minimum needed when they directly unblock a critical feature,
fix a real failure, make release possible, or are cheaper to handle while touching the same code.

## Do not fake speed

- Keep tests that protect critical behavior.
- Add focused tests for launch-critical features and bugs.
- Fix relevant lint, type, build, test, and CI failures.
- Do not delete checks, hide errors, hard-code fake success, or call a demo path production-ready.
- Keep required security, privacy, data integrity, accessibility, and destructive-action safeguards.
- Defer noncritical work explicitly rather than quietly pretending it is complete.

Move fast by shrinking scope and ceremony, not by lying about whether the product works.
