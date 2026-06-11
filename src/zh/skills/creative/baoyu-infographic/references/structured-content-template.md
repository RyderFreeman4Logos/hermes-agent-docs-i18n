# 结构化内容模板

用于生成结构化信息图内容的模板，为视觉设计师提供参考。

## 设计目的

本文档旨在衔接内容分析与视觉设计：
- 将原始素材转换为设计师可直接使用的格式
- 将学习目标分类整理为不同的视觉板块
- 原封不动地保留所有原始数据
- 分离内容信息与设计指令

## 教学设计流程

### 第一阶段：整体框架规划

1. **标题**：用富有吸引力的标题概括核心内容
2. **概述**：简短描述（1-2句话）
3. **学习目标**：列出读者将掌握的知识点

### 第二阶段：各板块详细设计

针对每个学习目标：

1. **核心概念**：用一句话总结该板块内容
2. **内容要点**：从原始资料中直接摘录的要点
3. **视觉元素**：需要呈现的可视化内容
4. **文字标签**：标题、子标题及标注的具体文字

### 第三阶段：数据完整性核查

确认所有原始数据均满足以下要求：
- 完全复制原貌（不得改写）
- 引用内容需标注出处
- 格式保持一致

## 重要规则

| 规则 | 要求 | 示例 |
|------|------|---------|
| **输出格式** | 仅限 Markdown | 正确使用标题、列表及代码块 |
| **语气风格** | 专业培训师风格 | 具有专业知识，表述清晰且富有鼓励性 |
| **禁止添加新内容** | 仅使用原始资料内容 | 不得添加原始资料中未提及的示例 |
| **数据必须原封不动** | 完全复制原文 | 应为“增长73%”，而非“显著增长” |

## 结构化内容格式规范

```markdown
# [Infographic Title]

## Overview
[Brief description of what this infographic conveys - 1-2 sentences]

## Learning Objectives
The viewer will understand:
1. [Primary objective]
2. [Secondary objective]
3. [Tertiary objective if applicable]

---

## Section 1: [Section Title]

**Key Concept**: [One-sentence summary of this section]

**Content**:
- [Point 1 - verbatim from source]
- [Point 2 - verbatim from source]
- [Point 3 - verbatim from source]

**Visual Element**: [Description of what to show visually]
- Type: [icon/chart/illustration/diagram/photo]
- Subject: [what it depicts]
- Treatment: [how it should be presented]

**Text Labels**:
- Headline: "[Exact text for headline]"
- Subhead: "[Exact text for subhead]"
- Labels: "[Label 1]", "[Label 2]", "[Label 3]"

---

## Section 2: [Section Title]

**Key Concept**: [One-sentence summary]

**Content**:
- [Point 1]
- [Point 2]

**Visual Element**: [Description]

**Text Labels**:
- Headline: "[text]"
- Labels: "[Label 1]", "[Label 2]"

---

[Continue for each section...]

---

## Data Points (Verbatim)

All statistics, numbers, and quotes exactly as they appear in source:

### Statistics
- "[Exact statistic 1]"
- "[Exact statistic 2]"
- "[Exact statistic 3]"

### Quotes
- "[Exact quote]" — [Attribution]

### Key Terms
- **[Term 1]**: [Definition from source]
- **[Term 2]**: [Definition from source]

---

## Design Instructions

Extracted from user's steering prompt:

### Style Preferences
- [Any color preferences]
- [Any mood/aesthetic preferences]
- [Any artistic style preferences]

### Layout Preferences
- [Any structure preferences]
- [Any organization preferences]

### Other Requirements
- [Any other visual requirements from user]
- [Target platform if specified]
- [Brand guidelines if any]
```

## 按内容分类的章节类型

### 用于流程/步骤描述

```markdown
## Section N: Step N - [Step Title]

**Key Concept**: [What this step accomplishes]

**Content**:
- Action: [What to do]
- Details: [How to do it]
- Note: [Important consideration]

**Visual Element**:
- Type: numbered step icon
- Subject: [visual representing the action]
- Arrow: leads to next step

**Text Labels**:
- Headline: "Step N: [Title]"
- Action: "[Imperative verb + object]"
```

### 对比参考

```markdown
## Section N: [Item A] vs [Item B]

**Key Concept**: [What distinguishes them]

**Content**:
| Aspect | [Item A] | [Item B] |
|--------|----------|----------|
| [Factor 1] | [Value] | [Value] |
| [Factor 2] | [Value] | [Value] |

**Visual Element**:
- Type: split comparison
- Left: [Item A representation]
- Right: [Item B representation]

**Text Labels**:
- Headline: "[Item A] vs [Item B]"
- Left label: "[Item A name]"
- Right label: "[Item B name]"
```

### 层级结构相关功能

```markdown
## Section N: [Level Name]

**Key Concept**: [What this level represents]

**Content**:
- Position: [Top/Middle/Bottom]
- Priority: [Importance level]
- Contains: [Elements at this level]

**Visual Element**:
- Type: layer/tier
- Size: [relative to other levels]
- Position: [where in hierarchy]

**Text Labels**:
- Level title: "[Name]"
- Description: "[Brief description]"
```

### 数据与统计功能

```markdown
## Section N: [Metric Name]

**Key Concept**: [What this data shows]

**Content**:
- Value: [Exact number/percentage]
- Context: [What it means]
- Comparison: [Benchmark if any]

**Visual Element**:
- Type: [chart/number highlight/gauge]
- Emphasis: [how to draw attention]

**Text Labels**:
- Main number: "[Exact value]"
- Label: "[Metric name]"
- Context: "[Brief context]"
```

## 质量检查清单

在确定结构化内容之前，请核对以下事项：

- [ ] 标题能够准确概括核心内容  
- [ ] 学习目标清晰且可衡量  
- [ ] 每个章节均对应一个明确的目标  
- [ ] 所有内容均直接来源于原始资料  
- [ ] 视觉元素有明确的描述  
- [ ] 文本标签的标注十分精确  
- [ ] 数据点已收集并经过核实  
- [ ] 设计相关说明已单独列出  
- [ ] 未添加任何新信息
