---
title: "Creative Ideation — Generate ideas via named methods from creative practice"
sidebar_label: "Creative Ideation"
description: "Generate ideas via named methods from creative practice"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 创意构思

通过创意实践中的特定方法来生成创意点子。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/creative-ideation` 安装 |
| 路径 | `optional-skills/creative/creative-ideation` |
| 版本 | `2.1.0` |
| 创建者 | SHL0MS |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `创意`, `构思`, `头脑风暴`, `方法`, `灵感` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# 创意构思

一个涵盖各领域的创意方法库。首先分析用户的需求状况，匹配对应的方法，再加以应用，最终生成具体且富有新意的成果。这些方法均为工具——需根据具体情况选择最合适的工具，而非全部使用。

## 适用场景

任何开放式的问题或需要选择的情况：“我想创造/构建/撰写/开始某件事”、“我陷入了僵局”、“给我一些灵感”、“让这个更奇特一点”、“帮我做选择”、“我需要发明X”、“给我一个研究课题”。

## 运行规则

1. **约束条件与明确方向是创造力的核心。** 没有约束则缺乏方向，没有方向则无法形成具体形态。这些方法能同时提供两者。
2. **拒绝前三个生成的点子。** 它们质量较差。需反复生成、舍弃后再重新生成。详情请参阅 `references/anti-slop.md`。
3. **除非用户另有要求，否则每次回复仅使用一种方法。** 不要叠加多种方法。
4. **具体性优于抽象性。** 应使用真实的专有名词、真实的材料与真实的运作机制。“一个用于X的应用程序”属于模糊表述；而“一个200行长的CLI工具，当Z发生时能输出Y”则更具方向性。仅提及技术栈并非具体表现——需明确具体的运作机制。
5. **奇特的同时也要具备可行性。** 破除常规是目标，但若某个点子虽然奇特，却缺乏实际背景、运作机制或存在依据，那它本身就属于失败案例。每组生成的点子中至少应包含一个真正*现在即可构建/实施*的方案——即虽不寻常但有现实基础，并且具备明确的第一个行动步骤。不要为了追求新奇而牺牲实用性。
6. **需注明所使用的方法及其发明者。** 明确归属能增强方法的严谨性。
7. **一旦用户选定某个方法，即应着手实现它。** 用户做出选择后不要再继续生成其他点子。

## 路由机制 —— 四步流程

在生成任何输出之前，必须先完成此步骤。若路由失败，生成的点子质量将很差。

如果表述更简洁，可省略对路由步骤的说明，但**绝不能以牺牲每个点子的深度为代价**：每个点子的具体运作机制、与用户情境的关联以及真实的失败可能性，才是决定输出质量的关键因素——它们并非临时框架，不可删减。

### 第一步 —— 从提示语中提取三个信号

**阶段** —— 用户当前处于哪个阶段？

| 阶段 | 指标 |
|---|---|
| **构思阶段** | “给我一个点子”、“我该做什么”、“给我一些灵感”——尚未形成具体想法 |
| **扩展阶段** | “还有别的吗”、“类似这样的更多”、“给我一些变体”——已有一个基础想法 |
| **选择阶段** | “帮我做选择”、“我该选哪个”、“我有这些选项” |
| **破局阶段** | “我陷入了僵局”、“进展受阻”、“一直在重复同样的思路”、“毫无新意”——已有相关素材 |
| **颠覆阶段** | “让这个更奇特一点”、“不要那么常规”、“这太安全了” |
| **优化阶段** | “这样还行，但缺少点什么”、“感觉还不够完善” |
| **综合阶段** | “我有一堆笔记/访谈记录/观察结果” |

**领域** —— 用户正在创造/处理的内容属于哪个领域？

| 领域 | 指标 |
|---|---|
| **文本** | 小说、散文、诗歌、歌词、剧本、广告文案 |
| **作品** | 视觉艺术、音乐、声音、表演、装置艺术、雕塑 |
| **制品** | 软件、硬件、机械装置、设备 |
| **系统** | 组织、公民团体、机构、生态系统、社区 |
| **个人** | 生活决策、职业规划、个人实践 |
| **研究** | 论文、学位论文、学术课题 |
| **产品** | 商业项目、市场方案、服务设计 |

**具体性程度** —— 提示语中包含多少约束条件？

| 程度 | 指标 |
|---|---|
| **无约束** | “我好无聊”、“给我一些灵感”——既未明确领域，也未指定项目 |
| **仅明确领域** | “我想写点什么”——知道所属领域，但未指定具体项目 |
| **已明确项目** | “我正在做具体的X项目” |
| **存在具体问题** | “在X领域中，我有这样的具体难题” |

### 第二步 —— 应用优先级更高的规则

这些优先级规则会覆盖常规的路由机制：

- **情绪信号** —— 用户提到“奇特”、“奇怪”、“令人惊讶”、“不要那么常规”、“更有趣” → 无论属于哪个领域，均使用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md` 中的方法。
- **用户指定了某种方法** —— 直接使用该方法。
- **用户请求推荐方法**（“用哪种方法？”） → 提供2–3种候选方法，每一种用一句话简要说明，再询问用户选择哪一种。不要擅自默认。
- **属于低质量生成的高风险领域** —— 如“AI相关点子”、“初创公司点子”、“习惯追踪工具”、“提升效率/健康/健身/饮食/旅行类应用” → 强制使用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md`，而非常规方法。需拒绝前**5个**生成的点子，而非3个。

### 第三步 —— 先按阶段路由，再按领域分类

**按阶段路由（适用于所有领域）：**

| 阶段 | 默认路由路径 |
|---|---|
| 构思阶段 + 无具体约束 | `references/full-prompt-library.md` 的 **通用** 部分（约束条件处理模块） |
| 构思阶段 + 已明确领域 | 按对应领域进行路由（见下表） |
| 扩展阶段 | `references/methods/scamper.md` |
| 选择阶段 | `references/methods/premortem-and-inversion.md`（若需寻求积极方向，则使用 `references/methods/compression-progress.md`） |
| 破局阶段 | `references/methods/oblique-strategies.md` |
| 颠覆阶段 | `references/methods/lateral-provocations.md`（若仍不合适，则使用 `references/methods/pataphysics.md` 作为备选） |
| 优化阶段（文本类） | `references/methods/defamiliarization.md` |
| 优化阶段（其他类型） | `references/methods/creative-discipline.md`（Tharp的创意法则） |
| 综合阶段 | `references/methods/affinity-diagrams.md` |
| 需要快速生成大量点子 | `references/methods/volume-generation.md` |

**按领域路由（当处于构思阶段且已明确领域时）：**

| 领域 | 默认路由路径 |
|---|---|
| 文本 —— 正式文体/诗歌 | `references/methods/oulipo.md` |
| 文本 —— 叙事类 | `references/methods/story-skeletons.md` |
| 文本 —— 有可重新组合的素材 | `references/methods/chance-and-remix.md` |
| 作品 —— 音乐、视觉艺术、表演类 | `references/methods/oblique-strategies.md` |
| 作品 —— 实体制作类/需要初始约束条件 | `references/full-prompt-library.md` 的 **实体/作品** 部分 |
| 制品 —— 需要初始约束条件 | `references/full-prompt-library.md` 的 **软件/制品** 部分 |
| 制品 —— 存在参数冲突的工程发明 | `references/methods/triz-principles.md` |
| 制品 —— 软件架构设计 | `references/methods/pattern-languages.md` |
| 制品 —— 有自然系统类相似点 | `references/methods/biomimicry.md` |
| 制品 —— 需要质疑现有假设 | `references/methods/first-principles.md` |
| 系统 —— 公民组织、企业机构类 | `references/methods/leverage-points.md` |
| 系统 —— 集体/参与式系统 | `references/full-prompt-library.md` 的 **社会/集体** 部分 |
| 个人 —— 生活决策、职业规划、学习方向选择 | `references/methods/derive-and-mapping.md` |
| 研究 —— 选择研究课题 | `references/methods/compression-progress.md` |
| 研究 —— 解决已知问题 | `references/methods/polya.md` |
| 产品 —— 商业项目、服务设计 | `references/methods/jobs-to-be-done.md` |
| 需要打破常规思维/寻找类比 | `references/methods/analogy-and-blending.md` |

### 第四步 —— 处理歧义与矛盾情况

- **存在多条合理路径** → 选择最符合用户原始表述的路径。不要为了显得高明而选择最有趣的方法。
- **确实存在歧义** → 只询问一个澄清问题，不要擅自猜测。例如：“您是想要生成新的点子，还是从已有的点子中选择？” / “这是用于小说、散文，还是其他类型的内容？”
- **不同信号相互矛盾**（例如“奇特的初创公司点子”——产品领域 + 奇特的情绪） → **明确叠加两种方法**。需说明所采用的方法组合：“对于产品框架部分使用 `jobs-to-be-done` 方法，同时运用 `lateral-provocations` 方法来打破常规思维模式。”
- **没有匹配的路径** → 采用约束条件处理机制（`references/full-prompt-library.md`）作为安全备选。
- **再次提出相同问题** → 更换使用方法。不同的方法会带来不同的点子生成结果。

### 防止默认行为的检查（在生成前执行）

- 正准备输出“以下是5个点子：”或单纯的数字列表？→ 停下。先选择一个方法。
- 正准备直接采用通用的LLM式头脑风暴模式？→ 停下。先按照上述步骤选择路径。
- 生成的输出看起来像未经路由处理的LLM会产生的内容？→ 路由失败，需重新处理。

默认的LLM模式正是该技能旨在替代的。如果在不经过路由处理的情况下直接生成内容，就等于违背了该技能的设计初衷。关于更多边缘情况（如情绪信号、方法叠加、不良模式等），请参阅 `references/heuristics.md`。

## 输出格式

对于采用约束条件处理机制的默认路径：

```
## Constraint: [Name] — from [Source]
> [The constraint, one sentence]

### Ideas

1. **[One-line pitch]**
   [2-3 sentences — what specifically is made, why it's interesting]
   ⏱ [weekend/week/month]  •  🔧 [stack/medium/materials]

2. ...
3. ...
```

对于其他方法，则需遵循该方法所规定的格式（TRIZ用于生成矛盾分析；OuLiPo用于生成受限文本；Oblique Strategies则输出一张应用卡片及后续步骤）。切勿强行将所有方法都套入约束模板中。

**无论采用何种方法，每组创意都需满足以下要求：**
- 明确标注所使用的方法。在“平庸地形”模式下，还需列出那些被你否决的显而易见创意。
- 为每个创意详细说明其具体运作机制，以及其潜在的失败模式、权衡因素，还有适用人群。唯有具备这样的深度，创意才能真正落地——注重实用性而非表面装饰。
- 至少要确定一个**可行型**创意——即当前即可着手实施、虽非显而易见但确实存在明确第一步的创意。其余创意可以朝着更奇特的方向发展，但这个创意必须是真正可操作的。切勿让整组创意都流于奇怪却不可行。

## 文件结构

- `references/full-prompt-library.md` — 约束库，按领域分类（通用、软件、物理、社会、列表）。当设置 SPECIFICITY=NONE 时使用的默认路径。
- `references/method-catalog.md` — 每种方法的一行概要说明及适用场景。
- `references/heuristics.md` — 针对边缘情况的扩展决策树。
- `references/anti-slop.md` — 防止创意平庸化的规则，需应用于所有输出结果。
- `references/exercises.md` — 定时练习任务（5分钟/30分钟/1小时/每日/每周）。
- `references/methods/` — 包含22种命名方法，每个方法对应一个文件，只需加载当前正在使用的方法对应的文件即可。

## 出处说明

约束调度核心功能改编自 [wttdotm.com/prompts.html](https://wttdotm.com/prompts.html)。各方法则源自相应方法文件中引用的原始资料。
