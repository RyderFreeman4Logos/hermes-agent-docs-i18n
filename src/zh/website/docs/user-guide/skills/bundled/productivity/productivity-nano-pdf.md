---
title: "Nano Pdf — Edit text in existing PDFs via natural-language prompts"
sidebar_label: "Nano Pdf"
description: "Edit text in existing PDFs via natural-language prompts"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Nano Pdf

通过自然语言指令编辑现有 PDF 中的文本。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/nano-pdf` |
| 版本 | `1.0.0` |
| 创建者 | 社区用户 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `PDF`、`文档`、`编辑`、`NLP`、`生产力` |
| 相关技能 | [`pdf`](/docs/user-guide/skills/bundled/productivity/productivity-pdf)、[`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) |

## 参考：完整的 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当该技能处于激活状态时，智能体将依据此内容执行操作。
:::

# nano-pdf

利用自然语言指令编辑 PDF 文件。只需指定目标页面并描述需要进行的修改即可。如需处理 PDF 的结构化操作（合并、拆分、表单处理、水印添加、创建等），请使用 `pdf` 技能；如需从扫描件中提取文本，则可使用 `ocr-and-documents` 技能。

## 先决条件

```bash
# Install with uv (recommended — already available in Hermes)
uv pip install nano-pdf

# Or with pip
pip install nano-pdf
```

## 使用方法

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

## 示例

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"

# Update a date on a specific page
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

## 备注

- 页面编号可能因版本不同而采用0基或1基计数——如果编辑时选错了页面，可尝试调整±1后重新操作。
- 编辑完成后务必检查生成的PDF文件（可使用`read_file`命令查看文件大小，或直接打开文件进行确认）。
- 该工具在内部依赖大型语言模型运行，因此需要API密钥（具体配置信息请查阅`nano-pdf --help`）。
- 该工具非常适合文本修改；对于复杂的布局调整，则可能需要采用其他方法。
