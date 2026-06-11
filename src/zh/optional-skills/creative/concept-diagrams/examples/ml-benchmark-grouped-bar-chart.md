# 双坐标轴的机器学习基准分组柱状图

这是一种定量数据可视化图表，通过双Y轴、阈值标记以及内嵌的准确率表格，对比不同量化等级下大语言模型推理速度的差异。

## 主要设计元素

- **分组柱状图**：每类数据以明暗不同的颜色组合呈现最小/最大值范围（颜色越浅代表最小值，越深代表最大值）
- **双Y轴**：左侧轴用于显示主要指标（tokens/秒），右侧轴用于显示次要指标（VRAM占用量，单位：GB）
- **叠加折线图**：通过带标签的点状 `<polyline>` 图形展示不同类别下的VRAM使用情况
- **阈值标记**：红色虚线水平线，用于标示硬件限制值（24 GB GPU）
- **区域标注**：在阈值上下方添加细微的文字标签以提供背景说明
- **内嵌数据表**：图表下方以交替行填充的方式展示定量准确率数据
- **语义颜色编码**：每种量化等级都采用独特的颜色方案（红色=内存溢出，琥珀色=推理速度慢，青色=最佳性能区间，蓝色=推理速度快）

## 图表类型

这是一种**定量数据图表**，包含以下元素：
- **分组垂直柱状图**：展示每类数据的最低至最高性能范围
- **次要坐标轴线条**：以连续散点图的形式叠加显示VRAM占用情况
- **阈值标注**：硬件限制线
- **内嵌表格**：用于补充准确率相关指标

## 图表布局结构公式

```
Chart area:  x=90–590, y=70–410 (500px wide, 340px tall)
Left Y-axis: Primary metric (tok/s)
             y = 410 − (val / max_val) × 340
Right Y-axis: Secondary metric (VRAM GB)
              Same formula, different scale labels
Groups:       Divide width by number of categories
Bars:         Each group → min bar (34px) + 8px gap + max bar (34px)
Line overlay: <polyline> connecting data points across group centers
Threshold:    Horizontal dashed line at critical value
Table:        Below chart, alternating row fills
```

## 数据映射信息

| 量化格式 | 模型大小 | 处理速度（词/秒） | 显存占用（GB） | MMLU Pro得分 | 状态 |
|---------|---------|------------------|--------------|------------|------|
| FP16 | 62 GB | 0.5–2 | 62 | 75.2 | 内存不足/无法使用 |
| Q8_0 | 32 GB | 3–5 | 32 | 75.0 | 部分卸载 |
| Q4_K_M | 16.8 GB | 8–12 | 16.8 | 73.1 | 可完全放入显存 ✓ |
| IQ3_M | 12 GB | 12–15 | 12 | 70.5 | 达到GPU全速运行 |

## 标签栏CSS样式类

```css
/* Light mode */
.bar-fp16-min { fill: #FCEBEB; stroke: #A32D2D; stroke-width: 0.75; }
.bar-fp16-max { fill: #F7C1C1; stroke: #A32D2D; stroke-width: 0.75; }
.bar-q8-min   { fill: #FAEEDA; stroke: #854F0B; stroke-width: 0.75; }
.bar-q8-max   { fill: #FAC775; stroke: #854F0B; stroke-width: 0.75; }
.bar-q4-min   { fill: #E1F5EE; stroke: #0F6E56; stroke-width: 0.75; }
.bar-q4-max   { fill: #9FE1CB; stroke: #0F6E56; stroke-width: 0.75; }
.bar-iq3-min  { fill: #E6F1FB; stroke: #185FA5; stroke-width: 0.75; }
.bar-iq3-max  { fill: #B5D4F4; stroke: #185FA5; stroke-width: 0.75; }

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .bar-fp16-min { fill: #501313; stroke: #F09595; }
  .bar-fp16-max { fill: #791F1F; stroke: #F09595; }
  .bar-q8-min   { fill: #412402; stroke: #EF9F27; }
  .bar-q8-max   { fill: #633806; stroke: #EF9F27; }
  .bar-q4-min   { fill: #04342C; stroke: #5DCAA5; }
  .bar-q4-max   { fill: #085041; stroke: #5DCAA5; }
  .bar-iq3-min  { fill: #042C53; stroke: #85B7EB; }
  .bar-iq3-max  { fill: #0C447C; stroke: #85B7EB; }
}
```

## 叠加线 CSS 设置

```css
.vram-line { stroke: #534AB7; stroke-width: 2.5; fill: none; }
.vram-dot  { fill: #534AB7; stroke: var(--bg-primary); stroke-width: 2; }
.vram-label { font-family: system-ui, sans-serif; font-size: 10px; fill: #534AB7; font-weight: 500; }
```

## 阈值 CSS

```css
.threshold { stroke: #A32D2D; stroke-width: 1; stroke-dasharray: 6 3; fill: none; }
.threshold-label { font-family: system-ui, sans-serif; font-size: 10px; fill: #A32D2D; font-weight: 500; }
```

## 表格 CSS 样式

```css
.tbl-header { fill: var(--bg-secondary); stroke: var(--border); stroke-width: 0.5; }
.tbl-row    { fill: transparent; stroke: var(--border); stroke-width: 0.25; }
.tbl-alt    { fill: var(--bg-secondary); stroke: var(--border); stroke-width: 0.25; }
```

## 布局说明

- **视图框尺寸**：680×660（纵向布局，包含图表、图例与表格）
- **图表区域**：y轴范围为70–410，x轴范围为90–590
- **图例行位置**：y轴范围为458–470
- **内嵌表格区域**：y轴范围为490–620
- **柱状条宽度**：每根柱子宽34像素，最小值与最大值对应的柱子之间间距为8像素
- **分组间距**：各组中心点之间的间距为125像素
- **点晕效果**：在半径为5像素的彩色点后方添加半径为6像素的白色圆圈，以便在带有柱状条或网格的背景下提高可读性

## 适用场景

此图表样式适用于以下场景：
- 不同量化等级下的模型性能对比
- 性能与资源消耗之间的权衡分析
- 任何存在硬件/软件限制的多指标对比
- GPU/TPU/加速器性能测试仪表板
- 准确率与速度的帕累托前沿分析
- 硬件需求规格图表
