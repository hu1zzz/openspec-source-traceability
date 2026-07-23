# Traceablize: Traceable OpenSpec Workflow Installer

This skill derives four traceability-aware skills from the target project's currently installed official OpenSpec skills and deploys an optional requirement-packaging skill. It never replaces official skills. The generated propose skill creates a source inventory and task classes internally; the generated apply skill finishes local work before external dependencies can pause progress.

## Installs

- `openspec-traceable-propose`, `openspec-traceable-apply-change`, `openspec-traceable-sync-specs`, and `openspec-verify-with-report`
- `requirement-packaging`, an optional pre-propose helper for large, cross-module, or structurally inconsistent requirement documents; small, clear documents go directly to `openspec-traceable-propose`
- the `traceable-spec-driven` schema, including `source-inventory.yaml` and `source-requirements.yaml`

## Run

```powershell
python "<traceablize-skill>/scripts/install_traceable_skills.py" --project-root "<project-root>"
```

When packaging is used, review `validation-report.md` and `unresolved-items.md`, then send only each executable package's `input.md` through one full `propose -> apply -> verify -> sync -> archive` cycle before its dependents. The installer safely removes only its known legacy validator/GUI files and never recursively deletes the legacy directory or reports. Keep real requirements, mappings, and generated reports out of public repositories. Packaging outputs retain source text, filenames, line locations, hashes, source IDs, and revisions, so never publish `input.md`, `package.yaml`, `manifest.yaml`, or its reports without an independent sanitization review.
