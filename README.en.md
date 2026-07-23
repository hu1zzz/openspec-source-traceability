# OpenSpec Source Traceability Workflow

[中文说明](README.md)

This repository extends an OpenSpec workflow without replacing official skills. Install and invoke `traceablize`; it derives traceability-aware skills from the target project's official skills and adds source-to-Spec evidence tracking.

## What is OpenSpec, and what does this add?

[OpenSpec](https://openspec.pro/) is a lightweight spec-driven development framework for human and AI collaboration. A change is reviewed as a proposal, behavioral specs, technical design, and implementation tasks before code is written. This repository preserves that workflow and adds an auditable question that the base workflow does not require: which source requirement and revision led to each Spec Requirement, and what evidence supports its implementation?

The added traceability chain is:

```text
source document/work package → source-inventory.yaml → source-requirements.yaml → Spec Requirements
                                                                               ↓
                                                tasks / code / tests / verification report
```

For newly handled source requirements, the workflow also records independently testable `acceptancePoints`. A source is `mapped` only when every acceptance point links to an exact Requirement and named Scenario.

## Workflow

1. Initialize a normal OpenSpec project.
2. Copy `skills/traceablize/` into `<project>/.codex/skills/traceablize/`.
3. Invoke `$traceablize`, or run its installer script.
4. For a large, cross-module, or structurally inconsistent document, optionally run `requirement-packaging`; otherwise go directly to `openspec-traceable-propose`.
5. Use the generated `openspec-traceable-propose`, `openspec-traceable-apply-change`, `openspec-traceable-sync-specs`, and `openspec-verify-with-report` skills in place of the corresponding stages.
6. Continue using normal `openspec-archive-change` for archival.

The installer also deploys an optional `requirement-packaging` helper and the `traceable-spec-driven` schema. Packaging is not part of the default lifecycle. `traceable-propose` creates `source-inventory.yaml` internally and separates local work from external adapters and product decisions. `traceable-apply-change` completes local work before it may pause for an external dependency. `verify-with-report` audits task classes, split history, and pause evidence; no fixed-format parser or GUI is installed.

## Installation

```powershell
Copy-Item "<repository>\skills\traceablize" `
  "<project>\.codex\skills\traceablize" -Recurse -Force

python "<project>\.codex\skills\traceablize\scripts\install_traceable_skills.py" `
  --project-root "<project>"

```

The project must already contain its official OpenSpec propose, sync-specs, and verify-change skills. The installer rereads them on every run, preserving upstream changes while reapplying the traceability overlays.

## Privacy

Only synthetic examples are included. Never publish real requirement documents, source identifiers, mappings, generated reports, environment data, application code, or executables without a separate sanitization review. Packaging outputs (`input.md`, `package.yaml`, `manifest.yaml`, `validation-report.md`, and `unresolved-items.md`) retain source text, filenames, line locations, hashes, source IDs, and revisions; do not publish them without a separate sanitization review.
