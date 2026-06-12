# 医院急诊科流程图

这是一张多路径流程图，展示了患者从进入急诊科到后续处理的完整流程。该流程采用基于优先级的路由方式，并通过语义颜色进行区分（红色=危重，琥珀色=紧急，绿色=稳定）。

## 主要设计特点

- **语义颜色编码**：使用红色、琥珀色和绿色表示不同的优先级等级（并非随意的装饰）
- **阶段标签**：左对齐的浅色标签用于标注工作流程的各个阶段
- **汇聚路径**：多个入口点先汇合，再分叉，最后再次汇聚
- **嵌套容器**：将各项诊断检查归类于带有内部节点的容器中
- **图例**：底部的颜色说明表用于解释不同的优先级含义

## 图表展示

```xml
<svg width="100%" viewBox="0 0 680 620" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Stage labels -->
  <text class="ts" x="40" y="68" text-anchor="start" opacity=".5">Arrival</text>
  <text class="ts" x="40" y="168" text-anchor="start" opacity=".5">Assessment</text>
  <text class="ts" x="40" y="288" text-anchor="start" opacity=".5">Priority routing</text>
  <text class="ts" x="40" y="418" text-anchor="start" opacity=".5">Diagnostics</text>
  <text class="ts" x="40" y="518" text-anchor="start" opacity=".5">Outcome</text>

  <!-- Arrival: Ambulance -->
  <g class="node c-gray">
    <rect x="140" y="40" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="220" y="60" text-anchor="middle" dominant-baseline="central">Ambulance</text>
    <text class="ts" x="220" y="80" text-anchor="middle" dominant-baseline="central">Emergency transport</text>
  </g>

  <!-- Arrival: Walk-in -->
  <g class="node c-gray">
    <rect x="380" y="40" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="460" y="60" text-anchor="middle" dominant-baseline="central">Walk-in</text>
    <text class="ts" x="460" y="80" text-anchor="middle" dominant-baseline="central">Self-arrival</text>
  </g>

  <!-- Arrows to Triage -->
  <line x1="220" y1="96" x2="300" y2="140" class="arr" marker-end="url(#arrow)"/>
  <line x1="460" y1="96" x2="380" y2="140" class="arr" marker-end="url(#arrow)"/>

  <!-- Triage -->
  <g class="node c-purple">
    <rect x="240" y="140" width="200" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="160" text-anchor="middle" dominant-baseline="central">Triage</text>
    <text class="ts" x="340" y="180" text-anchor="middle" dominant-baseline="central">Nurse assessment, vitals</text>
  </g>

  <!-- Arrows from Triage to Priority -->
  <line x1="280" y1="196" x2="140" y2="260" class="arr" marker-end="url(#arrow)"/>
  <line x1="340" y1="196" x2="340" y2="260" class="arr" marker-end="url(#arrow)"/>
  <line x1="400" y1="196" x2="540" y2="260" class="arr" marker-end="url(#arrow)"/>

  <!-- Priority: Red - Trauma -->
  <g class="node c-red">
    <rect x="60" y="260" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="140" y="280" text-anchor="middle" dominant-baseline="central">Trauma bay</text>
    <text class="ts" x="140" y="300" text-anchor="middle" dominant-baseline="central">Priority: critical</text>
  </g>

  <!-- Priority: Yellow - Exam rooms -->
  <g class="node c-amber">
    <rect x="260" y="260" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="280" text-anchor="middle" dominant-baseline="central">Exam rooms</text>
    <text class="ts" x="340" y="300" text-anchor="middle" dominant-baseline="central">Priority: urgent</text>
  </g>

  <!-- Priority: Green - Waiting -->
  <g class="node c-green">
    <rect x="460" y="260" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="540" y="280" text-anchor="middle" dominant-baseline="central">Waiting area</text>
    <text class="ts" x="540" y="300" text-anchor="middle" dominant-baseline="central">Priority: stable</text>
  </g>

  <!-- Arrows to Diagnostics -->
  <line x1="140" y1="316" x2="220" y2="390" class="arr" marker-end="url(#arrow)"/>
  <line x1="340" y1="316" x2="340" y2="390" class="arr" marker-end="url(#arrow)"/>
  <line x1="540" y1="316" x2="460" y2="390" class="arr" marker-end="url(#arrow)"/>

  <!-- Diagnostics container -->
  <g class="c-teal">
    <rect x="140" y="390" width="400" height="56" rx="12" stroke-width="0.5"/>
  </g>

  <!-- Labs -->
  <g class="node c-teal">
    <rect x="160" y="400" width="110" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="215" y="418" text-anchor="middle" dominant-baseline="central">Labs</text>
  </g>

  <!-- Imaging -->
  <g class="node c-teal">
    <rect x="285" y="400" width="110" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="340" y="418" text-anchor="middle" dominant-baseline="central">Imaging</text>
  </g>

  <!-- Diagnosis -->
  <g class="node c-teal">
    <rect x="410" y="400" width="110" height="36" rx="6" stroke-width="0.5"/>
    <text class="ts" x="465" y="418" text-anchor="middle" dominant-baseline="central">Diagnosis</text>
  </g>

  <!-- Arrows to Outcomes -->
  <line x1="215" y1="446" x2="160" y2="490" class="arr" marker-end="url(#arrow)"/>
  <line x1="340" y1="446" x2="340" y2="490" class="arr" marker-end="url(#arrow)"/>
  <line x1="465" y1="446" x2="520" y2="490" class="arr" marker-end="url(#arrow)"/>

  <!-- Outcome: Admission -->
  <g class="node c-coral">
    <rect x="80" y="490" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="160" y="510" text-anchor="middle" dominant-baseline="central">Admission</text>
    <text class="ts" x="160" y="530" text-anchor="middle" dominant-baseline="central">Inpatient ward</text>
  </g>

  <!-- Outcome: Surgery -->
  <g class="node c-coral">
    <rect x="260" y="490" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="510" text-anchor="middle" dominant-baseline="central">Surgery</text>
    <text class="ts" x="340" y="530" text-anchor="middle" dominant-baseline="central">Operating room</text>
  </g>

  <!-- Outcome: Discharge -->
  <g class="node c-coral">
    <rect x="440" y="490" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="520" y="510" text-anchor="middle" dominant-baseline="central">Discharge</text>
    <text class="ts" x="520" y="530" text-anchor="middle" dominant-baseline="central">Home with instructions</text>
  </g>

  <!-- Legend -->
  <text class="ts" x="140" y="580" opacity=".5">Priority levels</text>
  <g class="c-red"><rect x="140" y="592" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="162" y="604">Critical</text>
  <g class="c-amber"><rect x="240" y="592" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="262" y="604">Urgent</text>
  <g class="c-green"><rect x="340" y="592" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="362" y="604">Stable</text>
</svg>
```

## 颜色分配

| 元素 | 颜色 | 原因 |
|---------|-------|------|
| 入口点（救护车接送、自行前往） | `c-gray` | 中性起始状态 |
| 分诊环节 | `c-purple` | 处理/评估阶段 |
| 创伤急救区 | `c-red` | 极高优先级（语义层面） |
| 检查室 | `c-amber` | 高优先级（语义层面） |
| 等候区 | `c-green` | 稳定优先级（语义层面） |
| 诊断环节 | `c-teal` | 临床服务类别 |
| 最终处理结果 | `c-coral` | 最终处置类别 |

## 布局说明

- **视图框尺寸**：680×620（标准宽度，为5个阶段设置加高的高度）
- **阶段间距**：各阶段行之间间距约为110-130像素
- **对角线箭头**：用于自然连接不同列中的节点
- **包含内部节点的容器**：诊断环节采用外层`c-teal`颜色矩形，内部再设置多个节点矩形
