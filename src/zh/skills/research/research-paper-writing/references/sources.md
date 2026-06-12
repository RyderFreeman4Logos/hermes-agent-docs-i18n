# 参考文献列表

本文档按主题分类，列出了构建该智能体所使用的所有权威参考资料。

---

## 起源与归属

该智能体的写作理念、引用验证流程以及会议相关参考资料，最初由 **[Orchestra Research](https://github.com/orchestra-research)** 于2026年1月作为 `ml-paper-writing` 智能体整理而成，其内容参考了Neel Nanda的博客文章以及下文列出的其他研究者指南。该智能体随后由technium在2026年1月集成到hermes-agent中，之后由SHL0MS在2026年4月通过PR #4654将其扩展为当前的 `research-paper-writing` 工作流。在扩展过程中，保留了原有的写作理念和参考文件，同时新增了实验设计、执行监控、迭代优化以及论文投稿等环节。

---

## 写作理念与指南

### 核心参考资料（必读）

| 参考资料 | 作者 | URL | 主要贡献 |
|--------|------|-----|----------|
| **关于如何撰写机器学习论文的极有见地的建议** | Neel Nanda | [Alignment Forum](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) | 叙事框架、“是什么/为什么/意义何在”、时间分配建议 |
| **如何撰写机器学习论文** | Sebastian Farquhar（DeepMind） | [博客](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) | 五句摘要公式、结构模板 |
| **博士生存指南** | Andrej Karpathy | [博客](http://karpathy.github.io/2016/09/07/phd/) | 论文结构框架、贡献阐述方法 |
| **科学写作的启发式原则** | Zachary Lipton（CMU） | [博客](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) | 词汇选择、章节平衡、强度词使用提醒 |
| **给作者的建议** | Jacob Steinhardt（UC Berkeley） | [博客](https://jsteinhardt.stat.berkeley.edu/blog/advice-for-authors) | 强调精确性优于简洁性、术语一致性 |
| **轻松撰写论文的技巧** | Ethan Perez（Anthropic） | [博客](https://ethanperez.net/easy-paper-writing-tips/) | 微观写作技巧、撇号使用规范、提升清晰度的方法 |

### 科学写作的基础理论

| 参考资料 | 作者 | URL | 主要贡献 |
|--------|------|-----|----------|
| **科学写作的科学** | Gopen & Swan | [PDF](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) | 主题/重音位置规则、“旧信息在前、新信息在后”原则、7项核心原则 |
| **《科学写作的科学》概要** | Lawrence Crowl | [概要](https://www.crowl.org/Lawrence/writing/GopenSwan90.html) | Gopen & Swan著作的简化版本 |

### 其他资源

| 参考资料 | URL | 主要贡献 |
|--------|-----|----------|
| 如何撰写机器学习研究论文 | [博客](https://grigorisg9gr.github.io/machine%20learning/research%20paper/how-to-write-a-research-paper-in-machine-learning/) | 实用操作步骤、LaTeX使用技巧 |
| 训练神经网络的“配方” | [Karpathy博客](http://karpathy.github.io/2019/04/25/recipe/) | 可转化为论文结构的调试方法 |
| ICML论文写作最佳实践 | [ICML](https://icml.cc/Conferences/2022/BestPractices) | 会议官方指导文档 |
| Bill Freeman的写作幻灯片 | [MIT](https://billf.mit.edu/sites/default/files/documents/cvprPapers.pdf) | 论文结构的可视化指南 |

---

## 各会议官方指南

### NeurIPS

| 文档 | URL | 用途 |
|------|-----|------|
| 论文检查清单指南 | [NeurIPS](https://neurips.cc/public/guides/PaperChecklist) | 16项必填检查项 |
| 2025年审稿人指南 | [NeurIPS](https://neurips.cc/Conferences/2025/ReviewerGuidelines) | 评估标准、评分规则 |
| 格式文件 | [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | LaTeX模板 |

### ICML

| 文档 | URL | 用途 |
|------|-----|------|
| 论文指南 | [ICML](https://icml.cc/Conferences/2024/PaperGuidelines) | 投稿要求 |
| 2025年审稿人须知 | [ICML](https://icml.cc/Conferences/2025/ReviewerInstructions) | 审稿表单、评估标准 |
| 格式与作者须知 | [ICML](https://icml.cc/Conferences/2022/StyleAuthorInstructions) | 格式规范 |

### ICLR

| 文档 | URL | 用途 |
|------|-----|------|
| 2026年作者指南 | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | 投稿要求、大语言模型相关披露事项 |
| 2025年审稿人指南 | [ICLR](https://iclr.cc/Conferences/2025/ReviewerGuide) | 审稿流程、评估标准 |

### ACL/EMNLP

| 文档 | URL | 用途 |
|------|-----|------|
| ACL格式文件 | [GitHub](https://github.com/acl-org/acl-style-files) | LaTeX模板 |
| ACL滚动审稿系统 | [ARR](https://aclrollingreview.org/) | 投稿处理流程 |

### AAAI

| 文档 | URL | 用途 |
|------|-----|------|
| 2026年作者工具包 | [AAAI](https://aaai.org/authorkit26/) | 模板与指南 |

### COLM

| 文档 | URL | 用途 |
|------|-----|------|
| 模板 | [GitHub](https://github.com/COLM-org/Template) | LaTeX模板 |

---

## 引用相关API与工具

### API接口

| API | 文档说明 | 适用场景 |
|-----|-----------|----------|
| **Semantic Scholar** | [文档](https://api.semanticscholar.org/api-docs/) | 机器学习/AI领域论文、引用关系图谱查询 |
| **CrossRef** | [文档](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | DOI查询、BibTeX格式文献检索 |
| **arXiv** | [文档](https://info.arxiv.org/help/api/basics.html) | 预印本查询、PDF文件获取 |
| **OpenAlex** | [文档](https://docs.openalex.org/) | 开源替代方案、批量数据访问 |

### Python库

| 库名称 | 安装命令 | 用途 |
|--------|----------|------|
| `semanticscholar` | `pip install semanticscholar` | Semantic Scholar接口封装工具 |
| `arxiv` | `pip install arxiv` | arXiv数据库搜索与下载工具 |
| `habanero` | `pip install habanero` | CrossRef客户端库 |

### 引用验证工具

| 工具 | URL | 用途 |
|------|-----|------|
| Citely | [citely.ai](https://citely.ai/citation-checker) | 批量引用验证 |
| ReciteWorks | [reciteworks.com](https://reciteworks.com/) | 正文引用格式检查 |

---

## 可视化与格式排版

### 图表制作工具

| 工具 | URL | 用途 |
|------|-----|------|
| PlotNeuralNet | [GitHub](https://github.com/HarisIqbal88/PlotNeuralNet) | 使用TikZ绘制神经网络结构图 |
| SciencePlots | [GitHub](https://github.com/garrettj403/SciencePlots) | 适合发表的matplotlib绘图工具 |
| Okabe-Ito色彩方案 | [参考资料](https://jfly.uni-koeln.de/color/) | 适配色盲人群的配色方案 |

### LaTeX相关资源

| 资源 | URL | 用途 |
|------|-----|------|
| Overleaf模板库 | [Overleaf](https://www.overleaf.com/latex/templates) | 在线LaTeX编辑器 |
| BibLaTeX使用指南 | [CTAN](https://ctan.org/pkg/biblatex) | 现代引用管理工具 |

---

## 关于AI写作与幻觉现象的研究

| 参考资料 | URL | 主要研究发现 |
|--------|-----|--------------|
| 引用中的AI幻觉现象 | [Enago](https://www.enago.com/academy/ai-hallucinations-research-citations/) | 错误率约为40% |
| AI写作中的幻觉问题 | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10726751/) | 引用错误的不同类型 |
| NeurIPS 2025 AI报告 | [ByteIota](https://byteiota.com/neurips-2025-100-ai-hallucinations-slip-through-review/) | 发现超过100处虚假引用 |

---

## 按主题分类的快速参考

### 叙事与结构优化
→ 首选参考：Neel Nanda、Sebastian Farquhar、Andrej Karpathy

### 句子层面清晰度提升
→ 首选参考：Gopen & Swan、Ethan Perez、Zachary Lipton

### 词汇选择与风格优化
→ 首选参考：Zachary Lipton、Jacob Steinhardt

### 各会议特定要求
→ 首选参考：对应会议的官方指南（NeurIPS、ICML、ICLR、ACL）

### 引用管理
→ 首选参考：Semantic Scholar API、CrossRef、citation-workflow.md

### 理解审稿人期望
→ 首选参考：各会议审稿人指南、reviewer-guidelines.md

### 人工评估
→ 首选参考：human-evaluation.md、Prolific/MTurk平台文档

### 非实证类论文（理论、综述、基准测试、立场文）
→ 首选参考：paper-types.md

---

## 人工评估与标注

| 参考资料 | URL | 主要贡献 |
|--------|-----|----------|
| **数据集的文档规范** | Gebru等人，2021年([arXiv](https://arxiv.org/abs/1803.09010)) | 结构化的数据集文档框架 |
| **模型报告的模型卡片规范** | Mitchell等人，2019年([arXiv](https://arxiv.org/abs/1810.03993)) | 结构化的模型文档框架 |
| **众包与人类计算** | [综述文章](https://arxiv.org/abs/2202.06516) | 众包标注的最佳实践 |
| **Krippendorff's Alpha一致性指标** | [维基百科](https://en.wikipedia.org/wiki/Krippendorff%27s_alpha) | 评估不同标注者一致性的参考指标 |
| **Prolific平台** | [prolific.co](https://www.prolific.co/) | 推荐的科研众包平台 |

## 伦理与更广泛的影响

| 参考资料 | URL | 主要贡献 |
|--------|-----|----------|
| **机器学习计算碳足迹** | [mlco2.github.io](https://mlco2.github.io/impact/) | 计算任务碳足迹计算工具 |
| **NeurIPS更广泛影响指南** | [NeurIPS](https://neurips.cc/public/guides/PaperChecklist) | 关于影响声明的官方指导 |
| **ACL伦理政策** | [ACL](https://www.aclweb.org/portal/content/acl-code-ethics) | NLP研究领域的伦理要求 |
