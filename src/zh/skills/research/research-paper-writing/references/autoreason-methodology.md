# Autoreason：迭代优化方法论

本文档全面介绍了基于主观写作任务、编程竞赛以及四种模型层级上的实验结果所总结出的Autoreason迭代优化方法。当任何输出内容（论文草稿、实验脚本、分析报告或任务定义）都需要进一步改进时，均可参考本指南。

**来源**：[NousResearch/autoreason](https://github.com/NousResearch/autoreason) — “Autoreason：为何LLM迭代优化有时有效，有时却失败”

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
| **单次处理** | 高端模型、模板化任务、预算受限的情况 | 中端模型且质量上限较低 | 1次调用 |
| **评审与修改** | 具体技术需求（系统设计、规格说明） | 模型性能较弱（输出质量下降）、无约束的主观任务 | 2次调用 |
| **自主推理** | 中端模型、任务范围受限、存在真实权衡的情况 | 模型性能较弱（如Llama 8B）、高端模型+无约束场景 | 约6次调用 |
| **N选最佳** | 几乎不推荐使用 | 尤其是模型性能较弱时——效果甚至不如单次处理 | N次调用 |

### 各策略失败原因

| 策略 | 失败模式 | 原因机制 |
|----------|----------|----------|
| **单次处理** | 质量上限受限 | 无法在首次尝试后进行优化 |
| **评审与修改** | 质量逐渐下降 | 模型可能编造问题（阿谀奉承），每次迭代范围都会扩大，且从不主动改进 |
| **N选最佳** | 随机选择 | 缺乏有效的排序依据，样本越多，选出的结果越平庸 |
| **自主推理（无约束）** | 合成内容偏离 | 性能更强的模型生成的合成内容始终更受青睐，导致现有结果无法稳定 |

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

### 角色职责

每个角色都是一个**独立且全新的智能体**，彼此之间没有共享的上下文：

| 角色 | 输入 | 输出 | 核心规则 |
|------|-------|--------|----------|
| **评审者** | 任务 + 当前版本A | 问题列表 | 仅用于识别问题。不得提供解决方案或建议。 |
| **作者B** | 任务 + A + 评审意见 | 修改后的版本B | 针对每一条评审意见进行修改，并明确说明每项改动解决了哪个问题。 |
| **综合者** | 任务 + X + Y（随机标签） | 综合版本AB | 汇聚各版本的优点，而非寻求折中方案。 |
| **评审小组** | 任务 + A、AB、B（随机标签及顺序） | 优劣排名 | 对各版本进行从优到差的排序。评审者与具体版本无关联。 |

### 配置参数

| 参数 | 值 | 设计原理 |
|------|-----|----------|
| **收敛次数k** | 2 | k=1时收敛过早（94%的版本会在后续被替换）。k=2时可实现100%收敛，且质量趋于稳定。k=3时失败率为24%，成本增加一倍但质量无提升。 |
| **作者生成温度** | 0.7-0.8 | 有助于产生更多样化的修改方案 |
| **评审者生成温度** | 0.3 | 保证评估结果的稳定性 |
| **每轮评审人数** | 3 | 在单次处理成本与评估稳定性之间取得平衡 |
| **最终评估人数** | 7 | 提高最终对比的统计可靠性 |
| **最大token数** | 4096 | 标准值；长文（如论文）可使用8192 |
| **评审者思维模式** | 思考链 | 在某些任务中可使收敛速度提升3倍。建议始终启用该模式。 |
| **平局处理规则** | 保守策略（保留当前版本） | 避免误判——只有当当前版本确实被超越时才视为失败 |
| **最大迭代次数** | 25次（受限值），50次（放宽限制） | 设置安全上限；大多数版本在10-15次迭代即可收敛 |

### 提示词模板

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

#### Judge（思维链模式）——务必始终使用此版本
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

| 基准类型 | 提示词内容 |
|----------|------------|
| **保守型** | “在保留现有有效内容的前提下进行最小化改进。不得添加新章节，也不得大幅扩展范围。” |
| **改进型** | “改进这份文档。”（无额外指导） |
| **严格批评型** | “对文档进行彻底评估并重写，修复所有发现的缺陷。” |
| **批评与修改型** | 第一步：“给出结构化的批评意见，列出具体的缺陷。”第二步：“针对每条批评意见进行修改。” |

---

## 评分方式：博尔达计数法

评委会对候选方案进行排名，根据排名给予相应分数：

| 名次 | 3个候选方案的得分 |
|------|-------------------|
| 第1名 | 3分 |
| 第2名 | 2分 |
| 第3名 | 1分 |

**分数汇总**：将所有评委的分数相加。得分最高者获胜。
**平局处理**：若出现平局，当前获胜者仍为赢家。

**示例**（3位评委）：
- 评委1：AB > A > B → AB得3分，A得2分，B得1分
- 评委2：A > AB > B → A得3分，AB得2分，B得1分
- 评委3：AB > B > A → AB得3分，B得2分，A得1分
- 总分：AB=8分，A=6分，B=4分 → AB获胜，成为新的冠军

**每位评委的随机化处理**：
- 候选方案标签随机分配（对于同一位评委，A可能被称作“提案X”，而另一位评委则称其为“提案Z”）
- 展示顺序也随机排列（AB可能出现在最前面或最后）
- 这些措施可避免因排名位置或标签带来的偏差

---

## 模型选择指南

### 各模型级别的实测结果

| 模型 | 自我推理获胜次数 | 自我推理平均博尔达分数 | 最佳基准方案 | 分数差值 | 推荐建议 |
|-------|------------------|----------------------|---------------|--------|----------|
| **Llama 3.1 8B** | 1/3 | 23.7 | 25.0（单一基准） | -1.3 | 不建议使用自我推理功能。该模型性能较弱，难以应对多样化的候选方案。 |
| **Gemini 2.0 Flash** | 2/3 | 25.0 | 20.0（单一基准） | +5.0 | 是不错的候选模型，能带来中等程度的提升效果。 |
| **Haiku 3.5** | 3/3 | **42.0** | 33.7（单一基准） | **+8.3** | **最佳候选模型**，得分完美。基准方案反而会降低文档质量。 |
| **Sonnet 4** | 3/5 | 27.8 | 22.4（批评与修改型基准） | +5.4 | 非常适合处理开放性任务。对于技术类任务，批评与修改型基准效果更佳。 |
| **Sonnet 4.6（无限制）** | 0/1 | 7.0 | 31.0（批评与修改型基准） | -24.0 | 无限制条件下切勿使用自我推理功能。 |
| **Sonnet 4.6（有限制）** | 2/3 | 29.0 | 27.0（改进型基准） | +2.0 | 仅建议在有明确范围限制时使用。 |

### 生成能力与评估能力之间的差距

核心观点在于：**自我推理功能的价值取决于模型在内容生成能力与自我评估能力之间的差距大小。**

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

**实用原则**：随着模型成本下降且性能提升，如今的顶尖模型明日便可能沦为中等水平。生成结果与评估标准之间的差距是结构性问题，而非暂时现象。应依据模型在能力曲线上的位置来选择相应的优化架构。

### 评判员选择

| 源模型 | 推荐评判员 | 理由 |
|-------|------------|------|
| Llama 8B | 不建议使用 Autoreason | 模型性能过弱 |
| Gemini Flash | Sonnet 4 | 跨模型评估有效 |
| Haiku 3.5 | Sonnet 4 | 强大的外部评估机制至关重要 |
| Haiku 3.5 | Haiku 3.5（同模型） | 仍然可行——即便评判员表现不佳，竞赛结构仍能带来价值（平均 Borda 分数分别为 20.7 和 18.3） |
| Sonnet 4 | Sonnet 4（同模型） | 在该层级，同模型评判员同样有效 |
| Sonnet 4.6 | Sonnet 4.6（同模型） | 仅限在设置范围约束的情况下使用 |

---

## 范围约束设计

### 为何范围约束能让 Autoreason 在受限任务中表现更好

同样的模型（Sonnet 4.6），在没有约束时排名**垫底**，而在加入范围约束后却能夺得**第一名**。这些约束限定了改进空间，从而防止了合成偏差的累积。

### 有效的约束类型

| 约束类型 | 示例 | 作用原理 |
|---------|------|----------|
| **固定事实** | “仅使用这 8 个数据点，不得添加其他内容” | 限制信息范围 |
| **固定输出格式** | “撰写 500 字的创业计划书”（而非“改进此内容”） | 明确完成标准 |
| **固定结构** | “必须包含恰好 4 个部分，每部分有 3 个编号项” | 防止结构偏差 |
| **固定修改范围** | “必须解决这 3 个评审意见” | 限定修改范围 |

### 无效的约束类型

| 约束内容 | 失败原因 | 实际后果 |
|---------|----------|----------|
| 仅限制字数 | 不属于有效范围约束 | 出现错误收敛——因长度问题被拒，而非质量问题 |
| “简洁表达” | 过于模糊 | 经过 2-3 轮迭代后被忽略 |
| “内容全面” | 实为反约束 | 容易导致范围扩大 |
| 完全不设约束 | 改进空间无限制 | 合成内容占主导，无法收敛 |

### 任务类别

| 任务类型 | Autoreason 是否有效 | 原因 |
|---------|-------------------|------|
| 需要权衡取舍的任务（策略、政策类） | 是 | 存在多种可行方案，可通过竞赛机制进行筛选 |
| 受限写作任务（创业计划书、备忘录、事后分析报告） | 大多有效（2/3） | 范围明确，评估标准清晰 |
| 模板填充类任务（事件事后分析） | 不有效 | 结构唯一，决策空间极小 |
| 竞赛编程 | 是 | 自带明确范围，测试套件可提供外部验证 |
| 开放式无约束任务 + 顶尖模型 | 不有效 | 存在合成偏差，无法收敛 |

---

## 失败类型分类

| 失败模式 | 发生条件 | 检测方法 | 证据 |
|---------|----------|----------|------|
| **自我修正不可靠** | 无外部评估信号 | 基准模型经过单次迭代后性能下降 | Haiku 模型基准：单次迭代平均分 33.7，多次迭代后降至 16.3 |
| **偏差/合成内容占主导** | 无范围约束 | 某模型得分低于 15%，另一模型组合占据主导 | Sonnet 4.6 无约束场景：模型 A 得分 12%，模型 A+B 组合得分超过 60% |
| **过度拟合于可见反馈** | 修正循环过浅（仅基于批评与建议） | 公开结果与私有结果差异过大 | 在复杂代码问题上，仅基于批评与建议的修正方式拟合度高达 32% |
| **无法收敛** | 评判流程出现故障 | 解析失败，有效评判员不足 3 个 | 混合评判组解析失败：需经过 11 轮以上迭代 |
| **模型性能过弱** | 生成内容多样性不足 | 所有候选结果相似度极高 | Llama 8B 仅在三分之一的任务中获胜 |

### 恢复策略

| 失败类型 | 恢复方法 |
|---------|----------|
| 无法收敛（出现偏差） | 为任务添加范围约束 |
| 无法收敛（评判流程故障） | 修复解析器，确保有 3 个有效评判员后再继续 |
| 迭代次数增加导致质量下降 | 改为单次迭代或添加约束 |
| 模型性能过弱 | 使用更强的模型进行生成，将性能较弱的模型用于低成本任务 |
| 过度拟合（代码问题） | 采用结构化分析步骤，而不仅仅是依赖测试反馈 |

---

## 代码领域的适配策略

Autoreason 方法在处理代码任务与写作任务时需采取不同的适配方式：

### 写作领域
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

**核心区别**：该代码策略用测试套件评估（即客观的真实标准）取代了人工评审小组。结构化分析步骤（第二次调用）是推动问题恢复的关键——它要求在尝试修复之前先分析方法失败的原因。

**实验结果**：问题恢复机制起到了重要作用。在初始阶段自动推理和单次处理均未能解决问题的案例中，自动推理的解决率为62%，而单次处理的解决率仅为43%（McNemar检验p值=0.041，Cohen’s h值=0.32）。

---

## 将自动推理应用于论文写作

本文本身也是通过自动推理进行优化的（见论文第8节）：

### 配置参数
- 模型：claude-opus-4
- 评审员：3名Opus模型评审员
- 增强功能：真实标准评估器（可访问实际实验数据）
- 最终结果：经过9次迭代后达成一致

### 论文优化的主要发现

1. **真实标准评估器不可或缺**：若无法获取真实数据，Opus模型会编造虚假的消融研究结果、伪造置信区间、使用错误的模型名称以及给出不准确的角色描述。而有了真实数据支持后，评估器在第一次迭代就能识别出所有这些问题。

2. **评审小组的完整性至关重要**：其中一名评审员的解析器出现故障（Gemini输出格式不匹配），导致评审小组从3人缩减为2人。这使得问题在11次以上迭代中都无法解决。一旦恢复到3名正常工作的评审员，同样的问题仅需2次迭代即可解决。出现故障的评审员并非只是增加噪声，而是会破坏系统的平衡状态。

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
| 单次迭代 | 1 | 1 | 1 | 1倍 |
| N次最佳结果法 | N | 1 | N | Nx倍 |
| 评审与修改 | 2 | 15 | 30 | 30倍 |
| 自动推理（循环式） | 约6次 | 10-15次 | 60-90次 | 60-90倍 |
| 自动推理（含最终评估） | 约6次 + 7次 | 10-15次 + 1次 | 67-97次 | 约80倍 |

**成本与质量的权衡**：自动推理方法每轮的计算量约为其他方法的6倍，且通常需要更多轮次才能完成。这是一种典型的权衡——即用更高的计算成本来换取更优的评估质量。在资源受限、使用中等性能模型的任务中，这种权衡带来的收益显著；而在资源充足、使用顶尖性能模型的任务中，则会出现负面效果。

**思维链评审员可降低成本**：1名思维链评审员的评估质量可媲美3名普通评审员，同时仅需约40%的成本。建议始终使用思维链评审员。
