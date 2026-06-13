---
title: "Baoyu Article Illustrator — Article illustrations: type × style × palette consistency"
sidebar_label: "Baoyu Article Illustrator"
description: "Article illustrations: type × style × palette consistency"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉文章插画师

文章插画：类型 × 风格 × 色彩方案一致性。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/creative/baoyu-article-illustrator` 安装 |
| 路径 | `optional-skills/creative/baoyu-article-illustrator` |
| 版本 | `1.57.0` |
| 开发者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `article-illustration`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，智能体将依据此内容作为操作指令。
:::

# 文章插画师

基于 [baoyu-article-illustrator](https://github.com/JimLiu/baoyu-skills) 为 Hermes Agent 的工具生态优化而来。

可分析文章内容，确定插图位置，并按照**类型 × 风格 × 色彩方案**的要求生成图像。

## 适用场景

当用户要求为文章配图、为文章添加图片、为内容生成插画，或使用“为文章配图”、“插画化文章”或“添加图片”等类似表述时，可触发此技能。用户需提供文章内容（文件路径或粘贴的文本），并可选择指定类型、风格、色彩方案或密度。

## 三个设计维度

| 维度 | 控制参数 | 示例 |
|-----------|----------|------|
| **类型** | 信息结构类型 | 信息图、场景图、流程图、对比图、框架图、时间轴图 |
| **风格** | 渲染风格 | 极简风、温暖风、极简风、蓝图风、水彩风、优雅风 |
| **色彩方案** | 颜色主题（可选） | 棒棒糖色系、温暖色系、霓虹色系 —— 可覆盖风格默认颜色 |

可自由组合参数：`type=infographic, style=vector-illustration, palette=macaron`。

也可使用预设方案：`edu-visual` —— 一次性设定类型、风格与色彩方案。详情请参阅 [style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/style-presets.md)。

## 类型说明

| 类型 | 最佳适用场景 |
|------|--------------|
| `infographic` | 数据展示、指标分析、技术内容 |
| `scene` | 叙事类内容、情感表达类内容 |
| `flowchart` | 流程展示、工作流程演示 |
| `comparison` | 并列对比、选项展示 |
| `framework` | 模型展示、架构呈现 |
| `timeline` | 历史发展、演变过程展示 |

## 风格说明

核心风格、完整风格库以及类型与风格的兼容性信息，请参阅 [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/styles.md)。

## 输出结构

<!-- ascii-guard-ignore -->
```
{output-dir}/
├── source-{slug}.{ext}    # Only for pasted content
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```
**默认输出目录**：

| 输入内容 | 输出目录 | Markdown插入路径 |
|---------|----------|------------------|
| 文章文件路径 | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| 粘贴的内容 | `illustrations/{topic-slug}/`（当前工作目录） | `illustrations/{topic-slug}/NN-{type}-{slug}.png` |

如果用户要求不同的布局（例如将图片置于文章旁，或使用`illustrations/`子目录），则应予以满足。

**Slug格式**：2-4个单词，采用连字符分隔的小写形式。**若出现重名**，则在名称后追加`-YYYYMMDD-HHMMSS`。

## 核心原则

- **呈现概念而非比喻** —— 若文章使用了比喻（例如“电锯切西瓜”），应绘制其背后的概念，而非字面意义上的图像。
- **标签使用文章中的实际数据** —— 应使用文章中的真实数字、术语和引文，而非通用占位符。
- **提示词文件是可复现性记录** —— 在生成任何图像之前，每幅插图都必须在`prompts/`目录下保存对应的提示词文件。
- **清除敏感信息** —— 在将任何内容写入磁盘之前，需先扫描源文件，删除其中的API密钥、令牌或凭证。

## 工作流程

```
- [ ] Step 1: Detect reference images (if provided)
- [ ] Step 2: Analyze content
- [ ] Step 3: Confirm settings (clarify tool, one question at a time)
- [ ] Step 4: Generate outline
- [ ] Step 5: Generate prompts
- [ ] Step 6: Generate images (image_generate)
- [ ] Step 7: Finalize
```

### 第1步：检测参考图片

如果用户提供了参考图片（直接粘贴的路径、附件或URL）：

1. 对每张参考图片，使用其路径/URL以及相关问题调用`vision_analyze`函数，询问风格、色彩方案、构图和主题等信息。随后通过`write_file`函数将返回的描述内容保存到`{output-dir}/references/NN-ref-{slug}.md`文件中。
2. **切勿**尝试通过`write_file`或`read_file`函数来复制二进制文件——这些函数仅支持处理文本数据。如果需要为记录目的保留本地副本，可使用`terminal`命令（如`cp "$src" "{output-dir}/references/NN-ref-{slug}.{ext}"`）。该技能本身无需读取二进制文件，仅需依据视觉描述即可完成工作。
3. 由于`image_generate`函数不支持直接接收图片输入，因此在第5步生成提示词时，将使用上述视觉描述内容。

完整流程请参阅：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/workflow.md#step-1-detect-reference-images)。

### 第2步：进行分析

| 分析维度 | 输出内容 |
|----------|----------|
| 内容类型 | 技术类 / 教程类 / 方法论类 / 叙事类 |
| 目的 | 信息传递 / 可视化展示 / 想象力激发 |
| 核心论点 | 2-5个主要观点 |
| 插图应用位置 | 明确说明插图可在何处提升内容价值 |

首先读取源文件内容（可通过文件路径使用`read_file`函数读取，或直接读取粘贴的文本），然后通过`write_file`函数将分析结果保存到`{output-dir}/analysis.md`文件中。

完整流程请参阅：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/workflow.md#step-2-analyze)。

### 第3步：确认设置参数

使用`clarify`工具来收集信息。由于该工具每次仅能处理一个问题，因此应先询问最关键的问题。对于那些在用户请求中已有明确答案的问题，则可直接跳过。

| 顺序 | 问题 | 选项 |
|------|------|------|
| Q1 | **预设模板或类型** | [推荐预设]、[其他预设]，或手动选择：信息图、场景图、流程图、对比图、框架图、时间轴图、混合类型 |
| Q2 | **内容密度** | 低密度（1-2个元素）/均衡密度（3-5个元素）/按章节划分（推荐）/高密度（6个以上元素） |
| Q3 | **风格** *（若Q1已选择预设则可跳过）* | [推荐风格]、极简扁平风、科幻风、手绘风、杂志风、场景风、海报风 |
| Q4 | **色彩方案** *（可选）* | 默认风格配色、马卡龙色系、暖色调、霓虹色调 |
| Q5 | **语言** *（仅当文章语言不明确时需选择）* | 文章原文语言 / 用户指定语言 |

建议每次连续使用`clarify`函数提问不超过2-3个问题。如果用户已在请求中明确说明了相关参数，则可直接跳过该步骤。

完整流程请参阅：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/workflow.md#step-3-confirm-settings)。

### 第4步：生成大纲 → 生成`outline.md`文件

使用`write_file`函数保存`{output-dir}/outline.md`文件，文件中需包含前置元数据（类型、密度、风格、色彩方案、图片数量），并且每张插图对应一个条目：

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what to show]
**Filename**: 01-infographic-concept-name.png
```

完整模板：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/workflow.md#step-4-generate-outline)。

### 第5步：生成提示词

**强制要求**：在生成任何图像之前，每幅插图都必须先保存好对应的提示词文件——该提示词文件即用于确保结果可复现的记录。

针对每幅插图需执行以下操作：

1. 按照[references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/prompt-construction.md)中的说明创建提示词文件。
2. 使用`write_file`函数并搭配YAML格式的页眉信息，将文件保存至`{output-dir}/prompts/NN-{type}-{slug}.md`路径下。
3. 提示词必须采用针对特定类型的模板，并包含结构化的各个板块（区域/ZONES、标签/LABELS、颜色/COLORS、风格/STYLE、宽高比/ASPECT）。
4. 标签中必须包含与文章相关的具体数据：真实数字、术语、指标及引文内容。
5. 需根据提示词页眉中的说明处理参考资料（直接引用/direct、风格引用/style、配色方案/palette）——对于直接引用类型，需在提示词中嵌入对该参考资料的文字描述（因为`image_generate`函数不支持直接传入参考图像）。

### 第6步：生成图像

针对每个提示词文件需执行以下操作：

1. 调用`image_generate(prompt=..., aspect_ratio=...)`函数。该函数会返回一个包含图像URL的JSON格式结果；它不会将图像写入磁盘，也不接受输出路径参数。
2. 将提示词中的宽高比`ASPECT`映射为`image_generate`函数所支持的枚举值：`16:9`对应`landscape`（横屏）、`9:16`对应`portrait`（竖屏）、`1:1`对应`square`（正方形）；若为自定义宽高比，则取最接近的预设值。
3. 通过`terminal`工具下载返回的图像URL，保存至`{output-dir}/NN-{type}-{slug}.png`路径下（例如可使用命令`curl -sSL -o "{output-dir}/NN-{type}-{slug}.png" "{url}"`）。
4. 若生成失败，系统会自动重试一次。

注意：底层的图像生成后端由用户自行配置（默认为FAL FLUX 2 Klein 9B），且无法通过`image_generate`函数进行选择。请勿在提示词中写入模型名称期望其能自动切换后端。

### 第7步：完成整理

在对应段落之后插入如下格式的图片链接：`![描述文字](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/{relative-path}/NN-{type}-{slug}.png)`。图片的替代文本应为用文章所在语言书写的简短描述。

报告：

```
Article Illustration Complete!
Article: [path] | Type: [type] | Density: [level] | Style: [style] | Palette: [palette or default]
Images: X/N generated
```

## 修改操作

| 操作 | 步骤 |
|------|-------|
| 编辑 | 更新提示词 → 重新生成 → 更新参考信息 |
| 添加 | 定位 → 输入提示词 → 生成 → 更新大纲 → 插入内容 |
| 删除 | 删除文件 → 移除参考信息 → 更新大纲 |

## 参考资料

| 文件路径 | 内容说明 |
|----------|----------|
| [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/workflow.md) | 详细操作流程 |
| [references/usage.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/usage.md) | 调用示例 |
| [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/styles.md) | 风格库与调色板库 |
| [references/style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/style-presets.md) | 预设快捷键（类型+风格+调色板） |
| [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-article-illustrator/references/prompt-construction.md) | 提示词模板 |

## 常见误区

1. **数据完整性至关重要** —— 绝对不可对原始数据中的统计信息进行总结、改写或修改。“增长73%”应保持为“增长73%”不变。
2. **清除敏感信息** —— 在将任何内容写入输出文件之前，务必先检查源文件中是否存在API密钥、令牌或其他凭证。
3. **避免对隐喻进行字面化呈现** —— 应聚焦于概念本身的可视化表达。
4. **提示词文件为必需项** —— 未保存提示词文件则无法生成图像。该文件可用于后续重新生成内容或切换后端。
5. **`image_generate`的分辨率选项** —— 该工具支持`横向`、`纵向`和`正方形`三种格式，自定义比例会自动映射为最接近的选项。
6. **`image_generate`返回的是URL链接而非本地文件** —— 在将本地图像路径插入文章之前，务必先通过终端命令（如`curl`）下载图片。
7. **无法通过代理选择后端** —— `image_generate`会使用用户配置的模型（默认为FAL FLUX 2 Klein 9B）。切勿在提示词中写入“使用<模型>生成此内容”之类的指令，期望其自动切换模型。
