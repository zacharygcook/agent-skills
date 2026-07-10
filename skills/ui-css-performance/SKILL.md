---
name: ui-css-performance
description: Prevent unused UI source, CSS growth, Tailwind scanning waste, and frontend dependency bloat while adding or changing components and visual effects. Use for UI primitives, Tailwind configuration, CSS files, component libraries, or frontend dependency changes.
---

# UI and CSS Performance

Add the smallest UI surface that solves the real task and measure the result when bundle or stylesheet size may change.

## Core Rules

- Prefer an existing component or simple local markup before adding a new reusable primitive.
- Add only component-library primitives that product code actually imports.
- Delete dormant components, providers, hooks, forms, and wrappers; source scanners may include them even when the JavaScript bundle does not.
- Declare every directly imported package and remove packages whose final consumer disappears.
- Keep utility-class names as static strings or finite maps of complete strings. Avoid dynamically assembled class fragments that scanners cannot discover reliably.
- Do not broaden content globs, enable plugins, or import global styles without measuring their effect.
- Keep admin/editor CSS out of public routes unless those routes need it.

## New Primitive Checklist

1. Confirm no existing primitive already fits.
2. Add only the primitive and direct dependencies it needs.
3. Import it from real application code in the same change.
4. Run the repository's UI lint, unused-code/dependency scan, typecheck, and build.
5. If it remains unused, remove it instead of suppressing the check.

## Measure

Use repository-native build and bundle tooling. Compare the relevant route chunks and emitted CSS before and after when the change adds a library, plugin, global stylesheet, animation system, icon set, or broad content glob. Record units and whether sizes are raw, minified, or compressed.

If exact bundle tooling is unavailable, report that limitation and use bounded evidence such as emitted asset sizes and import reachability. Do not claim a performance win without measurement.
