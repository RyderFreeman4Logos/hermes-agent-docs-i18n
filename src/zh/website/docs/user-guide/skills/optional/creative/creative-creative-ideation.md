---
title: "Creative Ideation — Generate ideas via named methods from creative practice"
sidebar_label: "Creative Ideation"
description: "Generate ideas via named methods from creative practice"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 创意构思

通过创意实践中的各类方法来生成创意点子。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/creative-ideation` 安装 |
| 路径 | `optional-skills/creative\creative-ideation` |
| 版本 | `2.1.0` |
| 开发者 | SHL0MS |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `创意`, `构思`, `头脑风暴`, `方法`, `灵感` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将以此作为操作指令。
:::

# 创意构思

涵盖各领域的创意构思方法库。首先分析用户所处的情境，匹配相应的方法并加以应用，最终生成具体且富有新意的成果。这些方法都是工具——请根据实际情况选择最合适的方法，无需全部使用。

## 适用场景

任何需要开放式生成或筛选答案的问题，例如：“我想创造/构建/撰写/启动某样东西”、“我遇到了瓶颈”、“给我一些灵感”、“让这个变得更有趣”、“帮我做选择”、“我需要发明X”、“给我一个研究课题”。

## 运行规则

1. **约束加方向方能催生创意。**没有约束便无从推进，没有方向则难以成形。方法正是为二者提供支撑。  
2. **舍弃前三个想法。**它们都是劣质内容。不断生成、抛弃、再生成。详情请参阅 `references/anti-slop.md`。  
3. **除非特别要求，每次回复仅提供一个方案。**切勿堆砌多个方案。  
4. **具体优于抽象。**使用真实的专有名词、真实的材料与真实的机制。“一款用于X的应用”属于劣质内容；而“一个200行长的CLI工具，当Z发生时输出Y”则具有明确方向。仅提及技术栈并不算具体——需明确具体的实现机制。  
5. **奇特也需具备价值。**打破常规是目标，但若某个想法仅凭怪异而缺乏实际场景、机制或存在依据，那它本身就是一种失败模式。每组方案中至少应包含一个真正*当下即可构建/推进*的想法——虽非显而易见，但有现实基础且具备明确的第一个行动步骤。切勿为追求新奇而牺牲实用性。  
6. **需注明所用的方法及其发明者。**明确归属能增强内容的严谨性。  
7. **用户选定方案后，立即着手实现。**切勿在他们做出选择后仍继续生成内容。  

## 路由规划——四步流程  

在生成任何输出之前，请先完成此步骤。若路由规划出现失误，只会产生劣质内容。  

如果表述会更清晰，可省略对路由步骤的描述，但**绝不能以牺牲每个方案的深度为代价来压缩内容**：每个方案的具体实现机制、适用场景以及坦诚的失败可能性，才是决定输出质量的关键要素——它们并非临时框架，切勿删减。  

### 第一步——从提示语中提取三个关键信号  

**阶段**——用户当前处于哪个阶段？

| 阶段 | 提示词 |
|---|---|
| **生成阶段** | “给我一个灵感”，“我该创作什么”，“启发我”，尚未有具体想法 |
| **扩展阶段** | “还有什么”，“类似的内容”，“给我一些变体”——已有一个基础想法 |
| **选择阶段** | “帮我挑选”，“我该选哪个”，“我有这些选项” |
| **突破瓶颈阶段** | “我卡住了”，“进展停滞”，“陷入循环”，“内容陈旧”——已有素材 |
| **颠覆创意阶段** | “让它更奇特些”，“减少直观感”，“这样太安全了” |
| **精炼优化阶段** | “这样还行，但缺点什么”，“感觉不够完善” |
| **综合整合阶段** | “我有一堆笔记/访谈记录/观察结果” |

**领域** —— 用户正在创作或处理的内容是什么？

| 领域 | 提示词 |
|---|---|
| **文本** | 小说、散文、诗歌、歌词、剧本、广告文案 |
| **物品** | 视觉艺术、音乐、声音、表演、装置艺术、雕塑 |
| **人工制品** | 软件、硬件、机械结构、设备 |
| **系统** | 组织、社会机构、制度、生态系统、社群 |
| **自我** | 生活决策、职业规划、个人实践 |
| **研究** | 论文、学位论文、学术问题 |
| **产品** | 商业项目、市场策略、服务设计 |

**具体性** —— 提示词中的约束条件有多少？

| 等级 | 提示词 |
|---|---|
| **无约束** | “我好无聊”，“启发我”——既无明确领域也无具体项目 |
| **领域明确** | “我想写点东西”——知道所属领域，但尚未确定项目 |
| **项目明确** | “我正在做具体的X项目” |
| **问题明确** | “在X领域中存在具体的难题” |

### 第二步 —— 应用优先级覆盖规则（优先级最高，优先处理）

覆盖规则优先于路由规则：

- **情绪信号** — 用户表示“奇怪”、“奇异”、“令人惊讶”、“不那么明显”、“更有趣” → 无论所属领域如何，均引用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md`。
- **用户指定了某种方法** — 直接使用该方法。
- **用户请求方法推荐**（如“用哪种方法”） → 提供2–3个候选方法，每个方法用一句话简要说明，再询问用户应选用哪个，不得擅自默认。
- **高竞争领域** — 如“AI创意”、“创业点子”、“习惯追踪器”、“效率/健康/健身/饮食/旅游类应用” → 优先强制使用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md`，而非显而易见的方法。需拒绝前**5**个想法，而非3个。

### 第3步 — 先按阶段分类，再按领域划分

**按阶段分类（适用于所有领域）：**

| 阶段 | 默认路径 |
|---|---|
| 生成 + SPECIFICITY=NONE | `references/full-prompt-library.md` 的 **General** 部分（约束分配） |
| 生成 + 已知领域 | 按领域路由（见下表） |
| 扩展思路 | `references/methods/scamper.md` |
| 选择方案 | `references/methods/premortem-and-inversion.md`（若需正向思路则使用 `references/methods/compression-progress.md`） |
| 突破限制 | `references/methods/oblique-strategies.md` |
| 打破常规 | `references/methods/lateral-provocations.md`（备用方案：`references/methods/pataphysics.md`） |
| 文本优化 | `references/methods/defamiliarization.md` |
| 其他类型优化 | `references/methods/creative-discipline.md`（Tharp法则） |
| 综合整合 | `references/methods/affinity-diagrams.md` |
| 需快速生成大量内容 | `references/methods/volume-generation.md` |

**按领域路由（当已知生成领域时）：**

| Domain | Default route |
|---|---|
| TEXT — formal / poetry | `references/methods/oulipo.md` |
| TEXT — narrative | `references/methods/story-skeletons.md` |
| TEXT — has source material to remix | `references/methods/chance-and-remix.md` |
| OBJECT (music, visual, performance) | `references/methods/oblique-strategies.md` |
| OBJECT — physical maker / wants a starting constraint | `references/full-prompt-library.md` **Physical / object** section |
| ARTIFACT — wants a starting constraint | `references/full-prompt-library.md` **Software / artifact** section |
| ARTIFACT — engineering invention with parameter conflict | `references/methods/triz-principles.md` |
| ARTIFACT — software architecture | `references/methods/pattern-languages.md` |
| ARTIFACT — has natural-system analog | `references/methods/biomimicry.md` |
| ARTIFACT — accumulated assumptions to question | `references/methods/first-principles.md` |
| SYSTEM (civic, org, institutional) | `references/methods/leverage-points.md` |
| SYSTEM — collective / participatory | `references/full-prompt-library.md` **Social / collective** section |
| SELF (life, career, what-to-study) | `references/methods/derive-and-mapping.md` |
| RESEARCH — picking a question | `references/methods/compression-progress.md` |
| RESEARCH — attacking a known problem | `references/methods/polya.md` |
| PRODUCT (business, service) | `references/methods/jobs-to-be-done.md` |
| Need to break a frame / find analogy | `references/methods/analogy-and-blending.md` |

### 第4步 — 处理歧义与矛盾情况

- **存在多种合理路径** → 选择最贴近用户原始表述的方案，切勿为了显得高明而选用最“有趣”的方法。
- **确实存在歧义** → 只需提出一个澄清问题，切勿擅自猜测。例如：“您是要生成新点子，还是从已有点子中挑选？” / “这是用于创作小说、论文还是其他用途？”
- **不同信号相互矛盾**（例如，“奇怪的创业点子”这一要求同时涉及产品领域和“奇怪”的风格） → **明确组合使用两种方法**。需说明所采用的具体方式，例如：“使用`jobs-to-be-done`方法确定产品框架，再结合`lateral-provocations`方法打破常规思路。”
- **无匹配方案** → 采用约束分发机制（参考`references/full-prompt-library.md`）作为安全兜底方案。
- **重复提出相同问题** → 更换处理方法。不同的处理方法会带来不同的创意输出结果。

### 防默认模式检查（生成内容前执行）

- 即将输出“以下是5个点子：”或单纯的数字列表？→ 停下！先选定一种处理方法。
- 即将默认采用通用的LLM式头脑风暴模式？→ 停下！先选择上述某种路径。
- 输出内容看起来像未经路径引导的LLM会产生的结果？→ 路径引导失败，需重新操作。

默认的LLM模式正是该技能旨在替代的。若不经过路径引导直接生成内容，就等于违背了该技能的设计初衷。

关于更复杂的边缘情况（如风格信号、方法组合、反模式等），请参阅`references/heuristics.md`。

## 输出格式

对于采用约束分发机制的默认路径：

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

对于其他方法，则需遵循该方法所规定的格式（TRIZ用于生成矛盾分析；OuLiPo用于生成受限文本；Oblique Strategies则输出一张应用过的卡片及下一步行动）。无需强行将所有方法都套入该约束模板中。

**无论采用何种方法，每组创意都需满足以下要求：**
- 明确标注所使用的方法。在“平庸思维”场景下，还需列出那些被你否决的显而易见创意。
- 为每个创意详细说明其具体运作机制，以及其潜在的失败模式、权衡因素，以及适用人群。唯有具备这样的深度，创意才能真正落地——注重实用性而非仅作装饰。
- 至少有一个创意需被标记为**可行型**——即当前即可着手实施，虽非显而易见，但已有明确的第一步。其余创意可进一步探索那些奇特的方案，但这个可行型创意必须是真正具备操作性的。切勿让整组创意都流于奇怪却不可行。

## 文件结构

- `references/full-prompt-library.md` — 约束规则库，按领域分类（通用、软件、物理、社会、列表）。当设置 SPECIFICITY=NONE 时默认引用此文件。
- `references/method-catalog.md` — 每种方法的一行摘要及适用场景说明。
- `references/heuristics.md` — 针对边缘情况的扩展决策树。
- `references/anti-slop.md` — 防止平庸思维的规则，需应用于所有输出结果。
- `references/exercises.md` — 定时练习任务（5分钟/30分钟/1小时/每天/每周）。
- `references/methods/` — 包含22种命名方法，每个方法对应一个文件，仅需加载当前正在使用的那个。

## 出处标注

约束调度核心功能借鉴自 [wttdotm.com/prompts.html](https://wttdotm.com/prompts.html)；各功能方法则源自对应方法文件中引用的原始资料。
