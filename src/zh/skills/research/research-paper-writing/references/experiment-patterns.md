# 实验设计模式

这些模式与最佳实践源于使用 Hermes Agent 执行大规模研究实验的经验总结，涵盖了实验基础设施、评估方案、监控以及故障恢复等方面。

---

## 实验基础设施

### 目录结构

采用统一的结构来组织实验：

```
workspace/
  experiments/
    run_main.py                # Core experiment runner
    run_baselines.py           # Baseline comparison
    run_ablation.py            # Ablation studies
    strategies.py              # Method implementations
    config.yaml                # Shared configuration
  results/
    <experiment_name>/
      <task_or_problem>/
        <strategy>/
          result.json          # Final metrics
          final_output.md      # Final output artifact
          history.json         # Full trajectory/log
          pass_01/             # Per-iteration artifacts (if iterative)
            intermediate.md
  analysis/
    analyze_results.py         # Statistical analysis
    compute_stats.py           # Significance tests
    make_charts.py             # Visualization
  paper/
    paper.tex                  # LaTeX source
    fig_*.pdf                  # Generated figures
```

### 脚本设计原则

**1. 逐步保存（崩溃恢复机制）**

每个实验脚本都应在完成每一项任务后保存结果，从而在程序重启时跳过已处理过的任务：

```python
import json, os
from pathlib import Path

def run_experiment(problems, strategies, output_dir):
    for problem in problems:
        for strategy in strategies:
            result_path = Path(output_dir) / problem["id"] / strategy / "result.json"
            if result_path.exists():
                print(f"Skipping {problem['id']}/{strategy} (already done)")
                continue
            
            # Run the experiment
            result = execute_strategy(problem, strategy)
            
            # Save immediately
            result_path.parent.mkdir(parents=True, exist_ok=True)
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
```

该模式能够确保重新运行过程的安全性与高效性。如果某个流程在处理到第 47/150 步时发生崩溃，重启时将跳过前 46 步。

**2. 输出结果保留**

需保存所有中间输出，而不仅仅是最终结果。这样一来，无需重新运行即可进行事后分析：

```python
def save_pass_artifacts(output_dir, pass_num, artifacts):
    """Save all artifacts from a single pass of an iterative method."""
    pass_dir = Path(output_dir) / f"pass_{pass_num:02d}"
    pass_dir.mkdir(parents=True, exist_ok=True)
    
    for name, content in artifacts.items():
        with open(pass_dir / f"{name}.md", 'w') as f:
            f.write(content)
```

**3. 配置管理**

采用 YAML 格式配置文件以确保结果可复现：

```yaml
# config.yaml
model: anthropic/claude-sonnet-4-20250514
author_temperature: 0.8
judge_temperature: 0.3
max_tokens: 4096
num_judges: 3
max_passes: 15
convergence_k: 2
```

```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)
```

**4. 职责分离**

将生成、评估和可视化功能分别放在不同的脚本中：

| 脚本名称 | 功能说明 |
|--------|---------|
| `run_experiment.py` | 核心方法执行 |
| `run_baselines.py` | 在相同计算环境下进行基线对比 |
| `run_eval.py` | 盲评/专家评审机制 |
| `analyze_results.py` | 统计分析 |
| `make_charts.py` | 图表生成 |

这样一来，无需重新运行耗时的生成过程即可再次进行评估，也无需重复分析即可重新生成图表。

---

## 评估方案

### 盲评机制（适用于主观任务）

在评估写作、分析或推荐等主观类输出时，可采用盲评机制：

```python
import random

def run_blind_evaluation(outputs: dict, task_prompt: str, num_judges: int = 7):
    """
    Run blind evaluation of multiple method outputs.
    
    Args:
        outputs: {"method_name": "output_text", ...}
        task_prompt: The original task description
        num_judges: Number of independent judge evaluations
    """
    rankings = []
    
    for judge_i in range(num_judges):
        # Randomize labels and presentation order per judge
        methods = list(outputs.keys())
        random.shuffle(methods)
        labels = {m: chr(65 + i) for i, m in enumerate(methods)}  # A, B, C...
        
        # Present to judge with randomized labels
        prompt = f"Task: {task_prompt}\n\n"
        for method in methods:
            prompt += f"--- Proposal {labels[method]} ---\n{outputs[method]}\n\n"
        prompt += "Rank all proposals from best to worst. Format: RANKING: [best], [second], [worst]"
        
        ranking = call_judge(prompt)
        rankings.append({"labels": labels, "ranking": ranking})
    
    # Aggregate via Borda count
    return compute_borda(rankings)

def compute_borda(rankings, n_methods=3):
    """Borda count: 3/2/1 points for 1st/2nd/3rd."""
    scores = {}
    points = {0: n_methods, 1: n_methods - 1, 2: n_methods - 2}  # Adjust for n_methods
    
    for r in rankings:
        for position, method in enumerate(r["ranking"]):
            scores[method] = scores.get(method, 0) + points.get(position, 0)
    
    return scores
```

核心设计决策：
- 为避免位置偏差，**为每位评审员随机分配标签及顺序**
- 采用**奇数数量的评审员**（3、5、7人）以打破平局
- 采用**保守型平局解决策略**：由原有模型/基准模型赢得平局（从而避免误报）
- **CoT评审员**在成本仅约为普通评审员的40%的情况下即可达到相近的质量水平（1名CoT评审员相当于3名普通评审员）

### 代码/目标评估

针对需要真实值评估的任务（如代码、数学题、事实类问题）：

```python
import subprocess

def evaluate_code(solution: str, test_cases: list, timeout: int = 30):
    """Run code solution against test cases with sandboxed execution."""
    results = {"public": [], "private": []}
    
    for test in test_cases:
        try:
            proc = subprocess.run(
                ["python3", "-c", solution],
                input=test["input"],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            actual = proc.stdout.strip()
            expected = test["expected"].strip()
            passed = actual == expected
        except subprocess.TimeoutExpired:
            passed = False
        
        category = "public" if test.get("public") else "private"
        results[category].append(passed)
    
    return {
        "public_pass_rate": sum(results["public"]) / max(len(results["public"]), 1),
        "private_pass_rate": sum(results["private"]) / max(len(results["private"]), 1),
    }
```

### 计算资源匹配的对比测试

所有方法的对比都应在相同的计算预算下进行。如果某方法需要执行 N 次 API 调用，各基准方法也将执行 N 次调用：

| 方法 | 调用预算 | 分配方式 |
|------|-----------|----------|
| 单次生成 | 6 次调用 | 6 次独立生成 |
| 评审与修改 | 6 次调用 | 1 次生成 + 5 轮修改 |
| 自动推理 | 6 次调用 | 1 次生成 + 1 次分析 + 4 轮修改 |
| N 种方法最佳选择 | 6 次调用 | 6 次独立生成，通过公开测试选出最优结果 |

### 人工评估设计

许多机器学习/自然语言处理论文都需要进行人工评估，尤其是那些涉及主观任务的场景（如文本生成、摘要生成、对话系统、创意写作）。设计不合理的人工评估往往是论文被拒的常见原因。

#### 需要人工评估的场景

| 任务类型 | 是否需要 | 备注 |
|--------|----------|------|
| 开放式文本生成 | 是 | 仅依靠大语言模型作为评判标准并不足以让论文在 ACL/EMNLP 等会议上被接受 |
| 摘要生成 | 通常需要 | 至少需要对部分输出结果进行人工评估 |
| 对话系统 | 是 | 需要通过用户测试或人工标注 |
| 代码生成 | 不需要 | 测试用例即可作为客观的基准 |
| 分类任务 | 不需要 | 标准指标已足够 |
| 任何涉及主观质量的任务 | 强烈建议 | 能显著提升论文的质量 |

#### 人工标注流程设计

```
Human Evaluation Protocol:
1. Define the evaluation dimensions (fluency, relevance, factual accuracy, etc.)
2. Create annotation guidelines with examples of each score level
3. Run a pilot with 2-3 annotators on 20-30 examples
4. Compute pilot inter-annotator agreement — if low, revise guidelines
5. Run full evaluation
6. Report: annotator count, agreement metrics, compensation, time per item
```

**评估维度**（请选择相关项）：

| 维度 | 定义 | 评分标准 |
|-----------|------|----------|
| 流畅性 | 语法正确性及自然度 | 1-5 分利克特量表 |
| 相关性 | 是否能够完成指定任务？ | 1-5 分利克特量表 |
| 事实准确性 | 所述事实是否正确？ | 二元制或 1-5 分 |
| 连贯性 | 逻辑结构是否清晰且一致 | 1-5 分利克特量表 |
| 信息量 | 是否提供了有用的信息？ | 1-5 分利克特量表 |
| 整体偏好 | 哪种输出更优？ | A/B/平局（两两对比） |

**两两对比法**（相比绝对评分更为可靠）：
- 将两种输出并排展示（随机调整左右顺序）
- 提问：“哪个更好？A / B / 平局”
- 此方法更具区分度，且不易受标注者评分标准偏差的影响

#### 标注者间一致性评估

务必报告一致性指标。若未提供这些数据，评审人员会认为您的标注结果不可靠。

```python
# Krippendorff's alpha (preferred — handles missing data, any scale)
# pip install krippendorffs-alpha
import krippendorff

# Ratings: rows = annotators, columns = items, values = scores
ratings = [
    [3, 4, 1, 2, 5, None, 3],  # Annotator 1
    [3, 5, 1, 3, 5, 2, 3],     # Annotator 2
    [4, 4, 2, 2, 4, 2, None],  # Annotator 3
]
alpha = krippendorff.alpha(reliability_data=ratings, level_of_measurement="ordinal")
print(f"Krippendorff's alpha: {alpha:.3f}")
# Interpretation: >0.80 good, 0.67-0.80 acceptable, <0.67 questionable
```

```python
# Cohen's kappa (for exactly 2 annotators, categorical data)
from sklearn.metrics import cohen_kappa_score

annotator_1 = [1, 2, 3, 1, 2, 3, 2]
annotator_2 = [1, 2, 2, 1, 3, 3, 2]
kappa = cohen_kappa_score(annotator_1, annotator_2)
print(f"Cohen's kappa: {kappa:.3f}")
# Interpretation: >0.80 excellent, 0.60-0.80 substantial, 0.40-0.60 moderate
```

| 指标 | 适用场景 | 评分员数量 | 量纲要求 |
|------|----------|-----------|---------|
| Krippendorff's alpha | 默认选择 | 任意数量 | 任意类型（有序、名义、比率） |
| Cohen's kappa | 2名评分员，分类数据 | 恰好2人 | 名义/有序类型 |
| Fleiss' kappa | 3名及以上评分员，分类数据 | 3人以上 | 名义类型 |
| Pearson/Spearman | 连续得分数据 | 2人 | 区间/比率类型 |

#### 流量众包平台

| 平台 | 最佳适用场景 | 成本 | 任务质量 |
|----------|--------------|------|---------|
| **Prolific** | 学术研究，高质量任务 | 每小时8-15美元 | 高——拥有优质的学术背景参与者群体 |
| **MTurk** | 大规模任务处理，快速交付 | 每小时2-10美元 | 不稳定——需根据评分员资质筛选 |
| **Surge AI** | 专注于自然语言处理领域的标注任务 | 高级套餐价格 | 高——由经过专业培训的评分员完成 |
| **专业评分员** | 需要领域专业知识的任务（如医疗、法律领域） | 成本最高 | 质量最高——但处理速度较慢 |

**伦理要求**：
- 需注明报酬标准（至少需达到当地最低工资标准）
- 如有必要，需描述评分员的基本信息
- 若所在机构有要求，需获得伦理审查委员会批准
- ACL相关会议明确要求提供报酬证明文件

#### 论文中需汇报的内容

```
Human Evaluation Section Checklist:
- [ ] Number of annotators
- [ ] Annotator qualifications / recruitment method
- [ ] Number of items evaluated
- [ ] Evaluation dimensions with definitions
- [ ] Scale used (Likert, pairwise, binary)
- [ ] Inter-annotator agreement (Krippendorff's alpha or Cohen's kappa)
- [ ] Compensation rate
- [ ] Time per annotation item
- [ ] Whether annotators saw model identities (should be blind)
- [ ] Randomization of presentation order
```

## 统计分析

### 所需测试

| 测试方法 | 适用场景 | Python库 |
|----------|----------|----------|
| McNemar检验 | 比较同一问题下两种方法的差异 | 小样本时使用`scipy.stats.binomtest` |
| 两比例z检验 | 比较成功率 | 可自行实现或使用`statsmodels` |
| Fisher精确检验 | 小样本的成对比较 | 使用`scipy.stats.fisher_exact` |
| 自举法置信区间 | 计算任意指标的置信区间 | 自行实现自举法 |
| Cohen's h值 | 衡量比例间的效应大小 | 手动计算 |

### 标准分析脚本

```python
import numpy as np
from scipy import stats
from pathlib import Path
import json

def load_all_results(results_dir):
    """Load all results into a structured format."""
    results = {}
    for result_file in Path(results_dir).rglob("result.json"):
        parts = result_file.relative_to(results_dir).parts
        if len(parts) >= 3:
            experiment, task, strategy = parts[0], parts[1], parts[2]
            data = json.loads(result_file.read_text())
            results.setdefault(experiment, {}).setdefault(strategy, {})[task] = data
    return results

def pairwise_mcnemar(method_a_results, method_b_results):
    """McNemar's test for paired binary outcomes."""
    a_win_b_lose = sum(1 for a, b in zip(method_a_results, method_b_results) if a and not b)
    b_win_a_lose = sum(1 for a, b in zip(method_a_results, method_b_results) if b and not a)
    
    n = a_win_b_lose + b_win_a_lose
    if n < 25:
        # Use exact binomial for small samples
        result = stats.binomtest(a_win_b_lose, n, 0.5)
        p_value = result.pvalue
    else:
        # Chi-squared approximation
        chi2 = (abs(a_win_b_lose - b_win_a_lose) - 1)**2 / (a_win_b_lose + b_win_a_lose)
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
    
    return {
        "a_wins": a_win_b_lose,
        "b_wins": b_win_a_lose,
        "n_discordant": n,
        "p_value": p_value,
        "significant": p_value < 0.05
    }

def bootstrap_ci(data, n_bootstrap=10000, ci=0.95):
    """Bootstrap confidence interval for mean."""
    means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))
    lower = np.percentile(means, (1 - ci) / 2 * 100)
    upper = np.percentile(means, (1 + ci) / 2 * 100)
    return {"mean": np.mean(data), "ci_lower": lower, "ci_upper": upper}

def cohens_h(p1, p2):
    """Cohen's h effect size for two proportions."""
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
```

### 报告标准

报告文档中必须包含以下内容：
- **样本量**：n=问题/任务数量
- **运行次数**：如适用，请说明独立运行的次数K
- **误差范围**：需明确标注标准差或标准误
- **置信区间**：关键结果需提供95%置信区间
- **显著性检验**：关键对比需给出p值
- **效应大小**：为体现实际意义，需标注Cohen's d或h值

---

## 监控（Cron表达式）

### Cron提示模板

针对每批实验，需创建相应的监控提示：

```
Check the status of the [EXPERIMENT_NAME] experiment:

1. Process check: ps aux | grep [PROCESS_PATTERN]
2. Log check: tail -30 [LOG_FILE]
3. Results check: ls [RESULT_DIR]/eval/ (or appropriate result location)
4. If results are available:
   - Read the result JSON files
   - Report metrics in a table (Borda scores, accuracy, etc.)
   - Compute key comparisons between methods
5. If all experiments in this batch are complete:
   - git add -A && git commit -m "[COMMIT_MESSAGE]" && git push
   - Report final summary
6. Key question: [SPECIFIC ANALYTICAL QUESTION]

If nothing has changed since the last check, respond with [SILENT].
```

### 监控最佳实践

1. **先检查进程状态** — 若实验仍在运行且结果尚未完整，切勿直接查看结果。
2. **查看日志尾部** — 寻找错误信息、进度指示及完成提示。
3. **统计已完成与预期数量** — “45/150 个问题已处理”比“存在部分结果”更具参考价值。
4. **以结构化表格呈现报告** — 始终将关键指标放入表格中。
5. **明确核心分析目标** — 每次实验都应设定一个具体的分析问题以便在完成后进行解答。
6. **无变化时静默处理** — 若一切正常无变动，则无需发送通知。
7. **完成即提交记录** — 每批处理完成后都应附上描述性说明并予以提交。

### 监控报告示例

```
## Code Experiments (Haiku 3.5) - COMPLETE

| Strategy | Pass Rate (150 problems) | vs Single |
|----------|------------------------|-----------|
| single_pass | 38.0% | — |
| critique_revise | 35.2% | -2.8pp |
| **autoreason** | **40.0%** | **+2.0pp** |
| best_of_6 | 31.0% | -7.0pp |

Key finding: Autoreason shows +2pp improvement over single pass, while 
best-of-6 collapses due to single-public-test selection issue.

Committed: `git commit -m "Add Haiku code results (150 problems, 4 strategies)"`
Next: Run significance tests on these results.
```

## 故障恢复

### 常见故障及恢复方法

| 故障类型 | 检测方式 | 恢复方法 |
|---------|-----------|----------|
| **API额度耗尽** | 日志中出现402错误，结果不完整 | 补充API额度后重新运行（系统会自动跳过已完成的部分） |
| **速率限制** | 出现429错误，任务进度缓慢 | 添加带有指数退避机制的重试逻辑 |
| **进程崩溃** | 进程ID消失，日志在出错时停止记录 | 重新运行脚本（从上一个检查点继续执行） |
| **模型ID错误** | 出现模型未找到的错误 | 更正模型ID（例如将`claude-opus-4-6`改为正确的`claude-opus-4.6`） |
| **并行处理变慢** | 每次实验的耗时变为原来的2倍 | 将并行实验数量控制在2-3个以内 |
| **安全扫描拦截** | 命令被安全机制阻止执行 | 改用`execute_code`函数，而非通过管道传递`terminal`命令 |
| **任务委托失败** | `delegate_task`函数返回错误 | 回退为直接执行任务 |
| **复杂问题超时** | 进程卡住，无日志进度更新 | 终止进程，跳过该问题，并在结果中记录说明 |
| **数据集路径错误** | 出现文件未找到的错误 | 在启动任务前确认路径正确性 |

### 重试命名规范

在重新运行失败的实验时，建议使用后缀来标识不同的重试轮次：

```
logs/experiment_haiku_0_50.log       # Round 1
logs/experiment_haiku_0_50_r2.log    # Round 2 (after credit exhaustion)
logs/experiment_haiku_0_50_r3.log    # Round 3 (after bug fix)
```

### 飞行前检查清单

在启动任何实验批次之前：

```
Pre-Flight:
- [ ] API credits sufficient for estimated calls
- [ ] Model IDs correct (test with 1 problem first)
- [ ] Output directory exists and is writable
- [ ] Resume logic works (re-run won't overwrite existing results)
- [ ] Log file path is unique (won't overwrite previous logs)
- [ ] Dataset/task files are accessible
- [ ] Config matches intended experiment
```

## 任务/基准测试设计

### 开放式任务（主观评估）

设计目标明确但质量评价具有主观性的任务：

```markdown
# Task: [Title]

## Context
[Specific scenario with concrete details: company size, constraints, timeline]

## Deliverable
[Exact format and structure required]

## Requirements
- [Specific, measurable requirements]
- [Not vague — "be comprehensive" is bad, "include exactly 6 sections" is good]
```

### 受限任务（用于测试范围约束效果）

受限任务用于检测方法是否遵循范围边界。设计时应考虑以下要素：

- **固定事实**：“仅使用这N个数据点，不得添加其他内容”
- **固定交付物格式**：指定具体格式（如报告、事后分析、备忘录——而非“改进此内容”）
- **固定结构**：“按此顺序排列这些章节，不得增减”
- **固定修改项**：“仅处理这N个问题，不得涉及其他内容”

**切勿将字数作为范围约束条件**。字数限制会导致错误的结果——输出被拒往往是因为长度而非质量。应约束的是内容范围（包含什么），而非长度。

### 示例：好的与坏的约束条件对比

| 错误的约束条件 | 原因 | 正确的约束条件 |
|---------------|------|-----------------|
| “最多500字” | 评审者会因长度问题拒绝 | “恰好4个章节，每个章节包含3个编号项” |
| “简洁明了” | 过于模糊 | “每条限制要求都必须对应某个具体的基础事实” |
| “改进此内容” | 范围无限制 | “按照此固定结构撰写一篇600字的事件事后分析报告” |
| “让它更好” | 没有明确标准 | “仅解决这3个评审者的顾虑” |

---

## 可视化最佳实践

### 设置：SciencePlots + matplotlib

安装SciencePlots以获得适合发布的默认配置：

```bash
pip install SciencePlots matplotlib numpy
```

**选项 A：SciencePlots 风格**（推荐使用——可自动处理大多数默认设置）：

```python
import matplotlib.pyplot as plt
import scienceplots  # registers the styles

# Pick a style:
# 'science'        — clean, serif fonts, suitable for most venues
# 'science+ieee'   — IEEE-style (good for two-column papers)
# 'science+nature' — Nature-style
# Add 'no-latex' if LaTeX is not installed on the machine generating plots

with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # single-column width
    # ... plot ...
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')
```

**选项 B：手动设置 rcParams**（适用于需要完全掌控设置的情况）：

```python
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (3.5, 2.5),    # single-column default
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,
})
```

### 标准图表尺寸（双列格式）

| 使用场景 | figsize | 备注 |
|----------|---------|-------|
| 单列 | `(3.5, 2.5)` | 适用于双列布局中的单列 |
| 双列 | `(7.0, 3.0)` | 覆盖整个页面宽度 |
| 正方形（热力图、混淆矩阵） | `(3.5, 3.5)` | 单列显示 |
| 高行数单列（行数较多） | `(3.5, 5.0)` | 建议谨慎使用 |

### 适合色盲人群的配色方案（Okabe-Ito）

所有纸质图表均建议使用此配色方案。它能够被所有常见类型的色觉缺陷者准确区分：

```python
COLORS = {
    'blue':    '#0072B2',
    'orange':  '#E69F00',
    'green':   '#009E73',
    'red':     '#D55E00',
    'purple':  '#CC79A7',
    'cyan':    '#56B4E9',
    'yellow':  '#F0E442',
    'black':   '#000000',
}

# As a list for cycling:
COLOR_CYCLE = ['#0072B2', '#D55E00', '#009E73', '#E69F00', '#CC79A7', '#56B4E9']
```

此外，还可以通过**标记符号和线条样式**来区分不同线路，而不仅仅依靠颜色。
```python
STYLES = [
    {'color': '#0072B2', 'marker': 'o', 'linestyle': '-'},
    {'color': '#D55E00', 'marker': 's', 'linestyle': '--'},
    {'color': '#009E73', 'marker': '^', 'linestyle': '-.'},
    {'color': '#E69F00', 'marker': 'D', 'linestyle': ':'},
]
```

### 完整示例：方法对比条形图

```python
import matplotlib.pyplot as plt
import numpy as np

try:
    import scienceplots
    style = ['science', 'no-latex']
except ImportError:
    style = 'default'

with plt.style.context(style):
    methods = ['Single Pass', 'Critique+Revise', 'Best-of-N', 'Ours']
    scores = [73.2, 74.1, 68.5, 77.0]
    errors = [2.1, 1.8, 3.2, 1.5]
    colors = ['#56B4E9', '#E69F00', '#CC79A7', '#0072B2']
    
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    bars = ax.bar(methods, scores, yerr=errors, capsize=3,
                  color=colors, edgecolor='black', linewidth=0.5)
    
    # Highlight "Ours"
    bars[-1].set_edgecolor('#0072B2')
    bars[-1].set_linewidth(1.5)
    
    ax.set_ylabel('Pass Rate (%)')
    ax.set_ylim(60, 85)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    fig.savefig('paper/fig_comparison.pdf', bbox_inches='tight')
```

### 完整示例：收敛/轨迹折线图

```python
with plt.style.context(style):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    
    passes = np.arange(1, 16)
    ours = [65, 72, 78, 82, 85, 87, 88, 89, 89.5, 90, 90, 90, 90, 90, 90]
    baseline = [65, 68, 70, 71, 69, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58]
    
    ax.plot(passes, ours, **STYLES[0], label='Ours', markersize=4)
    ax.plot(passes, baseline, **STYLES[1], label='Critique+Revise', markersize=4)
    
    # Mark convergence point
    ax.axvline(x=10, color='gray', linestyle=':', alpha=0.5, linewidth=0.8)
    ax.annotate('Converged', xy=(10, 90), fontsize=8, ha='center',
                xytext=(10, 93), arrowprops=dict(arrowstyle='->', color='gray'))
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Quality Score')
    ax.legend(loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    fig.savefig('paper/fig_trajectory.pdf', bbox_inches='tight')
```

### 输出规则

- **始终以 PDF 格式保存**：`fig.savefig('fig.pdf')` —— 向量图形，无论放大多少倍都保持清晰
- **切勿将用于打印的图表保存为 PNG 格式**——光栅格式的 PNG 在打印或放大时会出现模糊现象
- **例外情况**：截图、照片或像素艺术风格的可视化内容 → 可以使用 600 DPI 的 PNG 格式
- **验证灰度效果**：将图表打印为灰度 PDF，确认所有信息依然清晰可见

### 常见对比场景的图表类型

| 对比类型 | 图表类型 | 备注 |
|----------|----------|------|
| 不同方法之间的对比 | 分组柱状图 | 需包含误差条 |
| 不同模型规模间的对比 | 带置信区间带的折线图 | 模型规模轴建议使用对数刻度 |
| 消融实验 | 叠加/分组柱状图 | 需突出显示被移除的组件 |
| 趋势/收敛情况 | 迭代过程中的折线图 | 需展示每次迭代中的最优结果 |
| 各任务的性能差异 | 热力图或分组柱状图 | 需显示不同任务间的差异程度 |
