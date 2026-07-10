---
name: ban-type-assertions
description: Enforce a TypeScript policy that bans `as` type assertions and replace casts with compiler-verified narrowing or runtime validation. Use when introducing the ESLint rule, removing violations, reviewing assertion workarounds, or designing typed data boundaries.
---

# Ban Type Assertions

Configure `@typescript-eslint/consistent-type-assertions` with `assertionStyle: "never"`, then replace assertions with code the compiler or runtime can verify. Treat `as const` according to the repository's explicit policy.

## Decision Order

### 1. Validate external data

Parse JSON, network responses, storage, database rows, messages, and other untrusted inputs with the repository's runtime schema library.

```ts
// Avoid
const value = JSON.parse(raw) as Payload

// Prefer
const value = PayloadSchema.parse(JSON.parse(raw))
```

Use non-throwing parse APIs where failure needs structured handling or request context.

### 2. Narrow with control flow

Use discriminated unions, exhaustive `switch`, `typeof`, `instanceof`, and `in` when TypeScript can prove the result.

```ts
if (error instanceof Error && "code" in error) {
  handleCode(error.code)
}
```

### 3. Improve the API or types

Fix overly broad return types, generic inference, duplicate domain types, and missing package contracts. Prefer `satisfies` when checking an object without changing its inferred type.

### 4. Document a genuine exception

Use a narrow lint suppression only for an unavoidable library/type-system gap. Explain why it is safe and why normal narrowing cannot work. Do not quietly raise a ratchet threshold.

## Avoid Disguised Assertions

A custom predicate returning `value is T` is still an assertion unless its checks fully establish `T`. Use schema validation for rich object shapes. Do not replace one cast with a weak guard that only checks one property.

## Rollout

1. Locate all TypeScript packages and their ESLint configurations.
2. Enable the rule consistently.
3. Inventory violations and classify boundary, narrowing, API-design, and unavoidable cases.
4. Fix violations package by package.
5. Add a CI check or zero-tolerance report if repository lint scope can miss files.
6. Run lint, typecheck, focused tests, the full suite when practical, and unused-export checks after shared-type changes.

Test fixtures must satisfy the same schemas as production data; do not disable the rule in tests merely to keep incomplete mocks.
