# OpenSpec Source Traceability

An OpenSpec workflow extension and desktop GUI for validating bidirectional traceability between a source requirements document, `source-requirements.yaml`, and OpenSpec Requirements.

## What is included

- `openspec/schemas/traceable-spec-driven/`: a schema and templates that add the `source-requirements.yaml` artifact.
- `skills/traceablize/`: a Chinese-first installer skill with an English companion guide; it regenerates the traceable OpenSpec skills from the target project's official skills.
- `src/validate_source_traceability.py`: command-line validator and Markdown report generator.
- `src/traceability_report_gui.py`: Tkinter desktop GUI for running the validator.
- `examples/demo-project/`: synthetic source requirements and OpenSpec artifacts.
- `tests/`: unit tests for the validator and GUI discovery logic.

## Privacy boundary

This repository contains only synthetic examples. Do not commit real requirements documents, source identifiers, revisions, reports, mappings, environment data, or generated executables to a public repository.

## Quick start

```powershell
python -m pip install -r requirements.txt
python src/validate_source_traceability.py --project-root examples/demo-project --change demo
python src/traceability_report_gui.py
python -m unittest discover -s tests -v
```

The GUI lets you select any project directory containing `openspec/`, select a change with `source-requirements.yaml`, and generate a Markdown report.

## Traceability contract

1. Assign every source requirement a stable identifier and revision.
2. Give every OpenSpec Requirement a stable `REQ-*` identifier in an HTML comment immediately before its heading.
3. Maintain links in both directions: source YAML `specs` and Spec metadata `sources`.
4. Use explicit statuses (`pending`, `mapped`, `partial`, `excluded`, `not-applicable`, `conflict`) rather than silently omitting requirements.
5. Treat structure validation, source coverage, code tests, integration tests, and production validation as separate evidence layers.

## Security note

The validator reads local files selected by the user and writes a report to the specified project directory. Review reports before sharing them because they can contain source identifiers and titles from your own project.
