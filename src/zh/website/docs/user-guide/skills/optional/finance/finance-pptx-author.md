---
title: "Pptx Author — Build PowerPoint decks headless with python-pptx"
sidebar_label: "Pptx Author"
description: "Build PowerPoint decks headless with python-pptx"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pptx Author

使用 python-pptx 在无界面模式下创建 PowerPoint 演示文稿。可与 excel-author 配合使用，从而生成基于模型的演示文稿——文稿中的每个数字均可追溯至对应的 Excel 单元格。适用于商业计划书、内部备忘录及财报说明等场景。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/finance/pptx-author` 安装 |
| 路径 | `optional-skills/finance/pptx-author` |
| 版本 | `1.0.0` |
| 开发者 | Anthropic（由 Nous Research 改编） |
| 许可协议 | Apache-2.0 |
| 支持平台 | linux、macos、windows |
| 标签 | `powerpoint`、`pptx`、`python-pptx`、`presentation`、`finance` |
| 相关技能 | [`excel-author`](/docs/user-guide/skills/optional/finance/finance-excel-author)、[`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# pptx-author

使用 `python-pptx` 在磁盘上生成 .pptx 文件。适用于需要以文件形式交付演示文稿，而非启动实时 PowerPoint 会话的场景。

该技能改编自 Anthropic 在 [anthropics/financial-services](https://github.com/anthropics/financial-services) 中发布的 `pptx-author` 和 `pitch-deck` 技能。原版本中的 MCP / Office-JS 相关功能已被移除，因此仅支持无界面 Python 环境。

如需功能更全面的现成 PowerPoint 创建技能（包括幻灯片、演讲者备注、嵌入内容及媒体处理），请使用内置的 `powerpoint` 技能。本技能为轻量级设计，专为基于模型的演示文稿（如商业计划书、内部备忘录及财报说明）优化，此类文稿要求每个数据均有对应的源 Excel 文件作为依据。

## 输出规范

- 将文件写入 `./out/<名称>.pptx`。若目录不存在，则自动创建。
- 在最终回复中需返回该文件的相对路径。

## 设置指南

```bash
pip install "python-pptx>=0.6"
```

## 核心规范

### 每张幻灯片一个核心观点
标题应明确传达关键信息，正文则用于加以佐证。例如，“Q3营收”这样的标题较为单薄；而“Q3季度营收同比增长速度加快至14%”则更为有力。

### 所有数据均需追溯至模型来源
若幻灯片上的数据源自`./out/model.xlsx`文件，必须在脚注中注明对应的表格及单元格位置。

```
Revenue: $1,250M  (Source: model.xlsx, Inputs!C3)
```

切勿凭记忆或根据摘要来输入数字——请打开工作簿，读取指定的数据区域，尽可能通过编程方式将演示文稿中的数值与该区域绑定。

### 当模板已加载时使用公司专用模板
如果存在 `./templates/firm-template.pptx` 文件，请将其加载，这样演示文稿就能继承该公司的品牌颜色、字体以及整体布局。

```python
from pptx import Presentation
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()
```

### 图表：从模型生成的PNG格式图表优于原生PPTX图表
在图表精度至关重要的场景下（即要求模型的图表样式与演示文稿完全一致），建议从原始工作簿中将图表渲染为PNG格式后再嵌入其中。而原生`pptx.chart`格式的图表稳定性较差，且往往无法符合企业的规范要求。

```python
from pptx.util import Inches
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(2),
                         width=Inches(8))
```

### 无外部发送功能
该智能体仅负责生成文件，绝不会发送电子邮件、上传内容或发布信息。具体的内容传递工作由编排层来处理。

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Project Aurora — Strategic Alternatives"
slide.placeholders[1].text = "Preliminary Discussion Materials"

# Valuation summary slide (title-only layout)
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Valuation implies $38–$52 per share across methodologies"

# Add a table bound to model outputs
rows, cols = 5, 4
tbl_shape = slide.shapes.add_table(rows, cols,
                                   Inches(0.5), Inches(1.5),
                                   Inches(9), Inches(3))
tbl = tbl_shape.table
headers = ["Methodology", "Low ($)", "Mid ($)", "High ($)"]
for c, h in enumerate(headers):
    tbl.cell(0, c).text = h

# In a real deck, read these from the model workbook with openpyxl
data = [
    ("Trading comps",     "35", "41", "48"),
    ("Precedent M&A",     "39", "45", "52"),
    ("DCF (base)",        "36", "43", "51"),
    ("LBO (10% IRR)",     "33", "38", "44"),
]
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        tbl.cell(r, c).text = val

# Embed a chart rendered from the model
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Football field — current price $42"
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(1.8), width=Inches(8))

Path("./out").mkdir(exist_ok=True)
prs.save("./out/pitch-aurora.pptx")
```

## 将演示文稿编号与源工作簿绑定

从 Excel 模型中读取命名区域或特定单元格，从而确保演示文稿编号始终保持一致。

```python
from openpyxl import load_workbook

wb = load_workbook("./out/model.xlsx", data_only=True)
def nr(name):
    """Resolve a named range to its current computed value."""
    rng = wb.defined_names[name]
    sheet, coord = next(rng.destinations)
    return wb[sheet][coord].value

revenue_fy24 = nr("RevenueFY24")
implied_mid  = nr("ImpliedSharePriceBase")
```

接着使用这些值来构建牌组内容：
```python
slide.shapes.title.text = f"Implied share price of ${implied_mid:.2f} (base case)"
```

在读取工作簿之前，请务必先重新计算其数值——只有当已有程序计算过该工作表的内容时，openpyxl才能读取到这些计算后的数值。您可以先运行 `excel-author` 模块中的重新计算工具，或者通过真实的 Excel 会话来打开/保存文件。

## 演讲演示文稿的幻灯片结构清单

典型的银行行业演示文稿通常采用以下结构。虽非强制要求，但可作为搭建文稿框架的参考：

1. 封面/标题页
2. 免责声明
3. 目录页
4. 行业现状概述
5. 目标公司概况
6. 市场/行业背景
7. 估值概要（“足球场”图）——财务数据展示页
8. 对标公司的详细信息
9. 先前类似交易的详细资料
10. DCF估值分析概要
11. 杠杆收购/融资案例演示
12. 审批流程相关说明
13. 附录

## 何时不宜使用此功能

- 正在通过 Office MCP 进行实时 PowerPoint 演示的用户——请直接操作他们的实时文档。
- 非财务类的幻灯片内容（如季度全员会议材料、营销演示文稿）——建议使用更通用的 `powerpoint` 功能。
- 包含大量动画效果、过渡效果或演讲者备注的演示文稿——同样建议使用更通用的 `powerpoint` 功能。

## 出处说明

本格式参考了 Anthropic 的 Claude for Financial Services 插件套件，采用 Apache-2.0 许可协议。原始代码地址：https://github.com/anthropics/financial-services/tree/main/plugins/agent-plugins/pitch-agent/skills/pptx-author
