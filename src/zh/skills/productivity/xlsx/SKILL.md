---
name: xlsx
description: "Create, read, edit Excel .xlsx spreadsheets and CSVs."
version: 1.0.0
author: Anthropic (adapted by Nous Research)
license: Proprietary. LICENSE.txt has complete terms
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Excel, XLSX, Spreadsheets, Office, Productivity]
    category: productivity
    related_skills: [docx, pdf, powerpoint]
---

# XLSX 技能

用于创建、读取和编辑 Excel 工作簿——包括公式处理、格式设置、图表生成、数据清洗以及格式转换。所有包含公式的输出内容在交付之前都必须重新计算且确保无错误。

## 适用场景

每当电子表格文件作为主要输入或输出时，均可使用此技能：打开、读取、编辑或修复现有的 .xlsx、.xlsm、.xltx、.csv 或 .tsv 文件；从零开始或基于其他数据创建新表格；在各种表格格式之间进行转换；将杂乱无章的表格数据整理为规范的电子表格。只要用户通过文件名或路径提及电子表格文件，即可触发该技能——哪怕只是随意提及。但若输出结果为 Word 文档（`docx` 技能）、HTML 报告、独立脚本或 Google Sheets API 集成内容，则不应触发此技能。对于金融领域的建模需求（如 DCF、LBO、三表分析），可选的 `excel-author` 技能会在该技能的基础上进一步施加更严格的标准。

## 先决条件

```bash
pip install openpyxl pandas "markitdown[xlsx]"
which soffice || sudo apt install -y libreoffice   # formula recalculation (scripts/recalc.py)
```

macOS系统：执行`brew install libreoffice`命令进行安装。

## 快速参考指南

| 任务 | 实现方式 |
|---|---|
| 使用公式/格式**创建**或**编辑**表格 | `openpyxl` — 请注意以下注意事项 |
| **批量导入/导出数据** | `pandas`（使用`read_excel`、`to_excel`函数） |
| **快速浏览**工作表内容 | 使用`markitdown file.xlsx`命令 — 每个工作表以`## SheetName`的形式标注；同时支持读取`.xlsm`格式文件。该工具不显示单元格坐标，因此不可用于规划编辑操作。（`read_file`函数也可自动提取.xlsx格式文件的内容） |
| **读取**模型内容（包括公式与数值） | 需通过两次`load_workbook`调用完成 — 请注意相关注意事项 |

> 下方列出的脚本路径均相对于该技能对应的目录。

## 所有输出结果的要求

- 除用户另有指定外，全文需使用**专业字体**（如Arial、Times New Roman）。
- **不得出现任何公式错误**。若`recalc.py`检测到错误，切勿提交结果。若怀疑存在先前存在的错误，请通过`data_only=True`参数加载*原始文件*并检查相关单元格，以此证明错误并非由你造成。你自己引入的错误与原有错误表现完全一致。
- **必须使用公式，严禁直接写入固定数值**。应编写`sheet['B10'] = '=SUM(B2:B9)'`这样的代码，而非直接填写Python计算出的结果。当输入数据发生变化时，工作表必须能够自动重新计算。
- **需严格遵循用户的明确要求**，包括精确的标签名称、列标题以及用户指定的公式格式。即便设计思路再巧妙，只要计算结果与用户要求不符，即视为失败。
- **所有假设条件及硬编码数值都需在读者可见的位置进行标注**，可在单元格注释中说明，或放在表格末尾的相邻单元格中。若有真实数据来源，请注明出处；若数值来自用户，需直接说明。
- **若为你创建供他人填写的工作簿**，需添加简短的说明，标明哪些单元格需要修改，并提供一行包含实际数值的示例，以展示期望的格式。切勿在需要修改的文件中自行添加此类示例行。
- **编辑现有文件时：必须完全遵循该文件的格式规范**。这些规范优先于本指南中的所有要求。首先找出文件中标记为输入区域的单元格——它们通常会通过独特的字体颜色、填充色或阴影效果来标识——仅在这些单元格中进行修改，切勿触碰任何现有的公式。

## 重新计算（只要文件包含公式，此步骤即为必做）

`openpyxl`会将公式以字符串形式存储，**不会缓存计算结果**。在重新计算之前，所有公式单元格对于那些依赖缓存值的工具——如`pandas`、`load_workbook(data_only=True)`以及大多数预览工具——而言都会显示为`None`值。

```bash
python scripts/recalc.py output.xlsx [timeout_seconds]   # default 30
```

LibreOffice 会逐一计算所有公式，文件会在原位被**重新写入**，最终生成 JSON 格式的结果，其中包含 `status`（值为 `success` 或 `errors_found`）、`total_formulas`、`total_errors`，以及一个 `error_summary` 字段——每种错误类型最多会列出 100 个出错的单元格位置（若出现 `locations_truncated` 字段，则表示有部分位置被省略，应以 `total_errors` 的数值为准，而非列表长度）。修正这些被标记出错的单元格后，再重新运行该工具。如果 JSON 中包含的是 `error` 键而非 `status` 键，说明没有任何公式被重新计算，此时程序的退出码才不为零——而当检测到错误时退出码为 0，因此绝不能将正常退出就视为工作簿已无问题。

**重新计算后显示绿色仅能证明公式可以被计算出来，并不代表其结果正确。** 由于范围设置错误或引用了错误的行，即便文件表面上看没有错误，计算出的数值也可能不正确。在构建完整表格之前，建议先编写 2–3 个公式，确认它们能返回预期的数值。

如果使用 openpyxl 保存包含外部链接的工作簿后再进行重新计算，这些链接将会丢失。此类公式通常表现为 `='[1]Returns Analysis'!$**数值格式：** 货币格式为 `$#,##0`，单位名称显示在标题中（如“Revenue ($mm)”）；零值以“-”表示，百分比也同样如此（格式为 `$#,##0;($#,##0);-`）；负数需用括号括起；百分比格式为 `0.0%`，实际以分数形式存储（例如 `0.15` 会显示为 `15.0%`，而直接输入 `15` 则会显示为 `1500.0%`）；估值倍数用 `0.0x` 表示；年份以文本形式呈现（如“2024”，绝不会是 `2,024` 这种格式）。

**结构要求：** 每一项假设都需置于单独的带标签单元格中，后续公式可通过单元格引用进行计算（例如 `=B5*(1+$B$
