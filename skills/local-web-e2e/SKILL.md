---
name: local-web-e2e
description: Design, run, and debug trustworthy local browser end-to-end tests with isolated ports, disposable data, readiness checks, deterministic seeds, and state restoration. Use for local web smoke suites, authenticated flows, multi-service launchers, or E2E environment hardening.
---

# Local Web E2E

Make local browser tests safe to run beside normal development and strong enough to reveal real integration failures.

## Safety Invariants

- Use a dedicated E2E database or isolated datastore namespace.
- Fail closed before any reset: verify the target clearly identifies itself as E2E and require an explicit override for exceptions.
- Use dedicated ports and build/cache directories so tests do not collide with running dev servers.
- Never borrow an arbitrary existing server unless the suite verifies its configuration and data target.
- Keep credentials synthetic and secrets out of tracked files.

## Environment Lifecycle

1. Run a doctor/preflight check for runtimes, browsers, ports, database reachability, and required configuration.
2. Build shared packages needed by multiple services.
3. Reset, migrate, and seed the disposable datastore deterministically.
4. Start services with isolated ports and capture logs.
5. Wait on health/readiness endpoints, not fixed sleeps.
6. Run browser tests with intentional concurrency.
7. On failure, retain traces, screenshots, videos, and service logs.
8. Stop only processes launched by the suite and restore mutated state when a test exercises operator controls.

## Test Quality

Prefer a short set of high-signal journeys:

- authentication and authorization boundaries;
- a primary user workflow from UI through API and persistence;
- loading, empty, error, and retry states;
- cross-origin/session behavior in realistic local topology;
- admin/operator actions followed by explicit state restoration.

Use stable roles, labels, and test IDs. Avoid timing-only assertions and selectors tied to cosmetic DOM structure. Seed prerequisites directly when setup through the UI would add noise without testing meaningful behavior.

## Debugging Order

1. Read the first application/service error, not only the browser timeout.
2. Confirm the browser reached the intended port and build directory.
3. Confirm every service points at the disposable datastore.
4. Inspect readiness and seed output.
5. Open the trace and screenshot.
6. Re-run the narrowest failing test before the whole suite.

Document repository-specific commands and safety sentinels near the launcher. Do not encode one project's ports or package manager into this reusable skill.
