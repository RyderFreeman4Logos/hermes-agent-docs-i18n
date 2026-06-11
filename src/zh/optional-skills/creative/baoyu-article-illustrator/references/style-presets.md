# 样式预设

一个预设由类型 + 风格 + 可选配色方案组合构成。用户可在请求中自行修改任意参数。

## 按类别分类

### 技术与工程领域

| 预设名称 | 类型 | 风格 | 配色方案 | 适用场景 |
|----------|------|-------|---------|----------|
| `tech-explainer` | `infographic` | `blueprint` | — | API文档、系统指标展示、技术深度解析 |
| `system-design` | `framework` | `blueprint` | — | 架构图、系统设计说明 |
| `architecture` | `framework` | `vector-illustration` | — | 组件关系展示、模块结构图 |
| `science-paper` | `infographic` | `scientific` | — | 研究成果展示、实验室数据、学术内容 |

### 知识与教育领域

| 预设名称 | 类型 | 风格 | 配色方案 | 适用场景 |
|----------|------|-------|---------|----------|
| `knowledge-base` | `infographic` | `vector-illustration` | — | 概念解释、教程、操作指南 |
| `saas-guide` | `infographic` | `notion` | — | 产品指南、SaaS文档、工具使用说明 |
| `tutorial` | `flowchart` | `vector-illustration` | — | 分步教程、设置指南 |
| `process-flow` | `flowchart` | `notion` | — | 工作流程文档、新人引导流程 |
| `warm-knowledge` | `infographic` | `vector-illustration` | `warm` | 产品展示、团队介绍、功能卡片、品牌内容 |
| `edu-visual` | `infographic` | `vector-illustration` | `macaron` | 知识总结、概念解释、教育类文章 |
| `hand-drawn-edu` | `flowchart` | `sketch-notes` | `macaron` | 手绘式教育图表、流程说明、新人引导视觉素材 |
| `ink-notes-compare` | `comparison` | `ink-notes` | `mono-ink` | 前后对比分析、传统与现代对比、操作系统风格对比、思维转变阐述 |
| `ink-notes-flow` | `flowchart` | `ink-notes` | `mono-ink` | 专业流程解释、工作流管道图、手绘式技术指南 |
| `ink-notes-framework` | `framework` | `ink-notes` | `mono-ink` | 系统类比图、指挥中心式图表、以架构为隐喻的展示、技术宣言 |

### 数据与分析领域

| 预设名称 | 类型 | 风格 | 配色方案 | 适用场景 |
|----------|------|-------|---------|----------|
| `data-report` | `infographic` | `editorial` | — | 数据新闻、指标报告、数据看板 |
| `versus` | `comparison` | `vector-illustration` | — | 技术产品对比、框架性能评测 |
| `business-compare` | `comparison` | `elegant` | — | 产品评估、策略选项对比 |

### 叙事与创意领域

| 预设名称 | 类型 | 风格 | 配色方案 | 适用场景 |
|----------|------|-------|---------|----------|
| `storytelling` | `scene` | `warm` | — | 个人随笔、反思文章、成长故事 |
| `lifestyle` | `scene` | `watercolor` | — | 旅行、健康生活、生活方式相关内容、创意作品 |
| `history` | `timeline` | `elegant` | — | 历史概览、重要里程碑展示 |
| `evolution` | `timeline` | `warm` | — | 进步历程描述、成长轨迹展示 |

### 社论与观点领域

| 预设名称 | 类型 | 风格 | 配色方案 | 适用场景 |
|----------|------|-------|---------|----------|
| `opinion-piece` | `scene` | `screen-print` | — | 社论、评论文章、批判性论述 |
| `editorial-poster` | `comparison` | `screen-print` | — | 辩论内容、不同观点对比 |
| `cinematic` | `scene` | `screen-print` | — | 戏剧化叙事、文化类文章 |

## 根据内容类型推荐预设

在第三步中，可依据第二步的内容分析结果，参考下表选择合适的预设：

| 第二步确定的内容类型 | 推荐首选预设 | 其他可选预设 |
|----------------------|--------------|--------------|
| 技术相关内容 | `tech-explainer` | `system-design`、`architecture` |
| 教程类内容 | `tutorial` | `process-flow`、`knowledge-base`、`edu-visual` |
| 方法论/框架相关内容 | `system-design` | `architecture`、`process-flow` |
| 数据/指标相关内容 | `data-report` | `versus`、`tech-explainer` |
| 对比/评测类内容 | `versus` | `business-compare`、`editorial-poster`、`ink-notes-compare` |
| 宣言/思维转变/专业视觉笔记类内容 | `ink-notes-compare` | `ink-notes-framework`、`ink-notes-flow` |
| 叙事/个人经历类内容 | `storytelling` | `lifestyle`、`evolution` |
| 观点/社论类内容 | `opinion-piece` | `cinematic`、`editorial-poster` |
| 历史/时间线类内容 | `history` | `evolution` |
| 学术/研究类内容 | `science-paper` | `tech-explainer`、`data-report` |
| SaaS/产品相关内容 | `saas-guide` | `knowledge-base`、`process-flow`、`warm-knowledge` |
| 教育/知识传播类内容 | `edu-visual` | `knowledge-base`、`tutorial`、`hand-drawn-edu` |

## 参数覆盖示例

- “使用 `tech-explainer` 预设，但将风格改为 `notion`” = `infographic` 类型搭配 `notion` 风格
- “`storytelling` 预设，但类型设为时间线” = `timeline` 类型搭配 `warm` 风格

若用户在请求中明确指定了类型、风格或配色方案，则这些指定将优先覆盖预设的默认值。
