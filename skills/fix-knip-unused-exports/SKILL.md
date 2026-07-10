---
name: fix-knip-unused-exports
description: Resolve Knip unused-export findings by classifying each symbol before editing and preferring dead-code deletion, local visibility, or deliberate package contracts over suppression. Use for unused exports, exported types, barrel re-exports, test-only exports, and apparent false positives.
---

# Fix Knip Unused Exports

Unused-export reports are small but easy to “fix” incorrectly. Search the whole repository, classify the contract, then make the smallest truthful change.

## Workflow

1. Run the repository's Knip command from its expected root.
2. Search each symbol globally and separately outside tests.
3. Inspect package entry points, export maps, generated imports, and dynamic consumers.
4. Classify the finding.
5. Apply the preferred fix.
6. Rerun Knip plus focused typecheck, lint, and tests.

## Classification

| Category | Evidence | Preferred fix |
| --- | --- | --- |
| Internally used | Referenced only in its defining module | Remove `export` |
| Dead code | No real caller | Delete it and newly orphaned helpers |
| Dead barrel entry | Re-exported but not consumed | Remove the re-export |
| Test-only seam | Export exists only for tests | Test public behavior or extract a genuinely shared helper |
| Real consumer | Production/generated/dynamic consumer exists | Correct Knip entry/config/export metadata |

Do not add broad ignores, dummy imports, speculative barrel exports, or `@public` comments solely to silence the tool.

## Contract Checks

Before removing a package export, inspect:

- `package.json` exports and types;
- workspace consumers and build scripts;
- framework conventions for discovered files;
- code generation and dynamic import strings;
- documentation examples that form a supported API.

When deleting a value, remove stale tests, imports, docs, and adjacent helpers only after confirming they have no independent use. Preserve intentional public APIs even when the current monorepo has no internal consumer; document that decision in Knip configuration narrowly.

## Handoff

Report each classification, the change made, any intentional suppression, and validation results.
