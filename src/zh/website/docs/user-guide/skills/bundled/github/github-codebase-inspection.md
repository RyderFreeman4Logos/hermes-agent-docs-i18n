---
title: "Codebase Inspection — Inspect codebases w/ pygount: LOC, languages, ratios"
sidebar_label: "Codebase Inspection"
description: "Inspect codebases w/ pygount: LOC, languages, ratios"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 代码库检测

使用 pygount 对代码库进行检测，可获取行数、语言分布及代码与注释比例等信息。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/github/codebase-inspection` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `LOC`、`代码分析`、`pygount`、`代码库`、`指标`、`仓库` |
| 相关技能 | [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 会以此作为操作指令。
:::

# 使用 pygount 进行代码库检测

通过 `pygount` 工具分析仓库的代码行数、语言构成、文件数量以及代码与注释的比例。

## 适用场景

- 用户需要查询代码行数（LOC）
- 用户希望了解仓库中的语言分布情况
- 用户想了解代码库的规模或构成
- 用户需要获取代码与注释的比例数据
- 其他与“该仓库有多大”相关的一般性问题

## 前提条件

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. 基本概览（最常用）

获取包含文件数量、代码行数以及注释行数的完整语言分析数据：

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**重要提示：** 请务必使用 `--folders-to-skip` 参数来排除依赖项目录和构建目录，否则 pygount 会遍历这些目录，从而导致处理时间过长甚至程序挂起。

## 2. 常见需排除的目录

请根据项目类型进行相应调整：

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. 按特定语言进行筛选

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. 详细的逐文件输出信息

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. 输出格式

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. 结果解读

摘要表格的列说明：
- **Language** — 检测到的编程语言
- **Files** — 该语言对应的文件数量
- **Code** — 实际代码行数（包含可执行代码与声明性代码）
- **Comment** — 注释或文档行数
- **%** — 占比，即各类别占全部内容的百分比

特殊的伪语言类型：
- `__empty__` — 空文件
- `__binary__` — 二进制文件（如图片、编译后的文件等）
- `__generated__` — 自动生成的文件（通过规则推断得出）
- `__duplicate__` — 内容完全相同的文件
- `__unknown__** — 无法识别的文件类型

## 常见问题与注意事项

1. **务必排除 .git、node_modules、venv 目录** — 若不使用 `--folders-to-skip` 参数，pygount 会扫描所有目录，对于依赖关系复杂的庞大项目，不仅耗时数分钟，还可能陷入无限循环。
2. **Markdown 文件显示的代码行数为 0** — pygount 会将所有 Markdown 内容视为注释而非代码，这是其预期行为。
3. **JSON 文件的代码行数偏低** — pygount 可能会对 JSON 文件的行数进行保守统计。如需获取准确的行数，建议直接使用 `wc -l` 命令。
4. **大型单仓库项目** — 对于规模极大的项目，建议使用 `--suffix` 参数指定要扫描的特定语言，而非全面扫描整个项目。
