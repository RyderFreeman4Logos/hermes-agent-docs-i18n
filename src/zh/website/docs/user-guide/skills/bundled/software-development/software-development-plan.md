---
title: "Plan — Plan mode: write an actionable markdown plan to"
sidebar_label: "Plan"
description: "Plan mode: write an actionable markdown plan to"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 规划

规划模式：在 `.hermes/plans/` 目录下编写一份可执行的 Markdown 规划文档，仅用于规划，不执行实际操作。任务需拆分得足够细，路径要明确，代码也要完整。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development/plan` |
| 版本 | `2.0.0` |
| 创建者 | Hermes Agent（写作技巧参考自 obra/superpowers） |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `planning`、`plan-mode`、`implementation`、`workflow`、`design`、`documentation` |
| 相关技能 | [`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development)、[`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development)、[`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当该技能处于激活状态时，Agent 就会看到这些内容作为操作指南。
:::

# 规划模式

当用户希望获得规划方案而非直接执行任务时，可使用此技能。

## 核心行为

在当前轮次中，您仅负责进行规划。
- 不要编写实际代码。
- 除规划用的 Markdown 文件外，不得修改项目文件。
- 不要运行会修改数据的终端命令、执行提交、推送操作或进行任何外部操作。
- 如有需要，可使用只读命令/工具来查看代码库或其他相关上下文。
- 您的交付物是保存在当前工作空间下的 `.hermes/plans/` 目录中的 Markdown 规划文档。

## 输出要求

需编写一份具体且可操作的 Markdown 规划文档。如适用，应包含以下内容：
- 目标
- 当前上下文/假设条件
- 建议的实现方案
- 逐步执行计划
- 可能需要修改的文件
- 测试/验证方式
- 风险、权衡因素及未解决的问题

如果任务与代码相关，还需注明具体的文件路径、可能的测试目标以及验证步骤。

## 保存位置

使用 `write_file` 函数将规划文档保存至以下路径：
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

该路径是相对于当前工作目录/后端工作空间而言的。Hermes 的文件工具具备后端感知功能，因此使用此相对路径可确保无论是在本地、Docker、SSH、Modal 还是 Daytona 后端环境中，规划文档都能与工作空间保持一致。

如果运行环境指定了特定目标路径，则直接使用该路径；
如果没有指定，则需在 `.hermes/plans/` 目录下自行创建一个包含合理时间戳的文件名。

## 交互方式

- 如果请求足够明确，可直接编写规划方案。
- 如果没有随 `/plan` 请求提供明确指示，则需从当前对话上下文中推断任务内容。
- 如果信息确实不够充分，应提出简短的澄清问题，而非自行猜测。
- 保存规划文档后，简要回复说明所规划的方案内容及保存路径。

---

# 如何编写出色的规划方案

本技能的其余部分将介绍如何撰写一份*优质*的实现规划方案——即上述 Markdown 文件中的内容。

## 概述

在编写实现规划方案时，应假设执行者对代码库一无所知，且审美标准参差不齐。因此需详细记录所有必要信息：需要修改哪些文件、完整的代码内容、测试命令、需参考的文档以及验证方法。同时要将任务拆分得足够细，遵循 DRY、YAGNI 原则，采用 TDD 开发模式，并频繁提交代码。

假设执行者虽是技术娴熟的开发者，但对相关工具集或问题领域知之甚少，也不太熟悉优秀的测试设计方法。

**核心原则：** 一份好的规划方案能让实现过程一目了然。如果需要猜测，说明规划方案还不够完善。

## 何时需要完整的实现规划方案

**以下情况务必提前编写规划方案：**
- 实现多步骤功能
- 拆分复杂的业务需求
- 通过 subagent-driven-development 将任务分配给子 Agent 处理

**以下情况不可省略规划方案：**
- 功能看似简单（但假设条件可能导致错误）
- 计划由自己亲自实现（未来的自己需要参考指导）
- 独自工作（文档记录非常重要）

## 任务拆分的粒度标准

**每个任务的时间应控制在 2-5 分钟的专注工作时间之内。**

每一步都应对应一个具体动作：
- “编写失败的测试用例” —— 一步
- “运行测试以确保其确实失败” —— 一步
- “编写最简代码使测试通过” —— 一步
- “运行测试并确认全部通过” —— 一步
- “提交代码” —— 一步

**任务过大则不符合要求：**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**合适规模：**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## 计划文档结构

### 标题（必填）

每个计划都必须以以下内容开头：

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### 任务结构

每个任务均遵循以下格式：

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 开发流程

### 第一步：理解需求

仔细阅读并掌握以下内容：
- 功能需求
- 设计文档或用户需求描述
- 验收标准
- 各项限制条件

### 第二步：探索代码库

利用 Hermes 工具来深入了解项目结构：

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### 第3步：设计方案

需要确定以下内容：
- 架构模式
- 文件组织结构
- 所需依赖项
- 测试策略

### 第4步：编写任务

按顺序创建任务：
1. 基础设施搭建
2. 核心功能实现（每个功能均采用TDD测试驱动开发）
3. 边界情况处理
4. 系统集成
5. 代码清理与文档编写

### 第5步：补充完整细节

针对每项任务，需包含以下内容：
- **精确的文件路径**（而非笼统地写“配置文件”，而应明确为 `src/config/settings.py`）
- **完整的代码示例**（而非仅说明“添加验证逻辑”，而要提供实际代码）
- 带有预期输出结果的**精确命令**
- 能证明该任务已正常运行的**验证步骤**

### 第6步：审核计划

需检查以下要点：
- [ ] 任务顺序合理且逻辑连贯
- [ ] 每项任务的耗时控制在2-5分钟范围内
- [ ] 文件路径准确无误
- [ ] 代码示例完整，可直接复制粘贴使用
- [ ] 命令及预期输出均准确无误
- [ ] 无遗漏的背景信息
- [ ] 已遵循DRY、YAGNI及TDD开发原则

## 开发原则

### DRY原则（不要重复自己）

**错误做法：** 在多个地方重复编写相同的验证代码  
**正确做法：** 将验证逻辑提取为独立函数，然后在各处复用

### YAGNI原则（你不需要它）

**错误做法：** 为未来可能的需求预留“灵活性”接口  
**正确做法：** 仅实现当前确实需要的功能

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### 测试驱动开发（TDD）

所有生成代码的任务都应遵循完整的测试驱动开发流程：
1. 编写失败的测试用例
2. 运行测试以确认确实失败
3. 编写最简的代码实现
4. 运行测试以确认测试通过

详情请参阅“test-driven-development”技能文档。

### 频繁提交代码

完成每个任务后都应立即提交代码：
```bash
git add [files]
git commit -m "type: description"
```

## 常见错误

### 任务描述模糊

**错误示例：** “添加身份验证功能”
**正确示例：** “创建包含 email 和 password_hash 字段的 User 模型”

### 代码不完整

**错误示例：** “第一步：添加验证函数”
**正确示例：** “第一步：添加验证函数”，随后应给出完整的函数代码

### 缺少验证步骤

**错误示例：** “第三步：测试功能是否正常”
**正确示例：** “第三步：运行 `pytest tests/test_auth.py -v`，预期结果为：3 个测试通过”

### 未指定文件路径

**错误示例：** “创建模型文件”
**正确示例：** “创建文件：`src/models/user.py`”

## 执行交接流程

保存计划后，需明确说明执行方案：

**“计划已完整保存。现在将采用子代理驱动开发模式进行执行——我会为每个任务分配一个全新的子代理，并依次进行两阶段审查（先检查是否符合规范，再评估代码质量）。是否继续？”**

在执行过程中，请使用 `subagent-driven-development` 技能：
- 为每个任务分配全新的 `delegate_task` 并提供完整上下文
- 每完成一个任务后进行规范符合性审查
- 规范审查通过后再进行代码质量审查
- 仅当两阶段审查均通过后才继续执行

## 记住

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

完善的规划能让实施过程变得清晰明了。
