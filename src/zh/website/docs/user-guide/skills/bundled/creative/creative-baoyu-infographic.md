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
| 路径 | `skills/creative/baoyu-infographic` |
| 版本 | `1.56.1` |
| 开发者 | 宝玉 (JimLiu) |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `infographic`、`visual-summary`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容作为操作指令。
:::

# 信息图生成器

基于 [baoyu-infographic](https://github.com/JimLiu/baoyu-skills) 为 Hermes Agent 的工具生态系统定制开发。

该工具包含两个核心维度：**布局**（信息结构）与**风格**（视觉美学），用户可自由组合任意布局与风格。

## 适用场景

当用户要求创建信息图、可视化摘要、信息图表，或使用“信息图”、“可视化”或“高密度信息大图”等术语时，即可触发此技能。用户需提供内容（文本、文件路径、URL 或主题），并可选择指定布局、风格、宽高比或语言。

## 可选参数

| 参数 | 取值选项 |
|--------|----------|
| 布局 | 21种选项（详见布局图库），默认：bento-grid |
| 风格 | 21种选项（详见风格图库），默认：craft-handmade |
| 宽高比 | 固定值：横屏（16:9）、竖屏（9:16）、正方形（1:1）；自定义值：任意宽高比（如3:4、4:3、2.35:1） |
| 语言 | en、zh、ja 等 |

## 布局图库

| 布局类型 | 最佳适用场景 |
|----------|--------------|
| `linear-progression` | 时间线、流程说明、教程类内容 |
| `binary-comparison` | A与B对比、前后对比、优缺点分析 |
| `comparison-matrix` | 多因素对比 |
| `hierarchical-layers` | 层级结构、优先级展示 |
| `tree-branching` | 分类体系、分类法展示 |
| `hub-spoke` | 以核心概念为中心的关联内容展示 |
| `structural-breakdown` | 分解视图、截面图 |
| `bento-grid` | 多个主题的概览展示（默认） |
| `iceberg` | 表面内容与隐藏内容的对比展示 |
| `bridge` | 问题与解决方案的呈现 |
| `funnel` | 转化流程、筛选流程 |
| `isometric-map` | 空间关系展示 |
| `dashboard` | 指标面板、关键绩效指标展示 |
| `periodic-table` | 分类集合展示 |
| `comic-strip` | 叙事内容、系列情节展示 |
| `story-mountain` | 剧情结构、情绪起伏展示 |
| `jigsaw` | 相互关联的组成部分展示 |
| `venn-diagram` | 重叠概念的对比展示 |
| `winding-roadmap` | 成长历程、里程碑展示 |
| `circular-flow` | 循环流程、重复性操作展示 |
| `dense-modules` | 高密度模块、信息量大的指南 |

完整定义见：`references/layouts/<layout>.md`

## 风格图库

| 风格类型 | 描述 |
|----------|------|
| `craft-handmade` | 手绘风格，类似手工纸艺（默认） |
| `claymation` | 3D黏土人物，定格动画风格 |
| `kawaii` | 日式可爱风格，柔和的粉色调 |
| `storybook-watercolor` | 柔和的水彩画风，充满幻想感 |
| `chalkboard` | 黑板上的粉笔书写风格 |
| `cyberpunk-neon` | 霓虹灯光效果，未来主义风格 |
| `bold-graphic` | 漫画风格，半色调处理 |
| `aged-academia` | 复古科学风格，棕褐色调 |
| `corporate-memphis` | 平面矢量风格，色彩鲜明 |
| `technical-schematic` | 蓝图风格，工程领域适用 |
| `origami` | 折纸风格，几何感强 |
| `pixel-art` | 复古8位像素风格 |
| `ui-wireframe` | 灰度界面原型设计风格 |
| `subway-map` | 地铁线路图风格 |
| `ikea-manual` | 极简线条风格 |
| `knolling` | 有序的平铺展示风格 |
| `lego-brick` | 乐高积木构建风格 |
| `pop-laboratory` | 蓝图网格、坐标标记，具备实验室精确感 |
| `morandi-journal` | 手绘涂鸦风格，采用温暖的莫兰迪色调 |
| `retro-pop-grid` | 1970年代复古波普艺术风格，瑞士方格图案，轮廓粗犷 |
| `hand-drawn-edu` | 樱桃色系粉彩，手绘抖动效果，简笔画元素 |

完整定义见：`references/styles/<style>.md`

## 推荐组合

| 内容类型 | 布局 + 风格组合 |
|----------|----------------|
| 时间线/历史记录 | `linear-progression` + `craft-handmade` |
| 分步指南 | `linear-progression` + `ikea-manual` |
| A与B对比 | `binary-comparison` + `corporate-memphis` |
| 层级结构 | `hierarchical-layers` + `craft-handmade` |
| 概念重叠展示 | `venn-diagram` + `craft-handmade` |
| 转化流程 | `funnel` + `corporate-memphis` |
| 循环流程 | `circular-flow` + `craft-handmade` |
| 技术类内容 | `structural-breakdown` + `technical-schematic` |
| 指标展示 | `dashboard` + `corporate-memphis` |
| 教育类内容 | `bento-grid` + `chalkboard` |
| 成长历程展示 | `winding-roadmap` + `storybook-watercolor` |
| 分类展示 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 流行趋势指南 | `dense-modules` + `retro-pop-grid` |
| 教学类图表 | `hub-spoke` + `hand-drawn-edu` |
| 流程教程 | `linear-progression` + `hand-drawn-edu` |

默认组合：`bento-grid` + `craft-handmade`

## 关键词快捷指令

当用户输入包含以下关键词时，系统将**自动选择**对应的布局，并在第三步中将相关风格作为首选推荐。对于匹配的关键词，系统将跳过基于内容的布局推断。

如果某个快捷指令有**提示备注**，这些备注将在第五步生成的提示语中作为额外的风格说明附加进去。

| 用户关键词 | 布局类型 | 推荐风格 | 默认宽高比 | 提示备注 |
|------------|----------|----------|------------|----------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`、`pop-laboratory`、`retro-pop-grid` | 竖屏 | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | 横屏 | 极简风格：干净的画布，充足留白，无复杂背景纹理，仅包含简单的卡通元素和图标。 |

## 输出结构

<!-- ascii-guard-ignore -->
```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```
<!-- ascii-guard-ignore-end -->

标题：由主题构成的2-4个单词小写连写形式；若存在冲突，则在末尾添加 `-YYYYMMDD-HHMMSS`。

## 核心原则

- 如实保留原始数据——不得进行总结或改写（但在将数据放入输出结果前，**必须删除其中的所有凭证、API密钥、令牌或机密信息**）
- 在规划内容结构之前先明确学习目标
- 采用便于视觉呈现的结构（标题、标签、视觉元素）

## 工作流程

### 第1步：分析内容

**加载参考文件**：读取该技能对应的 `references/analysis-framework.md` 文件。

1. 保存原始内容（通过文件路径或直接粘贴，然后使用 `write_file` 函数保存为 `source.md`）
   - **备份规则**：如果已存在 `source.md`，则将其重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 分析内容：包括主题、数据类型、复杂度、语调及目标受众
3. 识别原始语言与用户使用的语言
4. 从用户输入中提取设计要求
5. 将分析结果保存到 `analysis.md` 文件中
   - **备份规则**：如果已存在 `analysis.md`，则将其重命名为 `analysis-backup-YYYYMMDD-HHMMSS.md`

详细格式规范请参阅 `references/analysis-framework.md`。

### 第2步：生成结构化内容 → `structured-content.md`

将内容转换为信息图结构：
1. 标题与学习目标
2. 各部分包含：核心概念、原文内容、视觉元素及文字标签
3. 数据点（所有统计数据/引文均需原样保留）
4. 用户指定的设计要求

**规则**：仅可使用 Markdown 格式，不得添加新信息，必须如实保留数据，并从输出结果中删除所有凭证或机密信息。

详细格式规范请参阅 `references/structured-content-template.md`。

### 第3步：推荐组合方案

**3.1 先检查关键词快捷方式**：如果用户输入与 **关键词快捷方式** 表中的某个关键词匹配，则自动选择对应的布局，并将相关风格作为首选推荐方案，无需再通过内容进行布局推断。

**3.2 若不匹配**，则根据以下因素推荐3-5种布局×风格的组合：
- 数据结构 → 匹配的布局
- 内容语调 → 匹配的风格
- 目标受众的期望
- 用户的设计要求

### 第4步：确认选项

使用 `clarify` 工具与用户确认所选方案。由于该工具一次仅能处理一个问题，因此应先询问最关键的问题：

**问题1——组合方案**：列出3种及以上的布局×风格组合及其选择理由，让用户从中挑选一个。

**问题2——宽高比**：询问用户希望使用的宽高比（横屏/竖屏/正方形，或自定义的宽:高比例）。

**问题3——语言**（仅当原始语言与用户语言不同时）：询问文本内容应使用哪种语言。

### 第5步：生成提示词 → `prompts/infographic.md`

**备份规则**：如果已存在 `prompts/infographic.md`，则将其重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

**加载参考文件**：从 `references/layouts/<layout>.md` 中读取选定的布局方案，从 `references/styles/<style>.md` 中读取对应的风格方案。

将以下内容整合在一起：
1. 来自 `references/layouts/<layout>.md` 的布局定义
2. 来自 `references/styles/<style>.md` 的风格定义
3. 来自 `references/base-prompt.md` 的基础提示词模板
4. 第2步中生成的结构化内容
5. 已确认语言的所有文本

关于 `{{ASPECT_RATIO}}` 的宽高比处理方式：
- 若为预设名称，则对应特定的比例字符串：横屏→`16:9`，竖屏→`9:16`，正方形→`1:1`
- 若为自定义的宽:高比例，则直接使用该比例值（例如 `3:4`、`4:3`、`2.35:1`）

使用 `write_file` 函数将整合好的提示词保存到 `prompts/infographic.md` 文件中。

### 第6步：生成图像

使用第5步中准备好的提示词，通过 `image_generate` 工具生成图像。

- 将宽高比转换为 `image_generate` 工具能识别的格式：`16:9` 对应 `landscape`（横屏），`9:16` 对应 `portrait`（竖屏），`1:1` 对应 `square`（正方形）
- 对于自定义比例，选择最接近的预设宽高比
- 若生成失败，自动尝试一次
- 将生成的图像URL或路径保存到输出目录中

### 第7步：输出汇总信息

报告内容包括：主题、布局方案、风格、宽高比、语言、输出路径以及已生成的文件列表。

## 参考文档

- `references/analysis-framework.md` —— 分析方法论
- `references/structured-content-template.md` —— 内容格式规范
- `references/base-prompt.md` —— 提示词模板
- `references/layouts/<layout>.md` —— 21种布局定义
- `references/styles/<style>.md` —— 21种风格定义

## 常见误区

1. **数据完整性至关重要**——绝不能对原始统计数据进行总结、改写或修改。例如，“73%的增长”必须保持原样，不得改为“显著增长”之类的表述。
2. **必须删除机密信息**——在将任何内容放入输出文件之前，务必先检查原始数据中是否存在API密钥、令牌或凭证等信息，并将其清除。
3. **每个部分只传达一个概念**——每张信息图的每个板块都应表达一个清晰的概念。内容过多会导致可读性下降。
4. **风格需保持一致**——必须在整个信息图中统一应用参考文档中的风格定义，不得混用不同风格。
5. **image_generate支持的宽高比**——该工具仅支持 `landscape`（横屏）、`portrait`（竖屏）和 `square`（正方形）三种格式。像 `3:4` 这样的自定义比例应选择最接近的预设选项（本例中为竖屏）。
