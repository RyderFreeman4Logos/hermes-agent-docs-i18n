---
title: "Baoyu Infographic — Infographics: 21 layouts x 21 styles (信息图, 可视化)"
sidebar_label: "Baoyu Infographic"
description: "Infographics: 21 layouts x 21 styles (信息图, 可视化)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉信息图生成器

信息图类型：21种布局 × 21种风格（信息图、可视化图表）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative\baoyu-infographic` |
| 版本 | `1.56.1` |
| 创建者 | 宝玉 (JimLiu) |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `infographic`、`visual-summary`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能运行时，智能体将依据此内容执行操作。
:::

# 信息图生成工具

基于 [baoyu-infographic](https://github.com/JimLiu/baoyu-skills) 为 Hermes Agent 的工具生态定制开发。

该工具包含两个核心维度：**布局**（信息结构）与**风格**（视觉美学），用户可自由组合不同的布局与风格。

## 适用场景

当用户要求创建信息图、可视化摘要或信息图表，或使用“信息图”、“可视化”及“高密度信息大图”等术语时，可触发此技能。用户需提供内容（文本、文件路径、URL或主题），并可选择性指定布局、风格、宽高比或语言。

## 可选参数

| 选项 | 可选值 |
|------|--------|
| 布局 | 21种布局选项（详见布局图库），默认值：bento-grid |
| 风格 | 21种风格选项（详见风格图库），默认值：craft-handmade |
| 宽高比 | 固定比例：横向（16:9）、纵向（9:16）、正方形（1:1）；自定义比例：任意宽高比（如3:4、4:3、2.35:1） |
| 语言 | 英语、中文、日语等 |

## 布局图库

| 布局类型 | 最佳适用场景 |
|----------|--------------|
| `linear-progression` | 时间轴、流程图、教程 |
| `binary-comparison` | A与B的对比、前后对比、优缺点分析 |
| `comparison-matrix` | 多因素对比 |
| `hierarchical-layers` | 金字塔结构、优先级层级 |
| `tree-branching` | 分类体系、目录结构 |
| `hub-spoke` | 中心主题与相关内容 |
| `structural-breakdown` | 展开视图、截面图 |
| `bento-grid` | 多个主题的概览展示（默认值） |
| `iceberg` | 显性内容与隐性内容的对比 |
| `bridge` | 问题与解决方案的呈现 |
| `funnel` | 转化流程、筛选机制 |
| `isometric-map` | 空间关系展示 |
| `dashboard` | 指标展示、关键绩效指标 |
| `periodic-table` | 分类集合展示 |
| `comic-strip` | 叙事内容、连续情节 |
| `story-mountain` | 剧情结构、紧张感递进 |
| `jigsaw` | 相互关联的组成部分 |
| `venn-diagram` | 重叠概念的可视化 |
| `winding-roadmap` | 发展历程、里程碑展示 |
| `circular-flow` | 循环过程、周期性任务 |
| `dense-modules` | 高密度模块、信息量大的指南 |

完整定义请参阅：`references/layouts/<layout>.md`

## 风格图库

| 风格 | 描述 |
|-------|-------------|
| `craft-handmade` | 手绘风格，纸质工艺效果（默认） |
| `claymation` | 3D黏土人物，定格动画风格 |
| `kawaii` | 日式可爱风格，柔和粉彩色调 |
| `storybook-watercolor` | 柔和的绘画风格，充满奇幻感 |
| `chalkboard` | 黑板上的粉笔书写效果 |
| `cyberpunk-neon` | 霓虹灯光，未来主义风格 |
| `bold-graphic` | 漫画风格，半色调设计 |
| `aged-academia` | 复古科学风格，棕褐色调 |
| `corporate-memphis` | 平面矢量风格，色彩鲜明 |
| `technical-schematic` | 蓝图风格，工程设计感 |
| `origami` | 折纸风格，几何图案 |
| `pixel-art` | 复古8位像素风格 |
| `ui-wireframe` | 灰度界面原型图 |
| `subway-map` | 公交线路图 |
| `ikea-manual` | 极简线条艺术风格 |
| `knolling` | 有序的平面摆放风格 |
| `lego-brick` | 玩具积木构建风格 |
| `pop-laboratory` | 蓝图网格、坐标标记，实验室精确感 |
| `morandi-journal` | 手绘涂鸦，温暖的莫兰迪色调 |
| `retro-pop-grid` | 1970年代复古波普艺术风格，瑞士网格布局，粗轮廓设计 |
| `hand-drawn-edu` | 水果塔色系粉彩，手绘抖动效果，火柴人图形 |

完整定义请参阅：`references/styles/<style>.md`

## 推荐组合方案

| 内容类型 | 布局与风格 |
|----------|------------|
| 时间线/历史记录 | `linear-progression` + `craft-handmade` |
| 分步指南 | `linear-progression` + `ikea-manual` |
| A与B的对比 | `binary-comparison` + `corporate-memphis` |
| 层级结构 | `hierarchical-layers` + `craft-handmade` |
| 重叠关系 | `venn-diagram` + `craft-handmade` |
| 转化流程 | `funnel` + `corporate-memphis` |
| 循环过程 | `circular-flow` + `craft-handmade` |
| 技术内容 | `structural-breakdown` + `technical-schematic` |
| 数据指标 | `dashboard` + `corporate-memphis` |
| 教学类内容 | `bento-grid` + `chalkboard` |
| 完整流程 | `winding-roadmap` + `storybook-watercolor` |
| 分类展示 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 流行趋势指南 | `dense-modules` + `retro-pop-grid` |
| 教学图表 | `hub-spoke` + `hand-drawn-edu` |
| 实操教程 | `linear-progression` + `hand-drawn-edu` |

默认设置：`bento-grid` + `craft-handmade`

## 关键词快捷选项

当用户输入包含以下关键词时，系统将**自动选择**对应的布局，并在第三步中将相关风格作为首选推荐。对于匹配的关键词，无需再通过内容进行布局推断。

如果某个快捷选项配有**提示说明**，则会在第五步生成的提示语中将其作为额外的风格指令添加进去。

| 用户关键词 | 布局方式 | 推荐风格 | 默认宽高比 | 提示词注意事项 |
|--------------|----------|----------|------------|--------------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid` | 竖屏 | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | 横屏 | 极简风格：干净的画布、充足的留白，无复杂的背景纹理，仅使用简单的卡通元素和图标。 |
```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```
<!-- ascii-guard-ignore-end -->

标题：由主题构成的2-4个单词小写连写形式；若存在冲突，则在末尾添加`-YYYYMMDD-HHMMSS`。

## 核心原则

- 忠实保留原始数据——不得进行总结或改写（但在将数据放入输出结果之前，**必须删除其中的任何凭证、API密钥、令牌或机密信息**）
- 在构建内容结构之前先明确学习目标
- 采用便于视觉呈现的结构（标题、标签、视觉元素）

## 工作流程

### 第1步：分析内容

**加载参考文档**：读取该技能对应的`references/analysis-framework.md`文件。

1. 保存原始内容（可通过提供文件路径或直接粘贴，然后使用`write_file`函数将其保存为`source.md`）
   - **备份规则**：如果已存在`source.md`文件，则将其重命名为`source-backup-YYYYMMDD-HHMMSS.md`
2. 分析内容：包括主题、数据类型、复杂度、语气以及目标受众
3. 识别原始语言与用户使用的语言
4. 从用户输入中提取设计要求
5. 将分析结果保存到`analysis.md`文件中
   - **备份规则**：如果已存在`analysis.md`文件，则将其重命名为`analysis-backup-YYYYMMDD-HHMMSS.md`

详细格式规范请参阅`references/analysis-framework.md`。

### 第2步：生成结构化内容 → `structured-content.md`

将内容转换为信息图结构：
1. 标题与学习目标
2. 各个板块，包含：核心概念、原文内容、视觉元素以及文字标签
3. 数据点（所有统计数据/引文均需原样保留）
4. 用户指定的设计要求

**规则**：仅允许使用Markdown格式。不得添加任何新信息。必须忠实保留数据，并从输出结果中删除所有凭证或机密信息。

有关详细格式说明，请参阅 `references/structured-content-template.md`。

### 第 3 步：推荐组合方案

**3.1 先检查关键词快捷方式**：如果用户输入与 **关键词快捷方式** 表中的某个关键词匹配，则自动选择对应的布局，并将相关的样式作为首选推荐。无需进行基于内容的布局推断。

**3.2 否则**，根据以下因素推荐 3-5 种布局×样式的组合：
- 数据结构 → 匹配的布局
- 内容风格 → 匹配的样式
- 目标受众的期望
- 用户的设计要求

### 第 4 步：确认选项

使用 `clarify` 工具与用户确认各项选项。由于 `clarify` 每次只能处理一个问题，因此请先提出最关键的问题：

**问题 1 — 组合方案**：列出 3 种及以上的布局×样式组合，并说明选择理由，让用户从中挑选一种。

**问题 2 — 宽高比**：询问用户希望采用的宽高比（横屏/竖屏/正方形或自定义的宽:高比例）。

**问题 3 — 语言**（仅当原文语言与用户语言不同时）：询问文本内容应使用哪种语言。

### 第 5 步：生成提示词 → `prompts/infographic.md`

**备份规则**：如果已存在 `prompts/infographic.md`，则将其重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`。

**加载参考资料**：从 `references/layouts/<layout>.md` 中读取选定的布局方案，从 `references/styles/<style>.md` 中读取样式设置。

随后将二者结合起来：
1. 布局定义来自 `references/layouts/<layout>.md`  
2. 样式定义来自 `references/styles/<style>.md`  
3. 基础模板来自 `references/base-prompt.md`  
4. 第2步中生成的结构化内容  
5. 所有文本均使用已确定的语言  

`{{ASPECT_RATIO}}` 的**宽高比处理规则**：  
- 预设的固定比例 → 对应字符串格式：横屏→`16:9`，竖屏→`9:16`，正方形→`1:1`  
- 自定义宽高比 → 直接使用原始数值（例如 `3:4`、`4:3`、`2.35:1`）  

使用 `write_file` 函数将组装好的提示词保存至 `prompts/infographic.md` 文件中。  

### 第6步：生成图像  

使用第5步中整理好的提示词，调用 `image_generate` 工具进行图像生成。  
- 将宽高比转换为 `image_generate` 所识别的格式：`16:9` → `landscape`（横屏），`9:16` → `portrait`（竖屏），`1:1` → `square`（正方形）  
- 对于自定义比例，选择最接近的预设宽高比  
- 若生成失败，自动重试一次  
- 将生成的图像URL或路径保存到输出目录中  

### 第7步：输出汇总  

需报告以下信息：主题、布局、样式、宽高比、语言、输出路径以及生成的文件列表。  

## 参考文档  

- `references/analysis-framework.md` — 分析方法  
- `references/structured-content-template.md` — 内容格式规范  
- `references/base-prompt.md` — 提示词模板  
- `references/layouts/<layout>.md` — 21种布局定义  
- `references/styles/<style>.md` — 21种样式定义  

## 常见问题与注意事项

1. **数据完整性至关重要**——绝不可对原始统计数据进行总结、改写或篡改。例如，“73%的增长”必须保持原样，不得将其替换为“显著增长”之类的表述。
2. **移除敏感信息**——在将任何内容写入输出文件之前，务必先检查其中是否包含API密钥、令牌或凭证等敏感数据。
3. **每部分仅一个核心信息**——每个信息图板块应传达一个清晰的概念。内容过多会降低可读性。
4. **风格保持一致**——整个信息图必须严格遵循参考文件中规定的样式标准，不得混用不同风格。
5. **image_generate的宽高比限制**——该工具仅支持`landscape`、`portrait`和`square`三种格式。像`3:4`这样的自定义比例需转换为最接近的选项（此时为portrait格式）。
