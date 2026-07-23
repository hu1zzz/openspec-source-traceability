# OpenSpec 来源需求追踪工作流

[English README](README.en.md)

这是一个对 OpenSpec 的工作流扩展：它不改写官方 skill，而是通过 `traceablize` 从目标项目现有的官方 skill 动态派生可追溯版本，并为来源需求、Spec、验证证据建立双向追踪。

## OpenSpec 是什么？本项目解决什么问题？

[OpenSpec](https://openspec.pro/) 是一个面向人类与 AI 协作的轻量级 Spec-Driven Development（规格驱动开发）框架。它把一次变更先整理为可审阅的文档，再开始编码：`proposal` 说明为什么做与范围，`specs` 描述系统应当如何行为，`design` 记录技术决策，`tasks` 把工作拆成可执行步骤。完成实现后，再把确认后的规范沉淀为长期维护的项目知识。

这能避免“先让 AI 写代码，再回头猜需求”的问题；但标准流程通常不要求回答另一个审计问题：**某条 Spec 到底来自哪一条原始需求，需求版本变化后又影响了哪些实现和测试？**

本项目在不替换 OpenSpec 的前提下补上这条证据链：

```text
原始需求/工作包 → source-inventory.yaml → source-requirements.yaml → Spec Requirement
                                                                  ↓
                                                  tasks / 代码 / 测试 / 验证报告
```

## 每一步做什么、为什么做？

| 阶段 | OpenSpec 的作用 | 本项目增加的作用 | 为什么需要它 |
|---|---|---|---|
| 需求分块（可选） | 标准流程以一个 change 为单位推进，不规定如何处理超大输入文档。 | 对大型、跨模块或结构/编号不一致的来源文档，先按可独立交付的业务能力拆成工作包，并记录边界、依赖和待确认项。小型且结构清晰的文档跳过此步。 | 避免一次 propose 读取过多无关内容；同时不把仅按页数切开的片段误当成可独立实施的需求。 |
| 来源清单 | 标准流程不定义原文盘点格式。 | `traceable-propose` 内部自动建立 `source-inventory.yaml`，使用稳定 `SRC-*` ID；原文编号和修订均可缺省。 | 先固定审计对象，避免把某一种外部系统编号格式当成通用需求语法。 |
| Proposal | 明确变更原因、范围和影响面。 | 从来源清单登记本次新增或修订的来源需求。 | 先确认“为什么做、哪些需求在范围内”，避免漏项。 |
| Specs | 用 Requirement 与 Scenario 定义应有行为。 | 为每条 Requirement 分配稳定 `REQ-*` ID，并写入来源 ID 与 Revision。 | 需求标题可以改，但稳定 ID 和来源版本可用于追溯影响。 |
| 验收点对账 | 标准流程不强制拆分来源内部义务。 | 每条新增或修订来源需求拆成 `acceptancePoints`；每点必须映射到 Requirement 和命名 Scenario。 | 防止详细表格、字段或约束只覆盖一部分却被误判为完整覆盖。 |
| Design | 记录架构、权衡和冲突裁决。 | 保留需求冲突、排除和派生需求的理由。 | 防止工程假设被误写成用户需求。 |
| Tasks / Apply | 将规范拆成任务并实现。 | 区分代码、集成和真实环境证据。 | “任务勾选”或“单测通过”不等于生产能力已验证。 |
| Verify / Archive | 检查变更并沉淀规范。 | agent 直接核验原文、inventory、映射、Spec、代码和测试证据。 | 适用于无编号、编号不统一、表格或自然语言文档；无法可靠读取时明确标记限制。 |

## 先理解完整流程

```text
初始化普通 OpenSpec 项目
        ↓
安装并调用 $traceablize
        ↓
生成 4 个追踪增强 skill、含 source-inventory 的 Schema 和分块 skill
        ↓
需求文档是否大型、跨模块或结构不一致？
   ├─ 是：可选运行 requirement-packaging，逐包进入 propose
   └─ 否：直接进入 traceable-propose
        ↓
按常规 OpenSpec 生命周期工作
（仅在 propose / sync / verify 阶段改用增强 skill）
```

## 产物与职责

执行 `$traceablize` 后，目标项目会获得：

| 产物 | 用途 |
|---|---|
| `openspec-traceable-propose` | 创建 change 时提取来源需求、生成稳定 `REQ-*` ID，并完成 YAML 与 Spec 双向对账。 |
| `openspec-traceable-apply-change` | 先完成所有可独立实施的本地任务；将跨模块真实接入单列为外部适配任务，只有没有可执行本地任务时才允许暂停。 |
| `openspec-traceable-sync-specs` | 将 delta Spec 同步到主 Spec 时保留来源 ID、Revision 和双向映射。 |
| `openspec-verify-with-report` | 核查任务、Requirement、Scenario、测试和环境证据，并生成持久化验证报告。 |
| `requirement-packaging` | 可选前置工具：将大型或结构复杂的来源文档整理为可独立执行的工作包；不是日常必经步骤。 |
| `openspec/schemas/traceable-spec-driven/` | 含 `source-inventory.yaml` 与 `source-requirements.yaml` 工件的追踪 Schema；安装器会将其设为项目 Schema。 |

官方的 `openspec-propose`、`openspec-sync-specs`、`openspec-verify-change` 不会被覆盖。

## 安装

### 1. 准备普通 OpenSpec 项目

先按 OpenSpec 的常规方式初始化项目。目标项目应已有：

```text
.codex/skills/openspec-propose/SKILL.md
.codex/skills/openspec-sync-specs/SKILL.md
.codex/skills/openspec-verify-change/SKILL.md
openspec/
```

### 2. 安装 `traceablize` 入口 skill

克隆本仓库后，将入口 skill 复制到目标项目：

```powershell
Copy-Item "<本仓库>\skills\traceablize" `
  "<目标项目>\.codex\skills\traceablize" -Recurse -Force
```

### 3. 在目标项目中调用 `$traceablize`

让支持 Codex skill 的代理执行 `$traceablize`；它会运行随附安装器。也可以直接运行：

```powershell
python "<目标项目>\.codex\skills\traceablize\scripts\install_traceable_skills.py" `
  --project-root "<目标项目>"
```

默认会生成四个增强 skill、一个可选的 `requirement-packaging` skill 和追踪 Schema。`traceable-propose` 内部自动创建来源清单并拆分本地/外部/产品决策任务；`traceable-apply-change` 先清空本地可执行任务；`verify-with-report` 直接进行语义核验；不再安装固定格式校验器或 GUI。安装器可重复执行；每次都会重新读取目标项目当前的官方 skill，以继承上游更新。

## 日常使用

如果需求文档小且结构清晰，跳过分块，直接按下表执行。仅当文档很大、跨多个业务模块或存在结构/编号不一致时，先运行 `requirement-packaging`；审阅 `validation-report.md`、`unresolved-items.md` 后，按 `manifest.yaml` 的依赖顺序逐包把可执行工作包的 `input.md` 交给 `openspec-traceable-propose`，每包完成一次完整生命周期后再处理依赖包。

| OpenSpec 阶段 | 使用方式 |
|---|---|
| 创建 change、proposal、Spec、tasks | 使用 `openspec-traceable-propose`。 |
| 实现 tasks | 使用 `openspec-traceable-apply-change`。 |
| 同步 delta Spec | 使用 `openspec-traceable-sync-specs`。 |
| 验证覆盖、实现和归档就绪度 | 使用 `openspec-verify-with-report`。 |
| 归档 | 继续使用常规 `openspec-archive-change`。 |


## 仓库结构

```text
skills/traceablize/             # 入口 skill：中文主说明，英文辅助说明
openspec/schemas/               # 可追溯 Schema 与模板
examples/demo-project/          # 完全合成的演示项目
tests/                          # 安装器与分块功能的单元测试
```

## 隐私与发布边界

本仓库只包含合成示例。请勿将真实需求文档、来源标识、版本、映射、验证报告、环境数据、业务代码或打包 EXE 上传到公开仓库。校验报告会包含目标项目的来源标识和标题，分享前必须人工审查。分块产生的 `input.md`、`package.yaml`、`manifest.yaml`、`validation-report.md` 和 `unresolved-items.md` 同样会保留原文、文件名、行号、哈希、来源 ID 或修订，不能直接公开。

## 开发验证

```powershell
python -m unittest discover -s tests -v
```
