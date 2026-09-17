# 参考文献

本文档按主题分类，列出了构建该技能所使用的所有权威资料。

---

## 起源与归属

该技能中的写作理念、引用验证流程以及会议参考资料，最初由 **[Orchestra Research](https://github.com/orchestra-research)** 于2026年1月作为 `ml-paper-writing` 技能整理而成，其内容借鉴了Neel Nanda的博客文章以及下文列出的其他研究者指南。该技能随后由technium在2026年1月被整合进hermes-agent，之后由SHL0MS在2026年4月通过PR #4654将其扩展为当前的 `research-paper-writing` 工作流。在保留原有写作理念和参考文件的基础上，该工作流还增加了实验设计、执行监控、迭代优化以及投稿等功能。

---

## 写作理念与指南

### 核心资料（必读）

| 来源 | 作者 | 网址 | 核心贡献 |
|------|------|-----|----------|
| **关于如何撰写机器学习论文的独到建议** | Neel Nanda | [Alignment Forum](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) | 叙事框架、“是什么/为什么/意义何在”的结构、时间分配策略 |
| **如何撰写机器学习论文** | Sebastian Farquhar（DeepMind） | [博客](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) | 五句摘要公式、论文结构模板 |
| **博士生涯生存指南** | Andrej Karpathy | [博客](http://karpathy.github.io/2016/09/07/phd/) | 论文结构撰写方法、研究贡献的表述方式 |
| **科学写作实用策略** | Zachary Lipton（CMU） | [博客](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) | 词汇选择技巧、各部分篇幅平衡原则、强度副词使用警示 |
| **给作者的建议** | Jacob Steinhardt（UC Berkeley） | [博客](https://jsteinhardt.stat.berkeley.edu/blog/advice-for-authors) | 强调精确性优于简洁性、术语一致性重要性 |
| **简易论文写作技巧** | Ethan Perez（Anthropic） | [博客](https://ethanperez.net/easy-paper-writing-tips/) | 微观层面写作技巧、撇号使用规范、提升清晰度的方法 |

### 科学写作的基础原理

| 来源 | 作者 | URL | 主要贡献 |
|------|------|-----|----------|
| **科学写作原理** | Gopen & Swan | [PDF](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) | 主题/重音位置、旧内容在前新内容在后的原则，以及7项写作准则 |
| **科学写作原理概要** | Lawrence Crowl | [概要](https://www.crowl.org/Lawrence/writing/GopenSwan90.html) | Gopen & Swan著作的简化版本 |

### 其他资源

| 来源 | URL | 主要贡献 |
|------|-----|----------|
| 如何撰写机器学习研究论文 | [博客](https://grigorisg9gr.github.io/machine%20learning/research%20paper/how-to-write-a-research-paper-in-machine-learning/) | 实用写作步骤指导，LaTeX使用技巧 |
| 训练神经网络的实用方法 | [Karpathy博客](http://karpathy.github.io/2019/04/25/recipe/) | 可用于论文结构的调试方法论 |
| ICML论文写作最佳实践 | [ICML](https://icml.cc/Conferences/2022/BestPractices) | 会议官方提供的写作指导 |
| Bill Freeman的论文结构幻灯片 | [MIT](https://billf.mit.edu/sites/default/files/documents/cvprPapers.pdf) | 论文结构的可视化指南 |

---

## 官方会议写作指南

### NeurIPS

| 文档 | 网址 | 用途 |
|------|------|------|
| 论文检查清单指南 | [NeurIPS](https://neurips.cc/public/guides/PaperChecklist) | 包含16项必填检查项的清单 |
| 2025年审稿人指南 | [NeurIPS](https://neurips.cc/Conferences/2025/ReviewerGuidelines) | 评估标准与评分规则 |
| 格式文件 | [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | LaTeX模板 |

### ICML

| 文档 | 网址 | 用途 |
|------|------|------|
| 论文提交指南 | [ICML](https://icml.cc/Conferences/2024/PaperGuidelines) | 论文提交要求 |
| 2025年审稿人须知 | [ICML](https://icml.cc/Conferences/2025/ReviewerInstructions) | 审稿表格与评估流程 |
| 格式与作者指南 | [ICML](https://icml.cc/Conferences/2022/StyleAuthorInstructions) | 格式规范要求 |

### ICLR

| 文档 | 网址 | 用途 |
|------|------|------|
| 2026年作者指南 | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | 论文提交要求及大语言模型相关披露规定 |
| 2025年审稿人指南 | [ICLR](https://iclr.cc/Conferences/2025/ReviewerGuide) | 审稿流程与评估标准 |

### ACL/EMNLP

| 文档 | 网址 | 用途 |
|------|------|------|
| ACL格式文件 | [GitHub](https://github.com/acl-org/acl-style-files) | LaTeX模板 |
| ACL滚动审稿系统 | [ARR](https://aclrollingreview.org/) | 论文提交流程 |

### AAAI

| 文档 | URL | 用途 |
|------|-----|------|
| Author Kit 2026 | [AAAI](https://aaai.org/authorkit26/) | 模板与指南 |

### COLM

| 文档 | URL | 用途 |
|------|-----|------|
| 模板 | [GitHub](https://github.com/COLM-org/Template) | LaTeX模板 |

---

## 引文API与工具

### API

| API | 文档 | 最佳适用场景 |
|-----|---------------|--------------|
| **Semantic Scholar** | [文档](https://api.semanticscholar.org/api-docs/) | 机器学习/AI论文、引文图谱 |
| **CrossRef** | [文档](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | DOI查询、BibTeX检索 |
| **arXiv** | [文档](https://info.arxiv.org/help/api/basics.html) | 预印本、PDF获取 |
| **OpenAlex** | [文档](https://docs.openalex.org/) | 开源替代方案、批量访问 |

### Python库

| 库 | 安装方式 | 用途 |
|-----|----------|------|
| `semanticscholar` | `pip install semanticscholar` | Semantic Scholar封装工具 |
| `arxiv` | `pip install arxiv` | arXiv搜索与下载 |
| `habanero` | `pip install habanero` | CrossRef客户端 |

### 引文验证

| 工具 | URL | 用途 |
|------|-----|------|
| Citely | [citely.ai](https://citely.ai/citation-checker) | 批量验证 |
| ReciteWorks | [reciteworks.com](https://reciteworks.com/) | 正文引文检查 |

---

## 可视化与格式化

### 图表创建

| 工具 | URL | 用途 |
|------|-----|---------|
| PlotNeuralNet | [GitHub](https://github.com/HarisIqbal88/PlotNeuralNet) | 用于绘制TikZ格式的神经网络图表 |
| SciencePlots | [GitHub](https://github.com/garrettj403/SciencePlots) | 生成适合发表的matplotlib图表 |
| Okabe-Ito配色方案 | [参考资料](https://jfly.uni-koeln.de/color/) | 专为色盲人群设计的安全色彩 |

### LaTeX相关资源

| 资源 | URL | 用途 |
|------|-----|---------|
| Overleaf模板 | [Overleaf](https://www.overleaf.com/latex/templates) | 在线LaTeX编辑器 |
| BibLaTeX使用指南 | [CTAN](https://ctan.org/pkg/biblatex) | 现代引文管理工具 |

---

## 关于AI写作与幻觉现象的研究

| 来源 | URL | 核心发现 |
|------|-----|---------|
| 引文中的AI幻觉现象 | [Enago](https://www.enago.com/academy/ai-hallucinations-research-citations/) | 错误率约为40% |
| AI写作中的幻觉问题 | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10726751/) | 引文错误的类型 |
| NeurIPS 2025 AI报告 | [ByteIota](https://byteiota.com/neurips-2025-100-ai-hallucinations-slip-through-review/) | 存在100多处虚假引文 |

---

## 按主题分类的快速参考

### 叙事与结构优化
→ 参考学者：Neel Nanda、Sebastian Farquhar、Andrej Karpathy

### 句子层面的清晰度提升
→ 参考研究：Gopen & Swan、Ethan Perez、Zachary Lipton

### 词汇选择与风格优化
→ 参考学者：Zachary Lipton、Jacob Steinhardt

### 针对会议特定要求
→ 参考起点：各官方会议的指南（NeurIPS、ICML、ICLR、ACL）

### 针对引文管理
→ 参考起点：Semantic Scholar API、CrossRef以及citation-workflow.md文档

### 针对审稿人期望
→ 参考起点：会议审稿人指南以及reviewer-guidelines.md文档

### 针对人机评估
→ 参考起点：human-evaluation.md文档以及Prolific/MTurk平台的使用指南

### 针对非实证类论文（理论研究、综述、基准测试、立场声明等）
→ 参考起点：paper-types.md文档

---

## 人机评估与标注

| 资源来源 | 网址 | 核心贡献 |
|--------|-----|----------|
| **数据集相关数据集** | Gebru等人，2021年（[arXiv](https://arxiv.org/abs/1803.09010)） | 结构化数据集文档框架 |
| **模型报告相关的模型卡片** | Mitchell等人，2019年（[arXiv](https://arxiv.org/abs/1810.03993)） | 结构化模型文档框架 |
| **众包与人机计算** | [综述文章](https://arxiv.org/abs/2202.06516) | 众包标注的最佳实践指南 |
| **Krippendorff's Alpha一致性指标** | [维基百科](https://en.wikipedia.org/wiki/Krippendorff%27s_alpha) | 用于衡量不同标注者之间一致性的参考指标 |
| **Prolific平台** | [prolific.co](https://www.prolific.co/) | 推荐用于研究的众包平台 |

## 伦理问题与更广泛的影响

| 来源 | 网址 | 主要贡献 |
|--------|-----|------------------|
| **ML CO2 Impact** | [mlco2.github.io](https://mlco2.github.io/impact/) | 提供碳足迹计算工具 |
| **NeurIPS 更广泛影响力指南** | [NeurIPS](https://neurips.cc/public/guides/PaperChecklist) | 关于影响力陈述的官方指导规范 |
| **ACL 伦理政策** | [ACL](https://www.aclweb.org/portal/content/acl-code-ethics) | 针对自然语言处理研究的伦理要求 |
