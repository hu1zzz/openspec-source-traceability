# OpenSpec Source Traceability Workflow

[中文说明](README.md)

This repository extends an OpenSpec workflow without replacing official skills. Install and invoke `traceablize`; it derives traceability-aware skills from the target project's official skills and adds source-to-Spec evidence tracking.

## Workflow

1. Initialize a normal OpenSpec project.
2. Copy `skills/traceablize/` into `<project>/.codex/skills/traceablize/`.
3. Invoke `$traceablize`, or run its installer script.
4. Use the generated `openspec-traceable-propose`, `openspec-traceable-sync-specs`, and `openspec-verify-with-report` skills in place of the corresponding propose, sync, and verify stages.
5. Continue using normal `openspec-apply-change` and `openspec-archive-change` for implementation and archival.

The installer also deploys the `traceable-spec-driven` schema plus a Python CLI validator and Tkinter GUI under `需求追踪验证工具/`.

## Installation

```powershell
Copy-Item "<repository>\skills\traceablize" `
  "<project>\.codex\skills\traceablize" -Recurse -Force

python "<project>\.codex\skills\traceablize\scripts\install_traceable_skills.py" `
  --project-root "<project>"

python -m pip install -r "<project>\需求追踪验证工具\requirements.txt"
```

The project must already contain its official OpenSpec propose, sync-specs, and verify-change skills. The installer rereads them on every run, preserving upstream changes while reapplying the traceability overlays.

## Privacy

Only synthetic examples are included. Never publish real requirement documents, source identifiers, mappings, generated reports, environment data, application code, or executables without a separate sanitization review.
