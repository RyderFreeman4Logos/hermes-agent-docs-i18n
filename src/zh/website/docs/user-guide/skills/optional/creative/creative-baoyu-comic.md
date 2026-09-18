---
title: "Baoyu Comic — Knowledge comics (知识漫画): educational, biography, tutorial"
sidebar_label: "Baoyu Comic"
description: "Knowledge comics (知识漫画): educational, biography, tutorial"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉漫画

知识漫画：用于教育、传记讲述或教程讲解。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/baoyu-comic` 安装 |
| 路径 | `optional-skills/creative\baoyu-comic` |
| 版本 | `1.56.1` |
| 创建者 | 宝玉 (JimLiu) |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `comic`、`knowledge-comic`、`creative`、`image-generation` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能激活后，智能体将依据此内容执行相应操作。
:::

# 知识漫画创作工具

基于 [baoyu-comic](https://github.com/JimLiu/baoyu-skills) 开发，专为 Hermes Agent 的工具生态设计。

支持通过灵活的画风与风格组合创作原创知识漫画。

## 适用场景

当用户要求创建知识类/教育类漫画、传记漫画或教程漫画，或使用“知识漫画”、“教育漫画”或“Logicomix风格”等术语时，可触发此技能。用户需提供内容（文本、文件路径、URL或主题），并可选择指定画风、风格基调、布局、宽高比或语言。

## 参考图片

Hermes的`image_generate`工具为**纯提示词驱动型**——它仅接受文本提示词和宽高比，然后返回图像URL，**不支持**接收参考图像。当用户提供参考图像时，需先从中**提取文字描述的特征**，这些特征会被嵌入到每个页面的提示词中：

**输入处理**：若用户提供了文件路径（或在对话中粘贴了图像），则予以接收。
- 文件路径 → 复制至`refs/NN-ref-{slug}.{ext}`目录中，与生成的漫画内容一同保存，以便追溯来源
- 未提供路径的粘贴图像 → 通过`clarify`功能询问用户路径，或直接以文字形式口头提取风格特征作为替代方案
- 无参考图像 → 跳过此步骤

**根据参考图像的不同，支持以下使用模式**：

| 使用模式 | 效果 |
|---------|------|
| `style` | 提取风格特征（如线条处理方式、纹理、氛围等），并将其添加到每个页面的提示词内容中 |
| `palette` | 提取十六进制颜色值，并将其添加到每个页面的提示词内容中 |
| `scene` | 提取场景构图或主体相关描述，将其添加到对应的页面中 |

**当存在参考图像时，需在每个页面的提示词前置信息中记录相关内容**：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: style
    traits: "muted earth tones, soft-edged ink wash, low-contrast backgrounds"
```

角色一致性由 `characters/characters.md` 文件中的**文本描述**（在步骤3中编写）决定，这些描述会被嵌入到每个页面的提示词中（步骤5）。步骤7.1中生成的可选PNG角色表仅用于人工审核，不会作为输入传递给 `image_generate` 功能。

## 选项

### 视觉风格参数

| 选项 | 取值 | 描述 |
|------|------|-------------|
| 艺术风格 | ligne-claire（默认）、漫画风、写实风、水墨风、粉笔风、极简风 | 艺术风格/渲染技术 |
| 氛围基调 | 中性（默认）、温暖、戏剧化、浪漫、活力十足、复古风、动作风 | 情绪/氛围 |
| 分格布局 | 标准（默认）、电影感、密集型、封面式、混合式、网络漫画风、四格布局 | 分格排列方式 |
| 页面比例 | 3:4（默认，竖屏）、4:3（横屏）、16:9（宽屏） | 页面长宽比 |
| 输出语言 | 自动（默认）、中文、英文、日文等 | 输出语言 |
| 参考图片 | 文件路径 | 用于提取风格/色调特征的参考图片（不会传递给图像模型）。详情请参见上文的[参考图片](#reference-images)部分。 |

### 部分流程选项

| 选项 | 描述 |
|------|-------------|
| 仅生成分镜 | 仅生成分镜，跳过提示词和图像生成 |
| 仅生成提示词 | 生成分镜+提示词，跳过图像生成 |
| 仅生成图像 | 从现有的提示词目录中直接生成图像 |
| 重新生成指定页面 | 仅重新生成特定页面（例如 `3` 或 `2,5,8`） |
详细信息：[references/partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/partial-workflows.md)

### 艺术风格、色调与预设目录

- **艺术风格**（6种）：`ligne-claire`、`manga`、`realistic`、`ink-brush`、`chalk`、`minimalist`。完整定义见 `references/art-styles/<style>.md`。
- **色调**（7种）：`neutral`、`warm`、`dramatic`、`romantic`、`energetic`、`vintage`、`action`。完整定义见 `references/tones/<tone>.md`。
- **预设**（5种）除了包含基础的艺术风格与色调组合外，还具备特殊规则：

  | 预设名称 | 对应组合 | 特点描述 |
  |--------|-----------|------|
  | `ohmsha` | manga + neutral | 使用视觉隐喻，不出现对话框，注重道具展示 |
  | `wuxia` | ink-brush + action | 包含气功效果、战斗场景以及浓郁的氛围感 |
  | `shoujo` | manga + romantic | 突出装饰性元素、眼睛细节以及浪漫情节 |
  | `concept-story` | manga + warm | 具有视觉符号系统，包含人物成长弧线，对话与动作比例均衡 |
  | `four-panel` | minimalist + neutral + 四格布局 | 采用起承转合的结构，以黑白与点缀色为主，角色为火柴人造型 |

  完整规则见 `references/presets/<preset>.md`——选择预设时会自动加载该文件。
- **兼容性矩阵**以及**内容特征 → 预设推荐**对照表位于 [references/auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/auto-selection.md)。在步骤2中进行组合推荐之前，请先查阅该文档。

## 文件结构

输出目录：`comic/{topic-slug}/`
- **slug**：由主题名称构成的2至4个单词的连字符分隔格式字符串（例如：`alan-turing-bio`）  
- **Conflict**：在原有字符串后附加时间戳（例如：`turing-story-20260118-143052`）

**目录结构**：
| 文件名 | 说明 |
|------|------|
| `source-{slug}.md` | 存储原始内容（连字符分隔的slug名称将与输出目录对应） |
| `analysis.md` | 内容分析报告 |
| `storyboard.md` | 包含分镜细节的故事板 |
| `characters/characters.md` | 角色定义文件 |
| `characters/characters.png` | 角色参考表（从`image_generate`功能生成） |
| `prompts/NN-{cover\|page}-[slug].md` | 用于图像生成的提示词文件 |
| `NN-{cover\|page}-[slug].png` | 生成后的图像文件（从`image_generate`功能下载） |
| `refs/NN-ref-{slug}.{ext}` | 用户提供的参考图片（可选，用于追溯内容来源） |

## 语言处理

**检测优先级**：
1. 用户明确指定的语言
2. 用户在对话中使用的语言
3. 原始内容的语言

**规则**：在所有交互中均使用用户输入的语言：
- 故事板大纲与场景描述
- 图像生成提示词
- 用户选择选项及确认信息
- 进度更新、问题提示、错误信息及总结内容

技术术语仍保留英文原貌。

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
| 1.2 | 检查现有目录 | 处理冲突问题 |
| 2 | 确定风格、核心主题、目标受众及审核需求 | 用户偏好设置 |
| 3 | 生成故事板与角色设定 | `storyboard.md`、`characters/` 目录 |
| 4 | （如用户要求）审核大纲 | 用户确认通过 |
| 5 | 生成提示词 | `prompts/*.md` 文件 |
| 6 | （如用户要求）审核提示词 | 用户确认通过 |
| 7.1 | （如需）生成角色资料表 | `characters/characters.png` 文件 |
| 7.2 | 生成页面图像 | 各种 `.png` 格式文件 |
| 8 | 完成报告 | 工作总结 |

### 用户提问

请使用 `clarify` 工具来确认各项选项。由于该工具每次仅能处理一个问题，因此请先提出最关键的问题，再依次进行后续提问。完整的步骤2相关问题集可见 [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/workflow.md)。

**超时处理（非常重要）**：如果 `clarify` 返回“用户在规定时间内未给出回复。请凭专业判断自行选择并继续操作。”——这并不意味着用户已同意使用默认设置。

- 请将此设置视为**仅针对该问题**的默认值。请继续按顺序提出第二步中的其余问题；每个问题都是一个独立的同意节点。
- 在后续消息中**以清晰可见的方式向用户展示默认值**，以便他们有机会进行更正。例如：“风格：已默认为 ohmsha 预设（因超时未明确选择）。如需更改，请告知。”——未被反馈的默认值与从未被询问过的情况并无区别。
- 一旦出现超时情况，**切勿将第二步简化为一次“使用所有默认值”的操作**。如果用户确实不在场，那么他们对全部五个问题都会保持未回答状态——但他们可以在返回后更正那些可见的默认值，而无法更正那些不可见的默认值。

### 第 7 步：图像生成

所有图像渲染均需使用 Hermes 内置的 `image_generate` 工具。该工具的架构仅接受 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）这两个参数；它**返回的是 URL 地址，而非本地文件**。因此，每张生成的页面或角色图都必须下载到输出目录中。

**提示词文件要求（强制）**：在调用 `image_generate` 之前，必须将每张图像的完整最终提示词写入 `prompts/` 目录下的独立文件中（文件命名规则为：`NN-{type}-[slug].md`）。该提示词文件即为结果可复现性的记录。

**宽高比映射**——故事板中的 `aspect_ratio` 字段与 `image_generate` 的格式对应关系如下：

| 分镜比例 | `image_generate` 格式 |
|------------------|-------------------------|
| `3:4`, `9:16`, `2:3` | `portrait`（竖屏） |
| `4:3`, `16:9`, `3:2` | `landscape`（横屏） |
| `1:1` | `square`（正方形） |

**下载步骤** — 每次调用 `image_generate` 后需执行：
1. 从工具返回的结果中获取 URL 地址。
2. 使用**绝对路径**下载图像数据，例如：  
   `curl -fsSL "<url>" -o /abs/path/to/comic/<slug>/NN-page-<slug>.png`
3. 在进入下一页之前，确认该路径下确实存在且文件非空。

**切勿依赖 shell 的当前工作目录来设定 `-o` 路径。** 终端工具的当前工作目录在不同批次之间可能会发生变化（如会话过期、`TERMINAL_LIFETIME_SECONDS` 设置限制，或 `cd` 操作失败导致进入错误目录）。使用 `curl -o relative/path.png` 的方式存在隐患：若当前工作目录发生变动，文件将会被下载到其他位置，而不会产生任何错误提示。**务必为 `-o` 参数提供完整的绝对路径**，或者为终端工具设置 `workdir=<绝对路径>` 参数。2026年4月曾发生过一起故障：在一部共10页的漫画中，第06至09页被错误地下载到了仓库根目录，而非 `comic/<slug>/` 目录，原因是第3批任务继承了第2批任务的过时当前工作目录，导致 `curl -o 06-page-skills.png` 命令写入到了错误的目录。随后，智能体多次误报称这些文件存在于实际不存在的位置。

**7.1 角色设定表** —— 当漫画为多页且包含重复出现的角色时，需生成该表格并保存至 `characters/characters.png`，图像比例为横向。对于简单的预设格式（如四格极简风格）或单页漫画，则无需生成此表。在调用 `image_generate` 前，必须确保 `characters/characters.md` 文件存在。生成的 PNG 图像是供**人类审阅使用的参考文件**（便于用户直观查看角色设计），同时也可作为后续重新生成图像或手动修改提示词的参考——它并不会直接影响第 7.2 步的流程。各页面的提示词已在第 5 步根据 `characters/characters.md` 中的**文字描述**编写完成；`image_generate` 不支持以图像形式作为输入。

**7.2 页面内容** —— 在调用 `image_generate` 之前，每个页面的提示词必须已存在于 `prompts/NN-{cover|page}-[slug].md` 文件中。由于 `image_generate` 仅能处理文本提示词，因此角色一致性是通过**在第 5 步将来自 `characters/characters.md` 的角色描述嵌入到每个页面的提示词中**来实现的。无论第 7.1 步是否生成了 PNG 图像表，这种嵌入操作都会统一执行；PNG 图像仅起到审阅或重新生成时的辅助作用。

**备份规则**：在重新生成之前，需将现有的 `prompts/…md` 和 `…png` 文件重命名为带有 `-backup-YYYYMMDD-HHMMSS` 后缀的文件。

完整的逐步工作流程（分析、故事板制作、审阅环节、多种生成方案）详见：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/workflow.md)。

## 参考资料

**核心模板**：
- [analysis-framework.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/analysis-framework.md) - 深度内容分析  
- [character-template.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/character-template.md) - 角色定义格式  
- [storyboard-template.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/storyboard-template.md) - 分镜结构  
- [ohmsha-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/ohmsha-guide.md) - Ohmsha漫画专属规范  

**风格定义**：  
- `references/art-styles/` - 绘画风格（线描、漫画、写实、水墨、粉笔风、极简风）  
- `references/tones/` - 色调风格（中性、温暖、戏剧化、浪漫、活力、复古、动作风）  
- `references/presets/` - 含特殊规则的预设模板（Ohmsha风格、武侠风、少女风、概念故事、四格漫画）  
- `references/layouts/` - 页面布局类型（标准型、电影感型、紧凑型、封面页、混合型、网络漫画、四格漫画）  

**工作流程**：
- [workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/workflow.md) - 完整的工作流程说明  
- [auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/auto-selection.md) - 内容特征分析  
- [partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\baoyu-comic/references/partial-workflows.md) - 部分工作流程选项  

## 页面修改

| 操作 | 步骤 |
|------|------|
| **编辑** | **首先更新提示词文件** → 重新生成图像 → 下载新的PNG文件 |
| **添加** | 在指定位置创建提示词 → 结合角色描述进行生成 → 重新编号后续页面 → 更新分镜脚本 |
| **删除** | 移除相关文件 → 重新编号后续页面 → 更新分镜脚本 |

**重要提示**：在更新页面时，务必先更新提示词文件（`prompts/NN-{cover|page}-[slug].md》），然后再进行图像生成。这样可以确保所有更改都有记录且可重复实现。  

## 常见问题与陷阱

- 图像生成：每页耗时10至30秒；失败时会自动重试一次  
- 请务必将`image_generate`返回的URL下载为本地PNG文件——后续工具处理及用户审核都需要输出目录中的实际文件，而非临时的URL链接  
- 使用绝对路径执行`curl -o`命令——切勿依赖批次处理过程中持续的Shell工作目录。否则可能会出现文件被误存到错误目录的情况，进而导致在目标路径下执行`ls`命令时无法找到文件。详见第7步“下载步骤”  
- 对于敏感的公众人物，应使用经过处理的替代形象  
- **必须完成第2步确认**——切勿跳过  
- **第4步和第6步为可选步骤**——仅当用户在第2步中提出要求时才需执行  
- **第7.1步：角色表**——多页漫画推荐使用，简单预设则可选。该PNG文件用于辅助审核和重新生成图像；而页面提示语（在第5步中编写）将依据`characters/characters.md`中的文本描述，而非PNG文件。`image_generate`功能不支持以图像作为视觉输入  
- **删除敏感信息**——在生成任何输出文件之前，需先扫描源内容，移除其中的API密钥、令牌或凭证等敏感数据
