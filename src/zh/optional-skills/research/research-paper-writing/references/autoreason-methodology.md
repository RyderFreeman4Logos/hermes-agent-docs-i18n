# Autoreason：迭代优化方法论

本文档提供了关于Autoreason迭代优化方法的完整参考，其内容基于在主观写作任务、编程竞赛以及四种不同模型层级上的实验结果总结而成。当任何输出内容（如论文草稿、实验脚本、分析报告或任务定义）需要逐步改进时，均可使用此方法。

**来源**：[NousResearch/autoreason](https://github.com/NousResearch/autoreason) — “Autoreason：为何迭代式LLM优化有效，又为何会失败”

---

## 策略选择指南

### 决策树

```
Is the task objectively verifiable (code, math, factual)?
├── YES → Does the model solve it on the first attempt?
│   ├── YES → Use single pass (no refinement needed)
│   └── NO → Use autoreason (structured analysis → reason-informed revision)
│
└── NO (subjective) → What model tier are you using?
    ├── Weak (Llama 8B, small models)
    │   → Single pass. Model too weak for refinement to help.
    │     Invest in generation quality, not iteration.
    │
    ├── Mid-tier (Haiku 3.5, Gemini Flash)
    │   → Autoreason with stronger judges. This is the sweet spot.
    │     Self-refinement DESTROYS weak model outputs — autoreason prevents this.
    │
    ├── Strong (Sonnet 4)
    │   → Autoreason for open-ended tasks. Wins 3/5.
    │     Critique-and-revise for concrete technical tasks (2/5).
    │
    └── Frontier (Sonnet 4.6, Opus)
        ├── Constrained scope? → Autoreason. Wins 2/3 constrained tasks.
        └── Unconstrained? → Critique-and-revise or single pass.
            Autoreason FAILS on unconstrained frontier tasks (comes last).
```

### 策略对比表

| 策略 | 最佳适用场景 | 应避免使用的场景 | 每次迭代计算量 |
|----------|--------------|------------------|----------------|
| **单次处理** | 高端模型、模板化任务、预算有限的情况 | 中端模型且质量上限较低 | 1次调用 |
| **批评与修改** | 具体技术需求（系统设计、规格说明） | 模型性能较弱（输出质量下降）、无约束的主观任务 | 2次调用 |
| **自主推理** | 中端模型、有约束的任务范围、存在真实权衡需求的任务 | 模型性能较弱（如Llama 8B）、高端模型且无约束场景 | 约6次调用 |
| **N选最佳** | 几乎不推荐使用 | 尤其是模型性能较弱的情况——效果甚至不如单次处理 | N次调用 |

### 各策略失败的原因

| 策略 | 失败模式 | 原因机制 |
|----------|----------|----------|
| **单次处理** | 质量上限受限 | 无法在首次尝试后进一步提升质量 |
| **批评与修改** | 质量逐渐下降 | 模型可能产生虚假问题（阿谀奉承式回答），任务范围每次迭代都在扩大，且从不主动改进 |
| **N选最佳** | 随机选择问题 | 缺乏有效的排序依据，样本越多，选出的选项质量越平庸 |
| **自主推理（无约束）** | 合成结果偏离目标 | 性能更强的模型生成的合成结果始终更受青睐，导致现有结果无法稳定下来 |

---

## 自主推理循环

### 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                    ITERATION LOOP                         │
│                                                           │
│   Incumbent A ──► Critic ──► Author B ──► Synthesizer     │
│       │                                      │            │
│       │              ┌───────────────────────┘            │
│       ▼              ▼                                    │
│      [A]           [AB]          [B]                      │
│       │              │            │                       │
│       └──────────────┼────────────┘                       │
│                      ▼                                    │
│              Judge Panel (blind)                          │
│                      │                                    │
│                      ▼                                    │
│                   Winner                                  │
│                      │                                    │
│              ┌───────┴───────┐                            │
│              ▼               ▼                            │
│         A wins k=2      B or AB wins                      │
│         consecutive?    → new incumbent                   │
│              │                                            │
│              ▼                                            │
│           CONVERGED                                       │
└──────────────────────────────────────────────────────────┘
```

### 角色定义

每个角色都是一个**独立且全新的智能体**，彼此之间没有共享上下文：

| 角色 | 输入 | 输出 | 核心规则 |
|------|-------|--------|----------|
| **评审者** | 任务 + 当前版本A | 问题列表 | 仅用于识别问题，不得提供解决方案或建议。 |
| **作者B** | 任务 + 版本A + 评审意见 | 修订后的版本B | 针对每一条评审意见进行修改，并明确说明每项改动解决了哪些问题。 |
| **综合者** | 任务 + X + Y（随机标签） | 综合版本AB | 汇聚各版本的优点，而非寻求折中方案。 |
| **评审小组** | 任务 + 版本A、AB、B（随机标签及顺序） | 排名结果 | 按质量从高到低进行排序，各角色与最终结果无关联。 |

### 配置参数

| 参数 | 值 | 设计原理 |
|------|-----|----------|
| **收敛轮次k** | 2 | k=1时收敛过早（后续有94%的版本会被替换）。k=2时可实现100%收敛，且质量趋于稳定。k=3时失败率高达24%，成本翻倍但质量无提升。 |
| **作者生成温度** | 0.7-0.8 | 促使生成更多样化的修订版本 |
| **评审者生成温度** | 0.3 | 确保评估结果的一致性 |
| **每轮评审人数** | 3 | 在单轮处理成本与评估稳定性之间取得平衡 |
| **最终评估人数** | 7 | 提高最终对比的统计效力 |
| **最大token数** | 4096 | 标准配置；长文（如论文）可使用8192 |
| **评审者思维模式** | 思考链 | 在某些任务上可使收敛速度提升3倍，建议始终启用该模式。 |
| **平局处理规则** | 保守策略（保留当前版本） | 避免误判——只有当版本A确实逊色时才会被替换 |
| **最大迭代轮次** | 25（受限值），50（应急值） | 设置安全上限；大多数任务在10-15轮即可收敛 |

### 提示词示例

#### 评审者
```
System: You are a critical reviewer. Your only job is to find real problems. 
Be specific and concrete. Do not suggest fixes.

User: Find real problems with this proposal. Focus on:
- Things that won't work as described
- Complexity that doesn't pay for itself
- Assumptions that are wrong
- Missing pieces
Do NOT propose fixes. Just the problems.
```

#### 作者 B
```
System: You are a senior consultant revising a proposal based on specific 
criticisms. Address each valid criticism directly. Do not make changes not 
motivated by an identified problem.

User: [TASK] + [VERSION A] + [CRITIC OUTPUT]
Revise to address these problems. For each change, state which problem it fixes.
```

#### 合成器
```
System: You are given two versions as equal inputs. Take the strongest elements 
from each and produce a coherent synthesis. This is not a compromise.

User: [TASK] + [VERSION X] + [VERSION Y]
(labels randomized — synthesizer doesn't know which is incumbent)
```

#### Judge（思维链模式）——始终请使用此版本
```
System: You are an independent evaluator. Think carefully before deciding.

User: [TASK] + Three proposals. For each, think step by step:
1. What does it get right?
2. What does it get wrong or miss?
3. Are numbers and claims defensible?
4. Is detail appropriate or bloated?
After reasoning, rank all three.
RANKING: [best], [second], [worst]
```

#### 基准提示词（用于对比实验）

| 基准类型 | 提示词 |
|----------|--------|
| **保守型** | “在保留现有有效内容的前提下进行最小化改进。不得新增章节或大幅扩展范围。” |
| **改进此内容** | “改进这份文档。”（无进一步指导） |
| **严厉批评型** | “对内容进行严格评估并重写，修正所有发现的缺陷。” |
| **批评与修改** | 第一步：“给出结构化的批评意见，列出具体的缺陷。”第二步：“针对每项批评进行修改。” |

---

## 评分方式：博尔达计数法

评审员对候选方案进行排名，根据排名位置给予分数：

| 名次 | 分数（3个候选方案） |
|------|----------------------|
| 第1名 | 3分 |
| 第2名 | 2分 |
| 第3名 | 1分 |

**总分计算**：所有评审员的得分相加。得分最高者获胜。
**平局处理**：当前胜出者（A）在平局中获胜。

**示例**（3名评审员）：
- 评审员1：AB > A > B → AB得3分，A得2分，B得1分
- 评审员2：A > AB > B → A得3分，AB得2分，B得1分
- 评审员3：AB > B > A → AB得3分，B得2分，A得1分
- 总分：AB=8分，A=6分，B=4分 → AB获胜，成为新胜出者

**每位评审员的随机化处理**：
- 候选方案标签随机分配（某位评审员可能将A称为“方案X”，而另一位称为“方案Z”）
- 展示顺序随机排列（AB可能出现在最前或最后）
- 这些措施可避免排名偏差和标签偏差

---

## 模型选择指南

### 各模型层级的实证结果

| 模型 | 自推理得分 | 自推理平均Borda值 | 最佳基准值 | 差距 | 建议 |
|-------|------------|-------------------|------------|------|------|
| **Llama 3.1 8B** | 1/3 | 23.7 | 25.0（单模型） | -1.3 | 不建议使用自推理功能。该模型能力较弱，难以应对多样化的任务场景。 |
| **Gemini 2.0 Flash** | 2/3 | 25.0 | 20.0（单模型） | +5.0 | 是不错的候选模型，性能提升较为显著。 |
| **Haiku 3.5** | 3/3 | **42.0** | 33.7（单模型） | **+8.3** | **最佳候选模型**，各项指标均达到满分。基准模型反而会降低模型质量。 |
| **Sonnet 4** | 3/5 | 27.8 | 22.4（C&R方法） | +5.4 | 非结构化任务中的优秀候选模型；C&R方法在技术类任务中表现更佳。 |
| **Sonnet 4.6（无约束）** | 0/1 | 7.0 | 31.0（C&R方法） | -24.0 | 无约束条件下切勿使用自推理功能。 |
| **Sonnet 4.6（有约束）** | 2/3 | 29.0 | 27.0（优化后） | +2.0 | 仅应在存在任务范围约束时使用。 |

### 生成能力与评估能力的差距

核心观点：**自推理功能的价值取决于模型在内容生成能力与自我评估能力之间的差距大小。**

```
Weak models (Llama 8B):
  Generation: Poor  |  Self-evaluation: Poor
  Gap: Small (both bad) → Autoreason can't help, no diverse candidates

Mid-tier models (Haiku, Flash):
  Generation: Decent  |  Self-evaluation: Poor
  Gap: LARGE → Autoreason's sweet spot. External eval bridges the gap.

Strong models (Sonnet 4):
  Generation: Good  |  Self-evaluation: Decent
  Gap: Moderate → Autoreason helps on 3/5 tasks

Frontier models (Sonnet 4.6):
  Generation: Excellent  |  Self-evaluation: Good
  Gap: Small → Simple methods suffice. Autoreason hurts on unconstrained tasks.
```

**实用原则**：随着模型成本降低且性能不断提升，如今的顶尖模型明日便可能沦为中等水平。生成结果与评估标准之间的差距是结构性问题，而非暂时现象。应根据模型在能力曲线上的位置来选择相应的优化架构。

### 评判者选择

| 模型名称 | 推荐评判者 | 理由 |
|---------|------------|------|
| Llama 8B | 不建议使用 Autoreason | 模型性能过弱 |
| Gemini Flash | Sonnet 4 | 跨模型评估方案可行 |
| Haiku 3.5 | Sonnet 4 | 强大的外部评估机制更为有效 |
| Haiku 3.5 | Haiku 3.5（同一模型） | 同样有效——即便没有优秀的评判者，竞赛机制仍能带来价值（平均 Borda 分数分别为 20.7 和 18.3） |
| Sonnet 4 | Sonnet 4（同一模型） | 在该层级，使用同一模型的评判者同样有效 |
| Sonnet 4.6 | Sonnet 4.6（同一模型） | 仅适用于有范围限制的任务 |

---

## 范围限制设计

### 为何范围限制能让 Autoreason 在受限任务中表现更好

同样的模型（Sonnet 4.6），在无范围限制时排名**最后**，而在加入范围限制后却能跃居**第一**。这些限制有效地约束了模型的优化空间，从而防止合成过程中的偏差不断累积。

### 有效的限制条件

| 约束类型 | 示例 | 有效原因 |
|----------|------|----------|
| **固定事实** | “仅使用这8个数据点，不得添加其他内容” | 限定信息范围 |
| **固定输出内容** | “500字的创业计划书”（而非“改进此内容”） | 明确完成标准 |
| **固定结构** | “恰好4个章节，每个章节包含3项编号内容” | 防止结构偏离 |
| **固定修改范围** | “必须解决这3项评审意见” | 限定修改范畴 |

### 无效约束

| 约束条件 | 失效原因 | 实际后果 |
|----------|----------|----------|
| 仅限制字数 | 不属于范围约束 | 出现错误收敛——因长度问题被拒，而非质量问题 |
| “简洁表达” | 过于模糊 | 经过2-3轮处理后被忽略 |
| “内容全面” | 属于反约束 | 容易导致范围扩大 |
| 完全无约束 | 改进空间无限 | 以综合生成为主，无法形成稳定结果 |

### 任务类别

| 任务类型 | 自动推理是否有效 | 原因 |
|----------|-------------------|-----|
| 存在真实权衡的任务（策略、政策制定） | 是 | 多种可行方案，可通过竞争机制选出最优 |
| 受约束的写作任务（创业计划书、备忘录、事后分析报告） | 大部分有效（2/3） | 范围明确，评估标准清晰 |
| 填写模板类任务（事件事后分析） | 无效 | 结构固定，决策空间极小 |
| 竞赛编程 | 有效 | 自然具有明确范围，测试套件可提供外部验证 |
| 开放式无约束+前沿模型 | 无效 | 综合生成易偏离目标，无法形成稳定结果 |

## 失败类型分类

| 失败模式 | 触发条件 | 检测方式 | 证据表现 |
|-----------|-----------|-----------|----------|
| **自我修正不可靠** | 无外部评估信号 | 基准性能在单次处理后下降 | Haiku基准：单次处理平均分33.7，多轮处理后降至16.3 |
| **漂移/合成内容占主导** | 任务范围无限制 | A模型胜率低于15%，AB模型占绝对优势 | Sonnet无限制模式下：A模型胜率12%，AB模型胜率超过60% |
| **过度拟合可见反馈** | 修订循环过浅（仅基于代码与结果对比） | 公开结果与私有结果差异过大 | 在复杂代码问题上，仅基于代码与结果对比的修正方式拟合度达32% |
| **无法收敛** | 评分流程出现故障 | 解析失败，有效评分者不足3人 | 混合评分组解析失败时，需进行11轮以上处理 |
| **模型性能过弱** | 生成内容多样性不足 | 所有候选结果相似度极高 | Llama 8B仅在三分之一的任务中获胜 |

### 恢复策略

| 失败类型 | 恢复方法 |
|---------|----------|
| 无法收敛（出现漂移） | 为任务添加范围限制 |
| 无法收敛（评分流程故障） | 修复解析器，确保有3名有效评分者后再继续处理 |
| 随迭代次数增加质量下降 | 改用单次处理方式或添加约束条件 |
| 模型性能过弱 | 使用更强大的模型进行生成，将较弱模型用于低成本任务 |
| 过度拟合（代码问题） | 采用结构化分析步骤，而不仅仅是依赖测试反馈 |

---

## 代码领域的适配策略

自动推理方法在处理代码任务与文本创作任务时的适配方式有所不同：

### 文本创作领域
```
Call 1: Critic (find problems in incumbent)
Call 2: Author B (revise based on critique)
Call 3: Synthesizer (merge A and B)
Calls 4-6: Judge Panel (3 blind judges rank A, B, AB)
```

### 代码领域（6次调用额度）
```
Call 1: Initial generation
Call 2: Structured analysis (5 points — NO CODE):
  - Problem analysis: what does the problem actually require?
  - Approach analysis: what approach did we use, is it correct?
  - Failure analysis: why did tests fail?
  - Alternative approaches: what else could work?
  - Edge cases: what inputs might break the solution?
Calls 3-6: Reason-informed revisions
  - Each revision must explain WHY it fixes the issue
  - Sees test results from public (visible) test cases
```

**核心区别**：代码策略采用测试套件评估（即客观的真实标准）来替代人工评审组。结构化分析步骤（第2次调用）是推动问题修复的关键——它在尝试解决方案之前，会强制要求分析方法失败的原因。

**实验结果**：问题修复机制起到了关键作用。在初始阶段自动推理与单次处理均无法解决问题的案例中，自动推理的解决率为62%，而单次处理的解决率仅为43%（McNemar检验p值=0.041，Cohen’s h值=0.32）。

---

## 将自动推理应用于论文写作

本文本身也是通过自动推理进行优化的（见论文第8节）：

### 配置参数
- 模型：claude-opus-4
- 评审员：3名Opus模型评审员
- 增强功能：真实标准评估器（可访问实际实验数据）
- 最终结果：经过9次迭代后达成一致

### 论文优化的主要发现

1. **真实标准评估器不可或缺**：若无法获取真实数据，Opus模型会编造虚假的消融研究内容、错误的置信区间、不正确的模型名称以及有偏差的角色描述。而有了真实数据支持后，评估器在第一次迭代就发现了上述所有问题。

2. **评审组完整性至关重要**：其中一名评审员的解析器出现故障（Gemini输出格式不匹配），导致评审组从3人缩减为2人。这使得问题在11次以上迭代中都无法解决。一旦恢复为3名正常工作的评审员，同样的问题在2次迭代后就得到了解决。出现故障的评审员并非只是增加干扰——它实际上会破坏系统的平衡状态。

### 论文优化的推荐配置

```
Critic prompt: "You are reviewing a research paper draft. You have access to the 
actual experimental results [GROUND TRUTH DATA]. Find factual errors, unsupported 
claims, hallucinated results, and structural problems. Do not suggest fixes."

Author B prompt: "Revise this paper draft to fix the identified problems. For each 
change, cite the specific problem it addresses. Do not add claims not supported by 
the provided experimental data."

Judge prompt (CoT): "Compare three versions of this paper. For each, evaluate:
1. Factual accuracy against the provided results
2. Clarity of the narrative and contribution
3. Whether claims are properly hedged and supported
4. Writing quality (concision, precision, no filler)
After reasoning, rank all three. RANKING: [best], [second], [worst]"
```

### 需提供的真实值数据
- 所有实验结果对应的 JSON 文件
- 统计检验的输出结果
- 每张表格及每幅图表中的原始数值
- 显示精确超参数的配置文件
- 用于生成结果的代码（以确保方法描述的准确性）

---

## 计算预算参考

| 方法 | 每轮调用次数 | 典型轮数 | 总调用次数 | 相对成本 |
|------|--------------|----------|------------|-----------|
| 单次遍历 | 1 | 1 | 1 | 1倍 |
| N 次最佳结果法 | N | 1 | N | Nx倍 |
| 评审与修改 | 2 | 15 | 30 | 30倍 |
| 自动推理（循环内执行） | 约6次 | 10-15次 | 60-90次 | 60-90倍 |
| 自动推理（含最终评估） | 约6次 + 7次 | 10-15次 + 1次 | 67-97次 | 约80倍 |

**成本与质量的权衡**：自动推理方法每轮的计算量约为其他方法的6倍，且通常需要更多轮次才能完成。这是一种真实的权衡——即用更高的计算成本换取更优的评估质量。在资源有限、使用中等性能模型的任务中，这种权衡带来的收益显著；而在资源充足、使用顶尖性能模型的任务中，则会出现负面效果。

**思维链评分员可降低成本**：1名思维链评分员的评估质量可与3名普通评分员相当，同时仅需约40%的成本。因此应始终优先使用思维链评分员。
