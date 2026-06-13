---
title: "Baoyu Comic — Knowledge comics (知识漫画): educational, biography, tutorial"
sidebar_label: "Baoyu Comic"
description: "Knowledge comics (知识漫画): educational, biography, tutorial"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉漫画

知识漫画：用于教育、传记讲述或教程讲解。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/baoyu-comic` 安装 |
| 路径 | `optional-skills/creative/baoyu-comic` |
| 版本 | `1.56.1` |
| 创建者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `comic`、`knowledge-comic`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能运行时，智能体将以此作为操作指令。
:::

# 知识漫画创作工具

基于 [baoyu-comic](https://github.com/JimLiu/baoyu-skills) 为 Hermes Agent 的工具生态系统定制开发。

支持灵活搭配艺术风格与色调，创作原创知识漫画。

## 适用场景

当用户要求创建知识类/教育类漫画、传记漫画或教程漫画，或使用“知识漫画”、“教育漫画”或“Logicomix风格”等术语时，可触发此技能。用户需提供内容（文本、文件路径、URL或主题），并可选择性指定艺术风格、色调、布局、宽高比或语言。

## 参考图片处理方式

Hermes 的 `image_generate` 工具仅支持**提示词输入** — 它接收文本提示词和宽高比，然后返回图像 URL，**不支持**参考图片。当用户提供参考图片时，需先将其用于**提取文字描述的特征**，这些特征会被嵌入到每页的提示词中：

**输入处理**：若用户提供文件路径（或在对话中粘贴图片），则将其复制到 `refs/NN-ref-{slug}.{ext}` 文件中，与漫画输出结果一同保存以追溯来源。
- 提供了文件路径 → 复制至对应路径；未提供路径的粘贴图片 → 通过 `clarify` 功能询问用户路径，或口头描述风格特征作为文本替代方案。
- 无参考图片 → 跳过此步骤。

**参考图片的使用模式**（按参考类型）：

| 使用模式 | 效果 |
|-------|------|
| `style` | 提取风格特征（线条处理方式、纹理、氛围等），并添加到每页的提示词中 |
| `palette` | 提取十六进制颜色值，并添加到每页的提示词中 |
| `scene` | 提取场景构图或主题相关描述，并添加到对应的页面中 |

当存在参考图片时，需将相关信息**记录在每页提示词的前置信息部分**：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: style
    traits: "muted earth tones, soft-edged ink wash, low-contrast backgrounds"
```

角色设定的一致性由 `characters/characters.md` 文件中的**文本描述**（在步骤3中编写）决定，这些描述会被嵌入到每个页面的提示词中（步骤5）。步骤7.1中生成的可选PNG角色表仅用于人工审核，不会作为输入传递给 `image_generate` 工具。

## 选项设置

### 视觉风格参数

| 选项 | 取值 | 描述 |
|------|------|-------------|
| 艺术风格 | 线条清晰风（默认）、漫画风、写实风、水墨风、粉笔风、极简风 | 绘画风格/渲染技术 |
| 氛围基调 | 中性（默认）、温暖、戏剧化、浪漫、充满活力、复古、动作感 | 整体情绪/氛围 |
| 分镜布局 | 标准（默认）、电影感、紧凑型、高潮场景专用、混合布局、网络漫画风、四格布局 | 分镜排列方式 |
| 页面比例 | 3:4（默认，竖屏）、4:3（横屏）、16:9（宽屏） | 页面长宽比 |
| 输出语言 | 自动检测（默认）、中文、英文、日文等 | 输出语言 |
| 参考图片 | 文件路径 | 用于提取风格特征/配色方案的参考图像（不会传递给图像生成模型）。详情见上文[参考图像](#reference-images)部分。 |

### 部分工作流选项

| 选项 | 描述 |
|------|-------------|
| 仅生成分镜 | 仅生成分镜，跳过提示词和图像生成环节 |
| 仅生成提示词 | 生成分镜+提示词，跳过图像生成环节 |
| 仅生成图像 | 根据现有的提示词目录直接生成图像 |
| 重新生成指定页数 | 仅重新生成特定页面（例如输入`3`或`2,5,8`） |

详细说明请参阅：[references/partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/partial-workflows.md)

### 艺术风格、氛围基调与预设组合目录

- **艺术风格**（6种）：`ligne-claire`、`manga`、`realistic`、`ink-brush`、`chalk`、`minimalist`。完整定义见 `references/art-styles/<style>.md` 文件。
- **氛围基调**（7种）：`neutral`、`warm`、`dramatic`、`romantic`、`energetic`、`vintage`、`action`。完整定义见 `references/tones/<tone>.md` 文件。
- **预设组合**（5种）：除单纯的艺术风格+氛围基调外，还包含特殊规则：

  | 预设名称 | 对应组合 | 特点说明 |
  |--------|-----------|----------|
  | `ohmsha` | 漫画风 + 中性基调 | 使用视觉隐喻，无对话框，侧重道具展示 |
  | `wuxia` | 水墨风 + 动作感 | 包含气场特效、战斗场景，氛围浓郁 |
  | `shoujo` | 漫画风 + 浪漫基调 | 具有装饰性元素、细腻的眼部描写，充满浪漫情节 |
  | `concept-story` | 漫画风 + 温暖基调 | 拥有独特的视觉符号体系，注重角色成长弧线，对话与动作平衡得当 |
  | `four-panel` | 极简风 + 中性基调 + 四格布局 | 采用起承转合的结构设计，黑白画面搭配局部彩色，角色为火柴人造型 |

完整规则见 `references/presets/<preset>.md` 文件——选择预设时即可加载该文件。

- **兼容性矩阵**以及**内容特征→预设推荐**对照表均收录于 [references/auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/auto-selection.md) 文件。在步骤2中推荐组合前，请先仔细阅读该文件。

## 文件结构

输出目录格式为：`comic/{主题标签}/`
- 主题标签：由主题名称提取的2-4个单词，采用下划线连接（例如 `alan-turing-bio`）
- 若存在同名文件冲突，则在标签后添加时间戳（例如 `turing-story-20260118-143052`）

**目录内容**：
| 文件名 | 描述 |
|--------|-------------|
| `source-{slug}.md` | 保存的原始内容（下划线连接的标签与输出目录对应） |
| `analysis.md` | 内容分析报告 |
| `storyboard.md` | 包含分镜详细拆解的分镜脚本 |
| `characters/characters.md` | 角色设定说明 |
| `characters/characters.png` | 角色参考图（由 `image_generate` 生成并下载） |
| `prompts/NN-{cover\|page}-[slug].md` | 用于图像生成的提示词文件 |
| `NN-{cover\|page}-[slug].png` | 生成后的图像文件（由 `image_generate` 生成并下载） |
| `refs/NN-ref-{slug}.{ext}` | 用户提供的参考图像（可选，用于追溯内容来源） |

## 语言处理机制

**语言检测优先级**：
1. 用户明确指定的语言
2. 用户在对话中使用的语言
3. 原始内容的语言

**规则**：所有交互均使用用户指定的语言：
- 分镜大纲与场景描述
- 图像生成提示词
- 用户选择的选项及确认信息
- 进度更新、问题提示、错误信息、总结内容

技术术语仍保持英文形式。

## 工作流程

### 进度检查清单

```
Comic Progress:
- [ ] Step 1: Setup & Analyze
  - [ ] 1.1 Analyze content
  - [ ] 1.2 Check existing directory
- [ ] Step 2: Confirmation - Style & options ⚠️ REQUIRED
- [ ] Step 3: Generate storyboard + characters
- [ ] Step 4: Review outline (conditional)
- [ ] Step 5: Generate prompts
- [ ] Step 6: Review prompts (conditional)
- [ ] Step 7: Generate images
  - [ ] 7.1 Generate character sheet (if needed) → characters/characters.png
  - [ ] 7.2 Generate pages (with character descriptions embedded in prompt)
- [ ] Step 8: Completion report
```

### 流程

```
Input → Analyze → [Check Existing?] → [Confirm: Style + Reviews] → Storyboard → [Review?] → Prompts → [Review?] → Images → Complete
```

### 步骤概要

| 步骤 | 操作 | 关键输出 |
|------|------|----------|
| 1.1 | 分析内容 | `analysis.md`、`source-{slug}.md` |
| 1.2 | 检查现有目录 | 处理文件冲突 |
| 2 | 确认风格、主题、目标受众及审核要求 | 用户偏好设置 |
| 3 | 生成分镜脚本与角色设定 | `storyboard.md`、`characters/` 目录 |
| 4 | （如用户要求）审核大纲 | 用户确认通过 |
| 5 | 生成提示词 | `prompts/*.md` 文件 |
| 6 | （如用户要求）审核提示词 | 用户确认通过 |
| 7.1 | （如需要）生成角色表 | `characters/characters.png` 文件 |
| 7.2 | 生成页面图像 | `*.png` 文件 |
| 8 | 完成报告 | 工作总结 |

### 用户提问处理

请使用 `clarify` 工具来确认各项选项。由于该工具一次仅能处理一个问题，因此应先询问最关键的问题，再依次进行后续提问。完整的步骤2问题集详见 [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/workflow.md)。

**超时处理（非常重要）**：`clarify` 可能会返回“用户在规定时间内未给出回复。请凭您的判断选择默认值并继续操作。”——这**不代表**用户已同意全部采用默认设置。

- 应将此视为**仅针对该单个问题**的默认值处理。需继续按顺序询问步骤2中的其余问题；每个问题都需单独获得用户同意。
- 在后续消息中**明确向用户展示所采用的默认值**，以便其有机会进行更正。例如：“风格已默认为 ohmsha 预设（因 clarify 超时）。如需更改，请告知。”——若未告知用户，默认值与从未询问过无异。
- **切勿在出现一次超时后就直接将步骤2全部视为使用默认值**。如果用户确实缺席，那么五个问题都会得不到回复——但当他们回来后可以更正那些明确显示的默认值，而无法更正那些未被提及的默认值。

### 第7步：图像生成

所有图像渲染均需使用Hermes内置的 `image_generate` 工具完成。该工具的参数结构仅支持 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）；它**返回的是URL链接**，而非本地文件。因此，每张生成的页面或角色表都必须下载到输出目录中。

**提示词文件要求（强制）**：在调用 `image_generate` 之前，必须将每张图像的完整最终提示词写入 `prompts/` 目录下的独立文件中（文件命名规则为：`NN-{type}-[slug].md`）。该提示词文件是确保结果可复现的关键记录。

**宽高比映射规则**——分镜脚本中的 `aspect_ratio` 字段与 `image_generate` 的格式对应关系如下：

| 分镜比例 | `image_generate` 格式 |
|----------|----------------------|
| `3:4`、`9:16`、`2:3` | `portrait`（竖屏） |
| `4:3`、`16:9`、`3:2` | `landscape`（横屏） |
| `1:1` | `square`（正方形） |

**下载步骤**——每次调用 `image_generate` 后需执行以下操作：
1. 从工具返回的结果中获取URL链接。
2. 使用**绝对路径**下载图像数据，例如：<br>
   `curl -fsSL "<url>" -o /abs/path/to/comic/<slug>/NN-page-<slug>.png`
3. 在继续处理下一页之前，必须确认该路径下确实存在且文件非空。

**切勿依赖shell的当前工作目录持久性来设置 `-o` 路径**。终端工具的当前工作目录在不同批次之间可能会发生变化（如会话超时、`TERMINAL_LIFETIME_SECONDS` 设置、`cd`命令执行失败导致路径错误等）。使用 `curl -o relative/path.png` 的方式存在潜在风险：如果当前工作目录发生变动，文件可能会被下载到其他位置，而不会产生任何错误提示。**始终为 `-o` 参数提供完整的绝对路径**，或为终端工具设置 `workdir=<绝对路径>` 参数。2026年4月曾发生过一起事故：某部共10页的漫画中第06至09页被错误地下载到了仓库根目录，而非 `comic/<slug>/` 目录，原因是第3批次继承了第2批次的过时当前工作目录，导致 `curl -o 06-page-skills.png` 命令将文件写入错误目录。此后该智能体多次声称这些文件存在于本应存放的位置，但实际上并不存在。

**7.1 角色表生成**——当漫画为多页且包含重复出现的角色时，需生成角色表并保存为 `characters/characters.png`，其宽高比为横屏。对于简单的预设格式（如四格极简风格）或单页漫画，则无需生成此文件。在调用 `image_generate` 之前，必须先确保 `characters/characters.md` 文件已存在。该PNG文件是供用户直观审核角色设计的**展示用文件**，也可作为后续重新生成内容或手动修改提示词的参考——它并不直接用于驱动第7.2步的操作。页面的提示词实际上已在第5步根据 `characters/characters.md` 中的**文字描述**编写完成；`image_generate` 工具不支持以图像作为视觉输入。

**7.2 页面生成**——在调用 `image_generate` 之前，每页的提示词必须已存在 `prompts/NN-{cover|page}-[slug].md` 文件中。由于 `image_generate` 仅接受提示词作为输入，因此角色一致性是通过**在第5步将来自 `characters/characters.md` 的角色描述嵌入到每页的提示词中**来实现的。无论第7.1步是否生成了角色表，这一嵌入操作都会统一执行；PNG文件仅起到审核和重新生成时的辅助作用。

**备份规则**：在重新生成内容之前，需将现有的 `prompts/…md` 和 `…png` 文件重命名为带有 `-backup-YYYYMMDD-HHMMSS` 后缀的版本。

完整的逐步工作流程（包括内容分析、分镜制作、审核环节以及不同生成方案）详见：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/workflow.md)。

## 参考资料

**核心模板**：
- [analysis-framework.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/analysis-framework.md) —— 深度内容分析模板
- [character-template.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/character-template.md) —— 角色定义格式模板
- [storyboard-template.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/storyboard-template.md) —— 分镜脚本结构模板
- [ohmsha-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/ohmsha-guide.md) —— Ohmsha漫画风格指南

**风格定义**：
- `references/art-styles/` —— 绘画风格（线描风格、漫画风格、写实风格、水墨风格、粉笔风格、极简风格）
- `references/tones/` —— 色调风格（中性色调、暖色调、戏剧化色调、浪漫色调、活力色调、复古色调、动作风格）
- `references/presets/` —— 含有特殊规则的预设模板（ohmsha风格、武侠风格、少女风格、概念故事风格、四格风格）
- `references/layouts/` —— 页面布局类型（标准布局、电影感布局、密集布局、封面页布局、混合布局、网络漫画布局、四格布局）

**工作流程相关文档**：
- [workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/workflow.md) —— 完整的工作流程说明
- [auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/auto-selection.md) —— 内容特征自动识别机制
- [partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/baoyu-comic/references/partial-workflows.md) —— 部分流程选项说明

## 页面修改操作

| 操作类型 | 具体步骤 |
|----------|----------|
| **编辑** | **首先更新提示词文件** → 重新生成图像 → 下载新的PNG文件 |
| **添加页面** | 在指定位置创建新的提示词 → 生成并嵌入角色描述 → 重新编号后续页面 → 更新分镜脚本 |
| **删除页面** | 移除对应文件 → 重新编号后续页面 → 更新分镜脚本 |

**重要提示**：在修改页面内容时，务必**先更新提示词文件`prompts/NN-{cover|page}-[slug].md`**，然后再进行重新生成。这样才能确保所有更改都有记录并可复现。

## 常见问题与注意事项

- **图像生成时间**：每页大约需要10至30秒；若生成失败，系统会自动尝试重新生成一次。
- **必须下载图像**：需将 `image_generate` 返回的URL链接对应的图像下载为本地PNG文件——后续的处理流程以及用户的审核工作都需要在输出目录中看到实际文件，而非临时的URL链接。
- **使用绝对路径进行下载**：请始终为 `curl -o` 指定绝对路径，切勿依赖shell的当前工作目录在不同批次之间的持久性。否则可能会出现隐蔽问题：文件会被下载到错误目录，而后续在目标路径下执行 `ls` 命令时却什么也查找不到。详情请参见第7步的“下载步骤”。
- 对于涉及敏感公众人物的内容，应使用经过处理的替代形象。
- **必须完成步骤2的确认**——不可跳过此步骤。
- **步骤4和步骤6为可选操作**：仅当用户在步骤2中明确要求时才需执行。
- **步骤7.1的角色表生成**：建议在多页漫画中使用，简单预设格式则可选。该PNG文件仅用于审核和重新生成参考，而页面的提示词（已在第5步根据 `characters/characters.md` 中的文字描述编写）并不依赖该PNG文件。`image_generate` 工具不支持以图像作为视觉输入。
- **清除敏感信息**：在写入任何输出文件之前，务必扫描源内容，确保其中没有API密钥、令牌或其他敏感凭证。
