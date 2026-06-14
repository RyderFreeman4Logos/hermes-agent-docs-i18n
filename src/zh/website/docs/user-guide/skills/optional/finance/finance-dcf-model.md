---
title: "Dcf Model"
sidebar_label: "Dcf Model"
description: "Build institutional-quality DCF valuation models in Excel — revenue projections, FCF build, WACC, terminal value, Bear/Base/Bull scenarios, 5x5 sensitivity t..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# DCF 模型

在 Excel 中构建具备机构级专业水准的 DCF 估值模型——包括收入预测、自由现金流测算、加权平均资本成本计算、终值分析、悲观/基准/乐观情景分析，以及 5×5 敏感性分析表。该技能与 excel-author 技能相配套，可用于股票内在价值分析。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/finance/dcf-model` 命令安装 |
| 路径 | `optional-skills/finance/dcf-model` |
| 版本 | `1.0.0` |
| 开发者 | Anthropic（由 Nous Research 改编） |
| 许可协议 | Apache-2.0 |
| 支持平台 | linux、macos、windows |
| 标签 | `finance`、`valuation`、`dcf`、`excel`、`openpyxl`、`modeling`、`investment-banking` |
| 相关技能 | [`excel-author`](/docs/user-guide/skills/optional/finance/finance-excel-author)、[`pptx-author`](/docs/user-guide/skills/optional/finance/finance-pptx-author)、[`comps-analysis`](/docs/user-guide/skills/optional/finance/finance-comps-analysis)、[`lbo-model`](/docs/user-guide/skills/optional/finance/finance-lbo-model)、[`3-statement-model`](/docs/user-guide/skills/optional/finance/finance-3-statement-model) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当该技能处于激活状态时，智能体看到的指令即为内容。
:::

## 环境要求

该技能依赖 **无界面模式的 openpyxl**——即需要在磁盘上生成 .xlsx 格式的文件。请遵循 `excel-author` 技能的相关规范来设置单元格颜色、公式、命名范围以及敏感性分析表。在交付结果之前，请先运行以下命令重新计算：`python /path/to/excel-author/scripts/recalc.py ./out/model.xlsx`。

# DCF 模型构建器

## 概述

该技能遵循投资银行行业标准，为股票估值创建具备机构级专业水准的 DCF 模型。每次分析都会生成一份结构完整的 Excel 模型（在 DCF 工作表的底部还会包含敏感性分析内容）。

## 工具

- 默认会使用用户提供的所有信息以及 MCP 服务器可获取的数据源。

## 重要约束——请先仔细阅读

以下约束适用于所有 DCF 模型构建过程。在开始工作前请务必查看：

**必须使用公式而非硬编码值（绝对不可违反）：**
- 所有的预测值、利润率、折现率、现值以及敏感性分析单元格都必须是 Excel 中的动态公式——绝不能是先用 Python 计算出数值后再以数字形式写入的
- 使用 openpyxl 时：`ws["D20"] = "=D19*(1+$B$
```
Historical Metrics (LTM):
Revenue: $X million
Revenue growth: X% CAGR
Gross margin: X%
EBIT margin: X%
D&A % of revenue: X%
CapEx % of revenue: X%
FCF margin: X%
```

### 第3步：制定收入预测

**预测方法：**
1. 以最新的实际收入数据（最近一个完整会计年度或当前财年的数据）作为起点；
2. 为每个预测年份应用相应的增长率；
3. 同时展示金额数值与计算得出的增长率。

**增长率设定原则：**
- 第1-2年：由于短期业务前景较为明确，因此设定较高的增长率；
- 第3-4年：增长率逐步放缓，趋向行业平均水平；
- 第5年及以后：接近最终稳定增长率。

**公式结构：**
- 第N年的收入 = 第N-1年的收入 × (1 + 增长率)
- 第N年的增长率 = 第N年的收入 / 第N-1年的收入 - 1

**三情景预测法：**
```
Bear Case: Conservative growth (e.g., 8-12%)
Base Case: Most likely scenario (e.g., 12-16%)
Bull Case: Optimistic growth (e.g., 16-20%)
```

### 第4步：运营成本建模

**固定成本/变动成本分析：**

运营成本模型应体现真实的经营杠杆效应：
- **销售与营销**：根据业务模式不同，通常占收入的15%-40%
- **研发**：对于科技企业而言，通常占收入的10%-30%
- **一般管理费用**：通常占收入的8%-15%，且会随着公司规模扩大而表现出杠杆效应

**核心原则：**
- 所有百分比均以收入为基数，而非毛利润
- 需体现经营杠杆效应：随着收入增长，该百分比应有所下降
- 需为销售与营销、研发以及一般管理费用分别设置独立科目
- 毛利润 = 毛利润额 - 总运营成本

**利润率提升框架：**
```
Current State → Target State (Year 5)
Gross Margin: X% → Y% (justify based on scale, efficiency)
EBIT Margin: X% → Y% (result of revenue growth + opex leverage)
```

### 第5步：自由现金流计算

**按正确顺序构建自由现金流：**

```
EBIT
(-) Taxes (EBIT × Tax Rate)
= NOPAT (Net Operating Profit After Tax)
(+) D&A (non-cash expense, % of revenue)
(-) CapEx (% of revenue, typically 4-8%)
(-) Δ NWC (change in working capital)
= Unlevered Free Cash Flow
```

**营运资金模型：**
- 按收入变动的百分比（收入增量）进行计算
- 典型范围：收入变动的 -2% 至 +2%
- 负数值表示现金流入（营运资金释放）
- 正数值表示现金流出（营运资金占用）

**维护性资本支出与增长型资本支出：**
- 维护性资本支出：用于维持现有运营（约占收入的 2-3%）
- 增长型资本支出：用于业务扩张（约占额外收入的 2-5%）
- 总资本支出应与公司的发展战略保持一致

### 第6步：资本成本（WACC）研究

**股权成本的CAPM模型法：**

```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium

Where:
- Risk-Free Rate = Current 10-Year Treasury Yield
- Beta = 5-year monthly stock beta vs market index
- Equity Risk Premium = 5.0-6.0% (market standard)
```

**债务成本计算：**

```
After-Tax Cost of Debt = Pre-Tax Cost of Debt × (1 - Tax Rate)

Determine Pre-Tax Cost of Debt from:
- Credit rating (if available)
- Current yield on company bonds
- Interest expense / Total Debt from financials
```

**资本结构权重：**

```
Market Value Equity = Current Stock Price × Shares Outstanding
Net Debt = Total Debt - Cash & Equivalents
Enterprise Value = Market Cap + Net Debt

Equity Weight = Market Cap / Enterprise Value
Debt Weight = Net Debt / Enterprise Value

WACC = (Cost of Equity × Equity Weight) + (After-Tax Cost of Debt × Debt Weight)
```

**特殊情况：**
- **净现金头寸**：若现金 > 债务，则净债务为负值
  - 债务权重也可能为负数
  - WACC的计算值会随之调整
- **无债务**：WACC = 股权成本

**典型的WACC范围：**
- 大型稳定企业：7-9%
- 成长型企业：9-12%
- 高增长/高风险企业：12-15%

### 第7步：折现率应用（5-10年预测）

**年中假设规则：**
- 假设现金流发生在每年年中
- 折现期分别为：0.5、1.5、2.5、3.5、4.5等
- 折现因子 = 1 / (1 + WACC)^周期数

**现值计算方法：**
```
For each projection year:
PV of FCF = Unlevered FCF × Discount Factor

Example (Year 1):
FCF = $1,000
WACC = 10%
Period = 0.5
Discount Factor = 1 / (1.10)^0.5 = 0.9535
PV = $1,000 × 0.9535 = $954
```

**预测期选择：**
- **5年**：适用于大多数分析场景的默认选项
- **7-10年**：适合具有较长发展前景的高增长企业
- **3年**：适用于成熟且稳定的企业

### 第8步：终值计算

**永续增长法（推荐方法）：**

```
Terminal FCF = Final Year FCF × (1 + Terminal Growth Rate)
Terminal Value = Terminal FCF / (WACC - Terminal Growth Rate)

Critical Constraint: Terminal Growth < WACC (otherwise infinite value)
```

**终端增长率选择：**
- 审慎型：2.0-2.5%（GDP增长率）
- 中等型：2.5-3.5%
- 积极型：3.5-5.0%（仅适用于市场领导者）

**上限限制**：不得超过无风险利率或长期GDP增长率

**退出倍数计算方法（备用方案）：**
```
Terminal Value = Final Year EBITDA × Exit Multiple

Where Exit Multiple comes from:
- Industry comparable trading multiples
- Precedent transaction multiples
- Typical range: 8-15x EBITDA
```

**终值现值：**
```
PV of Terminal Value = Terminal Value / (1 + WACC)^Final Period

Where Final Period accounts for timing:
5-year model with mid-year convention: Period = 4.5
```

**终值合理性检查：**
- 其数值应占企业价值的50%至70%
- 若超过75%，则模型可能过度依赖终值假设
- 若低于40%，则需检查终值假设是否过于保守

### 第9步：从企业价值转换为股权价值

**估值汇总结构：**

```
(+) Sum of PV of Projected FCFs = $X million
(+) PV of Terminal Value = $Y million
= Enterprise Value = $Z million

(-) Net Debt [or + Net Cash if negative] = $A million
= Equity Value = $B million

÷ Diluted Shares Outstanding = C million shares
= Implied Price per Share = $XX.XX

Current Stock Price = $YY.YY
Implied Return = (Implied Price / Current Price) - 1 = XX%
```

**关键调整项：**
- **净债务 = 总债务 - 现金及现金等价物**
  - 若数值为正：从企业价值中扣除（从而降低股权价值）
  - 若为负值（即净现金）：加到企业价值中（从而提升股权价值）
- **采用稀释后股数**：包括期权、受限股票单位以及可转换证券
- **其他调整项**（如适用）：
  - 少数股东权益
  - 养老金负债
  - 经营租赁义务

**估值输出格式：**
```csv
Valuation Component,Amount ($M)
PV Explicit FCFs,X.X
PV Terminal Value,Y.Y
Enterprise Value,Z.Z
(-) Net Debt,A.A
Equity Value,B.B
,,
Shares Outstanding (M),C.C
Implied Price per Share,$XX.XX
Current Share Price,$YY.YY
Implied Upside/(Downside),+XX%
```

### 第10步：敏感性分析

在DCF模型表的底部构建**三个敏感性表格**，用以展示在不同假设条件下的估值变化情况：

1. **WACC与终端增长率**——反映企业价值对折现率及永久增长率的敏感度；
2. **营收增长率与EBIT利润率**——体现营业收入增长及运营杠杆的影响；
3. **贝塔值与无风险利率**——展示对企业价值中权益成本各构成要素的敏感度。

**实现方式**：这些表格为简单的二维网格（并非Excel中的“数据表”功能），每个单元格均包含相应公式。每个单元格都必须针对该特定的假设组合重新进行完整的DCF计算。关于如何使用openpyxl编程填充全部75个单元格的详细要求，请参阅“关键约束”部分。

&lt;correct_patterns>

本节列出了构建DCF模型时需遵循的所有正确规范。

### 场景模块选择规范——请采用此方法

**每个场景的假设条件均应分置在不同的模块中：**

**关键结构要求——每个章节标题下方需有三行内容：**

```csv
BEAR CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),12%,10%,9%,8%,7%
EBIT Margin (%),45%,44%,43%,42%,41%

BASE CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),16%,14%,12%,10%,9%
EBIT Margin (%),48%,49%,50%,51%,52%

BULL CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),20%,18%,15%,13%,11%
EBIT Margin (%),50%,51%,52%,53%,54%
```

**每个场景区块都必须包含一行列标题行**，该行应紧接在板块标题下方，用于标注预测年份（如FY2025E、FY2026E等）。若没有这一行，用户将无法判断某个假设值对应的是哪一年。

**如何引用假设值——创建汇总列：**
1. 情景选择单元格（例如B6）中输入1代表看跌市场，2代表基准情况，3代表看涨市场；
2. 使用INDEX或OFFSET公式创建汇总列，从而从相应的场景区块中提取数据；
3. 预测公式引用该汇总列（使用简洁的单元格引用形式）；
4. 每个场景区块都会包含涵盖所有预测年份的完整DCF假设值。

**推荐的汇总列格式（使用INDEX函数）：**
`=INDEX(B10:D10, 1, $B$
```csv
Item,Formula,Reference
D&A,=E29*$E$21,$E$21 = consolidation column for D&A %
CapEx,=E29*$E$22,$E$22 = consolidation column for CapEx %
Δ NWC,=(E29-D29)*$E$23,$E$23 = consolidation column for NWC %
Unlevered FCF,=E57+E58-E60-E62,E57=NOPAT E58=D&A E60=CapEx E62=Δ NWC
```

**每个合并列单元格都包含一个 INDEX 公式**，该公式会根据案例选择器从相应的场景块中提取数据。这样一来，预测公式既简洁清晰，又便于审核。

在编写公式之前，请先确认场景块所在行位置，并设置好合并列。

### 正确的单元格注释格式

**所有硬编码值都必须遵循以下格式：**

“来源：[系统/文档]，[日期]，[参考资料]，[如有网址则填写]”

**示例：**
```csv
Item,Source Comment
Stock price,Source: Market data script 2025-10-12 Close price
Shares outstanding,Source: 10-K FY2024 Page 45 Note 12
Historical revenue,Source: 10-K FY2024 Page 32 Consolidated Statements
Beta,Source: Market data script 2025-10-12 5-year monthly beta
Consensus estimates,Source: Management guidance Q3 2024 earnings call
```

### 正确的假设表结构

**重要提示：每个场景模块都必须包含三个结构要素：**

1. **章节标题行**（合并单元格）：例如“最坏情况假设”
2. **显示年份的列标题行**——此项为必填项，切勿省略
3. **包含假设数值的数据行**

**结构如下：**
```csv
BEAR CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,

BASE CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,

BULL CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,
```

**若未设置用于显示预测年份（如FY2025E、FY2026E等）的列标题行，用户将无法判断哪个假设值对应哪一年。此行是必须存在的。**

**接着创建一个汇总列**（通常位于右侧的下一列），该列通过INDEX函数根据案例选择器从选定的情景块中提取数据。您的预测公式将会引用这一汇总列。

### 正确的行规划流程

**1. 首先编写所有的标题和标签：**
```csv
Row,Content
1,[Company Name] DCF Model
2,Ticker | Date | Year End
4,Case Selector
7,KEY ASSUMPTIONS
26,Assumption headers
27-31,Growth assumptions
...,...
```

**2. 编写所有的章节分隔符及空行**

**3. 接着，利用已锁定的行位置来编写公式**

**4. 公式创建后立即进行测试**

**可以将其类比为建筑工程：**
- 正确做法：先浇筑基础，再建造墙壁（结构稳固）
- 错误做法：先建造墙壁，再浇筑基础（墙壁会倒塌）

**Excel版本中的对应逻辑：**
- 正确做法：先添加表头，再编写公式（公式更稳定）
- 错误做法：先编写公式，再添加表头（公式会出错）

### 正确的敏感性表格实现方式

**重要提示**：这些并非Excel中的“数据表”功能。它们只是简单的网格结构，您需要使用openpyxl在这些网格中编写常规公式。虽然这意味着总共需要约75个公式（3个表格，每个表格25个单元格），但这种方式简单直接，且是必需的。

**通过编程方式填充公式：**

每个敏感性表格都必须完整地填入公式，以便针对各种假设组合重新计算相应的预期股价。**请勿使用Excel的“数据表”功能**（该功能需要人工操作，无法通过openpyxl实现自动化）。

**实现方法——具体示例：**

**表格结构——5×5网格（奇数尺寸，基准情况位于中心）：**

如果模型的基准WACC为9.0%，基准终端增长率为3.0%，则应围绕这两个数值对称地构建坐标轴：

```csv
WACC vs Terminal Growth,  2.0%,  2.5%,  3.0%,  3.5%,  4.0%
              8.0%,       [fml], [fml], [fml], [fml], [fml]
              8.5%,       [fml], [fml], [fml], [fml], [fml]
              9.0%,       [fml], [fml], [★  ], [fml], [fml]   ← middle row = base WACC
              9.5%,       [fml], [fml], [fml], [fml], [fml]
             10.0%,       [fml], [fml], [fml], [fml], [fml]
                                   ↑
                          middle col = base terminal g
```

**★ = 中间单元格。**该单元格的公式计算结果必须与估值汇总表中显示的模型实际隐含股价完全一致。请为该单元格应用浅蓝色填充色（`#BDD7EE`）并设置加粗字体，以便在视觉上突出显示基准情况。

**坐标轴数值规则：** `axis_values = [base - 2*step, base - step, base, base + step, base + 2*step]`——数值以基准值为中心对称分布，奇数个数值可确保存在中间单元格。

**公式示例——B88单元格（WACC=8.0%，终端增长率=2.0%）：**

B88单元格中的公式应使用以下参数重新计算隐含股价：
- 来自行标题的加权平均资本成本：`$
```python
# Pseudocode for populating sensitivity table
for row_idx, wacc_value in enumerate(wacc_range):
    for col_idx, term_growth_value in enumerate(term_growth_range):
        # Build formula that uses wacc_value and term_growth_value
        formula = f"=<DCF recalc using {wacc_value} and {term_growth_value}>"
        ws.cell(row=start_row+row_idx, column=start_col+col_idx).value = formula
```

**在打开模型时，敏感性表格应立即生效，无需用户进行任何手动操作。**

&lt;/correct_patterns>

&lt;common_mistakes>

本节列出了在构建DCF模型时需避免的所有错误做法。

### 错误做法：使用简化的敏感性表格近似值或占位文本

**切勿使用线性近似方法：**

```
// WRONG - Linear approximation
B97: =B88*(1+(0.096-0.116))    // Assumes linear relationship

// WRONG - Division shortcut
B105: =B88/(1+(E48-0.07))      // Doesn't recalculate full DCF
```

**请勿留下占位符文本：**
```
// WRONG - Placeholder note
"Note: Use Excel Data Table feature (Data → What-If Analysis → Data Table) to populate sensitivity tables."

// WRONG - Empty cells
[leaving cells blank because "this is complex"]
```

**请勿混淆相关术语：**
- ❌ “敏感性分析表需要使用 Excel 的数据表功能”（错误——那是一种我们无法使用的特定 Excel 工具）
- ✅ “敏感性分析表其实就是包含各单元格公式的简单表格”（正确——这正是我们要构建的内容）

**为何这些简化做法是错误的：**
- 线性近似公式实际上并不会重新计算现金流折现值，而只是进行简单的数学调整
- 各变量之间的关系并非线性，因此计算结果会不准确
- 占位文本需要用户手动补充
- 模型在交付时无法直接使用
- 输出结果既不专业，也不适合呈现给客户
- 空单元格意味着交付物不完整

**常被用来作为拒绝理由的说法：**
“编写75个以上的公式太复杂了，我会在文档中留备注，让用户手动补充。”

**实际情况是：**只要使用 Python 的 openpyxl 库并配合循环结构，编写75个公式其实非常简单。每个公式的格式都一致，只需替换行号和列号即可。这是交付物中不可或缺的一部分。

**正确做法应是：**在每个敏感性分析单元格中输入公式，以便针对特定的假设组合重新计算完整的现金流折现值。

### 错误示例：缺少单元格注释

**请避免以下行为：**
- 创建所有硬编码输入值却不加注释
- 以为“稍后再添加”
- 写上“TODO：补充来源信息”
- 对蓝色标记的输入值不作任何说明

**为何这样做是错误的：**
- 无法追溯数据的来源
- 不符合相关技能要求
- 无法通过审计
- 后期修复会浪费大量时间

**正确做法应是：**在为每个硬编码值创建单元格时，立即添加注释。

### 错误示例：公式中的行引用有误

**症状表现：**
自由现金流部分引用的假设行号错误：
`D&A: =E29*$E$
```csv
Assumption,Bear,Base,Bull
Revenue Growth FY1,10%,13%,16%
Revenue Growth FY2,9%,12%,15%
```
这种垂直布局使得难以查看每个情景下多年间的变化趋势。

**问题所在：**
- 难以了解每个情景中各假设值随时间的变化情况
- 很难在整个预测期内对比不同情景的假设条件
- 审查情景逻辑时不够直观

**改进方案：**
- 为每种情景（熊市、基准、牛市）创建独立的区域
- 在每个区域内，按预测年份横向展示各项假设值
- 这样就能将每种情景的假设条件作为一个整体更便捷地查看

### 错误示例：无边框

**切勿提交没有边框的模型：**
- 无法区分不同板块
- 所有单元格融为一体
- 难以阅读，且显得不专业

**问题所在：**
- 不适合呈交给客户
- 难以导航
- 看起来很业余

**改进方案：** 为所有主要板块添加边框

### 错误示例：字体颜色不当或无区分

**切勿这样做：**
- 所有文本均为黑色
- 仅使用填充色而不用不同字体颜色
- 混淆蓝色单元格与黑色单元格的用途

**问题所在：**
- 无法区分输入数据与公式结果
- 审计工作将无法进行
- 违反xlsx技能的要求

**改进方案：** 所有硬编码输入用蓝色文字显示，所有公式用黑色文字显示，工作表链接则用绿色文字显示

### 错误示例：运营费用基于毛利润计算

**切勿这样做：**
`S&M: =E33*0.15    // E33 = 毛利润（错误）`

**问题所在：**
- 运营费用应随收入变化，而非毛利润
- 会导致利润率变化不切实际
- 不符合企业的实际运营方式

**改进方案：**
`S&M: =E29*0.15    // E29 = 收入（正确）`

### 五大常见错误总结

1. **公式行引用错误** → 在编写公式之前先确定所有行号
2. **缺少单元格注释** → 应在创建单元格时立即添加注释，而非到最后
3. **敏感性分析表过于简化** → 所有单元格都应填写完整的DCF重算公式，而非近似值
4. **情景区域引用错误** → 确保IF公式引用的是正确的熊市/基准/牛市区域
5. **无边框** → 为模型添加专业的板块边框，以便呈现给客户

此外，还需注意以下错误：

### WACC计算错误
- 在资本结构中混用账面价值与市场价值
- 错误地使用股权贝塔值而非资产或无杠杆贝塔值
- 对债务成本应用错误的税率
- 无风险利率使用不当（必须使用当前10年期国债利率）
- 未对净债务与净现金状况进行适当调整

### 增长假设缺陷
- 终值增长率高于WACC（会导致估值无限膨胀）
- 预测增长率与历史表现不一致
- 未考虑行业增长限制
- 收入增长与单位经济模型不匹配
- 利润率提升缺乏运营层面的合理解释

### 终值计算错误
- 使用了错误的增长方法（永续增长法与退出倍数法混淆）
- 终值占企业价值的比例超过80%（表明过度依赖该假设）
- 终值利润率与稳态假设不一致
- 终值的折现期设置错误

### 现金流预测错误
- 运营费用基于毛利润而非收入计算
- 折旧与摊销费用及资本支出比例与业务模型不匹配
- 流动资金变动计算有误
- 各年度税率不一致
- NOPAT计算出错

**这些错误最为常见。在开始构建任何DCF模型之前，请务必重新阅读本部分内容。**

&lt;/common_mistakes>

## Excel文件创建

**该技能所有电子表格操作均依赖`xlsx`技能。** xlsx技能可提供：
- 标准化的公式构建规则
- 数字格式设置规范
- 通过`recalc.py`脚本实现自动公式重算
- 全面的错误检测与验证功能

由该技能生成的所有Excel文件都必须符合xlsx技能的要求，包括零公式错误以及正确的重算功能。

## 质量评估标准

每个DCF模型都需做到以下几点：
1. 基于历史表现，制定**现实合理的收入与利润率假设**
2. 采用正确的CAPM方法，计算**恰当的资本成本**
3. 进行**全面的敏感性分析**，明确估值范围
4. 提供**清晰的终值计算过程**及相应依据
5. 拥有便于进行情景分析的**专业模型结构**
6. 对所有关键假设提供**详尽的文档说明**

## 输入要求

### 最低必要输入项
1. **公司标识符**：股票代码或公司名称
2. **增长假设**：预测期内的收入增长率（或“采用市场共识值”）
3. **可选参数**：
   - 预测期长度（默认：5年）
   - 不同情景设定（熊市/基准/牛市下的增长与利润率假设）
   - 终值增长率（默认：2.5%-3.0%）
   - 若不使用CAPM方法，则需输入特定的WACC相关数值

## Excel模型结构

### 工作表架构

需创建**两个工作表**：

1. **DCF** – 主要估值模型，敏感性分析放在页面底部
2. **WACC** – 资本成本计算相关内容

**重要提示**：敏感性分析表必须放在DCF工作表的底部（而非单独的工作表中），这样才能将所有估值结果集中展示。

### 公式重算（强制要求）

在创建或修改Excel模型后，必须使用`excel-author`技能中的`recalc.py`脚本来**重新计算所有公式**：

```bash
python recalc.py [path_to_excel_file] [timeout_seconds]
```

示例：
```bash
python recalc.py AAPL_DCF_Model_2025-10-12.xlsx 30
```

该脚本将执行以下操作：
- 使用 LibreOffice 重新计算所有工作表中的所有公式；
- 扫描所有单元格，检测 Excel 错误（如 #REF!、#DIV/0!、#VALUE!、#NAME?、#NULL!、#NUM!、#N/A）；
- 返回包含错误位置及出现次数的详细 JSON 数据。

**预期输出格式：**
```json
{
  "status": "success",           // or "errors_found"
  "total_errors": 0,              // Total error count
  "total_formulas": 42,           // Number of formulas in file
  "error_summary": {}             // Only present if errors found
}
```

**如果检测到错误**，输出结果中将包含相关详细信息：
```json
{
  "status": "errors_found",
  "total_errors": 2,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["DCF!B25", "DCF!C25"]
    }
  }
}
```

在交付模型之前，需**修正所有错误**并反复运行 recalc.py，直至状态显示为“success”。

### 格式标准

**重要提示**：请遵循 xlsx 技能规范中的公式构建规则及数字格式要求。DCF 技能则规定了特定的视觉呈现标准。

**双层颜色方案**：

**第一层：字体颜色（遵循 xlsx 技能的强制要求）**
- **蓝色文字（RGB: 0,0,255）**：所有硬编码输入数据（股票价格、股数、历史数据、假设条件）
- **黑色文字（RGB: 0,0,0）**：所有公式及计算结果
- **绿色文字（RGB: 0,128,0）**：指向其他工作表的链接（如 WACC 工作表引用）

**第二层：填充颜色——专业蓝灰色调（除非用户另有指定，否则默认使用此方案）**
- **保持极简**——仅使用蓝色和灰色作为填充色。严禁使用绿色、黄色、橙色或其他多种强调色。色彩过多的模型看起来会显得很业余。
- **默认填充色方案：**
  - **章节标题**：深蓝色背景（RGB: 31,78,121 / `#1F4E79`），搭配白色粗体文字
  - **子标题/列标题**：浅蓝色背景（RGB: 217,225,242 / `#D9E1F2`），搭配黑色粗体文字
  - **输入单元格**：浅灰色背景（RGB: 242,242,242 / `#F2F2F2`），搭配蓝色字体；若追求极致极简，也可仅使用白色背景搭配蓝色字体
  - **计算结果单元格**：白色背景，搭配黑色字体
  - **输出/汇总行**（如每股价值、企业价值等）：中等蓝色背景（RGB: 189,215,238 / `#BDD7EE`），搭配黑色粗体文字
- **仅此而已——3种蓝色 + 1种灰色 + 白色**。切勿擅自添加更多颜色。
- 用户提供的模板或明确的颜色偏好将始终优先于这些默认设置。

**各层颜色的作用逻辑：**
- 输入单元格：蓝色字体 + 浅灰色填充 = “硬编码输入”
- 公式单元格：黑色字体 + 白色背景 = “计算结果”
- 工作表链接：绿色字体 + 白色背景 = “来自其他工作表的引用”
- 核心输出结果：黑色粗体字体 + 中等蓝色填充 = “这就是最终答案”

**字体颜色用于标识内容类型（输入/公式/链接），而填充颜色则用于表明所在区域（标题/数据/输出）。**

### 边框标准（专业外观的必备要素）

主要章节周围需设置**粗边框**（1.5磅）：
- 关键输入部分
- 预测假设部分
- 5年现金流预测部分
- 终值部分
- 估值汇总部分
- 各敏感性分析表格

各子章节之间需设置**中等宽度边框**（1磅）：
- 公司概况与历史表现部分
- 增长假设与息税前利润率及自由现金流参数部分

数据表格周围需设置**细边框**（0.5磅）：
- 不同情景假设表（看跌 | 基准 | 看涨 | 已选）
- 历史数据与预测财务数据对比矩阵

**表格内的单个单元格无需加边框**——这样能保持界面整洁、便于阅读。

**边框是必需的**——没有专业边框的模型无法直接呈现给客户。

**数字格式**（遵循 xlsx 技能规范）：
- **年份**：以文本字符串形式显示（例如“2024”，而非“2,024”）
- **百分比**：格式为 `0.0%`（保留一位小数）
- **货币金额**：百万级格式为 `$#,##0`；每股金额格式为 `$#,##0.00`——标题中务必注明单位（如“营收（百万美元）”）
- **零值处理**：通过数字格式设置，将所有零显示为“-”（例如 `$#,##0;($#,##0);-`）
- **大数值**：使用带千位分隔符的 `#,##0` 格式
- **负数**：用括号表示，格式为 `(#,##0)`（不可使用减号）

**单元格注释（所有硬编码输入项均需添加）：**

根据 xlsx 技能规范，所有硬编码值都必须附带单元格注释，说明其来源。注释格式应为：“来源：[系统/文档]，[日期]，[参考资料]，[如有网址请注明]”

**至关重要**：请在创建单元格时立即添加注释，切勿拖延到最后。

### DCF 工作表的详细结构

**第1部分：标题栏**
```csv
Row,Content
1,[Company Name] DCF Model
2,Ticker: [XXX] | Date: [Date] | Year End: [FYE]
3,Blank
4,Case Selector Cell (1=Bear 2=Base 3=Bull)
5,Case Name Display (formula: =IF([Selector]=1"Bear"IF([Selector]=2"Base""Bull")))
```

**第2节：市场数据（与案例无关）**
```csv
Item,Value
Current Stock Price,$XX.XX
Shares Outstanding (M),XX.X
Market Cap ($M),[Formula]
Net Debt ($M),XXX [or Net Cash if negative]
```

**第3节：DCF情景假设**

需为每种情景（看跌、基准、看涨）分别创建独立的假设模块，在这些模块中，与DCF分析相关的各项假设——如收入增长率、息税前利润率、税率、销售及管理费用占收入的比例、资本支出占收入的比例、净营运资本随收入变动的百分比、终端增长率以及加权平均资本成本——应按照预测年份的顺序横向排列。每个模块都必须包含节标题、显示预测年份（FY1、FY2等）的列标题行，以及数据行。具体的布局要求请参见 `<correct_patterns>` 部分中的“正确的假设表结构”说明。

**第4节：历史及预测财务数据**

应引用从各情景模块中提取的汇总列（例如“选定案例”），而非在每一行的预测数据中都使用零散的IF函数。

```csv
Income Statement ($M),2020A,2021A,2022A,2023A,2024E,2025E,2026E
Revenue,XXX,XXX,XXX,XXX,[=E29*(1+$E$10)],[=F29*(1+$E$11)],[=G29*(1+$E$12)]
  % growth,XX%,XX%,XX%,XX%,[=E29/D29-1],[=F29/E29-1],[=G29/F29-1]
,,,,,,
Gross Profit,XXX,XXX,XXX,XXX,[=E29*E33],[=F29*F33],[=G29*G33]
  % margin,XX%,XX%,XX%,XX%,[=E33/E29],[=F33/F29],[=G33/G29]
,,,,,,
Operating Expenses:,,,,,,,
  S&M,XXX,XXX,XXX,XXX,[=E29*0.15],[=F29*0.14],[=G29*0.13]
  R&D,XXX,XXX,XXX,XXX,[=E29*0.12],[=F29*0.11],[=G29*0.10]
  G&A,XXX,XXX,XXX,XXX,[=E29*0.08],[=F29*0.07],[=G29*0.07]
  Total OpEx,XXX,XXX,XXX,XXX,[=E36+E37+E38],[=F36+F37+F38],[=G36+G37+G38]
,,,,,,
EBIT,XXX,XXX,XXX,XXX,[=E33-E39],[=F33-F39],[=G33-G39]
  % margin,XX%,XX%,XX%,XX%,[=E41/E29],[=F41/F29],[=G41/G29]
,,,,,,
Taxes,(XX),(XX),(XX),(XX),[=E41*$E$24],[=F41*$E$24],[=G41*$E$24]
  Tax rate,XX%,XX%,XX%,XX%,[=E43/E41],[=F43/F41],[=G43/G41]
,,,,,,
NOPAT,XXX,XXX,XXX,XXX,[=E41-E43],[=F41-F43],[=G41-G43]
```

**核心公式模式**：
- 收入增长计算：`=E29*(1+$E$

```csv
Cash Flow ($M),2020A,2021A,2022A,2023A,2024E,2025E,2026E
NOPAT,XXX,XXX,XXX,XXX,[=E45],[=F45],[=G45]
(+) D&A,XXX,XXX,XXX,XXX,[=E29*$E$21],[=F29*$E$21],[=G29*$E$21]
    % of Rev,XX%,XX%,XX%,XX%,[=E58/E29],[=F58/F29],[=G58/G29]
(-) CapEx,(XX),(XX),(XX),(XX),[=E29*$E$22],[=F29*$E$22],[=G29*$E$22]
    % of Rev,XX%,XX%,XX%,XX%,[=E60/E29],[=F60/F29],[=G60/G29]
(-) Δ NWC,(XX),(XX),(XX),(XX),[=(E29-D29)*$E$23],[=(F29-E29)*$E$23],[=(G29-F29)*$E$23]
    % of Δ Rev,XX%,XX%,XX%,XX%,[=E62/(E29-D29)],[=F62/(F29-E29)],[=G62/(G29-F29)]
,,,,,,
Unlevered FCF,XXX,XXX,XXX,XXX,[=E57+E58-E60-E62],[=F57+F58-F60-F62],[=G57+G58-G60-G62]
```

**行引用示例**（基于报表布局）：
- $E$
```csv
DCF Valuation,2024E,2025E,2026E,2027E,2028E,Terminal
Unlevered FCF ($M),XXX,XXX,XXX,XXX,XXX,
Period,0.5,1.5,2.5,3.5,4.5,
Discount Factor,0.XX,0.XX,0.XX,0.XX,0.XX,
PV of FCF ($M),XXX,XXX,XXX,XXX,XXX,
,,,,,,
Terminal FCF ($M),,,,,,,XXX
Terminal Value ($M),,,,,,,XXX
PV Terminal Value ($M),,,,,,,XXX
,,,,,,
Valuation Summary ($M),,,,,,
Sum of PV FCFs,XXX,,,,,
PV Terminal Value,XXX,,,,,
Enterprise Value,XXX,,,,,
(-) Net Debt,(XX),,,,,
Equity Value,XXX,,,,,
,,,,,,
Shares Outstanding (M),XX.X,,,,,
IMPLIED PRICE PER SHARE,$XX.XX,,,,,
Current Stock Price,$XX.XX,,,,,
Implied Upside/(Downside),XX%,,,,,
```

### WACC表格结构

```csv
COST OF EQUITY CALCULATION,,
Risk-Free Rate (10Y Treasury),X.XX%,[Yellow input]
Beta (5Y monthly),X.XX,[Yellow input]
Equity Risk Premium,X.XX%,[Yellow input]
Cost of Equity,X.XX%,[Calculated blue]
,,
COST OF DEBT CALCULATION,,
Credit Rating,AA-,[Yellow input]
Pre-Tax Cost of Debt,X.XX%,[Yellow input]
Tax Rate,XX.X%,[Link to DCF sheet]
After-Tax Cost of Debt,X.XX%,[Calculated blue]
,,
CAPITAL STRUCTURE,,
Current Stock Price,$XX.XX,[Link to DCF]
Shares Outstanding (M),XX.X,[Link to DCF]
Market Capitalization ($M),"X,XXX",[Calculated]
,,
Total Debt ($M),XXX,[Yellow input]
Cash & Equivalents ($M),XXX,[Yellow input]
Net Debt ($M),XXX,[Calculated]
,,
Enterprise Value ($M),"X,XXX",[Calculated]
,,
WACC CALCULATION,Weight,Cost,Contribution
Equity,XX.X%,X.X%,X.XX%
Debt,XX.X%,X.X%,X.XX%
,,
WEIGHTED AVERAGE COST OF CAPITAL,X.XX%,[Green output]
```

**关键WACC计算公式：**
```
Market Cap = Price × Shares
Net Debt = Total Debt - Cash
Enterprise Value = Market Cap + Net Debt
Equity Weight = Market Cap / EV
Debt Weight = Net Debt / EV
WACC = (Cost of Equity × Equity Weight) + (After-tax Cost of Debt × Debt Weight)
```

### 敏感性分析（DCF表格底部）

**术语说明**：“敏感性表格”指的是包含行标题、列标题以及每个数据单元格中公式构成的简单二维网格，**并非**Excel中的“数据表”功能（位于“数据”→“假设分析”→“数据表”路径下）。你需要使用openpyxl在每个单元格中输入常规的Excel公式。

**位置**：DCF表格的第87行及以后（**不在单独的页面上**）

**共三个垂直堆叠的敏感性表格**：

1. **加权平均资本成本与终端增长率**（第87-100行）——5×5网格，共25个包含公式的单元格
2. **营收增长率与息税前利润率**（第102-115行）——5×5网格，共25个包含公式的单元格
3. **贝塔系数与无风险利率**（第117-130行）——5×5网格，共25个包含公式的单元格

**需输入的公式总数为75个**（此为必填项，非可选）

**重要注意事项**：所有敏感性表格的单元格都必须通过openpyxl以编程方式填充公式，严禁使用线性近似等简化手段。不得留下任何占位文本或关于手动操作步骤的说明，也绝不能以“内容过于复杂”为由留空单元格——应使用Python循环来生成这些公式。

**表格设置要求**：
1. 创建包含行/列标题的表格结构（即需要测试的假设数值）
2. 为**每一个**数据单元格填充如下公式：
   - 使用行标题数值（例如：加权平均资本成本 = 9.0%）
   - 使用列标题数值（例如：终端增长率 = 3.0%）
   - 基于这些特定假设重新计算完整的DCF模型
   - 输出该情景下对应的股票价格估算值
3. 交付的文件中所有单元格都必须包含可运行的公式
4. 使用条件格式对单元格进行颜色标注：数值较高时显示绿色，数值较低时显示红色
5. 将基准情景对应的单元格加粗显示
6. 在各个表格之间保留1-2行空白行

**无需人工干预**——用户打开文件时，这些敏感性表格必须能够完全正常使用。

## 情景选择器实现方案

**三情景框架**：

### 负面情景
- 保守的营收增长率（处于历史数据范围的较低端）
- 利润率出现下滑或无增长空间
- 更高的加权平均资本成本（风险溢价上升）
- 更低的终端增长率
- 更高的资本支出假设值

### 基准情景
- 市场普遍预期或管理层给出的营收增长率
- 基于运营杠杆效应的适度利润率提升
- 当前市场所反映的加权平均资本成本
- 与GDP增长水平相匹配的终端增长率（2.5%-3.0%）
- 标准的资本支出假设值

### 正面情景
- 乐观的营收增长率（处于预测范围的较高端）
- 显著的利润率提升
- 更低的加权平均资本成本（风险溢价下降）
- 更高的终端增长率（3.5%-5.0%）
- 较低的资本支出强度

**公式实现方式**：

**严禁在各个公式中散布嵌套的IF函数**。相反，应创建一个汇总列，通过INDEX或OFFSET函数从对应的情景数据块中提取数值。

**推荐的使用INDEX函数的格式**：
`=INDEX(B10:D10, 1, $B$
