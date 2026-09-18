# 第5阶段：论文撰写（完整流程）

**目标**：撰写一篇内容完整、可直接投稿的论文。

### 大型项目的上下文管理

对于包含50个以上实验文件、多个结果目录以及大量文献注释的论文项目，其内容很容易超出智能体的上下文窗口限制。需主动采取以下措施进行管理：

**每项撰写任务应加载到上下文中的内容：**

| 撰写任务 | 应加载至上下文的内容 | 不建议加载的内容 |
|-----------|----------------------|------------------|
| 撰写引言部分 | `experiment_log.md`、贡献说明、5-10篇最相关的论文摘要 | 原始结果JSON文件、完整的实验脚本、所有文献注释 |
| 撰写方法部分 | 实验配置、伪代码、架构描述 | 原始日志、其他实验的结果 |
| 撰写结果部分 | `experiment_log.md`、结果汇总表、图表列表 | 完整的分析脚本、中间数据 |
| 撰写相关工作部分 | 已整理好的引用注释（步骤1.4的输出）、.bib文件 | 实验文件、原始PDF文档 |
| 修订阶段 | 完整的论文初稿、审稿人提出的具体问题 | 其他所有内容 |

**管理原则：**
- **`experiment_log.md` 是主要的上下文桥梁**——它无需加载原始数据文件，即可汇总写作所需的所有信息（详见第4.6步）。  
- 在分配任务时，**每次仅加载一个部分的上下文**。负责撰写“方法”部分的子智能体无需相关文献综述笔记。  
- **需进行总结，而非直接上传原始文件**。对于包含200行内容的JSON结果，只需加载10行的总结表格；而对于50页长的相关论文，则只需上传5句的摘要以及你写的2行关于其相关性的说明。  
- **针对规模极大的项目**：可创建一个`context/`目录，存放预先压缩好的总结内容。
  ```
  context/
    contribution.md          # 1 sentence
    experiment_summary.md    # Key results table (from experiment_log.md)
    literature_map.md        # Organized citation notes
    figure_inventory.md      # List of figures with descriptions
  ```

### 叙事原则

**最关键的见解**：你的论文并非一系列实验的简单堆砌——而是一个以证据为支撑、围绕一个明确贡献展开的故事。

每一篇成功的机器学习论文都围绕着尼尔·南达（Neel Nanda）所称的“叙事”展开：一个简短、严谨、基于证据的技术故事，其中包含读者关心的核心结论。

**三大核心要素（在引言部分结束时必须清晰明确）：**

| 核心要素 | 描述 | 验证方式 |
|----------|------|----------|
| **是什么** | 1-3个具体的创新性主张 | 能否用一句话概括它们？ |
| **为什么** | 严谨的实证证据 | 实验是否证明了你的假设优于其他替代方案？ |
| **意义何在** | 为何读者应关注此研究 | 它是否与领域内公认的问题相关？ |

**如果你无法用一句话概括自己的贡献，那就还称不上是一篇论文。**

### 这一指导原则的来源

该技能整合了那些在顶级学术期刊上发表过多论文的研究人员所倡导的写作理念。这一写作理念框架最初由[Orchestra Research](https://github.com/orchestra-research)作为`ml-paper-writing`技能进行整理编撰。

| 来源 | 核心贡献 | 链接 |
|------|----------|------|
| **Neel Nanda**（谷歌DeepMind） | 叙事原则、What/Why/So What框架 | [如何撰写机器学习论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) |
| **Sebastian Farquhar**（DeepMind） | 五句摘要公式 | [如何撰写机器学习论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| **Gopen & Swan** | 读者预期七原则 | [科学写作科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| **Zachary Lipton** | 词汇选择、避免含糊表述 | [科学写作启发式方法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| **Jacob Steinhardt**（加州大学伯克利分校） | 精确性、术语一致性 | [写作技巧](https://bounded-regret.ghost.io/) |
| **Ethan Perez**（Anthropic） | 微观层面的清晰度提升技巧 | [简易论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/) |
| **Andrej Karpathy** | 单一贡献聚焦原则 | 多场演讲 |

**如需深入了解以上内容，可参考：**
- [references/writing-guide.md](references/writing-guide.md) —— 包含示例的详细解释
- [references/sources.md](references/sources.md) —— 完整参考文献列表

### 时间分配建议

建议为以下各项分配**大致相等的时间**：
1. 摘要  
2. 引言  
3. 图表  
4. 其余所有内容  

**原因何在？** 大多数审稿人会在阅读研究方法之前便形成初步判断。读者阅读论文的顺序通常是：标题 → 摘要 → 引言 → 图表 → 可能还有其余部分。  

### 写作流程

```
Paper Writing Checklist:
- [ ] Step 1: Define the one-sentence contribution
- [ ] Step 2: Draft Figure 1 (core idea or most compelling result)
- [ ] Step 3: Draft abstract (5-sentence formula)
- [ ] Step 4: Draft introduction (1-1.5 pages max)
- [ ] Step 5: Draft methods
- [ ] Step 6: Draft experiments & results
- [ ] Step 7: Draft related work
- [ ] Step 8: Draft conclusion & discussion
- [ ] Step 9: Draft limitations (REQUIRED by all venues)
- [ ] Step 10: Plan appendix (proofs, extra experiments, details)
- [ ] Step 11: Complete paper checklist
- [ ] Step 12: Final review
```

### 两轮优化模式

在使用 AI 智能体撰写文档时，可采用**两轮优化法**（该方法在 SakanaAI 的 AI-Scientist 工作流中已被验证有效）：

**第一轮——分章节撰写并立即优化：**
针对每个章节，先完成整篇草稿的撰写，随后立即在相同上下文中对其进行优化。这样可以在内容尚新鲜时及时发现局部问题，如表达清晰度、行文流畅性以及内容完整性等方面的缺陷。

**第二轮——结合全文上下文进行整体优化：**
在所有章节都撰写完成后，以整篇文档的全局视角重新审视每一章。此步骤有助于发现跨章节的问题，例如内容重复、术语不一致、叙事逻辑不连贯，以及某些章节承诺的内容与其它章节未能实现的情况。

```
Second-pass refinement prompt (per section):
"Review the [SECTION] in the context of the complete paper.
- Does it fit with the rest of the paper? Are there redundancies with other sections?
- Is terminology consistent with Introduction and Methods?
- Can anything be cut without weakening the message?
- Does the narrative flow from the previous section and into the next?
Make minimal, targeted edits. Do not rewrite from scratch."
```

### LaTeX错误检查清单

请在每个优化提示中附上此清单。这些是大型语言模型在编写LaTeX时最常出现的错误：

```
LaTeX Quality Checklist (verify after every edit):
- [ ] No unenclosed math symbols ($ signs balanced)
- [ ] Only reference figures/tables that exist (\ref matches \label)
- [ ] No fabricated citations (\cite matches entries in .bib)
- [ ] Every \begin{env} has matching \end{env} (especially figure, table, algorithm)
- [ ] No HTML contamination (</end{figure}> instead of \end{figure})
- [ ] No unescaped underscores outside math mode (use \_ in text)
- [ ] No duplicate \label definitions
- [ ] No duplicate section headers
- [ ] Numbers in text match actual experimental results
- [ ] All figures have captions and labels
- [ ] No overly long lines that cause overfull hbox warnings
```

### 第5.0步：标题

标题是论文中被阅读最多的部分，它决定了是否有人会继续点击查看摘要。

**优秀的标题**：
- 直接说明研究贡献或发现：“Autoreason：迭代式大语言模型优化何时有效以及为何失败”
- 突出令人惊讶的成果：“扩展数据受限的语言模型”（暗示该方法可行）
- 明确方法名称及其功能：“DPO：语言模型的直接偏好优化”

**糟糕的标题**：
- 过于笼统：“一种改进语言模型输出的方法”
- 过长：字数超过15词
- 全是专业术语：“迭代随机策略优化的渐近收敛性”（这类标题对谁有意义？）

**撰写规则**：
- 如果有自定义方法名称，请务必包含在内（便于引用）
- 置入1-2个审稿人可能会搜索的关键词
- 尽量避免使用冒号，除非两部分内容都有实际意义
- 进行测试：仅通过标题，审稿人能否了解该研究的领域及贡献？

### 第5.1步：摘要（五句式结构）

出自Sebastian Farquhar（DeepMind）：

```
1. What you achieved: "We introduce...", "We prove...", "We demonstrate..."
2. Why this is hard and important
3. How you do it (with specialist keywords for discoverability)
4. What evidence you have
5. Your most remarkable number/result
```

**删除**诸如“大型语言模型已取得显著成就……”这类通用开头语。

### 第5.2步：图1

图1是除摘要之外，大多数读者最先关注的元素。应在撰写引言之前先完成图1的构思——这能迫使你明确核心思想。

| 图1类型 | 适用场景 | 示例 |
|---------|----------|-------|
| **方法示意图** | 新架构或处理流程 | 用TikZ绘制的系统流程图 |
| **结果预览图** | 一个引人注目的结果即可说明全部内容 | 柱状图：展示“本方法与基准方法的对比”，并清晰显示差距 |
| **问题示意图** | 问题本身难以直观理解时 | 对比问题出现前后的故障模式 |
| **概念性图表** | 抽象的贡献需要可视化支撑时 | 方法特性的2×2矩阵 |

**规则**：图1无需阅读任何文字即可被理解。仅通过图注就能传达核心思想。使用颜色要有明确目的——切勿仅用于装饰。

### 第5.3步：引言（最多1-1.5页）

必须包含以下内容：
- 明确的问题陈述
- 简要的方法概述
- 2-4条贡献清单（每条最多1-2行，采用双栏格式）
- 方法相关内容应从第2-3页开始阐述

### 第5.4步：方法部分

为便于重新实现，需提供：
- 概念性概要或伪代码
- 所有超参数的列表
- 足以用于复现研究的架构细节
- 需明确说明最终的设计决策；实验部分再讨论各种替代方案

### 第5.5步：实验与结果

对于每个实验，需明确说明：
### 5.6节：相关研究

应按方法论进行归类，而非逐篇列举。请大量引用相关文献——审稿人很可能就是这些论文的作者。

### 5.7节：局限性分析（必填）

所有重要学术会议都要求撰写此部分。诚实的态度会带来诸多好处：
- 审稿人被要求不会因作者如实说明局限性而给出负面评价；
- 可通过提前指出缺陷来避免后续的批评；
- 能够解释为何这些局限性不会动摇核心论点。

### 5.8节：结论与讨论

**结论部分**（必填，0.5–1页）：
- 用一句话重申本研究的贡献（表述方式需与摘要不同）；
- 用2–3句话总结关键发现（无需以列表形式呈现）；
- 阐述研究意义：这对该领域有何影响？
- 规划未来工作：列出2–3项具体的下一步计划（避免使用“我们将在未来研究中解决X问题”这类模糊表述）。

**讨论部分**（可选，有时与结论合并）：
- 探讨超出直接研究结果的更广泛意义；
- 分析与其他子领域的关联；
- 诚实地评估该方法在何种情况下有效、何种情况下无效；
- 讨论实际应用时的相关考量。

**切勿**在结论部分引入新的研究结果或论点。

### 5.9节：附录编写策略

所有重要学术会议均允许使用无限数量的附录，且附录对于确保研究的可复现性至关重要。其结构如下：

| 附录章节 | 内容说明 |
|----------|----------|
| **证明与推导** | 长度过长的完整证明内容。正文中可仅陈述定理，并标注“证明见附录A”。 |
| **额外实验** | 对比实验结果、扩展曲线、各数据集的详细分析、超参数敏感性分析 |
| **实现细节** | 完整的超参数表、训练细节、硬件配置、随机种子信息 |
| **数据集文档** | 数据收集流程、标注指南、许可协议、预处理步骤 |
| **提示词与模板** | 实际使用的提示词（针对基于大语言模型的方法）、评估模板 |
| **人工评估** | 标注界面截图、给标注人员的操作说明、伦理审查委员会相关资料 |
| **其他图表** | 各任务的详细分析结果、任务进展可视化图表、失败案例示例 |

**规则**：
- 正文部分需具备独立性——审稿人无需阅读附录内容
- 绝不可将关键证据仅放在附录中
- 引用格式：应写为“完整结果见表5（附录B）”，而非简单的“参见附录”
- 需使用`\appendix`命令，随后再写`\section{A: Proofs}`等格式

### 页面预算管理

当超出页面限制时：

| 缩写策略 | 节省篇幅 | 风险程度 |
|-------------|---------|----------|
| 将证明内容移至附录 | 0.5-2页 | 低 — 为常规做法 |
| 拼接相关研究内容 | 0.5-1页 | 中 — 可能遗漏关键引用 |
| 合并表格与子图 | 0.25-0.5页 | 低 — 通常有助于提升可读性 |
| 少量使用`\vspace{-Xpt}`指令 | 0.1-0.3页 | 若调整幅度微小则风险低，若过于明显则风险高 |
| 删除定性示例 | 0.5-1页 | 中 — 审稿人通常喜欢示例内容 |
| 缩小图表尺寸 | 0.25-0.5页 | 高 — 图表必须保持清晰可读 |

**严禁**：缩小字体大小、更改页边距、删除必要部分（如局限性分析、更广泛的影响说明），或对正文使用`\small`/`\footnotesize`指令。

### 第5.10步：伦理与更广泛影响声明

目前大多数期刊都要求或强烈建议提交伦理/更广泛影响声明。这并非格式化模板——审稿人会认真阅读该声明，若发现伦理问题可能会直接导致论文被拒。

**应包含的内容：**

| 组件 | 内容 | 要求提交的会议 |
|-----------|---------|--------------|
| **积极的社会影响** | 您的工作如何造福社会 | NeurIPS、ICML |
| **潜在的负面影响** | 滥用风险、双重用途问题及故障模式 | NeurIPS、ICML |
| **公平性与偏见** | 您的方法或数据是否存在已知的偏见？ | 所有会议（均隐含要求） |
| **环境影响** | 大规模训练产生的计算碳足迹 | ICML，NeurIPS也越来越重视此项要求 |
| **隐私问题** | 您的工作是否涉及个人数据的处理或使用？ | ACL、NeurIPS |
| **大语言模型披露** | 写作或实验过程中是否使用了人工智能？ | ICLR（强制要求），ACL |

**撰写说明：**

```latex
\section*{Broader Impact Statement}
% NeurIPS/ICML: after conclusion, does not count toward page limit

% 1. Positive applications (1-2 sentences)
This work enables [specific application] which may benefit [specific group].

% 2. Risks and mitigations (1-3 sentences, be specific)
[Method/model] could potentially be misused for [specific risk]. We mitigate
this by [specific mitigation, e.g., releasing only model weights above size X,
including safety filters, documenting failure modes].

% 3. Limitations of impact claims (1 sentence)
Our evaluation is limited to [specific domain]; broader deployment would
require [specific additional work].
```

**常见错误：**
- 写出“我们预计不会产生任何负面影响”（这种说法几乎从未成立——审稿人对此深感怀疑）
- 表述含糊：仅称“这可能被滥用”却未说明具体方式
- 未考虑大规模任务所带来的计算成本
- 在要求披露的场合忽略说明是否使用了大语言模型

**计算碳足迹**（针对训练成本较高的论文）：
```python
# Estimate using ML CO2 Impact tool methodology
gpu_hours = 1000  # total GPU hours
gpu_tdp_watts = 400  # e.g., A100 = 400W
pue = 1.1  # Power Usage Effectiveness (data center overhead)
carbon_intensity = 0.429  # kg CO2/kWh (US average; varies by region)

energy_kwh = (gpu_hours * gpu_tdp_watts * pue) / 1000
carbon_kg = energy_kwh * carbon_intensity
print(f"Energy: {energy_kwh:.0f} kWh, Carbon: {carbon_kg:.0f} kg CO2eq")
```

### 第5.11步：数据集说明表与模型卡片（如适用）

如果您的论文引入了**新的数据集**或**发布了新模型**，请附上结构化的文档。审稿人越来越期望看到此类内容，而且NeurIPS的数据集与基准测试跟踪系统也要求必须提供。

**数据集的说明表**（Gebru等人，2021年）——可放入附录中：

```
Dataset Documentation (Appendix):
- Motivation: Why was this dataset created? What task does it support?
- Composition: What are the instances? How many? What data types?
- Collection: How was data collected? What was the source?
- Preprocessing: What cleaning/filtering was applied?
- Distribution: How is the dataset distributed? Under what license?
- Maintenance: Who maintains it? How to report issues?
- Ethical considerations: Contains personal data? Consent obtained?
  Potential for harm? Known biases?
```

**模型卡片**（Mitchell等人，2019年）——应作为模型使用授权的附录内容予以包含：

```
Model Card (Appendix):
- Model details: Architecture, training data, training procedure
- Intended use: Primary use cases, out-of-scope uses
- Metrics: Evaluation metrics and results on benchmarks
- Ethical considerations: Known biases, fairness evaluations
- Limitations: Known failure modes, domains where model underperforms
```

### 写作风格

**句子层面的清晰度（Gopen与Swan提出的7项原则）：**

| 原则 | 规则 |
|------|------|
| 主语与动词靠近 | 将主语和动词置于相近位置 |
| 重音位置 | 将强调部分放在句子末尾 |
| 主题优先 | 先介绍背景信息，再呈现新内容 |
| 旧信息在前，新信息在后 | 先阐述已知内容，再介绍未知内容 |
| 一个单元，一个功能 | 每段只表达一个观点 |
| 使用动词而非名词化表达 | 多用动词，避免使用名词化结构 |
| 先铺垫背景，再引入新内容 | 在呈现新信息前先做好背景铺垫 |

**词汇选择（Lipton与Steinhardt的建议）：**
- 表述要具体：使用“准确性”而非“性能”
- 避免含糊表述：除非确实不确定，否则不要使用“可能”这类词
- 全文保持术语一致
- 避免重复使用相近词汇：用“开发”而非“组合”

**包含示例的完整写作指南**：请参阅 [references/writing-guide.md](references/writing-guide.md)

### 使用LaTeX模板

**务必先复制整个模板目录，然后再在其中进行编写。**

```
Template Setup Checklist:
- [ ] Step 1: Copy entire template directory to new project
- [ ] Step 2: Verify template compiles as-is (before any changes)
- [ ] Step 3: Read the template's example content to understand structure
- [ ] Step 4: Replace example content section by section
- [ ] Step 5: Use template macros (check preamble for \newcommand definitions)
- [ ] Step 6: Clean up template artifacts only at the end
```

**步骤 1：复制完整模板**

```bash
cp -r templates/neurips2025/ ~/papers/my-paper/
cd ~/papers/my-paper/
ls -la  # Should see: main.tex, neurips.sty, Makefile, etc.
```

请复制整个目录，而不仅仅是 .tex 文件。模板中包含样式文件（.sty）、参考文献样式文件（.bst）、示例内容以及 Makefiles。

**第 2 步：先验证模板能否正常编译**

在进行任何修改之前：
```bash
latexmk -pdf main.tex
# Or manual: pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

如果未经修改的模板无法编译，请先解决该问题（通常是由于缺少TeX相关包——可通过`tlmgr install <package>`进行安装）。

**步骤3：将模板内容保留作为参考**

请勿立即删除示例内容，而应将其注释掉，用作格式参考：
```latex
% Template example (keep for reference):
% \begin{figure}[t]
%   \centering
%   \includegraphics[width=0.8\linewidth]{example-image}
%   \caption{Template shows caption style}
% \end{figure}

% Your actual figure:
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{your-figure.pdf}
  \caption{Your caption following the same style.}
\end{figure}
```

**第4步：逐部分替换内容**

请按顺序进行操作：标题/作者 → 摘要 → 引言 → 方法 → 实验 → 相关工作 → 结论 → 参考文献 → 附录。每完成一个部分后及时进行整合。 

**第5步：使用模板宏**

```latex
\newcommand{\method}{YourMethodName}  % Consistent method naming
\newcommand{\eg}{e.g.,\xspace}        % Proper abbreviations
\newcommand{\ie}{i.e.,\xspace}
```

### 模板使用常见误区

| 误区 | 问题 | 解决方案 |
|------|------|----------|
| 仅复制 `.tex` 文件 | 缺少 `.sty` 文件，无法编译 | 需复制整个目录 |
| 修改 `.sty` 文件 | 会破坏会议要求的格式规范 | 绝对不要编辑样式文件 |
| 添加随机软件包 | 可能引发冲突，导致模板失效 | 仅在必要时添加 |
| 过早删除模板内容 | 会导致格式参考信息丢失 | 在完成所有内容前将其保留为注释 |
| 不频繁编译 | 错误会逐渐累积 | 每写完一个章节后及时编译 |
| 使用光栅格式的 PNG 图片 | 打印输出时图像会模糊 | 始终通过 `savefig('fig.pdf')` 生成矢量 PDF 格式 |

### 模板快速参考表

| 会议名称 | 主文件 | 样式文件 | 页面限制 |
|----------|------|----------|----------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 9页 |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 8页 |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 9页 |
| ACL 2025 | `acl_latex.tex` | `acl.sty` | 8页（长文格式） |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 7页 |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 9页 |

**通用要求**：采用双盲评审机制，参考文献不计入页数限制，附录数量无上限，必须使用 LaTeX 编写。

模板文件位于 `templates/` 目录中。有关编译设置的相关信息（包括 VS Code、CLI、Overleaf 及其他集成开发环境的使用方法），请参阅 [templates/README.md](templates/README.md)。

### 表格与图表

**表格**——建议使用 `booktabs` 包以实现专业级的格式排版：

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

**格式规则：**
- 用粗体标出各项指标的最佳数值
- 使用方向符号表示数值趋势（$\uparrow$/数值越高越好，$\downarrow$/数值越低越好）
- 数值列需右对齐
- 小数精度保持一致

**图表要求：**
- 所有图表均需使用**矢量图形**格式（PDF或EPS）——可通过`plt.savefig('fig.pdf')`生成
- 照片仅允许使用**光栅格式**（PNG，分辨率600 DPI）
- 需选择**适合色盲人群的配色方案**（如Okabe-Ito或Paul Tol方案）
- 必须确保**灰度下的可读性**（有8%的男性存在色觉缺陷）
- **图表内不得添加标题**，说明文字可承担此功能
- 说明文字需**独立完整**，无需参考正文即可理解

### 会议投稿转投流程

如需在不同会议之间转换投稿，可参考第7阶段（投稿准备）——其中包含完整的转投工作流程、页面调整对照表以及被拒后的处理建议。

### 专业级LaTeX前置代码

为确保论文质量，可在任何文档中添加以下软件包。这些包与所有主流会议格式文件均兼容：

```latex
% --- Professional Packages (add after conference style file) ---

% Typography
\usepackage{microtype}              % Microtypographic improvements (protrusion, expansion)
                                     % Makes text noticeably more polished — always include

% Tables
\usepackage{booktabs}               % Professional table rules (\toprule, \midrule, \bottomrule)
\usepackage{siunitx}                % Consistent number formatting, decimal alignment
                                     % Usage: \num{12345} → 12,345; \SI{3.5}{GHz} → 3.5 GHz
                                     % Table alignment: S column type for decimal-aligned numbers

% Figures
\usepackage{graphicx}               % Include graphics (\includegraphics)
\usepackage{subcaption}             % Subfigures with (a), (b), (c) labels
                                     % Usage: \begin{subfigure}{0.48\textwidth} ... \end{subfigure}

% Diagrams and Algorithms
\usepackage{tikz}                   % Programmable vector diagrams
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc, fit, backgrounds}
\usepackage[ruled,vlined]{algorithm2e}  % Professional pseudocode
                                     % Alternative: \usepackage{algorithmicx} if template bundles it

% Cross-references
\usepackage{cleveref}               % Smart references: \cref{fig:x} → "Figure 1"
                                     % MUST be loaded AFTER hyperref
                                     % Handles: figures, tables, sections, equations, algorithms

% Math (usually included by conference .sty, but verify)
\usepackage{amsmath,amssymb}        % AMS math environments and symbols
\usepackage{mathtools}              % Extends amsmath (dcases, coloneqq, etc.)

% Colors (for figures and diagrams)
\usepackage{xcolor}                 % Color management
% Okabe-Ito colorblind-safe palette:
\definecolor{okblue}{HTML}{0072B2}
\definecolor{okorange}{HTML}{E69F00}
\definecolor{okgreen}{HTML}{009E73}
\definecolor{okred}{HTML}{D55E00}
\definecolor{okpurple}{HTML}{CC79A7}
\definecolor{okcyan}{HTML}{56B4E9}
\definecolor{okyellow}{HTML}{F0E442}
```

**备注：**
- `microtype` 是对视觉效果提升最为显著的包，它能够以亚像素级别精确调整字符间距，因此务必加入。
- `siunitx` 通过 `S` 列类型来实现表格中数值的对齐，从而无需手动调整间距。
- `cleveref` 必须在 `hyperref` 之后加载。由于大多数会议主题文件都会先加载 `hyperref`，因此请将 `cleveref` 放在最后。
- 请检查会议模板是否已加载了这些包中的任意一个（尤其是 `algorithm`、`amsmath`、`graphicx`），避免重复加载。

### siunitx 的表格对齐功能

`siunitx` 能显著提升包含大量数值的表格的可读性：

```latex
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1] S[table-format=2.1]}
\toprule
Method & {Accuracy $\uparrow$} & {F1 $\uparrow$} & {Latency (ms) $\downarrow$} \\
\midrule
Baseline         & 85.2  & 83.7  & 45.3 \\
Ablation (no X)  & 87.1  & 85.4  & 42.1 \\
\textbf{Ours}    & \textbf{92.1} & \textbf{90.8} & \textbf{38.7} \\
\bottomrule
\end{tabular}
```

`S` 类型的列会自动以小数点为对齐基准。位于 `{}` 内的标题可避免受此对齐规则影响。

### 子图

并排显示图表的标准格式：

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_a.pdf}
    \caption{Results on Dataset A.}
    \label{fig:results-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{fig_results_b.pdf}
    \caption{Results on Dataset B.}
    \label{fig:results-b}
  \end{subfigure}
  \caption{Comparison of our method across two datasets. (a) shows the scaling
  behavior and (b) shows the ablation results. Both use 5 random seeds.}
  \label{fig:results}
\end{figure}
```

使用 `\cref{fig:results}` 可表示为“图1”，而 `\cref{fig:results-a}` 则表示为“图1a”。

### 使用 algorithm2e 编写的伪代码

```latex
\begin{algorithm}[t]
\caption{Iterative Refinement with Judge Panel}
\label{alg:method}
\KwIn{Task $T$, model $M$, judges $J_1 \ldots J_n$, convergence threshold $k$}
\KwOut{Final output $A^*$}
$A \gets M(T)$ \tcp*{Initial generation}
$\text{streak} \gets 0$\;
\While{$\text{streak} < k$}{
  $C \gets \text{Critic}(A, T)$ \tcp*{Identify weaknesses}
  $B \gets M(T, C)$ \tcp*{Revised version addressing critique}
  $AB \gets \text{Synthesize}(A, B)$ \tcp*{Merge best elements}
  \ForEach{judge $J_i$}{
    $\text{rank}_i \gets J_i(\text{shuffle}(A, B, AB))$ \tcp*{Blind ranking}
  }
  $\text{winner} \gets \text{BordaCount}(\text{ranks})$\;
  \eIf{$\text{winner} = A$}{
    $\text{streak} \gets \text{streak} + 1$\;
  }{
    $A \gets \text{winner}$; $\text{streak} \gets 0$\;
  }
}
\Return{$A$}\;
\end{algorithm}
```

### TikZ 图表模板

TikZ 是机器学习论文中方法图的标准工具。常见图表模板包括：

**流程图/管道图**（在机器学习论文中最常用）：

```latex
\begin{figure}[t]
\centering
\begin{tikzpicture}[
  node distance=1.8cm,
  box/.style={rectangle, draw, rounded corners, minimum height=1cm, 
              minimum width=2cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
]
  \node[box, fill=okcyan!20] (input) {Input\\$x$};
  \node[box, fill=okblue!20, right of=input] (encoder) {Encoder\\$f_\theta$};
  \node[box, fill=okgreen!20, right of=encoder] (latent) {Latent\\$z$};
  \node[box, fill=okorange!20, right of=latent] (decoder) {Decoder\\$g_\phi$};
  \node[box, fill=okred!20, right of=decoder] (output) {Output\\$\hat{x}$};
  
  \draw[arrow] (input) -- (encoder);
  \draw[arrow] (encoder) -- (latent);
  \draw[arrow] (latent) -- (decoder);
  \draw[arrow] (decoder) -- (output);
\end{tikzpicture}
\caption{Architecture overview. The encoder maps input $x$ to latent 
representation $z$, which the decoder reconstructs.}
\label{fig:architecture}
\end{figure}
```

**对比/矩阵图**（用于展示不同的方法变体）：

```latex
\begin{tikzpicture}[
  cell/.style={rectangle, draw, minimum width=2.5cm, minimum height=1cm, 
               align=center, font=\small},
  header/.style={cell, fill=gray!20, font=\small\bfseries},
]
  % Headers
  \node[header] at (0, 0) {Method};
  \node[header] at (3, 0) {Converges?};
  \node[header] at (6, 0) {Quality?};
  % Rows
  \node[cell] at (0, -1) {Single Pass};
  \node[cell, fill=okgreen!15] at (3, -1) {N/A};
  \node[cell, fill=okorange!15] at (6, -1) {Baseline};
  \node[cell] at (0, -2) {Critique+Revise};
  \node[cell, fill=okred!15] at (3, -2) {No};
  \node[cell, fill=okred!15] at (6, -2) {Degrades};
  \node[cell] at (0, -3) {Ours};
  \node[cell, fill=okgreen!15] at (3, -3) {Yes ($k$=2)};
  \node[cell, fill=okgreen!15] at (6, -3) {Improves};
\end{tikzpicture}
```

**迭代循环图**（适用于具有反馈机制的方法）：

```latex
\begin{tikzpicture}[
  node distance=2cm,
  box/.style={rectangle, draw, rounded corners, minimum height=0.8cm, 
              minimum width=1.8cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick},
  label/.style={font=\scriptsize, midway, above},
]
  \node[box, fill=okblue!20] (gen) {Generator};
  \node[box, fill=okred!20, right=2.5cm of gen] (critic) {Critic};
  \node[box, fill=okgreen!20, below=1.5cm of $(gen)!0.5!(critic)$] (judge) {Judge Panel};
  
  \draw[arrow] (gen) -- node[label] {output $A$} (critic);
  \draw[arrow] (critic) -- node[label, right] {critique $C$} (judge);
  \draw[arrow] (judge) -| node[label, left, pos=0.3] {winner} (gen);
\end{tikzpicture}
```

### 用于版本追踪的 LaTeXdiff 工具

在撰写反驳意见时不可或缺——该工具可生成带标记的 PDF 文件，清晰显示不同版本之间的差异：

```bash
# Install
# macOS: brew install latexdiff (or comes with TeX Live)
# Linux: sudo apt install latexdiff

# Generate diff
latexdiff paper_v1.tex paper_v2.tex > paper_diff.tex
pdflatex paper_diff.tex

# For multi-file projects (with \input{} or \include{})
latexdiff --flatten paper_v1.tex paper_v2.tex > paper_diff.tex
```

这样生成的 PDF 文件中，被删除的内容会以红色划线标出，新增内容则用蓝色标示——这正是用于补充反驳意见的标准格式。

### 适用于 matplotlib 的 SciencePlots 工具

安装该工具后，即可生成具备出版级质量的图表：

```bash
pip install SciencePlots
```

```python
import matplotlib.pyplot as plt
import scienceplots  # registers styles

# Use science style (IEEE-like, clean)
with plt.style.context(['science', 'no-latex']):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # Single-column width
    ax.plot(x, y, label='Ours', color='#0072B2')
    ax.plot(x, y2, label='Baseline', color='#D55E00', linestyle='--')
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Accuracy')
    ax.legend()
    fig.savefig('paper/fig_results.pdf', bbox_inches='tight')

# Available styles: 'science', 'ieee', 'nature', 'science+ieee'
# Add 'no-latex' if LaTeX is not installed on the machine generating plots
```

**标准图表尺寸**（双栏格式）：
- 单栏：`figsize=(3.5, 2.5)` —— 适合单列显示
- 双栏：`figsize=(7.0, 3.0)` —— 覆盖两列
- 正方形：`figsize=(3.5, 3.5)` —— 适用于热力图和混淆矩阵

