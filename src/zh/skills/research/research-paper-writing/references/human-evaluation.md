# 机器学习/人工智能研究的人类评估指南

本指南全面介绍了在机器学习与人工智能论文中设计、实施及报告人类评估的方法。对于许多自然语言处理、人机交互以及对齐相关的研究而言，人类评估是核心证据；而在所有机器学习领域，人们也越来越期望将其作为补充性证据。

---

## 目录

- [何时需要进行人类评估](#when-human-evaluation-is-needed)
- [研究设计](#study-design)
- [标注指南](#annotation-guidelines)
- [平台与参与者招募](#platforms-and-recruitment)
- [质量控制](#quality-control)
- [一致性指标](#agreement-metrics)
- [人类评估的统计分析](#statistical-analysis-for-human-eval)
- [报告要求](#reporting-requirements)
- [机构审查委员会与伦理问题](#irb-and-ethics)
- [常见误区](#common-pitfalls)

---

## 何时需要进行人类评估

| 场景 | 是否需要人类评估 | 备注 |
|------|-------------------|-------|
| 文本生成质量（流畅性、连贯性） | **需要** | 自动化指标（如BLEU、ROUGE）与人类判断关联度较低 |
| 生成文本的事实准确性 | **强烈建议** | 自动化事实核查并不可靠 |
| 安全性/毒性评估 | **复杂场景下需要** | 分类模型难以识别依赖上下文的危害 |
| 两种系统之间的偏好对比 | **需要** | 比较大语言模型输出结果的最可靠方法 |
| 摘要质量 | **需要** | ROUGE指标无法有效衡量摘要的忠实度与相关性 |
| 任务完成情况（用户界面、智能体） | **需要** | 用户研究是公认的金标准 |
| 分类准确性 | **通常不需要** | 真实标签已足够；人类评估会增加成本却无法提供额外洞察 |
| 混乱度或损失值对比 | **不需要** | 应使用自动化指标进行评估 |

---

## 研究设计

### 评估类型

| 类型 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **成对比较** | 比较两个系统 | 最可靠，能最大程度降低规模偏差 | 仅能比较成对系统，系统数量越多计算量呈二次方增长 |
| **李克特量表**（1-5分或1-7分） | 对单个输出进行评分 | 易于汇总数据 | 存在主观锚定效应，且分数区间易压缩 |
| **排序法** | 对3个及以上系统进行排序 | 能完整反映偏好顺序 | 系统数量增加会提升认知负荷 |
| **最优-最差评分法** | 高效比较多个系统 | 比李克特量表更可靠，计算量与系统数量成线性关系 | 需要精心挑选评估项 |
| **二元判断** | 作出是/否决策（如语法正确？事实准确？） | 简单，一致性高 | 会丢失细节层次 |
| **错误标注** | 识别特定类型的错误 | 能提供丰富的诊断信息 | 成本高昂，需要经过培训的标注人员 |

**针对大多数机器学习论文的建议**：成对比较是最具说服力的方法，审稿人很少对其有效性提出质疑。对于李克特量表，务必同时报告平均值与分布情况。

### 样本量规划

**最低可行样本量：**

| 研究类型 | 最少评估项数 | 最少标注人数 | 备注 |
|------------|--------------|----------------|------|
| 成对比较 | 100对 | 每对3人 | 在p<0.05水平下可检测出约10%的胜率差异 |
| 李克特量表评分 | 100项 | 每项3人 | 足够得出有意义的平均值 |
| 排序法 | 50组 | 每组3人 | 每组包含所有需比较的系统 |
| 错误标注 | 200项 | 每项2人 | 结构化评估方案下预期一致性更高 |

**功效分析**（用于更精确地规划样本量）：

```python
from scipy import stats
import numpy as np

def sample_size_pairwise(effect_size=0.10, alpha=0.05, power=0.80):
    """
    Estimate sample size for pairwise comparison (sign test).
    effect_size: expected win rate difference from 0.50
    """
    p_expected = 0.50 + effect_size
    # Normal approximation to binomial
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = ((z_alpha * np.sqrt(0.25) + z_beta * np.sqrt(p_expected * (1 - p_expected))) ** 2) / (effect_size ** 2)
    return int(np.ceil(n))

print(f"Sample size for 10% effect: {sample_size_pairwise(0.10)}")  # ~200
print(f"Sample size for 15% effect: {sample_size_pairwise(0.15)}")  # ~90
print(f"Sample size for 20% effect: {sample_size_pairwise(0.20)}")  # ~50
```

### 偏见控制

| 偏见类型 | 缓解措施 |
|----------|----------|
| **顺序偏见**（优先选择首项） | 为每位标注员随机排列展示顺序 |
| **长度偏见**（长度越长越好） | 对长度进行控制或单独分析 |
| **锚定效应**（首个标注决定整体评分标准） | 加入热身题目（不计入评分） |
| **疲劳效应**（随时间推移质量下降） | 限制会话时长（最多30-45分钟），随机排列题目顺序 |
| **标注员专业水平** | 报告标注员的背景信息；使用资格测试题 |

---

## 标注指南

完善的标注指南是决定评估质量的最关键因素。请在此方面投入足够的时间。

### 优秀指南的结构

```markdown
# [Task Name] Annotation Guidelines

## Overview
[1-2 sentences describing the task]

## Definitions
[Define every term annotators will use in their judgments]
- Quality: [specific definition for this study]
- Fluency: [specific definition]
- Factuality: [specific definition]

## Rating Scale
[For each scale point, provide:]
- Numeric value
- Label (e.g., "Excellent", "Good", "Acceptable", "Poor", "Unacceptable")
- Definition of what qualifies for this rating
- 1-2 concrete examples at this level

## Examples

### Example 1: [Rating = 5]
Input: [exact input]
Output: [exact output]
Rating: 5
Explanation: [why this is a 5]

### Example 2: [Rating = 2]
Input: [exact input]
Output: [exact output]
Rating: 2
Explanation: [why this is a 2]

[Include at least 2 examples per rating level, covering edge cases]

## Edge Cases
- If the output is [ambiguous case]: [instruction]
- If the input is [unusual case]: [instruction]

## Common Mistakes
- Don't [common annotator error]
- Don't let [bias] influence your rating
```

### 试点测试

在正式开展研究之前，务必先进行试点测试：
1. 选取3-5名标注员，处理20-30项任务；
2. 计算一致性指标；
3. 在小组会议上讨论存在分歧的案例；
4. 根据常见问题调整标注指南；
5. 若一致性较差（卡帕值低于0.40），则需进行第二次试点测试。

---

## 平台与人员招募

| 平台 | 适用场景 | 费用 | 标注质量 |
|------|----------|------|---------|
| **Prolific** | 通用标注、调查任务 | 每小时8-15美元 | 高（用户多为学术领域从业者） |
| **Amazon MTurk** | 大规模简单任务 | 每小时5-12美元 | 不稳定（需严格的质量控制） |
| **Surge AI** | 面向自然语言处理领域的专项标注 | 每小时15-25美元 | 极高（标注员均经过专业培训） |
| **Scale AI** | 需达到生产级标准的标注任务 | 费用不定 | 高（拥有规范化的标注团队） |
| **内部团队** | 需要特定领域专业知识的任务 | 费用不定 | 专项任务质量最高 |
| **Upwork/自由职业者** | 长期标注项目 | 每小时10-30美元 | 质量取决于具体招聘对象 |

**公平薪酬**：务必为标注员支付与其所在地区最低工资相当的报酬。目前许多学术会议（尤其是ACL）都会要求明确标注员的薪酬标准。低于最低工资标准支付薪酬存在伦理风险。

**Prolific平台设置建议（适用于大多数机器学习相关论文）：**
1. 在prolific.co上创建研究项目；
2. 设置预筛选条件（语言、国家，以及通过率需高于95%）；
3. 通过试点测试估算每项任务所需时间，从而确定合理的薪酬；
4. 使用Prolific内置的注意力检查功能，或自行添加相关检查；
5. 收集标注员的Prolific账号信息以便后续质量跟踪（但切勿在论文中公开这些信息）。

---

## 质量控制

### 注意力检查

可加入一些正确答案毫无争议的任务，用于检测标注员的注意力集中度。

```python
# Types of attention checks
attention_checks = {
    "instructed_response": "For this item, please select 'Strongly Agree' regardless of content.",
    "obvious_quality": "Rate this clearly ungrammatical text: 'The cat dog house green yesterday.'",  # Should get lowest score
    "gold_standard": "Items where expert consensus exists (pre-annotated by authors)",
    "trap_question": "What color is the sky on a clear day? (embedded in annotation interface)"
}

# Recommended: 10-15% of total items should be checks
# Exclusion criterion: fail 2+ attention checks → exclude annotator
```

### 标注员资质要求

针对需要专业技能的任务：

```
Qualification Task Design:
1. Create a set of 20-30 items with known-correct labels
2. Require annotators to complete this before the main task
3. Set threshold: ≥80% agreement with gold labels to qualify
4. Record qualification scores for reporting
```

### 数据收集过程中的监控功能

```python
# Real-time quality monitoring
def monitor_quality(annotations):
    """Check for annotation quality issues during collection."""
    issues = []
    
    # 1. Check for straight-lining (same answer for everything)
    for annotator_id, items in annotations.groupby('annotator'):
        if items['rating'].nunique() <= 1:
            issues.append(f"Annotator {annotator_id}: straight-lining detected")
    
    # 2. Check time per item (too fast = not reading)
    median_time = annotations['time_seconds'].median()
    fast_annotators = annotations.groupby('annotator')['time_seconds'].median()
    for ann_id, time in fast_annotators.items():
        if time < median_time * 0.3:
            issues.append(f"Annotator {ann_id}: suspiciously fast ({time:.0f}s vs median {median_time:.0f}s)")
    
    # 3. Check attention check performance
    checks = annotations[annotations['is_attention_check']]
    for ann_id, items in checks.groupby('annotator'):
        accuracy = (items['rating'] == items['gold_rating']).mean()
        if accuracy < 0.80:
            issues.append(f"Annotator {ann_id}: failing attention checks ({accuracy:.0%})")
    
    return issues
```

## 一致性指标

### 应选择哪种指标

| 指标 | 适用场景 | 解释说明 |
|------|----------|----------|
| **科恩卡帕值（κ）** | 恰好2名标注者，分类数据 | 经过机会水平校正的一致性度量 |
| **弗莱斯卡帕值** | 3名及以上标注者，所有标注者对同一项目评分相同，分类数据 | 科恩卡帕值的多标注者扩展版本 |
| **克里彭多夫阿尔法值（α）** | 标注者数量不限，可处理缺失数据 | 最通用的指标；推荐作为默认选择 |
| **组内相关系数（ICC）** | 连续型评分（李克特量表） | 用于衡量不同评分者之间的稳定性 |
| **一致性百分比** | 与卡帕值/阿尔法值一同报告 | 原始一致性度量（未经过机会水平校正） |
| **肯德尔W值** | 排名数据 | 用于衡量不同排名者之间的吻合度 |

**建议至少报告两项指标**：一项经过机会水平校正的指标（卡帕值或阿尔法值），以及原始的一致性百分比。

### 解读指南

| 数值范围 | 克里彭多夫α值 / 科恩κ值 | 质量等级 |
|----------|------------------------|----------|
| > 0.80 | 极高一致性 | 大多数场景下均可信赖 |
| 0.67 - 0.80 | 良好一致性 | 大多数机器学习论文可接受 |
| 0.40 - 0.67 | 中等一致性 | 程度有限，需在论文中加以说明 |
| < 0.40 | 差异较大的一致性 | 需重新调整标注规范并重新进行标注 |

**注意**：克里彭多夫认为，若要得出初步结论，阿尔法值应至少达到0.667。涉及主观判断的NLP任务（如流畅度、实用性评估）的典型一致性数值在0.40-0.70之间。

### 实现方式

```python
import numpy as np
from sklearn.metrics import cohen_kappa_score
import krippendorff  # pip install krippendorff

def compute_agreement(annotations_matrix):
    """
    annotations_matrix: shape (n_items, n_annotators)
    Values: ratings (int or float). Use np.nan for missing.
    """
    results = {}
    
    # Krippendorff's alpha (handles missing data, any number of annotators)
    results['krippendorff_alpha'] = krippendorff.alpha(
        annotations_matrix.T,  # krippendorff expects (annotators, items)
        level_of_measurement='ordinal'  # or 'nominal', 'interval', 'ratio'
    )
    
    # Pairwise Cohen's kappa (for 2 annotators at a time)
    n_annotators = annotations_matrix.shape[1]
    kappas = []
    for i in range(n_annotators):
        for j in range(i + 1, n_annotators):
            mask = ~np.isnan(annotations_matrix[:, i]) & ~np.isnan(annotations_matrix[:, j])
            if mask.sum() > 0:
                k = cohen_kappa_score(
                    annotations_matrix[mask, i].astype(int),
                    annotations_matrix[mask, j].astype(int)
                )
                kappas.append(k)
    results['mean_pairwise_kappa'] = np.mean(kappas) if kappas else None
    
    # Raw percent agreement
    agree_count = 0
    total_count = 0
    for item in range(annotations_matrix.shape[0]):
        ratings = annotations_matrix[item, ~np.isnan(annotations_matrix[item, :])]
        if len(ratings) >= 2:
            # All annotators agree
            if len(set(ratings.astype(int))) == 1:
                agree_count += 1
            total_count += 1
    results['percent_agreement'] = agree_count / total_count if total_count > 0 else None
    
    return results
```

## 人工评估的统计分析

### 成对比较

```python
from scipy import stats

def analyze_pairwise(wins_a, wins_b, ties=0):
    """
    Analyze pairwise comparison results.
    wins_a: number of times system A won
    wins_b: number of times system B won
    ties: number of ties (excluded from sign test)
    """
    n = wins_a + wins_b  # exclude ties
    
    # Sign test (exact binomial)
    p_value = stats.binom_test(wins_a, n, 0.5, alternative='two-sided')
    
    # Win rate with 95% CI (Wilson score interval)
    win_rate = wins_a / n if n > 0 else 0.5
    z = 1.96
    denominator = 1 + z**2 / n
    center = (win_rate + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt((win_rate * (1 - win_rate) + z**2 / (4 * n)) / n) / denominator
    ci_lower = center - margin
    ci_upper = center + margin
    
    return {
        'win_rate_a': win_rate,
        'win_rate_b': 1 - win_rate,
        'p_value': p_value,
        'ci_95': (ci_lower, ci_upper),
        'significant': p_value < 0.05,
        'n_comparisons': n,
        'ties': ties,
    }
```

### 利克特量表分析

```python
def analyze_likert(ratings_a, ratings_b):
    """Compare Likert ratings between two systems (paired)."""
    # Wilcoxon signed-rank test (non-parametric, paired)
    stat, p_value = stats.wilcoxon(ratings_a, ratings_b, alternative='two-sided')
    
    # Effect size (rank-biserial correlation)
    n = len(ratings_a)
    r = 1 - (2 * stat) / (n * (n + 1))
    
    return {
        'mean_a': np.mean(ratings_a),
        'mean_b': np.mean(ratings_b),
        'std_a': np.std(ratings_a),
        'std_b': np.std(ratings_b),
        'wilcoxon_stat': stat,
        'p_value': p_value,
        'effect_size_r': r,
        'significant': p_value < 0.05,
    }
```

### 多重比较校正

在对比两个以上的系统时：

```python
from statsmodels.stats.multitest import multipletests

# After computing p-values for all pairs
p_values = [0.03, 0.001, 0.08, 0.04, 0.15, 0.002]
rejected, corrected_p, _, _ = multipletests(p_values, method='holm')
# Use corrected p-values in your paper
```

## 报告要求

自然语言处理领域的会议（ACL、EMNLP、NAACL）的审稿人会检查所有这些内容。机器学习领域的会议（NeurIPS、ICML）也越来越要求提供相关报告。

### 强制性报告内容

```latex
% In your paper's human evaluation section:
\paragraph{Annotators.} We recruited [N] annotators via [platform].
[Describe qualifications or screening.] Annotators were paid
\$[X]/hour, above the [country] minimum wage.

\paragraph{Agreement.} Inter-annotator agreement was [metric] = [value]
(Krippendorff's $\alpha$ = [value]; raw agreement = [value]\%).
[If low: explain why the task is subjective and how you handle disagreements.]

\paragraph{Evaluation Protocol.} Each [item type] was rated by [N]
annotators on a [scale description]. We collected [total] annotations
across [N items]. [Describe randomization and blinding.]
```

### 附录中包含哪些内容

```
Appendix: Human Evaluation Details
- Full annotation guidelines (verbatim)
- Screenshot of annotation interface
- Qualification task details and threshold
- Attention check items and failure rates
- Per-annotator agreement breakdown
- Full results table (not just averages)
- Compensation calculation
- IRB approval number (if applicable)
```

## IRB审批与伦理规范

### 何时需要IRB审批

| 场景 | 是否需要IRB审批？ |
|-----------|------------------|
| 让众包人员对文本质量进行评分 | **通常不需要**（在大多数机构中不属于“人类受试者研究”） |
| 对真实用户开展用户研究 | 在大多数美国/欧盟机构中**需要** |
| 收集个人信息 | **需要** |
| 研究标注员的行为或认知特征 | **需要**（标注员本身即成为研究受试者） |
| 使用现有的已标注数据 | **通常不需要**（属于二次数据分析） |

**请查阅您所在机构的政策。**“人类受试者研究”的定义因机构而异。如有疑问，建议提交IRB审批申请——对于风险较低的研究，审核流程通常较为快捷。

### 人工评估的伦理检查清单

```
- [ ] Annotators informed about task purpose (not deceptive)
- [ ] Annotators can withdraw at any time without penalty
- [ ] No personally identifiable information collected beyond platform ID
- [ ] Content being evaluated does not expose annotators to harm
  (if it does: content warnings + opt-out + higher compensation)
- [ ] Fair compensation (>= equivalent local minimum wage)
- [ ] Data stored securely, access limited to research team
- [ ] IRB approval obtained if required by institution
```

## 常见陷阱

| 陷阱类型 | 问题表现 | 解决方案 |
|---------|---------|---------|
| 标注员数量过少（1-2人） | 无法计算一致性指标 | 每个任务至少需要3名标注员 |
| 未设置注意力检查 | 无法识别低质量标注结果 | 需包含10-15%的注意力检查样本 |
| 未报告报酬信息 | 审核人员会将其视为伦理问题 | 必须始终注明每小时薪酬标准 |
| 仅使用自动化指标进行生成评估 | 审核人员会要求人工评估 | 至少需添加成对对比环节 |
| 未进行试点测试 | 一致性较低且预算浪费 | 每次都应先让3-5人参与试点 |
| 仅报告平均值 | 无法体现标注员之间的分歧 | 需同时报告数据分布情况与一致性指标 |
| 未控制顺序/位置因素 | 位置偏差会导致结果失真 | 需随机调整内容的呈现顺序 |
| 将标注员的一致性等同于真实标准 | 高一致性并不代表结果正确 | 需以专家判断作为验证依据 |
