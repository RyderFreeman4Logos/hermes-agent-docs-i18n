# 电影制作流程

该流程图以分阶段的方式展示了电影制作的五个环节，每个阶段内部通过容器、子节点以及横向子流程来呈现具体内容。

## 主要设计元素

- **阶段容器**：采用中性背景与虚线边框的大型圆形矩形
- **内部任务节点**：容器内的小型彩色节点，用于表示各项子任务
- **容器内的横向流程**：后期制作环节通过箭头依次展示处理顺序（剪辑 → 调色 → 视觉特效 → 音效 → 配乐）
- **统一的阶段间距**：各阶段容器之间保持约30像素的间距
- **带说明的阶段标签**：每个容器均包含标题与详细描述

## 图表展示

```xml
<svg width="100%" viewBox="0 0 680 780" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Phase 1: Development -->
  <g>
    <rect x="40" y="30" width="600" height="110" rx="16" stroke-width="1" stroke-dasharray="6 4" fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="56">Development</text>
    <text class="ts" x="66" y="74">Concept to greenlight</text>
  </g>
  <g class="node c-purple">
    <rect x="70" y="90" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="150" y="108" text-anchor="middle" dominant-baseline="central">Script / screenplay</text>
  </g>
  <g class="node c-purple">
    <rect x="260" y="90" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="108" text-anchor="middle" dominant-baseline="central">Financing / budget</text>
  </g>
  <g class="node c-purple">
    <rect x="450" y="90" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="530" y="108" text-anchor="middle" dominant-baseline="central">Casting leads</text>
  </g>

  <!-- Arrow to Phase 2 -->
  <line x1="340" y1="140" x2="340" y2="170" class="arr" marker-end="url(#arrow)"/>

  <!-- Phase 2: Pre-production -->
  <g>
    <rect x="40" y="170" width="600" height="110" rx="16" stroke-width="1" stroke-dasharray="6 4" fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="196">Pre-production</text>
    <text class="ts" x="66" y="214">Planning and preparation</text>
  </g>
  <g class="node c-teal">
    <rect x="70" y="230" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="150" y="248" text-anchor="middle" dominant-baseline="central">Storyboards</text>
  </g>
  <g class="node c-teal">
    <rect x="260" y="230" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="248" text-anchor="middle" dominant-baseline="central">Location scouting</text>
  </g>
  <g class="node c-teal">
    <rect x="450" y="230" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="530" y="248" text-anchor="middle" dominant-baseline="central">Crew hiring</text>
  </g>

  <!-- Arrow to Phase 3 -->
  <line x1="340" y1="280" x2="340" y2="310" class="arr" marker-end="url(#arrow)"/>

  <!-- Phase 3: Production -->
  <g>
    <rect x="40" y="310" width="600" height="110" rx="16" stroke-width="1" stroke-dasharray="6 4" fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="336">Production</text>
    <text class="ts" x="66" y="354">Principal photography</text>
  </g>
  <g class="node c-coral">
    <rect x="70" y="370" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="150" y="388" text-anchor="middle" dominant-baseline="central">Filming / shooting</text>
  </g>
  <g class="node c-coral">
    <rect x="260" y="370" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="388" text-anchor="middle" dominant-baseline="central">Production sound</text>
  </g>
  <g class="node c-coral">
    <rect x="450" y="370" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="530" y="388" text-anchor="middle" dominant-baseline="central">VFX plates</text>
  </g>

  <!-- Arrow to Phase 4 -->
  <line x1="340" y1="420" x2="340" y2="450" class="arr" marker-end="url(#arrow)"/>

  <!-- Phase 4: Post-production -->
  <g>
    <rect x="40" y="450" width="600" height="150" rx="16" stroke-width="1" stroke-dasharray="6 4" fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="476">Post-production</text>
    <text class="ts" x="66" y="494">Assembly and finishing</text>
  </g>
  <g class="node c-amber">
    <rect x="70" y="510" width="110" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="125" y="528" text-anchor="middle" dominant-baseline="central">Editing</text>
  </g>
  <g class="node c-amber">
    <rect x="195" y="510" width="110" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="250" y="528" text-anchor="middle" dominant-baseline="central">Color grade</text>
  </g>
  <g class="node c-amber">
    <rect x="320" y="510" width="90" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="365" y="528" text-anchor="middle" dominant-baseline="central">VFX</text>
  </g>
  <g class="node c-amber">
    <rect x="425" y="510" width="100" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="475" y="528" text-anchor="middle" dominant-baseline="central">Sound mix</text>
  </g>
  <g class="node c-amber">
    <rect x="540" y="510" width="80" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="580" y="528" text-anchor="middle" dominant-baseline="central">Score</text>
  </g>
  <!-- Flow arrows within post -->
  <line x1="180" y1="528" x2="195" y2="528" class="arr" marker-end="url(#arrow)"/>
  <line x1="305" y1="528" x2="320" y2="528" class="arr" marker-end="url(#arrow)"/>
  <line x1="410" y1="528" x2="425" y2="528" class="arr" marker-end="url(#arrow)"/>
  <line x1="525" y1="528" x2="540" y2="528" class="arr" marker-end="url(#arrow)"/>
  <!-- Final delivery label -->
  <g class="node c-amber">
    <rect x="240" y="556" width="200" height="32" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="572" text-anchor="middle" dominant-baseline="central">Final master / DCP</text>
  </g>
  <line x1="340" y1="546" x2="340" y2="556" class="arr" marker-end="url(#arrow)"/>

  <!-- Arrow to Phase 5 -->
  <line x1="340" y1="600" x2="340" y2="630" class="arr" marker-end="url(#arrow)"/>

  <!-- Phase 5: Distribution -->
  <g>
    <rect x="40" y="630" width="600" height="110" rx="16" stroke-width="1" stroke-dasharray="6 4" fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="656">Distribution</text>
    <text class="ts" x="66" y="674">Release and exhibition</text>
  </g>
  <g class="node c-blue">
    <rect x="70" y="690" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="150" y="708" text-anchor="middle" dominant-baseline="central">Film festivals</text>
  </g>
  <g class="node c-blue">
    <rect x="260" y="690" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="708" text-anchor="middle" dominant-baseline="central">Theatrical release</text>
  </g>
  <g class="node c-blue">
    <rect x="450" y="690" width="160" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="530" y="708" text-anchor="middle" dominant-baseline="central">Streaming / VOD</text>
  </g>
</svg>
```

## 颜色分配

| 元素 | 颜色 | 原因 |
|------|------|------|
| 阶段容器 | 中性色（虚线） | 用于柔和区分各阶段，不会与内容产生冲突 |
| 开发任务 | `c-purple` | 适用于创意与概念设计工作 |
| 预生产任务 | `c-teal` | 用于规划与准备工作 |
| 正式拍摄任务 | `c-coral` | 对应实际拍摄环节（核心阶段） |
| 后期制作任务 | `c-amber` | 用于内容处理与精细化调整 |
| 发行任务 | `c-blue` | 负责内容的最终输出与发布 |

## 布局说明

- **视图框尺寸**：680×780（标准宽度，因包含5个阶段而较高）
- **容器样式**：虚线边框（`stroke-dasharray="6 4"`），中性填充色（`var(--bg-secondary)`），边框宽度为1像素
- **容器高度**：3节点阶段为110像素，后期制作阶段因结构更复杂而为150像素
- **内部节点尺寸**：常规任务为160×36像素，后期制作的顺序流程则采用可变宽度
- **阶段间距**：各容器之间保留30像素的间距
- **横向子流程**：后期制作部分会使用紧密排列的节点，并通过箭头标注顺序关系
- **汇聚节点**：“最终母版 / DCP”节点位于横向流程下方，用于汇总所有后期输出结果 |
