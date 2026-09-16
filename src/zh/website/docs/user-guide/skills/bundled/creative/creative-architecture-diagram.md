---
title: "Architecture Diagram — Dark-themed SVG architecture/cloud/infra diagrams as HTML"
sidebar_label: "Architecture Diagram"
description: "Dark-themed SVG architecture/cloud/infra diagrams as HTML"
---

【背景信息】
Hermes Agent技术文档、CLI使用指南、智能体技能、插件、提供方以及开发者指南。

【目标文本翻译】
{/* 本页面由website/scripts/generate-skill-docs.py工具根据该技能的SKILL.md文件自动生成。请直接编辑源文件SKILL.md，而非此页面。 */}

# 架构图

以HTML格式呈现深色主题的SVG架构/云/基础设施图表。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative\architecture-diagram` |
| 版本 | `1.0.0` |
| 开发者 | Cocoon AI（hello@cocoon-ai.com），由Hermes Agent移植实现 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `architecture`、`diagrams`、`SVG`、`HTML`、`visualization`、`infrastructure`、`cloud` |
| 相关技能 | [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams)、[`excalidraw`](/docs/user-guide/skills/optional/creative/creative-excalidraw) |

## 参考：完整SKILL.md内容

:::info
以下为Hermes在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 架构图技能

能够生成专业级的深色主题技术架构图，这些图表以独立的HTML文件形式呈现，并内置SVG图形。无需任何外部工具、API密钥或渲染库——只需编写HTML文件并在浏览器中打开即可。

## 适用场景

**最适合用于：**
- 软件系统架构（前端/后端/数据库层）
- 云基础设施（VPC、区域、子网、托管服务）
- 微服务/服务网格拓扑结构
- 数据库与API关系图、部署示意图
- 任何符合深色网格风格的技术基础设施相关内容

**如需以下类型内容，请另寻其他工具：**
- 物理、化学、数学、生物学等科学主题
- 实物对象（车辆、硬件、人体解剖结构、截面图）
- 平面布局图、叙事流程图、教育类/教科书风格的视觉内容
- 手绘白板草图（可考虑使用`excalidraw`工具）
- 动画演示视频（可考虑使用动画生成技能）

若该主题有更专业的生成技能，优先选择此类技能。若没有合适选项，此技能也可作为通用SVG图表的后备方案——输出结果仍将呈现下文所述的深色科技风格。

基于[Cocoon AI的架构图生成器](https://github.com/Cocoon-AI/architecture-diagram-generator)（MIT许可协议）。

## 工作流程

1. 用户描述其系统架构（组件、连接关系及技术栈）
2. 按照以下设计规范生成HTML文件
3. 使用`write_file`函数将文件保存为`.html`格式（例如`~/architecture-diagram.html`）
4. 用户在任意浏览器中打开该文件——支持离线使用，无依赖项

### 输出路径

可将图表保存到用户指定的路径，若未指定则默认保存至当前工作目录：
```
./[project-name]-architecture.html
```

### 预览功能

保存后，建议用户打开该预览内容：
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

## 设计系统与视觉语言

### 颜色方案（语义映射）

通过特定的 `rgba` 填充色和十六进制描边色对组件进行分类：

| 组件类型 | 填充色 (rgba) | 描边色 (十六进制) |
| :--- | :--- | :--- |
| **前端** | `rgba(8, 51, 68, 0.4)` | `#22d3ee`（青色-400） |
| **后端** | `rgba(6, 78, 59, 0.4)` | `#34d399`（绿松石色-400） |
| **数据库** | `rgba(76, 29, 149, 0.4)` | `#a78bfa`（紫罗兰色-400） |
| **AWS/云服务** | `rgba(120, 53, 15, 0.3)` | `#fbbf24`（琥珀色-400） |
| **安全** | `rgba(136, 19, 55, 0.4)` | `#fb7185`（玫瑰色-400） |
| **消息队列** | `rgba(251, 146, 60, 0.3)` | `#fb923c`（橙色-400） |
| **外部系统** | `rgba(30, 41, 59, 0.5)` | `#94a3b8`（石板灰-400） |

### 字体与背景
- **字体：** JetBrains Mono（等宽字体），从 Google Fonts 加载
- **字号：** 标题为 12px，子标签为 9px，注释为 8px，极小标签为 7px
- **背景：** 石板灰-950 颜色（`#020617`），并带有淡淡的 40px 网格图案

```svg
<!-- Background Grid Pattern -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## 技术实现细节

### 组件渲染
组件为带 1.5px 边框的圆角矩形（`rx="6"`）。为避免箭头在半透明填充区域中显现，需采用**双矩形遮罩技术**：
1. 先绘制不透明的背景矩形（`#0f172a`）
2. 再在其上方绘制半透明的样式矩形

### 连接规则
- **层叠顺序：** 需在 SVG 文件的早期阶段（网格之后）绘制箭头，以便其显示在组件框的下方
- **箭头样式：** 通过 SVG 标记定义
- **安全流路径：** 使用玫瑰色虚线（`#fb7185`）表示
- **边界标识：**
  - *安全组：* 玫瑰色虚线，线宽为 `4,4`
  - *区域：* 橙黄色粗虚线，线宽为 `8,4`，并带有圆角 `rx="12"`

### 空间布局逻辑
- **标准高度：** 小型组件为 60px；大型组件为 80-120px
- **垂直间距：** 组件之间至少保留 40px 的间距
- **消息总线：** 必须放置在各服务组件之间的间隙中，不得与其重叠
- **图例位置：** **极为重要。** 图例必须置于所有边界框之外。需计算所有边界线的最低 Y 坐标，并将图例放置在该坐标下方至少 20px 处。

## 文档结构

生成的 HTML 文件采用四部分布局：
1. **页头：** 包含带闪烁点指示器的标题及副标题
2. **主 SVG 图形：** 图表显示在带圆角边框的卡片中
3. **概要卡片：** 图表下方为三张卡片组成的网格，用于展示高级详细信息
4. **页脚：** 包含最基本的元数据

### 信息卡片格式
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## 输出要求
- **单个文件**：需生成一个完整的独立 `.html` 文件
- **无外部依赖**：所有 CSS 和 SVG 文件必须内联（Google Fonts 除外）
- **禁止使用 JavaScript**：所有动画效果（如脉冲点动效果）均需通过纯 CSS 实现
- **兼容性**：必须在所有现代网页浏览器中正常显示

## 模板参考

如需查看完整的 HTML 模板，以及其中的结构、CSS 和 SVG 组件示例，请参考此处：

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

该模板包含了各类组件（前端、后端、数据库、云服务、安全组件）、箭头样式（实线、虚线、曲线）、安全组、区域边界以及图例的实际应用示例——在生成图表时，可将其作为结构参考。
