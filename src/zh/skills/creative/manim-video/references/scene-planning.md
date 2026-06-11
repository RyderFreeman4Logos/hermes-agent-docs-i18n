# 场景规划参考指南

## 叙事结构类型

### 发现型叙事弧（最常见）
1. 吸引注意力——提出问题或令人惊讶的结果
2. 建立直观认知——形成视觉上的理解
3. 形式化表达——引入方程/算法
4. 揭示真相——呈现“顿悟时刻”
5. 拓展延伸——探讨其意义或普遍规律

### 问题-解决方案型叙事弧
1. 问题描述——当前存在的缺陷
2. 失败尝试——显而易见的解决方法行不通
3. 关键洞察——有效的解决思路
4. 方案实施——将思路付诸实践
5. 结果展示——呈现改进效果

### 对比型叙事弧
1. 背景铺垫——介绍两种方法
2. 方法A——运作原理
3. 方法B——运作原理
4. 对比分析——两者之间的差异
5. 最终判断——哪种方法更优

### 逐步构建型叙事弧（用于架构/系统介绍）
1. 组件A——第一个组成部分
2. 组件B——第二个组成部分
3. 相互连接——各组件之间的交互方式
4. 扩展规模——增加更多组件
5. 全局视角——从整体上把握结构

## 场景过渡方式

### 清晰分隔（默认选项）
```python
self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
self.wait(0.3)
```

### 保留元素
仅保留某个元素，其余元素逐渐淡出。下一个场景开始时，该元素仍会显示在屏幕上。

### 形态转换过渡
以某种形态结束当前场景，并通过对该形态进行变换来开启下一个场景。

## 场景间一致性

```python
# Shared constants at file top
BG = "#1C1C1C"
PRIMARY = "#58C4DD"
SECONDARY = "#83C167"
ACCENT = "#FFFF00"
TITLE_SIZE = 48
BODY_SIZE = 30
LABEL_SIZE = 24
FAST = 0.8; NORMAL = 1.5; SLOW = 2.5
```

## 场景检查清单

- [ ] 背景颜色已设置
- [ ] 所有动画均配有字幕
- [ ] 每次内容展示后均使用 `self.wait()` 函数
- [ ] 边缘对齐所需的文本缓冲区大小 >= 0.5
- [ ] 文本之间无重叠现象
- [ ] 使用颜色常量（而非硬编码值）
- [ ] 已应用透明度叠加效果
- [ ] 场景结束时能平滑结束
- [ ] 同时显示的元素数量不超过5-6个

## 时长估算

| 内容类型 | 预计时长 |
|---------|----------|
| 标题页 | 3-5秒 |
| 概念介绍 | 10-20秒 |
| 公式展示 | 15-25秒 |
| 算法步骤 | 5-10秒 |
| 数据对比 | 10-15秒 |
| “顿悟时刻” | 15-30秒 |
| 总结部分 | 5-10秒 |

## 规划模板

```markdown
# [Video Title]

## Overview
- **Topic**: [Core concept]
- **Hook**: [Opening question]
- **Aha moment**: [Key insight]
- **Target audience**: [Prerequisites]
- **Length**: [seconds/minutes]
- **Resolution**: 480p (draft) / 1080p (final)

## Color Palette
- Background: #1C1C1C
- Primary: #58C4DD -- [purpose]
- Secondary: #83C167 -- [purpose]
- Accent: #FFFF00 -- [purpose]

## Arc: [Discovery / Problem-Solution / Comparison / Build-Up]

## Scene 1: [Name] (~Ns)
**Purpose**: [one sentence]
**Layout**: [FULL_CENTER / LEFT_RIGHT / GRID / PROGRESSIVE]

### Visual elements
- [Mobject: type, position, color]

### Animation sequence
1. [Animation] -- [what it reveals] (~Ns)

### Subtitle
"[text]"
```
