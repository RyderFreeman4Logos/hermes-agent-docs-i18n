# 主题风格

所有组件都应遵循统一的设计系统。请直接复用这些样式标识，切勿为每个文件单独创建配色方案。这正是决定输出效果是专业精致还是杂乱无章的最关键因素。

## 标准的`:root`块

请将此代码粘贴到每个组件的 `<style>` 标签中（它已存在于 `templates/base.html` 文件中）：

```css
:root {
  /* surfaces */
  --ivory:    #FAF9F5;   /* page background (warm paper) */
  --white:    #FFFFFF;   /* cards / panels */
  --slate:    #141413;   /* near-black text & inverted/dark panels */
  /* accents (semantic — see convention below) */
  --clay:     #D97757;   /* primary accent: focus / attention */
  --olive:    #788C5D;   /* success / additions / "after" / done */
  --rust:     #B04A3F;   /* error / deletions / failure path */
  --oat:      #E3DACC;   /* warm neutral fill / highlight */
  /* warm gray ramp */
  --gray-150: #F0EEE6;
  --gray-300: #D1CFC5;
  --gray-500: #87867F;   /* secondary text, arrows, muted labels */
  --gray-700: #3D3D3A;
  /* shape tokens */
  --border:        1.5px solid var(--gray-300);
  --radius-panel:  12px;
  --radius-row:    8px;
  --radius-pill:   999px;
  /* fonts (OS-native — zero loading) */
  --serif: ui-serif, Georgia, "Times New Roman", serif;
  --sans:  system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono:  ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
```

## 语义化颜色规范

颜色用于编码**含义**，在所有文档模式下应用方式一致：

| 标识符 | 含义 |
|---|---|
| `--clay` | 焦点对象/重点内容/主要强调项/“关键路径” |
| `--olive` | 成功、正向变化、新增内容、“后续步骤”、已完成 |
| `--rust` | 错误、负向变化、已删除内容、失败路径（仅当文档存在错误时使用） |
| `--oat` | 中性高亮/暖色填充/通用徽章 |
| `--gray-500` | 次要文本、箭头符号、柔和的元数据 |

切勿像彩虹般交替使用不同颜色。每个文档最多使用2–3种强调色。

## 类型系统——按角色划分的三种字体

- **衬线体**（`--serif`）→ 所有标题及大型显示数字。`font-weight: 500`（中等粗细，不可加粗），`letter-spacing: -0.01em`。
- **无衬线体**（`--sans`）→ 正文内容。`line-height: 1.55–1.65`。
- **等宽体**（`--mono`）→ 所有标签、代码、路径、指标、时间戳、信息块及标题行。

大多数文档都采用“标题行”格式作为开头：

```css
.eyebrow { font-family: var(--mono); font-size: 11px; letter-spacing: 0.08em;
           text-transform: uppercase; color: var(--gray-500); }
h1 { font-family: var(--serif); font-weight: 500; letter-spacing: -0.01em; }
```

## 基础模板

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: var(--ivory); color: var(--gray-700);
  font-family: var(--sans); line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  padding: 56px 24px 120px;   /* generous bottom gutter */
}
.page { max-width: 860px; margin: 0 auto; }   /* tune width per density */
html { scroll-behavior: smooth; }
```

**`.page` 根据密度设定的最大宽度：** 单栏报告/说明文为 820–860px；双栏计划书/拉取请求为 1040–1120px；幻灯片内部区域则为约 780px。

## 卡片式布局（最常用的设计风格）

以象牙白为背景的白色卡片，配有细边框与圆角，可可选添加左侧强调边框。通过这一标准方案，即可创建数据统计卡片、重点标注内容、简述框、信息面板以及设计原型框架等元素：

```css
.card {
  background: var(--white); border: var(--border);
  border-radius: var(--radius-panel); padding: 20px;
}
.card.warn { border-left: 4px solid var(--clay); }   /* or --olive / --rust */
```

## 页面布局

使用 CSS Grid 进行结构布局，Flexbox 实现对齐功能。文档界面采用双列设计：

```css
.layout { display: grid; grid-template-columns: 220px minmax(0,1fr); gap: 40px; }
/* minmax(0,1fr) prevents the content column from overflowing */
aside { position: sticky; top: 32px; align-self: start; }   /* in-page nav / TOC */
h2 { scroll-margin-top: 24px; }   /* so anchor jumps clear the top */

@media (max-width: 860px) {        /* the entire responsive strategy: */
  .layout { grid-template-columns: 1fr; }   /* collapse to one column */
  aside { display: none; }                  /* hide the sidebar */
}
```

统计/汇总区域：使用 `display: grid; grid-template-columns: repeat(4, 1fr);`，在某个断点处变为 `repeat(2,1fr)`。

## 表格

用于展示表格数据的真实 `<table>` 元素：设置 `border-collapse` 属性，表头采用 `--gray-150` 颜色，使用小号大写等宽字体，行边框极细，并包裹在具有 `overflow: hidden` 属性的圆角卡片中以裁剪角落部分。仅当单元格需要丰富内容或必须响应式地重新排列时，才使用由 `.row`/`.cell` div 元素构成的 `display:grid` “表格”结构（在断点处可将 `border-left` 替换为 `border-top`）。

## 代码块 + 手动高亮显示

代码被置于深色的 `--slate` 颜色圆角面板中，启用 `overflow-x: auto`，字体为等宽字体且大小约为 13px。无需使用 Prism 或 highlight.js —— 可通过语义化的 `span` 元素来包裹代码片段以实现高亮效果：

```css
.code { background: var(--slate); color: #E8E6DF; border-radius: var(--radius-panel);
        padding: 16px 18px; font-family: var(--mono); font-size: 13px; overflow-x: auto; }
.code .kw  { color: var(--clay); }    /* keywords */
.code .str { color: var(--olive); }   /* strings */
.code .cm  { color: var(--gray-500); }/* comments */
.code .fn  { color: #C9B98A; }        /* function names (warm tan) */
```

**差异显示**——采用三列网格布局（行号 | 标记符 | 代码），每行均为带颜色的全宽显示。其内容与画廊中的 `03-code-review-pr.html` 文件内容完全一致：

```css
.diff-row { display: grid; grid-template-columns: 48px 18px 1fr; white-space: pre;
            font-family: var(--mono); font-size: 12.5px; }
.diff-row .ln   { color: var(--gray-500); text-align: right; padding-right: 10px; }
.diff-row .code { color: #E8E6DC; }
.diff-row.add { background: rgba(120,140,93,0.15); }   /* olive tint */
.diff-row.add .mark { color: var(--olive); }
.diff-row.del { background: rgba(176,74,63,0.15); }    /* rust tint */
.diff-row.del .mark { color: var(--rust); }
.diff-row.ctx  .code { color: #B8B6AC; }               /* unchanged context */
.diff-row.hunk .code { color: var(--gray-500); }       /* @@ -0,0 +1,58 @@ headers */
```

## 调用提示、信息卡片与徽章（纯 CSS 实现）

```css
.callout { background: rgba(217,119,87,0.06); border-left: 3px solid var(--clay);
           border-radius: var(--radius-row); padding: 14px 16px; }
.pill  { border-radius: var(--radius-pill); padding: 2px 10px; font-family: var(--mono);
         font-size: 11px; background: var(--oat); }
.badge { border-radius: 6px; padding: 1px 7px; font-family: var(--mono); font-size: 11px; }
.badge.new { background: rgba(120,140,93,0.18); color: var(--olive); }
.badge.del { background: rgba(176,74,63,0.18); color: var(--rust); }
```

带颜色的背景应使用强调色的 `rgba()` 格式——无需为此新增专用标记。

## 装饰元素为直接绘制，而非导入

- **时间轴** = 一条 `::before` 创建的垂直轨道，再加上根据状态变化的绝对定位圆点。
- **复选框对勾** = 一个带边框的正方形，在处于 `.done` 状态时会通过 `::after` 生成旋转边框的对勾。
- **进度条** = 一个轨道 div 加上一个 `width:%` 格式的填充 div。
- **图表/图标** = 手动编写的内联 `<svg>` 元素（详见 `svg-diagrams.md`）。

## 空间节奏

章节之间的间距约为 52–64px；各个元素之间的间距则按 8 / 12 / 14 / 18 / 22px 的比例设置。保持一致的间距是体现“设计感”的关键所在。
