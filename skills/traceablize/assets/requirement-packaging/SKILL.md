---
name: requirement-packaging
description: Use when splitting a Markdown or text requirement document into independently executable, traceable OpenSpec work packages, especially when interfaces, functions, constraints, missing IDs, conflicting sections, or inconsistent structure require an auditable packaging decision.
---

# Requirement Packaging

Use this optional skill before `openspec-traceable-propose` only for a large, cross-module, or structurally inconsistent requirement document. Small, clear documents can go directly to `openspec-traceable-propose`.

1. Run `python ".codex/skills/requirement-packaging/scripts/package_requirements.py" <requirement-file> <output-directory>`.
2. Review `validation-report.md` and `unresolved-items.md`; resolve every `BLOCKING` item.
3. Process `manifest.yaml` in dependency order. Submit only `input.md` for an executable package to `openspec-traceable-propose`.
4. Complete one package's `propose -> apply -> verify -> sync -> archive` cycle before dependents.

## Rules

- Package one independently deliverable business capability, not an arbitrary page count.
- Keep its interface, function, state, data, exception, performance, and security clauses together; put reusable constraints in a foundation package.
- Preserve source text, location, hash, ID, and revision. Do not invent identity or version.
- Assign each identifiable source requirement one primary package; cross-package reuse is a dependency.
- Record unclear boundaries, conflicts, image-only content, and inferred identities in `unresolved-items.md`; never silently exclude or mark them covered.

## Output contract

`manifest.yaml`, `validation-report.md`, and `unresolved-items.md` are global audit artifacts, not propose input. Each executable package has `input.md` (propose input) and `package.yaml` (boundary and dependencies).

## Business-module pass

Treat the script output as source fragments only. Before emitting final packages, read all fragments and build a capability map: group an interface, its corresponding functional behavior, state/validation rules, data fields, and named business flows when they govern the same entity or operation. Create one package per independently proposeable module; retain common constraints in a foundation package. Record only explicit prerequisite links as dependencies. If two fragments plausibly belong together but evidence is insufficient, put them in the same candidate package with a clear review note rather than splitting or inventing a dependency.
