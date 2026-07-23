---
name: traceablize
description: 当 OpenSpec 项目需要生成可追溯 propose、apply、sync-specs 与 verify-with-report skill，以及来源清单 Schema 时使用。
license: MIT
metadata:
  version: "2.1-public"
---

# Traceablize：可追溯 OpenSpec 工作流安装器

本 skill 从目标项目**当前安装的官方 OpenSpec skill**派生四个可追溯 skill，并追加来源追踪规则；不会覆盖官方 skill。来源核验由生成的 verify skill 完成，不安装固定格式 Python 校验器或 GUI。

英文说明见 [SKILL.en.md](SKILL.en.md)。

## 安装内容

1. `openspec-traceable-propose`
2. `openspec-traceable-apply-change`
3. `openspec-traceable-sync-specs`
4. `openspec-verify-with-report`
5. `requirement-packaging`：仅在大型、跨模块或结构不一致的需求文档需要先分块时调用；小型且结构清晰的文档直接进入 `openspec-traceable-propose`
5. `traceable-spec-driven` Schema、`source-inventory.yaml`、来源需求模板与 Spec 元数据模板

## 使用步骤

1. 确认目标目录含有 `openspec/` 或 `.codex/`。
2. 确认目标项目已有官方 skill：`openspec-propose`、`openspec-sync-specs`、`openspec-verify-change`。
3. 运行：

   ```powershell
   python "<traceablize-skill>/scripts/install_traceable_skills.py" --project-root "<项目根目录>"
   ```

4. 检查三个追踪增强 skill、`requirement-packaging/SKILL.md`、`openspec/schemas/traceable-spec-driven/source-inventory.yaml` 与 `source-requirements.yaml` 是否存在。

## 约束

- 官方 OpenSpec skill 只作为动态来源，绝不被覆盖或替换。
- 每次运行都会重新读取目标项目的官方 skill，因此能够继承上游更新。
- `requirement-packaging` 是可选前置步骤，不改变默认 OpenSpec 生命周期；需要时先审阅其 `validation-report.md` 与 `unresolved-items.md`，再仅将可执行工作包的 `input.md` 交给 `openspec-traceable-propose`。
- 源需求、映射、报告和生成的 EXE 可能含敏感信息；公开仓库仅允许使用合成示例。
- 分块产物会保留原文、来源文件名、行号、哈希、来源 ID 与修订；`input.md`、`package.yaml`、`manifest.yaml` 和报告必须经过独立脱敏审查，不能直接公开。
- 安装器迁移时只移除旧工具目录中它曾管理的程序文件，不递归删除目录或报告。
