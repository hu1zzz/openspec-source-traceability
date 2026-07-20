# Traceablize: Traceable OpenSpec Workflow Installer

This skill derives three traceability-aware skills from the target project's currently installed official OpenSpec skills and installs a source-traceability validator. It never replaces official skills.

## Installs

- `openspec-traceable-propose`, `openspec-traceable-sync-specs`, and `openspec-verify-with-report`
- the `traceable-spec-driven` schema and templates
- Python validator, GUI source, and requirements under `需求追踪验证工具/`

## Run

```powershell
python "<traceablize-skill>/scripts/install_traceable_skills.py" --project-root "<project-root>"
```

The public edition distributes source only; it does not include a packaged executable. Keep real requirements, mappings, and generated reports out of public repositories.
