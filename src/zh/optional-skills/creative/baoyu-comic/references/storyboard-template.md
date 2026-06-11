# 分镜模板

## 分镜文档格式

```markdown
---
title: "[Comic Title]"
topic: "[topic description]"
time_span: "[e.g., 1912-1954]"
narrative_approach: "[chronological/thematic/character-focused]"
recommended_style: "[style name]"
recommended_layout: "[layout name or varies]"
aspect_ratio: "3:4"    # 3:4 (portrait), 4:3 (landscape), 16:9 (widescreen)
language: "[zh/en/ja/etc.]"
page_count: [N]
generated: "YYYY-MM-DD HH:mm"
---

# [Comic Title] - Knowledge Comic Storyboard

**Character Reference**: characters/characters.png

---

## Cover

**Filename**: 00-cover-[slug].png
**Core Message**: [one-liner]

**Visual Design**:
- Title typography style
- Main visual composition
- Color scheme
- Subtitle / time span notation

**Visual Prompt**:
[Detailed image generation prompt]

---

## Page 1 / N

**Filename**: 01-page-[slug].png
**Layout**: [standard/cinematic/dense/splash/mixed]
**Narrative Layer**: [Main narrative / Narrator layer / Mixed]
**Core Message**: [What this page conveys]

### Panel Layout

**Panel Count**: X
**Layout Type**: [grid/irregular/splash]

#### Panel 1 (Size: 1/3 page, Position: Top)

**Scene**: [Time, location]
**Image Description**:
- Camera angle: [bird's eye / low angle / eye level / close-up / wide shot]
- Characters: [pose, expression, action]
- Environment: [scene details, period markers]
- Lighting: [atmosphere description]
- Color tone: [palette reference]

**Text Elements**:
- Dialogue bubble (oval): "Character line"
- Narrator box (rectangular): 「Narrator commentary」
- Caption bar: [Background info text]

#### Panel 2...

**Page Hook**: [Cliffhanger or transition at page end]

**Visual Prompt**:
[Full page image generation prompt]

---

## Page 2 / N
...
```

## 封面设计原则

- 兼具学术严谨性与视觉吸引力  
- 标题字体需体现知识/科学主题特色  
- 构图需暗示核心主题（人物轮廓、标志性符号、概念图）  
- 需添加副标题或时间范围以凸显宏大叙事背景  

## 分格构图指南

| 分格类型 | 建议数量 | 用途 |
|---------|----------|------|
| 主要叙事部分 | 每页3-5格 | 叙事推进 |
| 概念图 | 每页1-2格 | 可视化抽象概念 |
| 叙述者旁白栏 | 每页0-1格 | 评论与过渡说明 |
| 全页/半页插图 | 适时使用 | 关键场景展示 |

## 分格尺寸参考

- **全页（插图）**：用于呈现重大时刻或关键突破  
- **半页**：重要场景及转折点  
- **1/3页**：常规叙事分格  
- **1/4页或更小**：快速叙事推进或连续动作展示  

## 概念可视化技巧

将抽象概念转化为具体视觉元素：

| 抽象概念 | 可视化方法 |
|---------|------------|
| 神经网络 | 带连接线的发光节点 |
| 梯度下降 | 滚下山谷的球体 |
| 数据流 | 在管道中流动的发光粒子 |
| 算法迭代 | 上升的螺旋楼梯 |
| 突破时刻 | 破碎的屏障与穿透的光芒 |
| 逻辑证明 | 逐步组合的积木 |
| 不确定性 | 分叉路径、迷雾及多重阴影 |

## 文本元素设计

| 文本类型 | 样式 | 用途 |
|---------|------|------|
| 角色对话 | 椭圆形对话框 | 主要叙事中的对话内容 |
| 叙述者评论 | 矩形框 | 解释与旁白说明 |
| 字幕栏 | 边缘固定的矩形 | 时间、地点等信息标注 |
| 思考气泡 | 云状图案 | 角色内心独白 |
| 术语标签 | 加粗字体/特殊颜色 | 技术术语首次出现时标注 |

## 为确保一致性而设计的提示词结构

每页的提示词都应包含角色相关信息：

```
[CHARACTER REFERENCE]
(Key details from characters.md for characters in this page)

[PAGE CONTENT]
(Specific scene, panel layout, and visual elements)

[CONSISTENCY REMINDER]
Maintain exact character appearances as defined in character reference.
- [Character A]: [key identifying features]
- [Character B]: [key identifying features]
```
