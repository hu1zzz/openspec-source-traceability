#!/usr/bin/env python3
"""Derive Traceablize skills from the project's current official OpenSpec skills."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml

DERIVATIONS = [
    {
        "source": "openspec-propose",
        "target": "openspec-traceable-propose",
        "description": (
            "Use when creating or regenerating an OpenSpec proposal and specs from a "
            "requirement document where source requirements must remain bidirectionally "
            "traceable to stable Spec Requirement IDs, including incremental updates "
            "compared with current main specs."
        ),
        "overlay": "propose.md",
    },
    {
        "source": "openspec-apply-change",
        "target": "openspec-traceable-apply-change",
        "description": (
            "Use when implementing an OpenSpec change whose tasks must finish local work "
            "before external dependencies or product decisions can pause progress."
        ),
        "overlay": "apply-change.md",
    },
    {
        "source": "openspec-sync-specs",
        "target": "openspec-traceable-sync-specs",
        "description": (
            "Use when synchronizing traceable OpenSpec delta specs into main specs while "
            "stable Requirement IDs and source requirement ID/revision metadata must be "
            "preserved, merged, replaced, or removed correctly."
        ),
        "overlay": "sync-specs.md",
    },
    {
        "source": "openspec-verify-change",
        "target": "openspec-verify-with-report",
        "description": (
            "Use when an OpenSpec change must be checked for implementation completeness, "
            "requirement or scenario omissions, test evidence, design adherence, archive "
            "readiness, or a persistent verification report."
        ),
        "overlay": "verify-with-report.md",
    },
]

ALLOWED_FRONTMATTER_KEYS = ("license", "metadata", "allowed-tools")
LEGACY_TOOL_DIRECTORY = "需求追踪验证工具"
LEGACY_TOOL_FILES = (
    "validate_source_traceability.py",
    "traceability_report_gui.py",
    "requirements.txt",
)
SCHEMA_NAME = "traceable-spec-driven"
SOURCE_SCHEMA_NAME = "spec-driven"


def asset_root() -> Path:
    return Path(__file__).resolve().parents[1] / "assets"


def schema_overlay_root() -> Path:
    return asset_root() / "schema-overlays"


def resolve_official_schema() -> Path:
    command = ["openspec.cmd", "schema", "which", SOURCE_SCHEMA_NAME, "--json"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("OpenSpec CLI is unavailable: openspec.cmd") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"Cannot resolve official {SOURCE_SCHEMA_NAME} schema: {message}") from exc
    try:
        path = Path(json.loads(result.stdout)["path"])
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError("OpenSpec returned invalid schema resolution JSON") from exc
    if not (path / "schema.yaml").is_file():
        raise FileNotFoundError(f"Official schema is incomplete: {path}")
    return path


def apply_schema_overlays(target_schema: Path) -> None:
    overlay_root = schema_overlay_root()
    schema_overlay = overlay_root / "schema.yaml"
    source_schema = target_schema / "schema.yaml"
    if not schema_overlay.is_file():
        raise FileNotFoundError(f"Traceablize schema overlay is missing: {schema_overlay}")
    if not source_schema.is_file():
        raise FileNotFoundError(f"Target schema is missing schema.yaml: {source_schema}")

    base = yaml.safe_load(source_schema.read_text(encoding="utf-8")) or {}
    overlay = yaml.safe_load(schema_overlay.read_text(encoding="utf-8")) or {}
    artifacts = list(base.get("artifacts") or [])
    artifact_by_id = {artifact.get("id"): artifact for artifact in artifacts}
    source_artifacts = overlay["source_artifacts"]
    for source_artifact in source_artifacts:
        artifact_by_id[source_artifact["id"]] = source_artifact
    ordered_artifacts = list(source_artifacts)
    for artifact in artifacts:
        if artifact.get("id") not in {item["id"] for item in source_artifacts}:
            ordered_artifacts.append(artifact)
    for artifact in ordered_artifacts:
        override = (overlay.get("requires_overrides") or {}).get(artifact.get("id"))
        if override is not None:
            artifact["requires"] = override

    base["name"] = overlay["name"]
    base["description"] = overlay["description"]
    base["artifacts"] = ordered_artifacts
    source_schema.write_text(
        yaml.safe_dump(base, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )

    templates = overlay_root / "templates"
    for template in templates.iterdir():
        if template.is_file():
            shutil.copy2(template, target_schema / "templates" / template.name)


def install_traceable_schema(project_root: Path, source_schema: Path) -> Path:
    project_root = Path(project_root).resolve()
    source_schema = Path(source_schema).resolve()
    if not (source_schema / "schema.yaml").is_file():
        raise FileNotFoundError(f"Official source schema is incomplete: {source_schema}")
    target = project_root / "openspec" / "schemas" / SCHEMA_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_schema, target, dirs_exist_ok=True)
    (target / "templates").mkdir(parents=True, exist_ok=True)
    apply_schema_overlays(target)
    return target


def configure_traceable_schema(project_root: Path) -> bool:
    config_path = Path(project_root).resolve() / "openspec" / "config.yaml"
    original = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    match = re.search(r"(?m)^schema\s*:\s*[^\r\n#]+", original)
    if match and re.sub(r"^schema\s*:\s*", "", match.group(0)).strip() == SCHEMA_NAME:
        return False
    backup_path = config_path.with_name(f"{config_path.name}.traceablize.bak")
    if config_path.exists() and not backup_path.exists():
        shutil.copy2(config_path, backup_path)
    if match:
        updated = original[: match.start()] + f"schema: {SCHEMA_NAME}" + original[match.end() :]
    else:
        updated = f"schema: {SCHEMA_NAME}\n{original}"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(updated, encoding="utf-8")
    return True


def split_skill(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"Official skill has no YAML frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"Official skill has invalid YAML frontmatter: {path}")
    frontmatter: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter, text[end + 5 :].lstrip()


def render_skill(source_file: Path, target: str, description: str, overlay_file: Path) -> str:
    source_frontmatter, source_body = split_skill(
        source_file.read_text(encoding="utf-8"), source_file
    )
    overlay = overlay_file.read_text(encoding="utf-8").strip()
    lines = [f"name: {target}", f"description: {description}"]
    for key in ALLOWED_FRONTMATTER_KEYS:
        value = source_frontmatter.get(key)
        if value:
            lines.append(f"{key}: {value}")
    frontmatter = "---\n" + "\n".join(lines) + "\n---"
    return (
        f"{frontmatter}\n\n{source_body.rstrip()}\n\n---\n\n"
        f"# Traceablize 强制扩展\n\n{overlay}\n"
    )


def remove_legacy_tool_files(project_root: Path) -> list[str]:
    """Remove only former managed program files, never reports or the directory."""
    target_dir = Path(project_root).resolve() / LEGACY_TOOL_DIRECTORY
    removed: list[str] = []
    for name in LEGACY_TOOL_FILES:
        candidate = target_dir / name
        if candidate.is_file():
            candidate.unlink()
            removed.append(str(candidate))
    return removed


def install_skills(project_root: Path) -> list[str]:
    project_root = Path(project_root).resolve()
    destination = project_root / ".codex" / "skills"
    destination.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    for derivation in DERIVATIONS:
        source_file = destination / derivation["source"] / "SKILL.md"
        overlay_file = asset_root() / "overlays" / derivation["overlay"]
        if not source_file.is_file():
            raise FileNotFoundError(f"Updated official source skill is missing: {source_file}")
        if not overlay_file.is_file():
            raise FileNotFoundError(f"Traceablize overlay is missing: {overlay_file}")

        target_dir = destination / derivation["target"]
        target_dir.mkdir(parents=True, exist_ok=True)
        rendered = render_skill(
            source_file,
            derivation["target"],
            derivation["description"],
            overlay_file,
        )
        (target_dir / "SKILL.md").write_text(rendered, encoding="utf-8")

        agent_file = asset_root() / "agents" / f'{derivation["target"]}.yaml'
        if agent_file.is_file():
            agents_dir = target_dir / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(agent_file, agents_dir / "openai.yaml")
        installed.append(derivation["target"])
    packaging_source = asset_root() / "requirement-packaging"
    if not (packaging_source / "SKILL.md").is_file():
        raise FileNotFoundError(f"Requirement packaging asset is missing: {packaging_source}")
    shutil.copytree(packaging_source, destination / "requirement-packaging", dirs_exist_ok=True)
    installed.append("requirement-packaging")
    remove_legacy_tool_files(project_root)
    return installed


def install_project(project_root: Path) -> dict[str, object]:
    project_root = Path(project_root).resolve()
    source_schema = resolve_official_schema()
    schema_path = install_traceable_schema(project_root, source_schema)
    schema_configured = configure_traceable_schema(project_root)
    legacy_tool_files_removed = remove_legacy_tool_files(project_root)
    installed = install_skills(project_root)
    return {
        "projectRoot": str(project_root),
        "installed": installed,
        "count": len(installed),
        "legacyToolFilesRemoved": legacy_tool_files_removed,
        "schemaSource": str(source_schema),
        "schemaPath": str(schema_path),
        "schemaConfigured": schema_configured,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Derive traceability-aware skills from the project's current official "
            "OpenSpec skills"
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="OpenSpec project root; defaults to the current directory",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()
    result = install_project(args.project_root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Traceablize installed {result['count']} skills:")
        for name in result["installed"]:
            print(f"  - {name}")
        if result["legacyToolFilesRemoved"]:
            print("Removed legacy validation-tool files:")
            for path in result["legacyToolFilesRemoved"]:
                print(f"  - {path}")
        print(f"Schema: {result['schemaPath']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
