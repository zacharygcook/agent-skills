---
name: mermaid-diagrams
description: Create, review, render, and maintain Mermaid diagrams for architecture, flows, sequences, state machines, schemas, timelines, and tradeoffs. Use when a visual model materially clarifies structure or behavior and the result should remain diagrams-as-code or exported SVG/PNG.
---

# Mermaid Diagrams

Use a diagram only when relationships, sequence, hierarchy, state, or ownership are harder to understand in prose or a small table.

## Choose the Smallest Useful Form

- `flowchart` / `graph`: pipelines, decisions, dependencies.
- `sequenceDiagram`: request/response and async interaction.
- `stateDiagram-v2`: lifecycle and transition rules.
- `erDiagram`: entities, keys, and cardinality.
- `classDiagram`: type/object relationships.
- C4 context/container: system boundaries and ownership.
- `timeline`: history or roadmap.
- `quadrantChart`: explicit two-axis tradeoffs.

Start with fewer than ten meaningful nodes when possible; split crowded diagrams by concern.

## Authoring Rules

- Verify labels and edges against source code or authoritative docs.
- Use short nouns or verb phrases, and quote labels containing punctuation.
- Draw direction only when it carries meaning.
- Encode status or category with color sparingly; never rely on color alone.
- Add a caption that states the diagram's purpose.
- Keep layout deterministic enough that future edits remain readable.
- Prefer SVG for documentation and PNG for quick review when both are supported.

## Validate and Render

Use repository-native docs/build tooling first. Otherwise use an already available Mermaid CLI or renderer; do not require a global install merely for a small draft. Inspect the actual render for syntax failures, clipped labels, crossing edges, and light/dark contrast.

Store source and exports according to repository convention. If the user wants only a review artifact, keep scratch source and renders in a gitignored location. If the diagram is durable documentation, track the source next to its consumer and ensure docs do not link to disposable paths.

## Handoff

Provide the source, rendered artifact paths, validation command, and any assumptions the diagram makes. Do not claim the visual is authoritative unless it was checked against the implementation.
