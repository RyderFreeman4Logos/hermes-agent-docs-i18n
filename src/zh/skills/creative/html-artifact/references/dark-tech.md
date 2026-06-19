# 深色科技风格图表变体

专为云架构、软件架构及系统架构图设计的深色“基础设施”风格——采用950号石板灰背景，搭配淡色网格以及类似霓虹灯效果的类别线条。该风格继承自之前的`architecture-diagram`技能（基于Cocoon AI的生成器MIT）。当主题涉及基础设施或软件系统时，请使用此风格；而对于教育类或实物主题，则建议使用`concept-archetypes.md`中定义的浅色9级渐变风格。

有关通用的结构化技术（如标记、节点组、坐标规范），请参阅`svg-diagrams.md`文档。

> **独立适配说明：** 原版设计从Google Fonts加载了JetBrains Mono字体。本技能禁止使用外部字体，应改用操作系统自带的`--mono`字体系列。除此之外，深色风格保持不变。

## 背景设置

采用950号石板灰背景，并叠加40像素宽度的细微网格：

```css
body { background: #020617; color: #e2e8f0; font-family: ui-monospace, "SF Mono", Menlo, monospace; }
.diagram-card { background: #0b1220; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; }
```

```xml
<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
  </pattern>
</defs>
<rect width="100%" height="100%" fill="url(#grid)"/>
```

## 符号组件调色板

填充色为半透明色调；边框色则为纯饱和度色彩：

| 组件类型 | 填充色 (rgba) | 边框色 (hex) |
|---|---|---|
| 前端 | `rgba(8,51,68,0.4)` | `#22d3ee` 青色 |
| 后端 | `rgba(6,78,59,0.4)` | `#34d399` 翠绿色 |
| 数据库 | `rgba(76,29,149,0.4)` | `#a78bfa` 紫色 |
| AWS/云服务 | `rgba(120,53,15,0.3)` | `#fbbf24` 橙黄色 |
| 安全 | `rgba(136,19,55,0.4)` | `#fb7185` 玫红色 |
| 消息总线 | `rgba(251,146,60,0.3)` | `#fb923c` 橙色 |
| 外部系统 | `rgba(30,41,59,0.5)` | `#94a3b8` 石板灰 |

字体大小：组件名称为12px，子标签为9px，注释为8px，极小标签为7px。

## 组件渲染——双矩形遮罩

半透明填充色可让箭头显示在背景之上。通过一个不透明的背景矩形对每个组件进行遮罩，再在其上方叠加样式化的矩形：

```xml
<rect x="100" y="80" width="160" height="60" rx="6" fill="#0f172a"/>                       <!-- opaque backing -->
<rect x="100" y="80" width="160" height="60" rx="6" fill="rgba(6,78,59,0.4)" stroke="#34d399" stroke-width="1.5"/>
<text x="180" y="114" text-anchor="middle" fill="#e2e8f0" font-size="12">API server</text>
```

各组件的边框半径为 `rx="6"`，线条宽度为 1.5px。标准组件高度为 60px；大型组件高度为 80–120px；组件之间需保持至少 40px 的垂直间距。

## 连接与边界标识

- **层叠顺序**：箭头应尽早绘制（紧随网格之后），这样组件框就能显示在箭头上方。
- **安全流**：采用虚线玫瑰线样式（`stroke-dasharray="4 4"`，颜色为 `#fb7185`）。
- **安全组边界**：虚线玫瑰线，样式为 `4 4`，边框半径为 `rx="8"`。
- **区域边界**：粗虚线，样式为 `8 4`，颜色为琥珀色，边框半径为 `rx="12"`。
- **消息总线**应位于各服务组件之间的间隙中，绝不能与组件重叠。
- **图例**（非常重要）：需放置在所有边界框之外——计算出所有边界框中最低点的 Y 值，然后将图例置于该点下方至少 20px 处。

## 文档结构

文档由四部分组成：(1) 包含跳动圆点及副标题的页眉；(2) 放在带圆角边框卡片中的 SVG 图像；(3) 下方排列的摘要信息卡片网格；(4) 最简化的页脚。跳动圆点效果完全通过 CSS（`@keyframes` 动画）实现，无需使用 JavaScript。

信息卡模板：

```html
<div class="card">
  <div class="card-header"><span class="card-dot cyan"></span><h3>Title</h3></div>
  <ul><li>Item one</li><li>Item two</li></ul>
</div>
```

所有动画效果（如脉冲点动效果）均可仅通过纯 CSS 实现，无需使用 JavaScript。`templates/diagram.html` 文件提供了双模式设计——既包含浅色版的教育用 CSS，也包含深色版 CSS；若需用于基础设施架构图，只需添加 `class="dark"` 属性（或使用深色主题的 `<style>` 块）即可。
