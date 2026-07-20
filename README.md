# OpenSpec 来源需求追踪工作流

[English README](README.en.md)

这是一个对 OpenSpec 的工作流扩展：它不改写官方 skill，而是通过 `traceablize` 从目标项目现有的官方 skill 动态派生可追溯版本，并为来源需求、Spec、验证证据建立双向追踪。

## OpenSpec 是什么？本项目解决什么问题？

[OpenSpec](https://openspec.pro/) 是一个面向人类与 AI 协作的轻量级 Spec-Driven Development（规格驱动开发）框架。它把一次变更先整理为可审阅的文档，再开始编码：`proposal` 说明为什么做与范围，`specs` 描述系统应当如何行为，`design` 记录技术决策，`tasks` 把工作拆成可执行步骤。完成实现后，再把确认后的规范沉淀为长期维护的项目知识。

这能避免“先让 AI 写代码，再回头猜需求”的问题；但标准流程通常不要求回答另一个审计问题：**某条 Spec 到底来自哪一条原始需求，需求版本变化后又影响了哪些实现和测试？**

本项目在不替换 OpenSpec 的前提下补上这条证据链：

```text
原始需求 ──双向映射── source-requirements.yaml ──双向映射── Spec Requirement
                                                              ↓
                                              tasks / 代码 / 测试 / 验证报告
```

## 每一步做什么、为什么做？

| 阶段 | OpenSpec 的作用 | 本项目增加的作用 | 为什么需要它 |
|---|---|---|---|
| Proposal | 明确变更原因、范围和影响面。 | 登记本次新增或修订的来源需求。 | 先确认“为什么做、哪些需求在范围内”，避免漏项。 |
| Specs | 用 Requirement 与 Scenario 定义应有行为。 | 为每条 Requirement 分配稳定 `REQ-*` ID，并写入来源 ID 与 Revision。 | 需求标题可以改，但稳定 ID 和来源版本可用于追溯影响。 |
| Design | 记录架构、权衡和冲突裁决。 | 保留需求冲突、排除和派生需求的理由。 | 防止工程假设被误写成用户需求。 |
| Tasks / Apply | 将规范拆成任务并实现。 | 区分代码、集成和真实环境证据。 | “任务勾选”或“单测通过”不等于生产能力已验证。 |
| Verify / Archive | 检查变更并沉淀规范。 | 检查 YAML 与 Spec 的双向链接、来源覆盖和证据矩阵。 | 发布或归档前可以发现断链、漏覆盖和未验证风险。 |

## 先理解完整流程

```text
初始化普通 OpenSpec 项目
        ↓
安装并调用 $traceablize
        ↓
生成 3 个追踪增强 skill、Schema 和校验工具
        ↓
按常规 OpenSpec 生命周期工作
（仅在 propose / sync / verify 阶段改用增强 skill）
```

## 产物与职责

执行 `$traceablize` 后，目标项目会获得：

| 产物 | 用途 |
|---|---|
| `openspec-traceable-propose` | 创建 change 时提取来源需求、生成稳定 `REQ-*` ID，并完成 YAML 与 Spec 双向对账。 |
| `openspec-traceable-sync-specs` | 将 delta Spec 同步到主 Spec 时保留来源 ID、Revision 和双向映射。 |
| `openspec-verify-with-report` | 核查任务、Requirement、Scenario、测试和环境证据，并生成持久化验证报告。 |
| `openspec/schemas/traceable-spec-driven/` | 含 `source-requirements.yaml` 工件的追踪 Schema；安装器会将其设为项目 Schema。 |
| `需求追踪验证工具/` | Python 命令行校验器和 Tkinter GUI 源码。 |

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

默认会生成三个增强 skill、追踪 Schema 和校验工具。安装器可重复执行；每次都会重新读取目标项目当前的官方 skill，以继承上游更新。

### 4. 安装校验器依赖

```powershell
python -m pip install -r "<目标项目>\需求追踪验证工具\requirements.txt"
```

## 日常使用

| OpenSpec 阶段 | 使用方式 |
|---|---|
| 创建 change、proposal、Spec、tasks | 使用 `openspec-traceable-propose`。 |
| 实现 tasks | 继续使用常规 `openspec-apply-change`。 |
| 同步 delta Spec | 使用 `openspec-traceable-sync-specs`。 |
| 验证覆盖、实现和归档就绪度 | 使用 `openspec-verify-with-report`。 |
| 归档 | 继续使用常规 `openspec-archive-change`。 |

来源追踪校验也可单独运行：

```powershell
python "<目标项目>\需求追踪验证工具\validate_source_traceability.py" `
  --project-root "<目标项目>" `
  --change <change名称>
```

GUI：

```powershell
python "<目标项目>\需求追踪验证工具\traceability_report_gui.py"
```

## 仓库结构

```text
skills/traceablize/             # 入口 skill：中文主说明，英文辅助说明
openspec/schemas/               # 可追溯 Schema 与模板
src/                            # 独立校验器和 GUI 源码
examples/demo-project/          # 完全合成的演示项目
tests/                          # 校验器与 GUI 的单元测试
```

## 隐私与发布边界

本仓库只包含合成示例。请勿将真实需求文档、来源标识、版本、映射、验证报告、环境数据、业务代码或打包 EXE 上传到公开仓库。校验报告会包含目标项目的来源标识和标题，分享前必须人工审查。

## 开发验证

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/validate_source_traceability.py --project-root examples/demo-project --change demo
```
