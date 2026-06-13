# 超出实证机器学习的论文类型

本指南旨在帮助撰写非标准类型的论文：理论论文、综述/教程类论文、基准/数据集论文以及立场声明类论文。不同类型的论文在结构、证据要求以及目标发表平台方面各有差异。

---

## 目录

- [理论论文](#theory-papers)
- [综述与教程类论文](#survey-and-tutorial-papers)
- [基准与数据集论文](#benchmark-and-dataset-papers)
- [立场声明类论文](#position-papers)
- [可复现性及重复实验论文](#reproducibility-and-replication-papers)

---

## 理论论文

### 何时撰写理论论文

当满足以下条件时，您的论文应归类为理论论文：
- 主要贡献为某个定理、界限、不可能性结论或形式化描述
- 实验仅作为补充验证手段，而非核心证据
- 该研究旨在深化理论理解，而非单纯追求最优性能指标

### 论文结构

```
1. Introduction (1-1.5 pages)
   - Problem statement and motivation
   - Informal statement of main results
   - Comparison to prior theoretical work
   - Contribution bullets (state theorems informally)

2. Preliminaries (0.5-1 page)
   - Notation table
   - Formal definitions
   - Assumptions (numbered, referenced later)
   - Known results you build on

3. Main Results (2-3 pages)
   - Theorem statements (formal)
   - Proof sketches (intuition + key steps)
   - Corollaries and special cases
   - Discussion of tightness / optimality

4. Experimental Validation (1-2 pages, optional but recommended)
   - Do theoretical predictions match empirical behavior?
   - Synthetic experiments that isolate the phenomenon
   - Comparison to bounds from prior work

5. Related Work (1 page)
   - Theoretical predecessors
   - Empirical work your theory explains

6. Discussion & Open Problems (0.5 page)
   - Limitations of your results
   - Conjectures suggested by your analysis
   - Concrete open problems

Appendix:
   - Full proofs
   - Technical lemmas
   - Extended experimental details
```

### 编写定理

**表述清晰的定理模板：**

```latex
\begin{assumption}[Bounded Gradients]\label{assum:bounded-grad}
There exists $G > 0$ such that $\|\nabla f(x)\| \leq G$ for all $x \in \mathcal{X}$.
\end{assumption}

\begin{theorem}[Convergence Rate]\label{thm:convergence}
Under Assumptions~\ref{assum:bounded-grad} and~\ref{assum:smoothness},
Algorithm~\ref{alg:method} with step size $\eta = \frac{1}{\sqrt{T}}$ satisfies
\[
\frac{1}{T}\sum_{t=1}^{T} \mathbb{E}\left[\|\nabla f(x_t)\|^2\right]
\leq \frac{2(f(x_1) - f^*)}{\sqrt{T}} + \frac{G^2}{\sqrt{T}}.
\]
In particular, after $T = O(1/\epsilon^2)$ iterations, we obtain an
$\epsilon$-stationary point.
\end{theorem}
```

**定理陈述的规则：**
- 明确列出所有假设（需编号并标注名称）
- 需给出正式的界，而不仅仅是“以 O(·) 的速率收敛”
- 添加通俗易懂的推论说明：“具体而言，这意味着……”
- 与已有界进行比较：“相较于[先前研究]中 O(·) 的界，该结果提升了……倍”

### 证明概要

在理论论文的正文中，证明概要是最为重要的部分。审稿人会通过它来判断你的工作是否具备真正的洞察力，还是仅仅是机械式的推导。

**优秀的证明概要结构：**

```latex
\begin{proof}[Proof Sketch of Theorem~\ref{thm:convergence}]
The key insight is that [one sentence describing the main idea].

The proof proceeds in three steps:
\begin{enumerate}
\item \textbf{Decomposition.} We decompose the error into [term A]
  and [term B] using [technique]. This reduces the problem to
  bounding each term separately.

\item \textbf{Bounding [term A].} By [assumption/lemma], [term A]
  is bounded by $O(\cdot)$. The critical observation is that
  [specific insight that makes this non-trivial].

\item \textbf{Combining.} Choosing $\eta = 1/\sqrt{T}$ balances
  the two terms, yielding the stated bound.
\end{enumerate}

The full proof, including the technical lemma for Step 2,
appears in Appendix~\ref{app:proofs}.
\end{proof}
```

**劣质证明草稿**：仅用略有不同的符号重新表述定理，或简单声明“该证明采用了标准方法”。 

### 完整证明见附录

```latex
\appendix
\section{Proofs}\label{app:proofs}

\subsection{Proof of Theorem~\ref{thm:convergence}}

We first establish two technical lemmas.

\begin{lemma}[Descent Lemma]\label{lem:descent}
Under Assumption~\ref{assum:smoothness}, for any step size $\eta \leq 1/L$:
\[
f(x_{t+1}) \leq f(x_t) - \frac{\eta}{2}\|\nabla f(x_t)\|^2 + \frac{\eta^2 L}{2}\|\nabla f(x_t)\|^2.
\]
\end{lemma}

\begin{proof}
[Complete proof with all steps]
\end{proof}

% Continue with remaining lemmas and main theorem proof
```

### 理论论文常见的误区

| 误区 | 问题 | 解决方案 |
|---------|------|----------|
| 假设过于强硬 | 使研究结果显得过于简单化 | 阐明哪些假设是必要的；证明下界 |
| 未与现有界限进行对比 | 审稿人无法评估研究的贡献价值 | 添加界限对比表 |
| 证明概要只是完整证明的简化版 | 无法体现核心思想 | 重点阐述1-2个关键思路，将具体推导过程放在附录中 |
| 无实验验证 | 审稿人会质疑其实际应用意义 | 增加合成实验来检验预测结果 |
| 符号使用不一致 | 令审稿人感到困惑 | 在“预备知识”部分列出符号说明表 |
| 存在简单证明时却采用过于复杂的证明方式 | 审稿人会怀疑其中存在错误 | 相比通用性，更应注重清晰性 |

### 理论论文的发表平台

| 发表平台 | 理论类论文接受率 | 备注 |
|---------|------------------|------|
| **NeurIPS** | 中等 | 重视具有实际应用价值的理论研究 |
| **ICML** | 高 | 拥有强大的理论研究板块 |
| **ICLR** | 中等 | 更青睐带有实证验证的理论研究 |
| **COLT** | 高 | 以理论研究为主的会议 |
| **ALT** | 高 | 专注于算法学习理论 |
| **STOC/FOCS** | 适合具有计算理论特色的研究成果 | 若研究内容主要为组合数学或算法层面 |
| **JMLR** | 高 | 无页数限制，适合篇幅较长的证明性论文 |

---

## 综述论文与教程论文

### 何时撰写综述论文

- 某个子领域已发展成熟，需要进行综合梳理
- 您发现了单篇论文未能揭示的各研究工作之间的关联
- 该领域的初学者缺乏合适的入门资料
- 自上一篇综述发表以来，该领域的研究格局发生了显著变化

**注意**：撰写综述需要深厚的专业功底。即使内容极为全面，但由领域外人士撰写的综述也难以把握细节，且可能对相关研究产生误判。

### 论文结构

```
1. Introduction (1-2 pages)
   - Scope definition (what's included and excluded, and why)
   - Motivation for the survey now
   - Overview of organization (often with a figure)

2. Background / Problem Formulation (1-2 pages)
   - Formal problem definition
   - Notation (used consistently throughout)
   - Historical context

3. Taxonomy (the core contribution)
   - Organize methods along meaningful axes
   - Present taxonomy as a figure or table
   - Each category gets a subsection

4. Detailed Coverage (bulk of paper)
   - For each category: representative methods, key ideas, strengths/weaknesses
   - Comparison tables within and across categories
   - Don't just describe — analyze and compare

5. Experimental Comparison (if applicable)
   - Standardized benchmark comparison
   - Fair hyperparameter tuning for all methods
   - Not always feasible but significantly strengthens the survey

6. Open Problems & Future Directions (1-2 pages)
   - Unsolved problems the field should tackle
   - Promising but underexplored directions
   - This section is what makes a survey a genuine contribution

7. Conclusion
```

### 分类体系设计

分类体系是调研报告的核心价值所在。它应当满足以下要求：

- **具有实际意义**：各类别应对应真实的方法学差异，而非随意划分的群体  
- **覆盖全面**：所有相关论文都应有归属之处  
- **尽可能互斥**：每篇论文仅属于一个主要类别  
- **名称清晰明确**：使用“基于注意力机制的方法”而非“第3类”  
- **便于可视化呈现**：附上分类体系示意图通常能极大提升可读性  

**以“大语言模型推理”主题调研为例的分类维度：**
- 按技术路线划分：思维链法、思维树法、自我一致性方法、工具使用方法  
- 按训练要求划分：仅通过提示训练、微调模型、基于强化学习的人类反馈优化  
- 按推理类型划分：数学推理、常识推理、逻辑推理、因果推理  

### 撰写标准

- **引用所有相关论文**——作者需核查自己的研究是否被纳入评估  
- **保持客观公正**——避免因个人偏好而否定某些方法  
- **进行综合分析而非简单罗列**——提炼出共性规律、权衡因素及未解问题  
- **添加对比表格**——即使是定性对比（如功能/特性清单）也可  
- **提交前及时更新**——检查自撰写开始后发表在arXiv上的新论文  

### 调研报告的发表渠道

| 发表平台 | 备注 |
|---------|------|
| **TMLR**（调研专题） | 专门接收调研类论文，无页数限制 |
| **JMLR** | 论文篇幅较长，学术认可度较高 |
| **《机器学习基础与趋势》** | 需邀请投稿，但也可主动申请 |
| **ACM计算调研系列** | 目标受众为更广泛的计算机科学领域读者 |
| **arXiv**（独立发布） | 无需同行评审，但若撰写精良则能获得较高关注度 |
| **会议教程** | 可在NeurIPS/ICML/ACL等会议上以教程形式展示，随后整理成论文发表 |

---

## 基准测试与数据集相关论文

### 何时撰写基准测试论文

- 现有基准测试无法衡量您认为重要的指标  
- 出现了新的能力，但目前尚无标准评估方法  
- 现有基准测试已趋于饱和（所有方法的得分均超过95%）  
- 您希望为某个发展较为分散的子领域建立统一的评估标准  

### 论文结构

```
1. Introduction
   - What evaluation gap does this benchmark fill?
   - Why existing benchmarks are insufficient

2. Task Definition
   - Formal task specification
   - Input/output format
   - Evaluation criteria (what makes a good answer?)

3. Dataset Construction
   - Data source and collection methodology
   - Annotation process (if human-annotated)
   - Quality control measures
   - Dataset statistics (size, distribution, splits)

4. Baseline Evaluation
   - Run strong baselines (don't just report random/majority)
   - Show the benchmark is challenging but not impossible
   - Human performance baseline (if feasible)

5. Analysis
   - Error analysis on baselines
   - What makes items hard/easy?
   - Construct validity: does the benchmark measure what you claim?

6. Intended Use & Limitations
   - What should this benchmark be used for?
   - What should it NOT be used for?
   - Known biases or limitations

7. Datasheet (Appendix)
   - Full datasheet for datasets (Gebru et al.)
```

### 评估标准

审稿人对基准测试的评估标准与方法类论文有所不同：

| 评估标准 | 审稿人检查的内容 |
|-----------|------------------|
| **评估新颖性** | 该指标是否衡量了现有基准测试未涉及的内容？ |
| **结构效度** | 该基准测试能否真正体现其所宣称的能力？ |
| **难度校准** | 难度既不能过低（导致结果饱和），也不能过高（导致性能出现随机波动） |
| **标注质量** | 一致性指标、标注人员资质以及相关标注指南 |
| **文档完整性** | 数据表、许可证及维护计划 |
| **可复现性** | 其他人能否轻松使用该基准测试？ |
| **伦理考量** | 偏见分析、用户同意机制以及敏感内容处理方式 |

### 数据集文档要求

请遵循《数据集数据表框架》（Gebru等人，2021年）：

```
Datasheet Questions:
1. Motivation
   - Why was this dataset created?
   - Who created it and on behalf of whom?
   - Who funded the creation?

2. Composition
   - What do the instances represent?
   - How many instances are there?
   - Does it contain all possible instances or a sample?
   - Is there a label? If so, how was it determined?
   - Are there recommended data splits?

3. Collection Process
   - How was the data collected?
   - Who was involved in collection?
   - Over what timeframe?
   - Was ethical review conducted?

4. Preprocessing
   - What preprocessing was done?
   - Was the "raw" data saved?

5. Uses
   - What tasks has this been used for?
   - What should it NOT be used for?
   - Are there other tasks it could be used for?

6. Distribution
   - How is it distributed?
   - Under what license?
   - Are there any restrictions?

7. Maintenance
   - Who maintains it?
   - How can users contact the maintainer?
   - Will it be updated? How?
   - Is there an erratum?
```

### 基准测试论文的发表平台

| 发表平台 | 备注 |
|-------|------|
| **NeurIPS 数据集与基准测试专题** | 专门设置的板块，最适合发布此类内容 |
| **ACL**（资源类论文） | 专注于自然语言处理领域的数据集 |
| **LREC-COLING** | 语言资源相关论文 |
| **TMLR** | 适合包含分析内容的基准测试论文 |

---

## 观点论文

### 何时撰写观点论文

- 您对该领域的未来发展有独到见解
- 您希望挑战某种普遍存在的假设
- 您希望基于分析结果提出研究规划
- 您发现了当前研究方法中存在的系统性问题

### 论文结构

```
1. Introduction
   - State your thesis clearly in the first paragraph
   - Why this matters now

2. Background
   - Current state of the field
   - Prevailing assumptions you're challenging

3. Argument
   - Present your thesis with supporting evidence
   - Evidence can be: empirical data, theoretical analysis, logical argument,
     case studies, historical precedent
   - Be rigorous — this isn't an opinion piece

4. Counterarguments
   - Engage seriously with the strongest objections
   - Explain why they don't undermine your thesis
   - Concede where appropriate — it strengthens credibility

5. Implications
   - What should the field do differently?
   - Concrete research directions your thesis suggests
   - How should evaluation/methodology change?

6. Conclusion
   - Restate thesis
   - Call to action
```

### 撰写标准

- **首先提出最有力的论点**——不要在首段含糊其辞  
- **诚实地回应反对意见**——优秀的立场论文会针对最有力的质疑进行回应，而非最微不足道的  
- **提供证据**——没有证据的立场论文不过是主观评论  
- **表述具体**——“该领域应采取X措施”比“还需要更多工作”更佳  
- **避免歪曲现有研究**——客观公正地描述对立观点  

### 适合发表立场论文的会议

| 会议 | 备注 |
|------|------|
| **ICML**（立场论文专题） | 设有专门的立场论文投稿渠道 |
| **NeurIPS**（研讨会论文） | 研讨会通常欢迎提交立场类论文 |
| **ACL**（主题论文） | 当你的观点与会议主题一致时 |
| **TMLR** | 接收论证充分的立场论文 |
| **CACM** | 面向更广泛的计算机科学受众 |

---

## 可复现性及重复实验论文

### 何时撰写可复现性论文

- 你尝试复现某项已发表的研究结果，并取得了成功或失败  
- 你想在不同条件下验证相关结论  
- 你发现某种流行方法的性能取决于未公开的细节  

### 论文结构

```
1. Introduction
   - What paper/result are you reproducing?
   - Why is this reproduction valuable?

2. Original Claims
   - State the exact claims from the original paper
   - What evidence was provided?

3. Methodology
   - Your reproduction approach
   - Differences from original (if any) and why
   - What information was missing from the original paper?

4. Results
   - Side-by-side comparison with original results
   - Statistical comparison (confidence intervals overlap?)
   - What reproduced and what didn't?

5. Analysis
   - If results differ: why? What's sensitive?
   - Hidden hyperparameters or implementation details?
   - Robustness to seed, hardware, library versions?

6. Recommendations
   - For original authors: what should be clarified?
   - For practitioners: what to watch out for?
   - For the field: what reproducibility lessons emerge?
```

### 活动与平台

| 活动/平台 | 说明 |
|-------|-------|
| **机器学习可复现性挑战赛** | 在 NeurIPS 上举办的年度竞赛 |
| **ReScience** | 专门发表可复现性研究论文的期刊 |
| **TMLR** | 接收附带分析内容的可复现性研究论文 |
| **研讨会** | 各大会议中关于可复现性的专题研讨会 |
