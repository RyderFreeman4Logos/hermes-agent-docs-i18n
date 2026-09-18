---
title: "Research Paper Writing — Write ML papers for NeurIPS/ICML/ICLR: design→submit"
sidebar_label: "Research Paper Writing"
description: "Write ML papers for NeurIPS/ICML/ICLR: design→submit"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 研究论文撰写

帮助用户为 NeurIPS/ICML/ICLR 等会议撰写机器学习论文：从设计到投稿全程支持。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/research/research-paper-writing` |
| 版本 | `1.1.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `semanticscholar`, `arxiv`, `habanero`, `requests`, `scipy`, `numpy`, `matplotlib`, `SciencePlots` |
| 支持平台 | linux, macos |
| 标签 | `研究`, `论文撰写`, `实验设计`, `机器学习`, `人工智能`, `NeurIPS`, `ICML`, `ICLR`, `ACL`, `AAAI`, `COLM`, `LaTeX`, `引用管理`, `统计分析` |
| 相关技能 | [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv), [`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development), `plan`（即内置的 `/plan` 命令） |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，智能体将依据此内容执行相应操作。
:::

# 研究论文撰写全流程

专为面向 **NeurIPS、ICML、ICLR、ACL、AAAI 和 COLM** 等会议发表而设计的端到端机器学习/人工智能研究论文撰写流程。该技能覆盖了从实验设计、执行与监控、数据分析，到论文撰写、审稿、修改直至最终投稿的完整研究生命周期。

这并非**线性的处理流程**，而是一个循环迭代的过程。实验结果会触发新的实验，审核反馈又会引发进一步的分析。智能体必须能够处理这些反馈循环。
```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 2: Experiment     Phase 5: Paper Drafting ◄──┐      │
│       Design                     │                   │      │
│       │                          ▼                   │      │
│       ▼                    Phase 6: Self-Review      │      │
│  Phase 3: Execution &           & Revision ──────────┘      │
│       Monitoring                 │                          │
│       │                          ▼                          │
│       ▼                    Phase 7: Submission               │
│  Phase 4: Analysis ─────► (feeds back to Phase 2 or 5)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
## 何时使用此技能

在以下情况下可使用此技能：
- 基于现有代码库或创意**启动新的研究论文撰写**
- **设计并执行实验**以支撑论文中的论点
- **撰写或修改**研究论文的任何部分
- 为向特定会议或研讨会**提交论文**做准备
- 通过补充实验或修改内容来**回应审稿意见**
- 在不同会议格式之间**转换论文**
- 撰写**非实证类论文**——如理论论文、综述论文、基准测试论文或立场声明（详见[超越实证机器学习的论文类型](#paper-types-beyond-empirical-ml)）
- 为自然语言处理、人机交互或对齐研究**设计人工评估方案**
- 准备**论文被接收后的交付物**——如海报、演讲材料或代码发布

## 核心理念

1. **主动出击。** 提供完整的初稿，而非问题。科学家们十分忙碌——请先给出他们能够直接回应的具体内容，再逐步优化。
2. **绝不要编造引用信息。** 人工智能生成的引用错误率约为40%。务必通过编程方式获取引用信息。对于无法核实的引用，请标注为 `[CITATION NEEDED]`。
3. **论文即故事，而非实验集合。** 每篇论文都需用一句话清晰阐述其核心贡献。若无法做到这一点，说明该论文尚未成熟。
4. **实验应为论点服务。** 每项实验都必须明确指出其所支持的论点。切勿进行与论文整体论述无关的实验。
5. **尽早提交，频繁提交。** 每完成一批实验，或每次更新论文初稿，都应使用描述性信息进行提交。Git日志便是实验的历史记录。

### 主动性与协作

**默认原则：主动出击。先撰写初稿，再基于初稿提出问题。**

| 自信度等级 | 应对措施 |
|------------|----------|
| **高**（代码库结构清晰，贡献点明确） | 撰写完整初稿并提交，根据反馈进行优化 |
| **中**（存在部分模糊之处） | 撰写初稿时标明不确定的内容，随后继续完善 |
| **低**（存在重大未知因素） | 通过 `clarify` 提出1-2个针对性问题，之后再撰写初稿 |

| 章节 | 是否自动起草？ | 标记为草稿 |
|---------|-------------------|------------|
| 摘要 | 是 | “将贡献框架定义为X——如有需要可进行调整” |
| 引言 | 是 | “强调了问题Y——如不正确请予以修正” |
| 方法 | 是 | “包含了A、B、C等细节——补充缺失的内容” |
| 实验部分 | 是 | “突出了1、2、3这些结果——如需可重新排序” |
| 相关工作 | 是 | “引用了X、Y、Z这些论文——如我有遗漏请补充” |

**仅在以下情况才需要输入框**：目标发表平台不明确、存在多种相互矛盾的表述、实验结果似乎不完整，或收到明确要求先进行审阅时。

---

## 第0阶段：项目准备

**目标**：搭建工作环境、了解现有研究、明确本次贡献点。

### 步骤0.1：探索代码库

```bash
# Understand project structure
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

请查找以下文件：
- `README.md` — 项目概述与功能说明
- `results/`、`outputs/`、`experiments/` — 现有的研究结果
- `configs/` — 实验配置参数
- `.bib` 文件 — 现有的参考文献
以及各类草稿文档或笔记。

### 步骤 0.2：整理工作空间

建立统一的工作空间结构：

```
workspace/
  paper/               # LaTeX source, figures, compiled PDFs
  experiments/         # Experiment runner scripts
  code/                # Core method implementation
  results/             # Raw experiment results (auto-generated)
  tasks/               # Task/benchmark definitions
  human_eval/          # Human evaluation materials (if needed)
```

### 步骤 0.3：配置版本控制

```bash
git init  # if not already
git remote add origin <repo-url>
git checkout -b paper-draft  # or main
```

**Git 使用规范**：每批完成后的实验数据都需通过提交操作进行保存，并附上描述性信息。示例如下：
```
Add Monte Carlo constrained results (5 runs, Sonnet 4.6, policy memo task)
Add Haiku baseline comparison: autoreason vs refinement baselines at cheap model tier
```

### 步骤 0.4：明确贡献点

在开始撰写之前，先清晰阐述以下内容：
- **核心贡献是什么**：本文究竟带来了哪一项独特贡献？
- **依据何在**：有哪些证据可以支撑这一观点？
- **为何重要**：读者为何应该关注此内容？

> 可向科研人员提出如下建议：“据我理解，本文的主要贡献可概括为：[一句话]。关键研究结果为[Y]。这样的表述是否符合您的预期？”

### 步骤 0.5：制定待办清单

使用 `todo` 工具来创建结构化的项目计划：

```
Research Paper TODO:
- [ ] Define one-sentence contribution
- [ ] Literature review (related work + baselines)
- [ ] Design core experiments
- [ ] Run experiments
- [ ] Analyze results
- [ ] Write first draft
- [ ] Self-review (simulate reviewers)
- [ ] Revise based on review
- [ ] Submission prep
```

请在整个项目中统一更新此内容。它将作为跨会话的持久状态存在。

### 步骤 0.6：估算计算预算

在开始实验之前，先预估总成本与所需时间：

```
Compute Budget Checklist:
- [ ] API costs: (model price per token) × (estimated tokens per run) × (number of runs)
- [ ] GPU hours: (time per experiment) × (number of experiments) × (number of seeds)
- [ ] Human evaluation costs: (annotators) × (hours) × (hourly rate)
- [ ] Total budget ceiling and contingency (add 30-50% for reruns)
```

在实验运行过程中追踪实际支出情况：
```python
# Simple cost tracker pattern
import json, os
from datetime import datetime

COST_LOG = "results/cost_log.jsonl"

def log_cost(experiment: str, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "experiment": experiment,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }
    with open(COST_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**预算紧张时**：在开展大规模测试之前，先进行试点实验（使用1-2个样本及部分任务）。在调试流程时可使用成本较低的模型，最终运行时再切换为目标模型。

### 步骤 0.7：多作者协作

大多数论文的作者数量为3至10人。建议尽早制定协作流程：

| 协作流程 | 工具 | 适用场景 |
|----------|------|----------|
| **Overleaf** | 基于浏览器的工具 | 多位作者需同时编辑，且没有Git使用经验 |
| **Git + LaTeX** | 配备`.gitignore`规则用于管理辅助文件的`git` | 技术团队，需要基于分支的代码审查功能 |
| **Overleaf + Git同步** | Overleaf高级版 | 结合两者优势——支持实时协作并保留版本历史记录 |

**章节负责制**：为每个章节指定一名主要作者，其他成员仅可评论，不得直接修改内容。这样能有效避免合并冲突和风格不一致的问题。

```
Author Coordination Checklist:
- [ ] Agree on section ownership (who writes what)
- [ ] Set up shared workspace (Overleaf or git repo)
- [ ] Establish notation conventions (before anyone writes)
- [ ] Schedule internal review rounds (not just at the end)
- [ ] Designate one person for final formatting pass
- [ ] Agree on figure style (colors, fonts, sizes) before creating figures
```

**需提前确定的 LaTeX 格式规范**：
- 使用 `\method{}` 宏以确保方法名称的一致性
- 引用格式：区分 `\citet{}` 与 `\citep{}` 的使用方式
- 数学符号：向量用小写粗体，矩阵用大写粗体等
- 英式拼写与美式拼写的选择

---

## 第一阶段：文献综述

**目标**：查找相关研究、确定基准方法、收集引用文献。

### 步骤 1.1：筛选初始参考论文

从代码库中已存在的参考文献开始入手：

```bash
# Via terminal:
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

### 第 1.2 步：搜索相关研究

为结构化查找论文，请**加载 `arxiv` 技能**：`skill_view("arxiv")`。该技能可支持通过 arXiv REST API 进行搜索、获取 Semantic Scholar 的引用关系图、作者简介以及生成 BibTeX 格式。

如需进行广泛检索，可使用 `web_search`；若要获取特定论文，则可使用 `web_extract`：

```
# Via web_search:
web_search("[main technique] + [application domain] site:arxiv.org")
web_search("[baseline method] comparison ICML NeurIPS 2024")

# Via web_extract (for specific papers):
web_extract("https://arxiv.org/abs/2303.17651")
```

可尝试的其他搜索查询：

```
Search queries:
- "[main technique] + [application domain]"
- "[baseline method] comparison"
- "[problem name] state-of-the-art"
- Author names from existing citations
```

**推荐**：为实现实时学术搜索，请安装 **Exa MCP**：
```bash
claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"
```

### 第1.2b步：深入搜索（先广度后深度）

单纯的平面搜索（仅进行一轮查询）往往无法发现重要的相关研究。建议采用受深度研究流程启发的迭代式**先广度后深度**策略：

```
Iterative Literature Search:

Round 1 (Breadth): 4-6 parallel queries covering different angles
  - "[method] + [domain]"
  - "[problem name] state-of-the-art 2024 2025"
  - "[baseline method] comparison"
  - "[alternative approach] vs [your approach]"
  → Collect papers, extract key concepts and terminology

Round 2 (Depth): Generate follow-up queries from Round 1 learnings
  - New terminology discovered in Round 1 papers
  - Papers cited by the most relevant Round 1 results
  - Contradictory findings that need investigation
  → Collect papers, identify remaining gaps

Round 3 (Targeted): Fill specific gaps
  - Missing baselines identified in Rounds 1-2
  - Concurrent work (last 6 months, same problem)
  - Key negative results or failed approaches
  → Stop when new queries return mostly papers you've already seen
```

**何时停止搜索**：如果某一轮次返回的论文中有超过80%已存在于您的收藏中，说明搜索已达到饱和状态。通常2-3轮即可完成目标，而对于综述类论文，则可能需要4-5轮。

**针对基于智能体的工作流**：可通过`delegate_task`功能并行委托每一轮次的查询任务。收集结果后进行去重处理，再结合这些信息生成下一轮的查询条件。

### 步骤1.3：验证每条引用

**绝不可凭记忆生成BibTeX格式，必须通过编程方式获取。**

对于每条引用，都必须遵循以下5个必经步骤：

```
Citation Verification (MANDATORY per citation):
1. SEARCH → Query Semantic Scholar or Exa MCP with specific keywords
2. VERIFY → Confirm paper exists in 2+ sources (Semantic Scholar + arXiv/CrossRef)
3. RETRIEVE → Get BibTeX via DOI content negotiation (programmatically, not from memory)
4. VALIDATE → Confirm the claim you're citing actually appears in the paper
5. ADD → Add verified BibTeX to bibliography
If ANY step fails → mark as [CITATION NEEDED], inform scientist
```

```python
# Fetch BibTeX via DOI
import requests

def doi_to_bibtex(doi: str) -> str:
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text
```

如果无法验证某条引用：

```latex
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: Verify this citation exists
```

**务必告知科研人员**：“我已将[X]处引用标记为需要核实的占位符。”

如需查看完整的API文档及`CitationManager`类的全部实现，可参阅[references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md)。

### 第1.4步：整理相关研究

应按方法论对论文进行归类，而非逐篇处理：

**正确示例**：“有一系列研究采用了X的假设[refs]，而我们采用Y的假设，原因是……”
**错误示例**：“Smith等人提出了X。Jones等人提出了Y。我们将两者结合使用。”

---

## 第2阶段：实验设计

**目标**：设计能够直接支撑论文论点的实验。每个实验都必须针对一个具体问题展开。

### 第2.1步：将论点与实验对应起来

建立明确的映射关系：

| 论点 | 实验 | 预期证据 |
|-------|-----------|-------------------|
| “我们的方法优于基准方法” | 主要对比实验（表1） | 胜率、统计显著性 |
| “在较弱模型上效果更显著” | 模型规模扩展研究 | 单调提升曲线 |
| “收敛需要范围约束” | 有约束与无约束条件对比 | 收敛速度比较 |

**规则**：如果某个实验无法对应到任何论点，则不应执行该实验。

### 第2.2步：设计基准方法

强大的基准方法往往是决定论文能否被接受的关键。审稿人往往会询问：“他们是否与X进行了对比？”

常见的基准方法类别：
- **朴素基线**：最简单的实现方式  
- **强基线**：目前最为成熟的现有方法  
- **消融基线**：在您的方法中移除某一组件后的版本  
- **计算资源匹配基线**：保持相同的计算预算，但调整资源分配方式  

### 2.3步：定义评估方案  

在开始任何实验之前，需明确以下内容：  
- **指标**：需要测量的内容以及方向性符号（数值越高/越低越好）  
- **聚合方式**：如何将多次运行或任务的结果进行整合  
- **统计检验**：用于判定结果显著性的检验方法  
- **样本量**：需要进行的运行、问题或任务的数量  

### 2.4步：编写实验脚本  

参考成功的研究流程中的以下规范：  

**逐步保存**——在每一步之后保存结果，以便在出现故障时能够恢复数据：
```python
# Save after each problem/task
result_path = f"results/{task}/{strategy}/result.json"
if os.path.exists(result_path):
    continue  # Skip already-completed work
# ... run experiment ...
with open(result_path, 'w') as f:
    json.dump(result, f, indent=2)
```

**工件保存**——存储所有中间输出结果：
```
results/<experiment>/
  <task>/
    <strategy>/
      final_output.md          # Final result
      history.json             # Full trajectory
      pass_01/                 # Per-iteration artifacts
        version_a.md
        version_b.md
        critic.md
```

**职责分离**——将生成、评估与可视化功能分开处理：
```
run_experiment.py              # Core experiment runner
run_baselines.py               # Baseline comparison
run_comparison_judge.py        # Blind evaluation
analyze_results.py             # Statistical analysis
make_charts.py                 # Visualization
```

如需了解完整的设计模式、定时监控以及错误恢复机制，请参阅 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md)。

### 第 2.5 步：设计人工评估（如适用）

许多自然语言处理、人机交互以及对齐相关的研究论文都需要以人工评估作为主要或补充证据。在开展自动化实验之前就应先规划好人工评估环节——因为人工评估往往需要更长的准备时间（如获得伦理委员会批准、招募评估员等）。

**何时需要进行人工评估：**
- 自动化指标无法体现您关注的关键要素（流畅性、实用性、安全性）
- 您的研究成果侧重于面向用户的品质（可读性、用户偏好、信任度）
- 在自然语言处理领域的重要会议（如 ACL、EMNLP）上，审稿人通常要求对生成式任务进行人工评估

**关键设计决策：**

| 决策项 | 可选方案 | 建议 |
|--------|----------|------|
| **评估员类型** | 专家、众包工作者、最终用户 | 根据研究需求选择合适的类型 |
| **评估方式** | 利克特量表（1-5 分）、成对比较、排序 | 对于大型语言模型生成的文本，成对比较比利克特量表更可靠 |
| **样本量** | 每位评估员的评估数量及总评估项数 | 可通过功效分析确定，建议至少 100 个评估项，由 3 名及以上评估员完成 |
| **一致性指标** | 科恩卡帕值、克里彭多夫阿尔法值、ICC 值 | 当评估员超过 2 名时使用克里彭多夫阿尔法值；同时需报告原始的一致性数据 |
| **平台选择** | Prolific、MTurk、内部团队 | 追求高质量评估可选 Prolific；大规模评估可使用 MTurk；需要领域专业知识的评估可交由内部团队完成 |

**标注指南检查清单：**
```
- [ ] Clear task description with examples (good AND bad)
- [ ] Decision criteria for ambiguous cases
- [ ] At least 2 worked examples per category
- [ ] Attention checks / gold standard items (10-15% of total)
- [ ] Qualification task or screening round
- [ ] Estimated time per item and fair compensation (>= local minimum wage)
- [ ] IRB/ethics review if required by your institution
```

**报告要求**（审核人员需检查以下所有内容）：
- 注解员人数及其资质
- 使用特定指标和数值计算的注解员间一致性
- 报酬详情（金额、预计时薪）
- 注解界面描述或截图（见附录）
- 总注解时长

如需包含针对人工评估数据的统计检验方法、众包质量控制策略以及机构审查委员会相关指导的完整指南，请参阅 [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md)。

---

## 第三阶段：实验执行与监控

**目标**：可靠地运行实验，监控进展，并从故障中恢复。

### 步骤 3.1：启动实验

对于需要长时间运行的实验，请使用 `nohup` 命令：

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!  # Record the PID
```

**并行执行**：可同时运行多个独立的实验，但需注意 API 的调用频率限制。同一 API 上同时进行的实验数量超过 4 个时，会降低所有实验的运行速度。

### 第 3.2 步：设置监控（Cron 表达式）

对于需要长时间运行的实验，应设置定期状态检查。Cron 表达式应遵循以下格式：

```
Monitor Prompt Template:
1. Check if process is still running: ps aux | grep <pattern>
2. Read last 30 lines of log: tail -30 <logfile>
3. Check for completed results: ls <result_dir>
4. If results exist, read and report: cat <result_file>
5. If all done, commit: git add -A && git commit -m "<descriptive message>" && git push
6. Report in structured format (tables with key metrics)
7. Answer the key analytical question for this experiment
```

**静默模式**：如果自上次检查以来没有发生变化，则回复 `[SILENT]` 以抑制对用户的通知。仅在有新变化时才进行报告。

### 第 3.3 步：处理故障

常见的故障类型及恢复方法：

| 故障类型 | 检测方式 | 恢复方法 |
|---------|-----------|----------|
| API 速率限制/额度耗尽 | 日志中出现 402/429 错误 | 等待片刻后重新运行（脚本会跳过已完成的工作） |
| 进程崩溃 | PID 失效，结果不完整 | 从上一个检查点重新运行 |
| 复杂问题超时 | 进程卡住，无日志进度更新 | 终止进程并跳过该任务，在结果中记录说明 |
| 模型 ID 错误 | 错误信息中提到错误的模型名称 | 更正 ID 后重新运行 |

**关键点**：脚本应始终检查现有结果并跳过已完成的工作。这样既能保证重新运行的安全性，又能提升效率。

### 第 3.4 步：提交已完成的结果

在每批实验完成后：

```bash
git add -A
git commit -m "Add <experiment name>: <key finding in 1 line>"
git push
```

### 第 3.5 步：维护实验日志

Git 提交记录可以追踪所发生的一切，但却无法呈现**探索路径**——即根据已获得的经验来决定下一步该尝试什么的内容。因此，应维护一份结构化的实验日志，以便完整记录这一探索路径。

```json
// experiment_journal.jsonl — append one entry per experiment attempt
{
  "id": "exp_003",
  "parent": "exp_001",
  "timestamp": "2025-05-10T14:30:00Z",
  "hypothesis": "Adding scope constraints will fix convergence failure from exp_001",
  "plan": "Re-run autoreason with max_tokens=2000 and fixed structure template",
  "config": {"model": "haiku", "strategy": "autoreason", "max_tokens": 2000},
  "status": "completed",
  "result_path": "results/exp_003/",
  "key_metrics": {"win_rate": 0.85, "convergence_rounds": 3},
  "analysis": "Scope constraints fixed convergence. Win rate jumped from 0.42 to 0.85.",
  "next_steps": ["Try same constraints on Sonnet", "Test without structure template"],
  "figures": ["figures/exp003_convergence.pdf"]
}
```

**为何要使用日志而非仅依赖 Git？** Git 用于追踪文件更改，而日志则用于记录决策过程：为何尝试了某种方法、从中获得了哪些经验，以及这些经验对后续实验有何启示。在撰写论文时，这样的记录对于“方法”部分（如“我们观察到了 X，这促使我们采用了 Y 方法”）以及如实报告失败案例而言具有不可替代的价值。

**选择最佳路径**：当日志显示出分支结构（exp_001 → exp_002a、exp_002b、exp_003）时，应挑选最能支撑论文论点的路径。可将那些无果可循的分支作为对比实验或负面结果记录在附录中。

**为每个实验保存代码快照**：每次运行实验后，都复制相应的脚本文件。
```bash
cp experiment.py results/exp_003/experiment_snapshot.py
```
这样一来，即便后续对代码进行修改，也能实现完全一致的复现效果。

```python
# Standard analysis pattern
import json, os
from pathlib import Path

results = {}
for result_file in Path("results/").rglob("result.json"):
    data = json.loads(result_file.read_text())
    strategy = result_file.parent.name
    task = result_file.parent.parent.name
    results.setdefault(strategy, {})[task] = data

# Compute aggregate metrics
for strategy, tasks in results.items():
    scores = [t["score"] for t in tasks.values()]
    print(f"{strategy}: mean={np.mean(scores):.1f}, std={np.std(scores):.1f}")
```

### 第 4.2 步：统计显著性分析

务必计算以下内容：
- **误差条**：标准差或标准误，需明确说明使用哪种
- **置信区间**：关键结果的 95% 置信区间
- **成对检验**：用于比较两种方法的 McNemar 检验
- **效应量**：用于衡量实际意义程度的 Cohen’s d 或 Cohen’s h

有关 McNemar 检验、自助法置信区间以及 Cohen’s h 的完整实现方式，请参阅 [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md) 文档。

### 第 4.3 步：明确研究核心内容

分析完成后，需明确回答以下问题：
1. **主要发现是什么？** 用一句话概括。
2. **有什么让你感到意外？** 出乎意料的结果往往能构成最优秀的论文。
3. **哪些实验失败了？** 失败的实验往往能提供最多启示。如实报告失败情况有助于提升论文质量。
4. **还需要进行哪些后续实验？** 研究结果常常会引发新的问题。

#### 处理阴性或无效结果

当假设不成立或研究结果无显著性时，你有三种选择：

| 情境 | 应对措施 | 适合发表的会议/平台 |
|------|----------|-------------------|
| 假设错误，但能阐明**原因** | 围绕对原因的分析来撰写论文 | NeurIPS、ICML（若分析严谨） |
| 方法虽未超越基准，但**揭示了新见解** | 将贡献重点定位为理解与分析 | ICLR（重视理论理解）、研讨会论文 |
| 对热门观点得到明确否定性结果 | 将其整理成文——领域内人士需要了解这些信息 | NeurIPS数据集与基准测试会议、TMLR、各类研讨会 |
| 结果模棱两可，缺乏清晰结论 | 调整策略——开展不同实验或重新构思研究方向 | 不要强行撰写本不该存在的论文 |

**如何撰写否定性结果论文：**
- 首先阐述学界当前的观点以及为何需要对其进行验证
- 详细说明严谨的研究方法（必须无懈可击——审稿人会更加严格审查）
- 用统计证据清晰呈现零结果
- 分析**为何**预期结果并未出现
- 讨论该结果对领域发展的影响

**明确欢迎提交否定性结果的会议/平台**：NeurIPS（数据集与基准测试分会场）、TMLR、ML可复现性挑战赛，以及各大会议举办的研讨会。部分研讨会还会专门征集否定性结果研究。

### 第4.4步：制作图表

**图表**：
- 所有绘图均使用矢量图形（PDF格式）：`plt.savefig('fig.pdf')`
- 选择对色盲友好的配色方案（Okabe-Ito或Paul Tol）
- 添加独立于正文的图注——读者无需阅读正文即可理解图表内容
- 图表内不应出现标题——图注承担此功能

**表格**：
- 使用 `booktabs` LaTeX 宏包  
- 将各项指标的最佳数值以粗体标出  
- 加入方向符号（数值越高/越低表示越好）  
- 保持小数位数一致

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
Method & Accuracy $\uparrow$ & Latency $\downarrow$ \\
\midrule
Baseline & 85.2 & 45ms \\
\textbf{Ours} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

### 第4.5步：决策——继续实验还是开始撰写？

| 情况 | 后续操作 |
|-----------|----------|
| 核心论点得到支持，且结果具有显著性 | 进入第5阶段（撰写） |
| 结果尚无定论，需要更多数据 | 回到第2阶段（设计） |
| 出现意外发现，提示新的研究方向 | 回到第2阶段（设计） |
| 缺少某个消融实验，审稿人会要求补充 | 先完成该实验，再进入第5阶段 |
| 所有实验均已完成，但部分实验失败 | 记录失败情况，然后进入第5阶段 |

### 第4.6步：撰写实验日志（为正文写作做准备）

在开始撰写论文之前，需先创建一份结构化的实验日志，用于将实验结果转化为文字描述。它是连接实验数据与论文正文的最为重要的纽带——若没有这份日志，写作智能体就不得不从原始结果文件中重新梳理研究内容。

请按照以下结构创建 `experiment_log.md` 文件：

```markdown
# Experiment Log

## Contribution (one sentence)
[The paper's main claim]

## Experiments Run

### Experiment 1: [Name]
- **Claim tested**: [Which paper claim this supports]
- **Setup**: [Model, dataset, config, number of runs]
- **Key result**: [One sentence with the number]
- **Result files**: results/exp1/final_info.json
- **Figures generated**: figures/exp1_comparison.pdf
- **Surprising findings**: [Anything unexpected]

### Experiment 2: [Name]
...

## Figures
| Filename | Description | Which section it belongs in |
|----------|-------------|---------------------------|
| figures/main_comparison.pdf | Bar chart comparing all methods on benchmark X | Results, Figure 2 |
| figures/ablation.pdf | Ablation removing components A, B, C | Results, Figure 3 |
...

## Failed Experiments (document for honesty)
- [What was tried, why it failed, what it tells us]

## Open Questions
- [Anything the results raised that the paper should address]
```

**为何如此重要**：在撰写初稿时，智能体（或被委派的子智能体）可以同时加载 `experiment_log.md` 与 LaTeX 模板，从而基于实际实验结果生成初稿。若没有这一桥梁，写作智能体就不得不解析原始的 JSON/CSV 文件并自行推断内容——而这正是导致数据失真或报告错误的高发原因。

**Git 使用规范**：将此日志文件与其描述的结果一起提交。

---

## 逐步优化：策略选择

该流程中的任何输出——论文初稿、实验脚本、分析报告——均可通过迭代方式不断优化。自动推理研究为各类优化策略的适用场景与失效条件提供了实证依据。请参考本节内容选择合适的优化方法。

### 快速决策表

| 您的应用场景 | 推荐策略 | 原因 |
|---------------|----------|-----|
| 中等性能模型 + 有约束的任务 | **Autoreason** | 此类场景最能发挥其优势。模型的生成能力与自我评估能力之间的差距最大，基准方法能有效优化那些表现较差的模型输出。 |
| 中等性能模型 + 无约束的任务 | 带有范围限制的 **Autoreason** | 通过设定固定事实、结构或输出要求，限定改进空间。 |
| 最先进模型 + 有约束的任务 | **Autoreason** | 即使使用最先进的模型，在有约束的任务中也能在2/3的情况下取得最佳效果。 |
| 最先进模型 + 无约束的任务 | **Critique-and-revise** 或 **Single pass** | 此类场景下Autoreason表现最差，因为模型自身的自我评估能力已经足够出色。 |
| 具体技术任务（如系统设计） | **Critique-and-revise** | 直接的“发现问题-修复问题”循环效率更高。 |
| 填写模板类任务（仅需一个正确结构） | **Single pass** 或 **Conservative** | 决策空间极小，迭代不会带来额外价值。 |
| 包含测试用例的代码 | **Autoreason (code variant)** | 先对代码失败的原因进行结构化分析，再加以修复。其修复成功率可达62%，而其他方法仅为43%。 |
| 性能极弱的模型（如Llama 8B级别） | **Single pass** | 这类模型能力太弱，无法生成多种候选方案，应优先提升代码的生成质量。 |

### 生成能力与自我评估能力之间的差距

**核心观点**：Autoreason的价值取决于模型在内容生成能力与自我评估能力之间的差距大小。
```
Model Tier        │ Generation │ Self-Eval │ Gap    │ Autoreason Value
──────────────────┼────────────┼───────────┼────────┼─────────────────
Weak (Llama 8B)   │ Poor       │ Poor      │ Small  │ None — can't generate diverse candidates
Mid (Haiku 3.5)   │ Decent     │ Poor      │ LARGE  │ MAXIMUM — 42/42 perfect Borda
Mid (Gemini Flash)│ Decent     │ Moderate  │ Large  │ High — wins 2/3
Strong (Sonnet 4) │ Good       │ Decent    │ Medium │ Moderate — wins 3/5
Frontier (S4.6)   │ Excellent  │ Good      │ Small  │ Only with constraints
```
这种差距是结构性的，而非暂时的。随着成本下降，如今的先进模型明日便可能沦为中等水平，但那个最佳平衡点始终存在，只是位置会发生变化。

### 自动推理循环（概述）

每次迭代都会从全新的独立智能体中生成三个候选方案：

1. **批评者** → 找出现有方案A的问题（不提供修复方案）
2. **作者B** → 根据批评意见对方案A进行修改
3. **合成器** → 合并方案A和B（标签随机分配）
4. **评审小组** → 3名盲评的链式思维评审员通过博尔达计数法对A、B及AB组合进行评分
5. **收敛判定** → 若方案A在连续k=2次迭代中均胜出，则流程结束

**关键参数：**
- k=2次迭代即视为收敛（k=1则收敛过早，k=3则成本过高且无法提升质量）
- 始终使用3名链式思维评审员（可加快3倍收敛速度）
- 作者的随机温度值为0.8，评审员的为0.3
- 保守的平局处理规则：若出现平局，则保留原有方案
- 每个角色均为独立的智能体，彼此之间不共享上下文信息

### 在论文初稿优化中的应用

通过自动推理功能对论文本身进行优化时：
- **为批评者提供真实依据**：包括实际的实验数据、结果JSON文件以及统计输出。若缺乏这些信息，模型就会编造虚假的消融实验和伪造的置信区间。
- **至少使用3名评审智能体**：若某个评审智能体的解析功能出现故障，不会仅产生噪声，而是会完全阻碍系统达到平衡状态。
- **明确限定修改范围**：应指定“针对这些具体缺陷进行改进”，而非笼统地要求“提升论文质量”。

### 失效模式

| 失败类型 | 检测方式 | 解决方案 |
|---------|-----------|---------|
| 无法收敛（A从未获胜） | 连续20次以上迭代后A的胜率仍低于15% | 为任务添加范围约束 |
| 合成偏差 | 单词数量无限制增长 | 对结构与输出结果设置限制 |
| 单次迭代性能下降 | 基线分数高于迭代后的输出结果 | 改为单次迭代模式；可能是模型强度不足 |
| 过拟合（代码） | 公开测试通过率高，但私有测试通过率低 | 除测试反馈外，还需使用结构化分析方法 |
| 评分工具故障 | 解析错误导致评审小组人数少于3人 | 继续之前需先修复解析器 |

如需完整的提示词、Borda评分规则、模型选择指南、范围约束设计模式以及计算预算参考信息，请参阅 [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md)。

---

## 第5阶段：论文初稿撰写

完整的初稿撰写流程（各章节顺序、LaTeX框架、图表规范、摘要与引言中的公式格式、相关研究部分的定位等）均记载在 `references/phase5-paper-drafting.md` 中——进入该阶段后请使用 `read_file` 函数加载该文件。同时可结合 `references/writing-guide.md` 了解正文层面的风格规范。

## 第6阶段：自我审阅与修改

**目标**：在提交前模拟评审流程，尽早发现不足之处。

### 步骤6.1：模拟评审（集成模式）

从多个角度生成评审意见。自动化研究流程（尤其是 SakanaAI 的 AI-Scientist 工具）带来的重要启示是：**通过元评审员进行集成式评审，所能产生的反馈意见比仅进行一次评审要精准得多。**

**第一步：生成 N 份独立的评审意见**（N=3-5）

可选用不同的模型或温度参数。每位评审员仅能看到论文内容，而无法看到其他人的评审意见。**默认采用负面倾向**——已有大量研究证明，大型语言模型在评估时存在明显的正面偏差。

```
You are an expert reviewer for [VENUE]. You are critical and thorough.
If a paper has weaknesses or you are unsure about a claim, flag it clearly
and reflect that in your scores. Do not give the benefit of the doubt.

Review this paper according to the official reviewer guidelines. Evaluate:

1. Soundness (are claims well-supported? are baselines fair and strong?)
2. Clarity (is the paper well-written? could an expert reproduce it?)
3. Significance (does this matter to the community?)
4. Originality (new insights, not just incremental combination?)

Provide your review as structured JSON:
{
  "summary": "2-3 sentence summary",
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1 (most critical)", "weakness 2", ...],
  "questions": ["question for authors 1", ...],
  "missing_references": ["paper that should be cited", ...],
  "soundness": 1-4,
  "presentation": 1-4,
  "contribution": 1-4,
  "overall": 1-10,
  "confidence": 1-5
}
```

**步骤 2：元评审（领域主席汇总）**

将所有 N 条评审提交给元评审员进行处理：

```
You are an Area Chair at [VENUE]. You have received [N] independent reviews
of a paper. Your job is to:

1. Identify consensus strengths and weaknesses across reviewers
2. Resolve disagreements by examining the paper directly
3. Produce a meta-review that represents the aggregate judgment
4. Use AVERAGED numerical scores across all reviews

Be conservative: if reviewers disagree on whether a weakness is serious,
treat it as serious until the authors address it.

Reviews:
[review_1]
[review_2]
...
```

**步骤3：反馈循环**（可选，进行2-3轮）

每位审稿人在查看综合评审意见后均可进一步完善自己的评审内容。可设置提前终止条件：若审稿人回复“我已完成评审”（即无需任何修改），则停止迭代。

**用于评审的模型选择**：即便论文最初是用性能较低的模型撰写的，也应优先使用性能最强的模型进行评审。审稿模型应与撰写模型分开选择。

**少样本校准**：如果条件允许，可提供1-2篇来自目标期刊的真实已发表评审意见作为示例。这能显著提升评分的准确性。相关示例请参阅[references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md)。

### 步骤6.1b：视觉审稿环节（VLM）

仅基于文本的审稿会遗漏一类问题：图表质量、排版问题以及视觉一致性。如果您拥有具备视觉处理能力的模型，可以对编译后的PDF文件进行单独的**视觉审稿**：

```
You are reviewing the visual presentation of this research paper PDF.
Check for:
1. Figure quality: Are plots readable? Labels legible? Colors distinguishable?
2. Figure-caption alignment: Does each caption accurately describe its figure?
3. Layout issues: Orphaned section headers, awkward page breaks, figures far from their references
4. Table formatting: Aligned columns, consistent decimal precision, bold for best results
5. Visual consistency: Same color scheme across all figures, consistent font sizes
6. Grayscale readability: Would the figures be understandable if printed in B&W?

For each issue, specify the page number and exact location.
```

该方法能够检测出基于文本审查无法发现的问题：轴标签难以辨认的图表、距离首次引用位置有三页之远的插图、图2与图5之间不统一的颜色方案，或是宽度明显超过列宽的表格。

### 第6.1c步：声明验证通过

在完成模拟审查后，需进行单独的验证流程。该步骤可发现审查人员可能忽略的事实性错误：

```
Claim Verification Protocol:
1. Extract every factual claim from the paper (numbers, comparisons, trends)
2. For each claim, trace it to the specific experiment/result that supports it
3. Verify the number in the paper matches the actual result file
4. Flag any claim without a traceable source as [VERIFY]
```

在基于智能体的工作流中：可将验证任务委托给一个**全新的子智能体**，该子智能体仅接收论文文本和原始结果文件。通过使用全新的上下文，可以避免确认偏误——验证者不会“记住”结果本应是什么样的。

### 6.2步：确定反馈优先级

收集完评审意见后，对它们进行分类：

| 优先级 | 操作措施 |
|--------|----------|
| **关键**（存在技术缺陷或缺失基准数据） | 必须修复。可能需要开展新的实验 → 回到第2阶段 |
| **高**（存在表述不清问题或缺少消融实验） | 应在本次修订中解决 |
| **中**（存在轻微的写作问题或需补充额外实验） | 若时间允许则进行修复 |
| **低**（涉及风格偏好或无关建议） | 记录下来以便日后处理 |

### 6.3步：修订循环

针对每一项关键/高优先级的问题：
1. 确定受影响的具体章节
2. 起草修复方案
3. 验证修复方案不会破坏其他论点
4. 更新论文内容
5. 根据评审者的意见再次检查

### 6.4步：撰写反驳意见

在提交论文后回应实际评审意见时，撰写反驳意见是一项与常规修订不同的专项技能：

**格式**：逐条回应。针对每位评审者的意见分别进行回复：
```
> R1-W1: "The paper lacks comparison with Method X."

We thank the reviewer for this suggestion. We have added a comparison with 
Method X in Table 3 (revised). Our method outperforms X by 3.2pp on [metric] 
(p<0.05). We note that X requires 2x our compute budget.
```

**规则**：
- 解决所有问题——若遗漏任何一点，审稿人都会察觉。
- 首先给出最有力的回应。
- 表达简洁明了——审稿人需要阅读大量反驳意见。
- 若在反驳期内进行了实验，需包含新的结果。
- 即使面对轻微的批评，也绝不能采取防御或轻视的态度。
- 使用 `latexdiff` 生成标出修改处的 PDF 文件（详见“专业 LaTeX 工具”部分）。
- 对于具体且具有可操作性的反馈，应向审稿人表示感谢（而非泛泛的表扬）。

**禁止的做法**：无依据地声称“我们坚决不同意”；不加解释地称“这超出了研究范围”；仅回应优点而忽视缺陷。

### 第 6.5 步：论文进展跟踪

在关键节点保存快照：
```
paper/
  paper.tex                    # Current working version
  paper_v1_first_draft.tex     # First complete draft
  paper_v2_post_review.tex     # After simulated review
  paper_v3_pre_submission.tex  # Final before submission
  paper_v4_camera_ready.tex    # Post-acceptance final
```

## 第7阶段：投稿准备

**目标**：最终核查、格式调整及正式提交。

### 步骤7.1：会议特定检查清单

各类会议均设有必填的检查清单。请务必仔细填写——若清单不完整，论文可能会被直接拒收。

相关内容详见 [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md)，包括：
- NeurIPS会议的16项论文检查清单
- ICML会议关于更大影响力与可复现性的要求
- ICLR会议关于大语言模型披露的政策
- ACL会议要求的限制条件部分
- 通用投稿前检查清单

### 步骤7.2：匿名化检查清单

由于采用双盲评审机制，审稿人无法知晓论文的作者身份。请逐一核对以下所有项目：

```
Anonymization Checklist:
- [ ] No author names or affiliations anywhere in the PDF
- [ ] No acknowledgments section (add after acceptance)
- [ ] Self-citations written in third person: "Smith et al. [1] showed..." not "We previously showed [1]..."
- [ ] No GitHub/GitLab URLs pointing to your personal repos
- [ ] Use Anonymous GitHub (https://anonymous.4open.science/) for code links
- [ ] No institutional logos or identifiers in figures
- [ ] No file metadata containing author names (check PDF properties)
- [ ] No "our previous work" or "in our earlier paper" phrasing
- [ ] Dataset names don't reveal institution (rename if needed)
- [ ] Supplementary materials don't contain identifying information
```

**常见错误**：补充代码中显示了 Git 提交信息、使用了机构工具添加的水印图片、遗留了先前草稿中的致谢内容，以及在匿名期结束前发布了 arXiv 预印本。

### 第 7.3 步：格式校验

```
Pre-Submission Format Check:
- [ ] Page limit respected (excluding references and appendix)
- [ ] All figures are vector (PDF) or high-res raster (600 DPI PNG)
- [ ] All figures readable in grayscale
- [ ] All tables use booktabs
- [ ] References compile correctly (no "?" in citations)
- [ ] No overfull hboxes in critical areas
- [ ] Appendix clearly labeled and separated
- [ ] Required sections present (limitations, broader impact, etc.)
```

### 第 7.4 步：预编译验证

在尝试运行 `pdflatex` 之前，先执行这些自动化检查。在此阶段发现错误比之后调试编译器输出要高效得多。

```bash
# 1. Lint with chktex (catches common LaTeX mistakes)
# Suppress noisy warnings: -n2 (sentence end), -n24 (parens), -n13 (intersentence), -n1 (command terminated)
chktex main.tex -q -n2 -n24 -n13 -n1

# 2. Verify all citations exist in .bib
# Extract \cite{...} from .tex, check each against .bib
python3 -c "
import re
tex = open('main.tex').read()
bib = open('references.bib').read()
cites = set(re.findall(r'\\\\cite[tp]?{([^}]+)}', tex))
for cite_group in cites:
    for cite in cite_group.split(','):
        cite = cite.strip()
        if cite and cite not in bib:
            print(f'WARNING: \\\\cite{{{cite}}} not found in references.bib')
"

# 3. Verify all referenced figures exist on disk
python3 -c "
import re, os
tex = open('main.tex').read()
figs = re.findall(r'\\\\includegraphics(?:\[.*?\])?{([^}]+)}', tex)
for fig in figs:
    if not os.path.exists(fig):
        print(f'WARNING: Figure file not found: {fig}')
"

# 4. Check for duplicate \label definitions
python3 -c "
import re
from collections import Counter
tex = open('main.tex').read()
labels = re.findall(r'\\\\label{([^}]+)}', tex)
dupes = {k: v for k, v in Counter(labels).items() if v > 1}
for label, count in dupes.items():
    print(f'WARNING: Duplicate label: {label} (appears {count} times)')
"
```

在继续操作之前，请先解决所有警告信息。对于基于智能体的工作流：需将 chktex 的检测结果反馈给智能体，并给出仅进行最小程度修复的指令。

### 第 7.5 步：最终编译

```bash
# Clean build
rm -f *.aux *.bbl *.blg *.log *.out *.pdf
latexmk -pdf main.tex

# Or manual (triple pdflatex + bibtex for cross-references)
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Verify output exists and has content
ls -la main.pdf
```

**如果编译失败**：请解析 `.log` 文件以找出首个错误。常见解决方案如下：
- “未定义的控制序列” → 缺少相关包或命令名称拼写有误
- “缺少插入的 $ 符号” → 数学符号位于数学模式之外
- “文件未找到” → 图片路径错误或缺少 `.sty` 文件
- “引用未定义” → 缺少对应的 `.bib` 条目或未运行 bibtex 工具

### 7.6步：会议特定要求

| 会议名称 | 特殊要求 |
|---------|----------|
| **NeurIPS** | 需在附录中列出论文检查清单，若被录用还需提供通俗版摘要 |
| **ICML** | 需提交更详细的“广泛影响声明”（置于结论之后，不计入字数限制） |
| **ICLR** | 需披露所使用的LLM模型信息，并签署互审协议 |
| **ACL** | 必须包含“局限性说明”部分，还需填写“负责任自然语言处理”检查清单 |
| **AAAI** | 风格文件有严格规定——严禁进行任何修改 |
| **COLM** | 需明确阐述该工作对语言模型领域的贡献 |

### 7.7步：会议重新投稿与格式转换

在不同会议模板之间转换时，**绝不可直接复制LaTeX文档的开头部分**：

```bash
# 1. Start fresh with target template
cp -r templates/icml2026/ new_submission/

# 2. Copy ONLY content sections (not preamble)
#    - Abstract text, section content, figures, tables, bib entries

# 3. Adjust for page limits
# 4. Add venue-specific required sections
# 5. Update references
```

| 从 → 到 | 页面调整 | 主要修改内容 |
|-----------|-------------|-----------------|
| NeurIPS → ICML | 9 → 8 | 删除1页内容，增加“更广泛的影响力”相关描述 |
| ICML → ICLR | 8 → 9 | 扩展实验部分，补充大语言模型相关说明 |
| NeurIPS → ACL | 9 → 8 | 按自然语言处理领域的规范重新组织结构，补充“局限性”章节 |
| ICLR → AAAI | 9 → 7 | 大幅删减内容，严格遵循格式要求 |
| 任意方向 → COLM | 不固定 → 9 | 重新调整内容重点，突出语言模型的应用 |

在删减页面时：可将证明性内容移至附录，精简相关研究综述，合并表格，使用子图。  
在扩展内容时：可增加消融实验，详细阐述局限性，补充更多基准测试结果，提供定性示例。

**被拒后**：在新版本中回应审稿人的意见，但不要添加“修改说明”章节，也不要提及之前的投稿内容（因采用盲审机制）。

### 第7.8步：准备最终提交版本（录用后）

论文被录用后，需准备最终提交版本：

```
Camera-Ready Checklist:
- [ ] De-anonymize: add author names, affiliations, email addresses
- [ ] Add Acknowledgments section (funding, compute grants, helpful reviewers)
- [ ] Add public code/data URL (real GitHub, not anonymous)
- [ ] Address any mandatory revisions from meta-reviewer
- [ ] Switch template to camera-ready mode (if applicable — e.g., AAAI \anon → \camera)
- [ ] Add copyright notice if required by venue
- [ ] Update any "anonymous" placeholders in text
- [ ] Verify final PDF compiles cleanly
- [ ] Check page limit for camera-ready (sometimes differs from submission)
- [ ] Upload supplementary materials (code, data, appendix) to venue portal
```

### 第7.9步：arXiv与预印本发布策略

在机器学习领域，将论文发布到arXiv是常见做法，但需注意时间选择和匿名性相关问题。

**时间决策树：**

| 情况 | 建议 |
|------|------|
| 向双盲评审会议投稿（如NeurIPS、ICML、ACL） | 应在提交截止日期**之后**再发布到arXiv，切勿提前。虽然不同会议的执行标准有所差异，但提前发布可能在技术上违反匿名性政策。 |
| 向ICLR投稿 | ICLR明确允许在提交前将论文发布到arXiv。但提交的论文中不得出现作者姓名。 |
| 论文已发布在arXiv上，现向其他会议投稿 | 大多数会议接受此类情况。但在审稿期间，切勿通过引用审稿意见的方式更新arXiv上的版本。 |
| 工作坊论文 | 任何时间发布到arXiv均可——因为工作坊通常不采用双盲评审机制。 |
| 希望抢占发表优先权 | 若担心被抢先发表，可立即发布——但需接受匿名性方面的妥协。 |

**arXiv分类选择**（针对机器学习/人工智能论文）：

| 分类 | 代码 | 适用领域 |
|------|------|----------|
| 机器学习 | `cs.LG` | 通用机器学习方法 |
| 计算与语言 | `cs.CL` | 自然语言处理、语言模型 |
| 人工智能 | `cs.AI` | 推理、规划、智能体技术 |
| 计算机视觉 | `cs.CV` | 视觉模型 |
| 信息检索 | `cs.IR` | 搜索系统、推荐算法 |

**请列出1个主要分类以及1-2个相关交叉分类。** 分类越多，论文的曝光度越高，但只有真正相关的分类才建议交叉标注。

**版本管理策略：**
- **v1版本**：首次提交（格式与会议投稿要求一致）  
- **v2版本**：论文被接收后进行最终润色并准备发表的版本（需在摘要中注明“已被[会议地点]录用”）  
请注意，在审稿期间切勿提交已针对审稿人意见作出明显修改的v2版本。

```bash
# Check if your paper's title is already taken on arXiv
# (before choosing a title)
pip install arxiv
python -c "
import arxiv
results = list(arxiv.Search(query='ti:\"Your Exact Title\"', max_results=5).results())
print(f'Found {len(results)} matches')
for r in results: print(f'  {r.title} ({r.published.year})')
"
```

### 第 7.10 步：代码打包研究

发布结构清晰、可直接运行的代码，能有效提升被引频次并增强审稿人的信任度。请将代码与最终提交版本一同打包。

**仓库结构：**

```
your-method/
  README.md              # Setup, usage, reproduction instructions
  requirements.txt       # Or environment.yml for conda
  setup.py               # For pip-installable packages
  LICENSE                # MIT or Apache 2.0 recommended for research
  configs/               # Experiment configurations
  src/                   # Core method implementation
  scripts/               # Training, evaluation, analysis scripts
    train.py
    evaluate.py
    reproduce_table1.sh  # One script per main result
  data/                  # Small data or download scripts
    download_data.sh
  results/               # Expected outputs for verification
```

**研究代码的README模板：**

```markdown
# [Paper Title]

Official implementation of "[Paper Title]" (Venue Year).

## Setup
[Exact commands to set up environment]

## Reproduction
To reproduce Table 1: `bash scripts/reproduce_table1.sh`
To reproduce Figure 2: `python scripts/make_figure2.py`

## Citation
[BibTeX entry]
```

**预发布检查清单：**
```
- [ ] Code runs from a clean clone (test on fresh machine or Docker)
- [ ] All dependencies pinned to specific versions
- [ ] No hardcoded absolute paths
- [ ] No API keys, credentials, or personal data in repo
- [ ] README covers setup, reproduction, and citation
- [ ] LICENSE file present (MIT or Apache 2.0 for max reuse)
- [ ] Results are reproducible within expected variance
- [ ] .gitignore excludes data files, checkpoints, logs
```

**待提交的无名代码**（在通过审核之前）：


请完整翻译整个输入内容，切勿提前终止。
```bash
# Use Anonymous GitHub for double-blind review
# https://anonymous.4open.science/
# Upload your repo → get an anonymous URL → put in paper
```

## 第8阶段：验收后的交付物

**目标**：通过演示材料与社区互动，最大化已获接受的论文的影响力。

### 步骤8.1：会议海报

大多数会议都要求设置海报展示环节。海报设计原则如下：

| 元素 | 设计指南 |
|---------|----------|
| **尺寸** | 需符合会议场地要求（通常为24英寸×36英寸或A0竖版/横版） |
| **内容** | 标题、作者姓名、一句话概括研究贡献、方法示意图、2-3项关键结果以及结论 |
| **排版逻辑** | 从左上角到右下角（Z型排列）或分栏布局 |
| **文字要求** | 标题需在3米距离处仍清晰可读，正文则在1米距离处可辨。不得使用完整段落，仅可使用项目符号 |
| **图表要求** | 可使用论文中的图表，但需提高分辨率；关键结果部分应放大展示 |

**常用工具**：LaTeX（`beamerposter`插件）、PowerPoint/Keynote、Figma、Canva。

**制作时间**：建议在会议开始前2周以上完成制作。帆布材质的海报更轻便，便于携带。如今许多会议也支持虚拟/数字海报形式。

### 步骤8.2：会议演讲/专题汇报

如果获得口头报告或专题汇报机会：

| 演讲类型 | 时长 | 内容要点 |
|---------|------|----------|
| **专题汇报** | 5分钟 | 阐述问题、研究方法以及一项关键结果。需严格控制在5分钟内完成 |
| **口头报告** | 15-20分钟 | 完整阐述研究全貌：包括问题提出、研究方法、关键结果、对比实验以及局限性分析 |
| **研讨会报告** | 10-15分钟 | 需根据研讨会听众的特点调整内容，可能需要补充更多背景信息 |

**幻灯片设计规则：**
- 每张幻灯片只呈现一个核心观点  
- 减少文字内容——详细内容需口头阐述，而非展示在幻灯片中  
- 通过动画逐步呈现关键数据，帮助听众逐步理解  
- 在最后添加一张“总结”幻灯片（用一句话概括核心要点）  
- 为可能出现的疑问准备备用幻灯片  

### 第8.3步：撰写博客文章/社交媒体内容  

简洁易懂的总结能显著提升传播效果：  

- **Twitter/X系列推文**：5-8条推文。先介绍研究成果，再说明方法；需包含图1及关键结果图表。  
- **博客文章**：字数在800-1500字之间。面向机器学习从业者撰写，而非评审专家；无需过度追求形式化，应侧重直观性和实际应用价值。  
- **项目页面**：包含摘要、图表、演示示例、代码链接及BibTeX格式的HTML页面，建议使用GitHub Pages搭建。  

**时间安排**：在论文被收录到会议论文集或发布在arXiv预印本平台后的1-2天内发布内容。  

---

## 研讨会论文与短篇论文  

研讨会论文及短篇论文（如ACL短篇论文、Findings系列论文）遵循相同的处理流程，但存在不同的要求与期望。  

### 研讨会论文

| 属性 | 研讨会论文 | 主会议论文 |
|------|----------|------------|
| **页数限制** | 通常为4-6页 | 7-9页 |
| **评审标准** | 对完整性要求较低 | 必须完整且详尽 |
| **评审流程** | 一般为单盲或轻度盲审 | 双盲且严格评审 |
| **重视内容** | 创意新颖的想法、初步结果、观点性文章 | 具有扎实基线数据的完整实证研究 |
| **arXiv投稿** | 随时可投 | 时间选择很重要（参见arXiv投稿策略） |
| **贡献要求** | 新颖的研究方向、有趣的负面结果、进行中的研究 | 具有有力证据的重大进展 |

**何时选择研讨会论文：**
- 处于早期阶段，希望在撰写完整论文前获取反馈的想法
- 无法用8页以上篇幅充分阐述的负面研究结果
- 关于当前热点话题的观点性文章或评论
- 复现研究或可重复性报告

### ACL短篇论文与发现类论文

ACL会议设有不同的投稿类型：

| 类型 | 页数 | 预期内容 |
|------|------|----------|
| **长篇论文** | 8页 | 完整的研究内容、扎实的基线数据及实验对比分析 |
| **短篇论文** | 4页 | 焦点明确的贡献：一个有证据支撑的清晰观点 |
| **发现类论文** | 8页 | 虽未达到主会议标准，但依然具有较高学术价值的成果 |

**短篇论文写作策略**：选定一个核心论点并予以充分论证。不要试图将长篇论文的内容压缩到4页内——应另起一篇更为聚焦的论文。

---

## 非实证机器学习领域的论文类型

上述主要流程适用于实证型机器学习论文。其他类型的论文则需要不同的结构与证据标准。有关各类论文的详细指导，请参阅 [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md)。

### 理论论文

**结构**：引言 → 基础知识（定义、符号）→ 主要结果（定理）→ 证明概要 → 讨论 → 完整证明（附录）

**与实证论文的主要区别**：
- 研究贡献表现为定理、界限或反例——而非实验数据
- “方法”部分被“基础知识”和“主要结果”取代
- 证据为证明而非实验结果（尽管对理论进行实证验证也是可接受的）
- 正文提供证明概要，完整证明放在附录中是常见做法
- 实验部分为可选内容，但若能验证理论预测则能增强论文说服力

**证明撰写原则**：
- 以正式方式陈述定理，并明确列出所有假设
- 在正式证明之前给出直观解释（“关键思路在于……”）
- 证明概要应在0.5至1页内阐述核心思想
- 使用 `\begin{proof}...\end{proof}` 格式
- 为假设编号并在定理中引用：“在假设1-3的前提下，……”

### 综述/教程类论文

**结构**：引言 → 分类/框架 → 详细内容覆盖 → 待解决问题 → 结论

**主要区别**：
- 贡献在于对现有开放问题的整理、归纳与识别，而非提出新方法  
- 内容必须在研究范围内做到全面详尽（审稿人会检查是否存在遗漏的参考文献）  
- 需要明确的分类体系或结构框架  
- 其价值体现在不同研究成果之间的关联，而这些关联是单篇论文难以实现的  
- 最适合发表的期刊/会议：《TMLR》（综述栏目）、《JMLR》、《机器学习基础与趋势》、《ACM计算调查》  

### 基准测试论文  

**结构**：引言 → 任务定义 → 数据集构建 → 基线评估 → 分析 → 预期用途与局限性  

**主要区别**：  
- 贡献在于基准测试本身——它必须填补真正的评估空白  
- 数据集文档是必需项，而非可选项（参见数据表，第5.11步）  
- 需证明该基准测试具有挑战性（基线方法无法轻松完成测试）  
- 需证明该基准测试确实能衡量其所宣称的指标（结构效度）  
- 最适合发表的期刊/会议：NeurIPS“数据集与基准测试”栏目、ACL（资源论文栏目）、LREC-COLING  

### 立场论文  

**结构**：引言 → 背景 → 论点/主张 → 支持证据 → 反驳观点 → 后续影响  

**主要区别**：  
- 贡献在于论点本身，而非实验结果  
- 需认真回应各种反驳观点  
- 证据可以是实证数据、理论分析或逻辑推导  
- 最适合发表的期刊/会议：ICML（立场论文栏目）、各类研讨会、《TMLR》  

---

## Hermes Agent集成

该技能专为Hermes智能体设计，它借助Hermes提供的工具、任务委派功能、调度机制以及内存管理能力，助力完成完整的研究全流程。

### 相关技能

可与其他Hermes技能组合使用，以覆盖研究的不同阶段：

| 技能 | 适用阶段 | 调用方式 |
|-------|---------|----------|
| **arxiv** | 第1阶段（文献综述）：检索arXiv数据库、生成BibTeX格式引用、通过Semantic Scholar查找相关论文 | `skill_view("arxiv")` |
| **subagent-driven-development** | 第5阶段（初稿撰写）：支持分阶段评审的并行章节写作（先核查是否符合规范，再评估内容质量） | `skill_view("subagent-driven-development")` |
| **plan** | 第0阶段（准备阶段）：在执行任务前制定结构化计划，计划内容会保存在`.hermes/plans/`目录中 | `skill_view("plan")` |
| **qmd** | 第1阶段（文献调研）：通过BM25与向量搜索相结合的方式，检索本地知识库中的资料（笔记、记录文档等） | 安装方式：`skill_manage("install", "qmd")` |
| **diagramming** | 第4-5阶段：用于生成基于Excalidraw的图表及架构图 | `skill_view("diagramming")` |
| **data-science** | 第4阶段（分析阶段）：提供Jupyter实时内核，支持交互式分析与数据可视化 | `skill_view("data-science")` |

**该技能已取代`ml-paper-writing`**——它不仅包含后者所有的功能，还进一步整合了完整的实验/分析流程以及自动推理方法。

### Hermes工具参考手册

| Tool | Usage in This Pipeline |
|------|----------------------|
| **`terminal`** | LaTeX compilation (`latexmk -pdf`), git operations, launching experiments (`nohup python run.py &`), process checks |
| **`process`** | Background experiment management: `process("start", ...)`, `process("poll", pid)`, `process("log", pid)`, `process("kill", pid)` |
| **`execute_code`** | Run Python for citation verification, statistical analysis, data aggregation. Has tool access via RPC. |
| **`read_file`** / **`write_file`** / **`patch`** | Paper editing, experiment scripts, result files. Use `patch` for targeted edits to large .tex files. |
| **`web_search`** | Literature discovery: `web_search("transformer attention mechanism 2024")` |
| **`web_extract`** | Fetch paper content, verify citations: `web_extract("https://arxiv.org/abs/2303.17651")` |
| **`delegate_task`** | **Parallel section drafting** — spawn isolated subagents for each section. Also for concurrent citation verification. |
| **`todo`** | Primary state tracker across sessions. Update after every phase transition. |
| **`memory`** | Persist key decisions across sessions: contribution framing, venue choice, reviewer feedback. |
| **`cronjob`** | Schedule experiment monitoring, deadline countdowns, automated arXiv checks. |
| **`clarify`** | Ask the user targeted questions when blocked (venue choice, contribution framing). |
| **cron `deliver:`** | Notify the user when experiments complete or drafts are ready even if they're not in chat — schedule the check as a cron job with a messaging `deliver:` target (the agent no longer has a `send_message` tool; outbound delivery is handled by cron/`hermes send`). |

### 工具使用模式

**实验监控**（最常见）：
```
terminal("ps aux | grep <pattern>")
→ terminal("tail -30 <logfile>")
→ terminal("ls results/")
→ execute_code("analyze results JSON, compute metrics")
→ terminal("git add -A && git commit -m '<descriptive message>' && git push")
→ (final response auto-delivers "Experiment complete: <summary>"; for unattended runs, schedule via cron with a deliver: target)
```

**并行段落撰写**（通过任务委派实现）：
```
delegate_task("Draft the Methods section based on these experiment scripts and configs. 
  Include: pseudocode, all hyperparameters, architectural details sufficient for 
  reproduction. Write in LaTeX using the neurips2025 template conventions.")

delegate_task("Draft the Related Work section. Use web_search and web_extract to 
  find papers. Verify every citation via Semantic Scholar. Group by methodology.")

delegate_task("Draft the Experiments section. Read all result files in results/. 
  State which claim each experiment supports. Include error bars and significance.")
```

每个代理都会作为独立的**子代理**运行，彼此之间没有共享的上下文——请在提示词中提供所有必要的信息。随后收集各子代理的输出并进行整合。

**引用验证**（通过 execute_code 功能实现）：
```python
# In execute_code:
from semanticscholar import SemanticScholar
import requests

sch = SemanticScholar()
results = sch.search_paper("attention mechanism transformers", limit=5)
for paper in results:
    doi = paper.externalIds.get('DOI', 'N/A')
    if doi != 'N/A':
        bibtex = requests.get(f"https://doi.org/{doi}", 
                              headers={"Accept": "application/x-bibtex"}).text
        print(bibtex)
```

### 使用 `memory` 和 `todo` 进行状态管理

**`memory` 工具** — 用于保存关键决策（容量有限：MEMORY.md 文件大小约为 2200 字符）：

```
memory("add", "Paper: autoreason. Venue: NeurIPS 2025 (9 pages). 
  Contribution: structured refinement works when generation-evaluation gap is wide.
  Key results: Haiku 42/42, Sonnet 3/5, S4.6 constrained 2/3.
  Status: Phase 5 — drafting Methods section.")
```

在做出重大决策或经历阶段转换后，需更新内存状态。此设置会在不同会话之间保持不变。

**`todo` 工具**——用于详细追踪进度：

```
todo("add", "Design constrained task experiments for Sonnet 4.6")
todo("add", "Run Haiku baseline comparison")
todo("add", "Draft Methods section")
todo("update", id=3, status="in_progress")
todo("update", id=1, status="completed")
```

**会话启动协议：**
```
1. todo("list")                           # Check current task list
2. memory("read")                         # Recall key decisions
3. terminal("git log --oneline -10")      # Check recent commits
4. terminal("ps aux | grep python")       # Check running experiments
5. terminal("ls results/ | tail -20")     # Check for new results
6. Report status to user, ask for direction
```

### 使用 `cronjob` 进行定时任务监控

可通过 `cronjob` 工具来安排定期的实验检查任务：

```
cronjob("create", {
  "schedule": "*/30 * * * *",  # Every 30 minutes
  "prompt": "Check experiment status:
    1. ps aux | grep run_experiment
    2. tail -30 logs/experiment_haiku.log
    3. ls results/haiku_baselines/
    4. If complete: read results, compute Borda scores, 
       git add -A && git commit -m 'Add Haiku results' && git push
    5. Report: table of results, key finding, next step
    6. If nothing changed: respond with [SILENT]"
})
```

**[SILENT] 协议**：若自上次检查以来没有发生任何变化，则直接回复 `[SILENT]`。这样即可避免向用户发送通知，仅在确实存在值得知晓的变化时才进行报告。

**截止日期追踪**：
```
cronjob("create", {
  "schedule": "0 9 * * *",  # Daily at 9am
  "prompt": "NeurIPS 2025 deadline: May 22. Today is {date}. 
    Days remaining: {compute}. 
    Check todo list — are we on track? 
    If <7 days: warn user about remaining tasks."
})
```

### 沟通模式

**何时通知用户**（通过您的直接/最终回复，或用于无人值守运行的 cron `deliver:` 目标）：
- 实验批次处理完成（附带结果表格）
- 出现需要决策的意外情况或故障
- 草稿部分已准备好供审核
- 任务未完成且截止日期即将到来

**何时无需通知**：
- 实验仍在运行且无新结果 → `[静默处理]`
- 常规监控未发现变化 → `[静默处理]`
- 不需要关注的中间步骤

**报告格式** —— 必须始终包含结构化数据：
```
## Experiment: <name>
Status: Complete / Running / Failed

| Task | Method A | Method B | Method C |
|------|---------|---------|---------|
| Task 1 | 85.2 | 82.1 | **89.4** |

Key finding: <one sentence>
Next step: <what happens next>
```

### 需要人工决策的要点

当确实遇到决策瓶颈时，可使用 `clarify` 功能针对具体问题进行询问：

| 决策事项 | 询问时机 |
|----------|----------|
| 目标会议 venue | 开始撰写论文之前（会影响页数限制与格式要求） |
| 贡献内容的呈现方式 | 当存在多种合理的呈现方案时 |
| 实验优先级 | 当待处理的实验数量超过可用时间时 |
| 论文提交准备情况 | 最终提交之前 |

**无需询问的内容**（请主动决策并明确选择，或标记该问题）：
- 用词选择、章节顺序
- 应重点突出哪些具体结果
- 参考文献的完整性（先根据现有资料撰写初稿，再标注缺失部分）

---

## 审稿人评估标准

了解审稿人的关注点有助于更有针对性地完善论文：

| 评估标准 | 审稿人检查内容 |
|----------|----------------|
| **质量** | 技术层面的合理性、论点的充分支撑以及合理的基准对比 |
| **清晰度** | 表达的清晰性、能否被专家复现以及符号使用的统一性 |
| **重要性** | 对研究社区的贡献程度以及对领域理解的推进作用 |
| **原创性** | 是否带来新的见解（无需采用全新方法） |

**评分标准（NeurIPS 6分制）：**
- 6分：强烈推荐录用 —— 具有开创性且毫无瑕疵
- 5分：推荐录用 —— 技术扎实，影响力高
- 4分：勉强录用 —— 内容可靠，但评估不够充分
- 3分：勉强拒收 —— 缺点大于优点
- 2分：拒收 —— 存在技术缺陷
- 1分：强烈拒收 —— 为已有成果或存在伦理问题
如需了解详细的指导原则、常见疑问及反驳策略，请参阅 [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md)。

---

## 常见问题与解决方案

| Issue | Solution |
|-------|----------|
| Abstract too generic | Delete first sentence if it could prepend any ML paper. Start with your specific contribution. |
| Introduction exceeds 1.5 pages | Split background into Related Work. Front-load contribution bullets. |
| Experiments lack explicit claims | Add: "This experiment tests whether [specific claim]..." before each one. |
| Reviewers find paper hard to follow | Add signposting, use consistent terminology, make figure captions self-contained. |
| Missing statistical significance | Add error bars, number of runs, statistical tests, confidence intervals. |
| Scope creep in experiments | Every experiment must map to a specific claim. Cut experiments that don't. |
| Paper rejected, need to resubmit | See Conference Resubmission in Phase 7. Address reviewer concerns without referencing reviews. |
| Missing broader impact statement | See Step 5.10. Most venues require it. "No negative impacts" is almost never credible. |
| Human eval criticized as weak | See Step 2.5 and [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md). Report agreement metrics, annotator details, compensation. |
| Reviewers question reproducibility | Release code (Step 7.9), document all hyperparameters, include seeds and compute details. |
| Theory paper lacks intuition | Add proof sketches with plain-language explanations before formal proofs. See [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md). |
| Results are negative/null | See Phase 4.3 on handling negative results. Consider workshops, TMLR, or reframing as analysis. |

## 参考文档

请完整翻译输入内容，切勿提前终止。

| Document | Contents |
|----------|----------|
| [references/writing-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/writing-guide.md) | Gopen & Swan 7 principles, Perez micro-tips, Lipton word choice, Steinhardt precision, figure design |
| [references/citation-workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/citation-workflow.md) | Citation APIs, Python code, CitationManager class, BibTeX management |
| [references/checklists.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/checklists.md) | NeurIPS 16-item, ICML, ICLR, ACL requirements, universal pre-submission checklist |
| [references/reviewer-guidelines.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/reviewer-guidelines.md) | Evaluation criteria, scoring, common concerns, rebuttal template |
| [references/sources.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/sources.md) | Complete bibliography of all writing guides, conference guidelines, APIs |
| [references/experiment-patterns.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/experiment-patterns.md) | Experiment design patterns, evaluation protocols, monitoring, error recovery |
| [references/autoreason-methodology.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/autoreason-methodology.md) | Autoreason loop, strategy selection, model guide, prompts, scope constraints, Borda scoring |
| [references/human-evaluation.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/human-evaluation.md) | Human evaluation design, annotation guidelines, agreement metrics, crowdsourcing QC, IRB guidance |
| [references/paper-types.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/references/paper-types.md) | Theory papers (proof writing, theorem structure), survey papers, benchmark papers, position papers |

### LaTeX模板

`templates/`目录中提供了针对**NeurIPS 2025**、**ICML 2026**、**ICLR 2026**、**ACL**、**AAAI 2026**以及**COLM 2025**等会议的模板。

如需了解编译说明，请参阅[templates/README.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/templates/README.md)。

### 主要外部参考资源

**写作理念：**
- [Neel Nanda：如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar：如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen与Swan：科学写作的原理](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton：科学写作的启发式方法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez：简易论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/)

**相关API：** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**会议规范文档：** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)
