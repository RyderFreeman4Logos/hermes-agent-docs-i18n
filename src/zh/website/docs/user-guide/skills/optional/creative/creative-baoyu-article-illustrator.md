---
title: "Baoyu Article Illustrator — Article illustrations: type × style × palette consistency"
sidebar_label: "Baoyu Article Illustrator"
description: "Article illustrations: type × style × palette consistency"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉文章插画师

文章插画：类型 × 风格 × 色彩统一性。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/baoyu-article-illustrator` 安装 |
| 路径 | `optional-skills/creative\baoyu-article-illustrator` |
| 版本 | `1.57.0` |
| 创建者 | 宝玉 (JimLiu) |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `article-illustration`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，智能体将依据此内容执行操作。
:::

# 文章插画师

基于 [baoyu-article-illustrator](https://github.com/JimLiu/baoyu-skills) 为 Hermes Agent 的工具生态系统定制。

可分析文章内容，确定插图位置，并按照**类型 × 风格 × 色彩**的标准生成统一风格的图像。

## 适用场景

当用户要求为文章添加插图、为内容生成图片，或使用“为文章配图”、“绘制文章插图”或“添加图片”等类似表述时，可触发此技能。用户需提供文章内容（文件路径或粘贴的文本），并可选择指定类型、风格、色彩方案或图像密度。

## 三大核心维度

| 维度 | 控制参数 | 示例 |
|------|----------|------|
| **类型** | 信息结构 | 信息图、场景图、流程图、对比图、框架图、时间轴图 |
| **风格** | 渲染方式 | 极简风、温暖风、极简风、蓝图风、水彩风、优雅风 |
| **配色方案** | 颜色主题（可选） | 糖果色系、温暖色系、霓虹色系——可覆盖风格默认颜色 |

可自由组合使用：`type=infographic, style=vector-illustration, palette=macaron`。

也可直接使用预设方案：`edu-visual`——可一次性设定类型、风格及配色方案。详情请参阅 [style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/style-presets.md)。

## 类型

| 类型 | 最佳适用场景 |
|------|--------------|
| `infographic` | 数据展示、指标呈现、技术内容 |
| `scene` | 叙事表达、情感传达 |
| `flowchart` | 流程展示、工作流呈现 |
| `comparison` | 并列对比、选项展示 |
| `framework` | 模型展示、架构呈现 |
| `timeline` | 历史发展、演变过程 |

## 风格

关于核心风格、完整风格库以及类型与风格的兼容性，可查看 [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/styles.md)。

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

| 输入内容 | 输出目录 | Markdown 插入路径 |
|---------|----------|------------------|
| 文章文件路径 | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| 粘贴的内容 | `illustrations/{topic-slug}/`（当前工作目录） | `illustrations/{topic-slug}/NN-{type}-{slug}.png` |

如果用户要求不同的布局（例如将图片置于文章旁，或使用 `illustrations/` 子目录），则应予以满足。

**Slug 规则**：由 2-4 个单词组成，采用下划线分隔的小写格式。**若出现冲突**，则在名称后追加 `-YYYYMMDD-HHMMSS`。

## 核心原则

- **呈现概念而非比喻** —— 若文章使用了比喻（例如“用电锯切西瓜”），应绘制其背后的概念，而非字面意义上的图像。
- **标签需使用文章中的实际数据** —— 应使用文章中的真实数字、术语和引文，而非通用占位符。
- **提示词文件是可复现性记录** —— 在生成任何图像之前，每幅插图都必须在 `prompts/` 目录下保存对应的提示词文件。
- **清除敏感信息** —— 在将任何内容写入磁盘之前，需先扫描源代码，删除其中的 API 密钥、令牌或凭证。

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

### 第一步：识别参考图片

如果用户提供了参考图片（直接粘贴的路径、附件或 URL）：

1. 对每张参考图片，使用其路径/URL以及相关问题调用 `vision_analyze` 函数，这些问题旨在了解风格、色彩搭配、构图及主题等内容。随后通过 `write_file` 函数将返回的描述内容保存到 `{output-dir}/references/NN-ref-{slug}.md` 文件中。
2. **切勿**尝试通过 `write_file` 或 `read_file` 函数来复制二进制文件——这些函数仅支持处理文本数据。如果需要为记录目的保留本地副本，可使用 `terminal` 函数（如 `cp "$src" "{output-dir}/references/NN-ref-{slug}.{ext}"`）。该智能体本身无需读取二进制文件，仅需依据视觉描述即可完成工作。
3. 由于 `image_generate` 函数不支持直接接收图片输入，因此在第五步中，提示词中将嵌入上述视觉描述内容。

完整流程说明请参阅：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/workflow.md#step-1-detect-reference-images)。

### 第二步：进行分析

| 分析维度 | 输出内容 |
|----------|----------|
| 内容类型 | 技术类 / 教程类 / 方法论类 / 叙事类 |
| 目的 | 传递信息 / 可视化展示 / 激发想象力 |
| 核心论点 | 2-5个主要观点 |
| 插图应用场景 | 说明插图可在何处发挥作用 |

首先读取原文内容（可通过文件路径使用 `read_file` 函数读取，或直接粘贴文本），然后通过 `write_file` 函数将分析结果保存到 `{output-dir}/analysis.md` 文件中。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/workflow.md#step-2-analyze)。

### 第3步：确认设置

使用 `clarify` 工具。由于该工具一次仅能处理一个问题，因此请先提出最重要的问题。对于那些答案已在用户请求中出现的选项，则可直接跳过。

| 序号 | 问题 | 选项 |
|-------|------|------|
| Q1 | **预设类型** | [推荐预设]、[其他预设] 或手动选择：信息图、场景图、流程图、对比图、框架图、时间轴图、混合类型 |
| Q2 | **内容密度** | 低密度（1-2）、均衡密度（3-5）、按章节划分（推荐）、高密度（6+） |
| Q3 | **风格** *（若Q1已选择预设则可跳过）* | [推荐风格]、极简扁平风、科幻风、手绘风、杂志风、场景风、海报风 |
| Q4 | **配色方案** *（可选）* | 默认风格色、马卡龙色系、暖色调、霓虹色调 |
| Q5 | **语言** *（仅当文章语言不明确时使用）* | 文章原文语言 / 用户指定语言 |

请避免连续提出超过2-3个 `clarify` 问题。如果用户已在请求中明确说明了这些设置，则可直接跳过相应步骤。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/workflow.md#step-3-confirm-settings)。

### 第4步：生成大纲 → 生成 `outline.md` 文件

使用 `write_file` 函数保存 `{output-dir}/outline.md` 文件，文件需包含 frontmatter 元数据（类型、密度、风格、配色方案、图片数量），并且每张插图对应一个条目：

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what to show]
**Filename**: 01-infographic-concept-name.png
```

完整模板：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/workflow.md#step-4-generate-outline)。

### 第5步：生成提示词

**强制要求**：在生成任何图像之前，每幅插图都必须先保存一个提示词文件——该提示词文件即为结果可复现性的记录。

针对每幅插图需执行以下操作：

1. 按照[references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/prompt-construction.md)中的说明创建提示词文件。
2. 使用`write_file`函数并添加YAML格式的页眉信息，将文件保存至`{output-dir}/prompts/NN-{type}-{slug}.md`路径下。
3. 提示词必须使用包含结构化板块（ZONES / LABELS / COLORS / STYLE / ASPECT）的类型专用模板。
4. LABELS字段必须包含与文章相关的具体数据：实际数字、术语、指标及引文内容。
5. 需根据提示词页眉中的说明处理参考资料（`direct`/`style`/`palette`三种类型）——对于`direct`类型，需在提示词中嵌入该参考资料的文字描述（因为`image_generate`函数不支持直接传入参考图像）。

### 第6步：生成图像

针对每个提示词文件：

1. 调用 `image_generate(prompt=..., aspect_ratio=...)` 函数。该函数会返回一个包含图像 URL 的 JSON 结果；它不会将图像写入磁盘，也不接受输出路径参数。
2. 将提示词中的 `ASPECT` 值映射到 `image_generate` 函数所支持的枚举值：`16:9` 对应 `landscape`（横屏），`9:16` 对应 `portrait`（竖屏），`1:1` 对应 `square`（正方形）。对于其他自定义比例，则匹配最接近的预设比例。
3. 使用终端工具将返回的 URL 下载到 `{output-dir}/NN-{type}-{slug}.png` 文件中（例如：`curl -sSL -o "{output-dir}/NN-{type}-{slug}.png" "{url}"`）。
4. 若图像生成失败，系统会自动重试一次。

注意：底层的图像生成后端由用户自行配置（默认为 FAL FLUX 2 Klein 9B），且无法通过 `image_generate` 函数进行选择。请勿在提示词中直接写入模型名称，期望其能触发对应后端。

### 第 7 步：完成整理

在相应段落之后插入如下格式的图片链接：`![描述文本](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/{相对路径}/NN-{type}-{slug}.png)`，其中“描述文本”应为用文章所在语言编写的简短说明。

报告：

```
Article Illustration Complete!
Article: [path] | Type: [type] | Density: [level] | Style: [style] | Palette: [palette or default]
Images: X/N generated
```

## 修改操作

| 操作类型 | 步骤 |
|--------|-------|
| 编辑 | 更新提示词 → 重新生成 → 更新参考信息 |
| 添加 | 定位 → 输入提示词 → 生成内容 → 更新大纲 → 插入元素 |
| 删除 | 删除文件 → 移除参考信息 → 更新大纲 |

## 参考资料

| 文件路径 | 内容说明 |
|--------|---------|
| [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/workflow.md) | 详细操作流程 |
| [references/usage.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/usage.md) | 调用示例 |
| [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/styles.md) | 风格库与调色板库 |
| [references/style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/style-presets.md) | 预设快捷键（类型+风格+调色板） |
| [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-article-illustrator/references/prompt-construction.md) | 提示词模板 |

## 常见问题与注意事项

1. **数据完整性至关重要**——绝不可对原始统计数据进行总结、改写或篡改。例如，“73%的增长”就必须保持为“73%的增长”，不得有任何变动。
2. **移除敏感信息**——在将任何内容写入输出文件之前，必须先扫描其中是否存在 API 密钥、令牌或凭证等敏感数据。
3. **切勿按字面意思呈现隐喻**——应通过可视化方式展现其背后的概念。
4. **提示词文件是必需的**——未保存提示词文件则无法生成图像。该文件还能用于后续重新生成图像或切换后端。
5. **`image_generate` 的分辨率选项**——该工具支持 `landscape`（横屏）、`portrait`（竖屏）和 `square`（正方形）三种格式。自定义比例会自动映射为最接近的选项。
6. **`image_generate` 返回的是 URL，而非本地文件**——在将本地图像路径插入文章之前，务必先通过终端命令（如 `curl`）下载该图像。
7. **代理无法选择后端**——`image_generate` 会使用用户配置的模型（默认为 FAL FLUX 2 Klein 9B）。请勿在提示词中写入“使用<模型>来生成此内容”之类的语句，期望其能自动切换后端。
