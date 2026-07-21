# Traceablize: Traceable OpenSpec Workflow Installer

This skill derives three traceability-aware skills from the target project's currently installed official OpenSpec skills, installs a source-traceability validator, and deploys an optional requirement-packaging skill. It never replaces official skills.

## Installs

- `openspec-traceable-propose`, `openspec-traceable-sync-specs`, and `openspec-verify-with-report`
- `requirement-packaging`, an optional pre-propose helper for large, cross-module, or structurally inconsistent requirement documents; small, clear documents go directly to `openspec-traceable-propose`
- the `traceable-spec-driven` schema and templates
- Python validator, GUI source, and requirements under `需求追踪验证工具/`

## Run

```powershell
python "<traceablize-skill>/scripts/install_traceable_skills.py" --project-root "<project-root>"
```

When packaging is used, review `validation-report.md` and `unresolved-items.md`, then send only each executable package's `input.md` through one full `propose -> apply -> verify -> sync -> archive` cycle before its dependents. The public edition distributes source only; it does not include a packaged executable. Keep real requirements, mappings, and generated reports out of public repositories. Packaging outputs retain source text, filenames, line locations, hashes, source IDs, and revisions, so never publish `input.md`, `package.yaml`, `manifest.yaml`, or its reports without an independent sanitization review.
