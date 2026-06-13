# 完整工作流程

生成知识漫画的完整流程。

## 进度检查表

复制并追踪进度：

```
Comic Progress:
- [ ] Step 1: Setup & Analyze
  - [ ] 1.1 Analyze content
  - [ ] 1.2 Check existing ⚠️ REQUIRED
- [ ] Step 2: Confirmation - Style & options ⚠️ REQUIRED
- [ ] Step 3: Generate storyboard + characters
- [ ] Step 4: Review outline (conditional)
- [ ] Step 5: Generate prompts
- [ ] Step 6: Review prompts (conditional)
- [ ] Step 7: Generate images
  - [ ] 7.1 Character sheet (if needed)
  - [ ] 7.2 Generate pages
- [ ] Step 8: Completion report
```

## 流程图

```
Input → Analyze → [Check Existing?] → [Confirm: Style + Reviews] → Storyboard → [Review Outline?] → Prompts → [Review Prompts?] → Images → Complete
```

## 第1步：设置与分析

### 1.1 分析内容 → `analysis.md`

读取源内容，必要时进行保存，随后进行深度分析。

**操作步骤**：
1. **保存源内容**（若尚未以文件形式存在）：
   - 若用户提供了文件路径：直接使用该路径
   - 若用户直接粘贴了内容：使用 `write_file` 函数将其保存到目标目录下的 `source-{slug}.md` 文件中，其中 `{slug}` 为用于输出目录的凯巴布式主题标识符
   - **备份规则**：若 `source-{slug}.md` 文件已存在，则在写入新内容前将其重命名为 `source-{slug}-backup-YYYYMMDD-HHMMSS.md`
2. 读取源内容
3. 按照 `analysis-framework.md` 中的框架进行**深度分析**：
   - 确定目标受众
   - 明确对读者的价值主张
   - 梳理核心主题与叙事潜力
   - 分析关键人物及其故事脉络
4. 识别源语言
5. **确定目标语言**：
   - 若用户已指定语言 → 使用该语言
   - 否则 → 使用检测到的源语言或用户当前使用的对话语言
6. 确定建议的页面数量：
   - 短篇故事：5-8页
   - 中等复杂度内容：9-15页
   - 完整传记：16-25页
7. 分析内容特征，为艺术风格、语气及排版提供参考建议
8. 使用 `write_file` 函数将分析结果保存到 `analysis.md` 文件中

**`analysis.md` 的格式要求**：包含 YAML 前置信息（标题、主题、时间范围、源语言、用户语言、宽高比、建议页面数、推荐艺术风格、推荐语气），以及针对目标受众、价值主张、核心主题、关键人物与故事脉络、内容特征、推荐方案等部分的详细内容。完整模板请参考 `analysis-framework.md`。

### 1.2 检查现有内容 ⚠️ 必做步骤

**在进入第2步之前必须执行此操作。**

首先检查输出目录是否存在（可通过 `test -d "comic/{topic-slug}"` 命令实现）。

**若目录已存在**，则使用 `clarify` 函数进行处理：

```
question: "Existing content found at comic/{topic-slug}. How to proceed?"
options:
  - "Regenerate storyboard — Keep images, regenerate storyboard and characters only"
  - "Regenerate images — Keep storyboard, regenerate images only"
  - "Backup and regenerate — Backup to {slug}-backup-{timestamp}, then regenerate all"
  - "Exit — Cancel, keep existing content unchanged"
```

保存结果并采取相应操作：
- **重新生成分镜脚本**：跳至步骤3，保留`prompts/`目录及所有图片
- **重新生成图片**：跳至步骤7，沿用现有提示词
- **备份后重新生成**：移动目录，从步骤2重新开始
- **退出**：立即终止当前工作流

---

## 步骤2：确认——风格与选项 ⚠️

**目的**：选择视觉风格，并决定在生成前是否需要审阅大纲。**请勿跳过此步骤。**

首先显示摘要信息：
- 已识别的内容类型与主题
- 提取的关键人物
- 检测到的时间跨度
- 建议的页数
- 语言（自动识别或用户指定）
- **推荐风格**：[艺术风格] + [语气风格]（基于内容特征确定）

请按优先级顺序，**每次仅使用`clarify`功能提出一个问题**：

> **超时处理（非常重要）**：如果`clarify`返回“用户在规定时间内未给出回复。请凭您的判断……”这样的提示，这仅代表针对当前问题的默认处理方式，并非用户全面同意。应继续提问，不得跳过步骤2。随后，在下一次向用户展示的反馈中，需明确列出所有采用的默认设置（例如：“默认风格→ohmsha，叙事重点→概念说明，目标受众→开发者（三个选项均超时未获回复）。如需调整，请告知。”）。若未提及的默认设置，对用户而言等同于“智能体从未提出过相关要求”。

### 问题1：视觉风格

如果系统推荐了预设风格（详见`auto-selection.md`），请先展示这些选项：

```
question: "Which visual style for this comic?"
options:
  - "[preset name] preset (Recommended) — [preset description] with special rules"
  - "[recommended art] + [recommended tone] (Recommended) — Best match for your content"
  - "ligne-claire + neutral — Classic educational, Logicomix style"
  - "ohmsha preset — Educational manga with visual metaphors, gadgets, NO talking heads"
  - "Custom — Specify your own art + tone or preset"
```

**预设模式与Art+Tone模式的区别**：预设模式除了包含Art+Tone模式的功能外，还额外应用了一些特殊规则。例如`ohmsha`模式会同时运用漫画风格、中性色调、视觉隐喻规则、角色设定规则，并且禁止出现对话框。而单纯的`manga + neutral`模式则不包含这些额外规则。

### 问题2：叙事重点

```
question: "What should the comic emphasize? (Pick the primary focus; mention others in a follow-up if needed)"
options:
  - "Biography/life story — Follow a person's journey through key life events"
  - "Concept explanation — Break down complex ideas visually"
  - "Historical event — Dramatize important historical moments"
  - "Tutorial/how-to — Step-by-step educational guide"
```

### 问题3：目标受众

```
question: "Who is the primary reader?"
options:
  - "General readers — Broad appeal, accessible content"
  - "Students/learners — Educational focus, clear explanations"
  - "Industry professionals — Technical depth, domain knowledge"
  - "Children/young readers — Simplified language, engaging visuals"
```

### 第4题：概要审核

```
question: "Do you want to review the outline before image generation?"
options:
  - "Yes, let me review (Recommended) — Review storyboard and characters before generating images"
  - "No, generate directly — Skip outline review, start generating immediately"
```

### 第5题：提示词审核

```
question: "Review prompts before generating images?"
options:
  - "Yes, review prompts (Recommended) — Review image generation prompts before generating"
  - "No, skip prompt review — Proceed directly to image generation"
```

**生成响应后**：
1. 根据用户的偏好更新 `analysis.md` 文件。
2. 根据第4题的回答设置 `skip_outline_review` 标志。
3. 根据第5题的回答设置 `skip_prompt_review` 标志。
4. → 转至步骤3。

---

## 步骤3：生成分镜脚本与角色设定

根据步骤2中确定的风格，创建分镜脚本及角色定义。

**加载风格参考文件**：
- 绘画风格：`art-styles/{art}.md`
- 氛围基调：`tones/{tone}.md`
- 若选择预设风格（如 ohmsha/wuxia/shoujo/concept-story/four-panel），还需加载 `presets/{preset}.md` 文件。

**生成内容**：

1. **分镜脚本**（`storyboard.md`）：
   - 包含 art_style、tone、布局方式及宽高比的 YAML 格式前言信息
   - 封面设计
   - 各页面的布局说明、分格细节以及视觉提示
   - **需使用用户在第1步中指定的语言**编写
   - 参考模板：`storyboard-template.md`
   - **若使用预设风格**：从 `presets/` 目录加载并应用相应预设规则

2. **角色定义**（`characters/characters.md`）：
   - 符合所选绘画风格的视觉描述（同样使用用户指定的语言）
   - 需包含用于后续图像生成的参考信息表提示
   - 参考模板：`character-template.md`
   - **若使用 ohmsha 预设风格**：将默认使用哆啦A梦系列角色（详见下表）

**Ohmsha 默认角色**（除非用户明确要求自定义角色，否则请使用这些角色）：

| 角色 | 名称 | 外貌描述 |
|------|------|----------|
| 学生 | 大雄 (Nobita) | 日本男孩，10岁，戴圆形眼镜，黑色头发从中分开，身穿黄色衬衫和蓝色短裤 |
| 导师 | 哆啦A梦 (Doraemon) | 圆形蓝色机器猫，拥有大大的白色眼睛、红色鼻子和胡须，腹部有4D口袋，还戴着金色铃铛，没有耳朵 |
| 挑战者 | 胖虎 (Gian) | 体格粗壮的男孩，五官粗犷，眼睛较小，穿着橙色衬衫 |
| 辅助角色 | 静香 (Shizuka) | 可爱的女孩，黑色短发，粉色连衣裙，面容温柔 |

以上即为标准的 ohmsha 风格角色。除非用户明确要求，否则请勿为 ohmsha 风格创建自定义角色。

**生成完成后**：
- 若 `skip_outline_review` 的值为 true → 跳过步骤4，直接进入步骤5
- 若 `skip_outline_review` 的值为 false → 继续执行步骤4

---

## 步骤4：审核分镜大纲（可选）

如果用户在步骤2中选择了“无需审核，直接生成”，则可跳过此步骤。

**目的**：让用户在最终生成前审核并确认分镜脚本及角色设定。

**展示内容**：
- 页面总数及整体结构
- 绘画风格与氛围基调的组合
- 逐页概览（封面 → 第1页 → 第2页……）
- 包含简要描述的完整角色列表

**可使用 `clarify` 功能**：

```
question: "Ready to generate images with this outline?"
options:
  - "Yes, proceed (Recommended) — Generate character sheet and comic pages"
  - "Edit storyboard first — I'll modify storyboard.md before continuing"
  - "Edit characters first — I'll modify characters/characters.md before continuing"
  - "Edit both — I'll modify both files before continuing"
```

**响应完成后**：
1. 若用户希望修改 → 等待用户编辑完毕后再进行提问
2. 若用户确认无误 → 进入步骤5

---

## 步骤5：生成提示词

为所有页面创建图像生成提示词。

**风格参考加载**：
- 读取 `art-styles/{art}.md` 文件以获取渲染指南
- 读取 `tones/{tone}.md` 文件以调整氛围与色彩
- 若使用预设方案：则读取 `presets/{preset}.md` 文件以获取特殊规则

**针对每个页面（封面页及内容页）**：
1. 按照既定的艺术风格与氛围指南编写提示词
2. **将角色描述直接嵌入提示词中**（从 `characters/characters.md` 中复制相关特征）——由于 `image_generate` 功能仅支持提示词输入，因此提示词文本是确保角色形象一致性的唯一方式
3. 使用 `write_file` 函数将提示词保存至 `prompts/NN-{cover|page}-[slug].md` 文件中
   - **备份规则**：若该文件已存在，则将其重命名为 `prompts/NN-{cover|page}-[slug]-backup-YYYYMMDD-HHMMSS.md`

**提示词文件格式**：
```markdown
# Page NN: [Title]

## Visual Style
Art: [art style] | Tone: [tone] | Layout: [layout type]

## Character Reference (embedded inline — maintain exact traits below)
- [Character A]: [detailed visual traits from characters/characters.md]
- [Character B]: [detailed visual traits from characters/characters.md]

## Panel Breakdown
[From storyboard.md - panel descriptions, actions, dialogue]

## Generation Prompt
[Combined prompt passed to image_generate]
```

**生成后**：
- 若 `skip_prompt_review` 的值为 `true` → 跳过第 6 步，直接进入第 7 步
- 若 `skip_prompt_review` 的值为 `false` → 继续执行第 6 步

---

## 第 6 步：审核提示词（可选）

如果用户在第 2 步选择了“否，跳过提示词审核”，则可**跳过此步骤**。

**目的**：让用户在图像生成前对提示词进行审核并确认。

**显示提示词概要表**：

| 页面 | 标题 | 关键元素 |
|------|-------|----------|
| 封面页 | [标题] | [主要视觉内容] |
| 第 1 页 | [标题] | [关键元素] |
| ... | ... | ... |

**可使用 `clarify` 命令**：

```
question: "Ready to generate images with these prompts?"
options:
  - "Yes, proceed (Recommended) — Generate all comic page images"
  - "Edit prompts first — I'll modify prompts/*.md before continuing"
  - "Regenerate prompts — Regenerate all prompts with different approach"
```

**响应完成后**：
1. 若用户希望编辑 → 等待用户编辑完毕后再进行提问
2. 若用户希望重新生成 → 回到第5步
3. 若用户确认 → 继续执行第7步

---

## 第7步：生成图像

使用第5/6步中确认好的提示词，调用 `image_generate` 工具。该工具仅接受 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）参数，并**返回一个URL地址**——它不支持参考图片，也不会在本地保存文件。每次调用后都必须执行下载操作。

**宽高比映射规则**：将故事板中的 `aspect_ratio` 值映射到工具支持的枚举值：

| 故事板宽高比 | `image_generate` 格式 |
|--------------|-------------------------|
| `3:4`、`9:16`、`2:3` | `portrait` |
| `4:3`、`16:9`、`3:2` | `landscape` |
| `1:1` | `square` |

**下载流程**（每次成功调用 `image_generate` 后执行）：
1. 从工具返回的结果中提取 `url` 字段
2. 将其下载到本地，例如使用命令 `curl -fsSL "<url>" -o comic/{slug}/<target>.png`
3. 检查文件是否非空（使用命令 `test -s <target>.png`）；若检查失败，则重新生成一次

### 7.1 生成角色参考表（可选）

对于包含重复出现角色的多页漫画，建议生成角色参考表，但**并非所有预设都要求必须生成**。

**何时生成**：
| 条件 | 操作 |
|------|------|
| 包含详细描述或重复出现角色的多页漫画 | 建议生成角色参考表 |
| 使用简化角色设计的预设（如四格极简风格） | 可跳过——提示词描述已足够 |
| 单页漫画 | 除非角色设计较为复杂，否则可跳过 |

**生成步骤**：
1. 使用 `characters/characters.md` 文件中的参考表提示词
2. **备份规则**：如果已存在 `characters/characters.png` 文件，则将其重命名为 `characters/characters-backup-YYYYMMDD-HHMMSS.png`
3. 调用 `image_generate` 并指定 `landscape` 格式
4. 下载返回的URL地址，将其保存为 `characters/characters.png`

**重要提示**：下载后的参考表仅用于**供用户直观审核角色设计**，同时也可作为后续重新生成图像或手动修改提示词的参考。它并不影响第7.2步的流程——因为页面的提示词早已在第5步根据 `characters/characters.md` 中的文本描述完成编写。由于 `image_generate` 工具无法接受图片作为视觉输入，因此文本描述是确保各页面设计一致性的唯一方式。

### 7.2 生成漫画页面

**在生成任何页面之前**：
1. 确认每个提示词文件都存在于 `prompts/NN-{cover|page}-[slug].md` 路径下
2. 确认每个提示词中都包含内嵌的角色描述（参见第5步）。由于 `image_generate` 工具仅支持文本提示词，因此提示词内容是确保设计一致性的唯一依据。

**页面生成策略**：每个页面的提示词都必须内嵌角色描述（这些描述取自 `characters/characters.md` 文件）。这一操作需在第5步完成，无论是否已通过7.1步生成了PNG参考表——PNG文件仅用于审核或重新生成时参考，绝不能作为生成页面的输入。

**内嵌提示词的示例**（位于 `prompts/01-page-xxx.md` 文件中）：

```markdown
# Page 01: [Title]

## Character Reference (embedded inline — maintain consistency)
- 大雄：Japanese boy, round glasses, yellow shirt, navy shorts, worried expression...
- 哆啦 A 梦：Round blue robot cat, white belly, red nose, golden bell, 4D pocket...

## Page Content
[Original page prompt body — panels, dialogue, visual metaphors]
```

**针对每一页（封面页及正文页）**：
1. 从 `prompts/NN-{cover|page}-[slug].md` 文件中读取提示词。
2. **备份规则**：若该页面存在图片文件，则将其重命名为 `NN-{cover|page}-[slug]-backup-YYYYMMDD-HHMMSS.png`。
3. 使用读取到的提示词及设定的宽高比调用 `image_generate` 函数进行图像生成。
4. 下载返回的图片链接，将其保存为 `NN-{cover|page}-[slug].png`。
5. 每次生成完成后反馈进度：“已生成 X/共 N 页：[页面标题]”

---

## 第 8 步：完成报告

```
Comic Complete!
Title: [title] | Art: [art] | Tone: [tone] | Pages: [count] | Aspect: [ratio] | Language: [lang]
Location: [path]
✓ source-{slug}.md (if content was pasted)
✓ analysis.md
✓ characters.png (if generated)
✓ 00-cover-[slug].png ... NN-page-[slug].png
```

## 页面修改

| 操作 | 步骤 |
|------|------|
| **编辑** | 更新提示词 → 重新生成图像 → 下载新的 PNG 文件 |
| **添加** | 在指定位置创建提示词 → 生成图像 → 下载 PNG 文件 → 为后续页面重新编号（NN+1）→ 更新故事板 |
| **删除** | 删除相关文件 → 为后续页面重新编号（NN-1）→ 更新故事板 |

**文件命名规则**：`NN-{封面|页面}-[唯一标识符].png`（例如：`03-page-enigma-machine.png`）
- 唯一标识符：采用下划线分隔的小写形式，需确保唯一性，且由页面内容决定
- 重新编号：仅修改前缀的 NN 数值，唯一标识符保持不变 |
