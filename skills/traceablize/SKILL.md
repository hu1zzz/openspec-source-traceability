---
name: traceablize
description: 当 OpenSpec 项目需要生成可追溯 propose、sync-specs 与 verify-with-report skill，并安装源需求追踪校验工具时使用。
license: MIT
metadata:
  version: "2.1-public"
---

# Traceablize：可追溯 OpenSpec 工作流安装器

本 skill 从目标项目**当前安装的官方 OpenSpec skill**派生三个可追溯 skill，并追加来源追踪规则；不会覆盖官方 skill。默认同时安装 Python 校验器和 GUI 源码。

英文说明见 [SKILL.en.md](SKILL.en.md)。

## 安装内容

1. `openspec-traceable-propose`
2. `openspec-traceable-sync-specs`
3. `openspec-verify-with-report`
4. `traceable-spec-driven` Schema、来源需求模板与 Spec 元数据模板
5. `需求追踪验证工具/`：Python 校验器、GUI 源码、依赖说明

## 使用步骤

1. 确认目标目录含有 `openspec/` 或 `.codex/`。
2. 确认目标项目已有官方 skill：`openspec-propose`、`openspec-sync-specs`、`openspec-verify-change`。
3. 运行：

   ```powershell
   python "<traceablize-skill>/scripts/install_traceable_skills.py" --project-root "<项目根目录>"
   ```

4. 检查三个生成的 `SKILL.md`、`openspec/schemas/traceable-spec-driven/` 和 `需求追踪验证工具/validate_source_traceability.py` 是否存在。
5. 在可用时用 skill 校验器验证生成的 skill；执行校验器前安装 `PyYAML`：

   ```powershell
   python -m pip install -r "<项目根目录>/需求追踪验证工具/requirements.txt"
   ```

## 约束

- 官方 OpenSpec skill 只作为动态来源，绝不被覆盖或替换。
- 每次运行都会重新读取目标项目的官方 skill，因此能够继承上游更新。
- 源需求、映射、报告和生成的 EXE 可能含敏感信息；公开仓库仅允许使用合成示例。
- 本公开版提供 Python GUI 源码，不分发二进制 EXE。
