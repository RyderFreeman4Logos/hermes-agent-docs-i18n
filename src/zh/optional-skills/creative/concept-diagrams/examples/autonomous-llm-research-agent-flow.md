# 自主式大语言模型研究智能体流程图

该流程图由多个部分组成，展示了Karpathy提出的自主研究框架：人机协作交接环节、包含“保留/丢弃”决策分支的自主实验循环，以及可自定义的训练流程。图中还运用了回环箭头、汇聚型决策路径，以及对不同结果进行语义化颜色标注。

## 主要设计模式

- **三部分布局**：设置区、主循环容器和细节容器——各部分在视觉上各有区分
- **中性虚线容器**：循环流程与训练流程采用`var(--bg-secondary)`背景色并搭配虚线边框，从而让彩色内容节点更加突出
- **具有汇聚特性的决策分支**：“val_bpb有提升吗？”这一分支会分为“保留”（绿色）和“丢弃”（红色）两个选项，随后两者又会汇聚到“记录至results.tsv”这一步
- **回环箭头**：容器右侧的带圆角虚线路径，用于表示无限循环
- **基于语义的结果颜色标注**：绿色代表有提升（保留），红色代表无提升（丢弃）——并非随意设计的装饰元素
- **关键步骤高亮显示**：“启动训练”操作使用`c-coral`颜色，以便在众多`c-teal`颜色的操作中突出显示这一最重要步骤
- **横向流程布局**：训练细节部分通过从左到右的箭头连接各个节点（GPT → MuonAdamW → 评估）
- **底部元数据栏**：固定格式的约束条件以居中的微妙文字形式显示在流程节点下方
- **图例行**：底部配有颜色说明，解释每种颜色的含义

## 图表展示

```xml
<svg width="100%" viewBox="0 0 680 920" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- ========================================== -->
  <!-- SECTION 1: SETUP (Human → program.md → AI) -->
  <!-- ========================================== -->

  <text class="ts" x="40" y="30" text-anchor="start" opacity=".5">One-time setup</text>

  <!-- Human -->
  <g class="node c-gray">
    <rect x="60" y="42" width="140" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="130" y="62" text-anchor="middle" dominant-baseline="central">Human</text>
    <text class="ts" x="130" y="82" text-anchor="middle" dominant-baseline="central">Researcher</text>
  </g>

  <!-- Arrow: Human → program.md -->
  <line x1="200" y1="70" x2="250" y2="70" class="arr" marker-end="url(#arrow)"/>

  <!-- program.md -->
  <g class="node c-gray">
    <rect x="250" y="42" width="180" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="62" text-anchor="middle" dominant-baseline="central">program.md</text>
    <text class="ts" x="340" y="82" text-anchor="middle" dominant-baseline="central">Agent instructions</text>
  </g>

  <!-- Arrow: program.md → AI Agent -->
  <line x1="430" y1="70" x2="470" y2="70" class="arr" marker-end="url(#arrow)"/>

  <!-- AI Agent -->
  <g class="node c-purple">
    <rect x="470" y="42" width="160" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="550" y="62" text-anchor="middle" dominant-baseline="central">AI agent</text>
    <text class="ts" x="550" y="82" text-anchor="middle" dominant-baseline="central">Claude / Codex</text>
  </g>

  <!-- Arrow: Setup row → Loop (from program.md center down) -->
  <line x1="340" y1="98" x2="340" y2="142" class="arr" marker-end="url(#arrow)"/>

  <!-- ========================================== -->
  <!-- SECTION 2: AUTONOMOUS EXPERIMENT LOOP      -->
  <!-- ========================================== -->

  <!-- Loop container (neutral dashed) -->
  <g>
    <rect x="40" y="142" width="600" height="528" rx="16"
          stroke-width="1" stroke-dasharray="6 4"
          fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="170">Autonomous experiment loop</text>
    <text class="ts" x="66" y="188">~12 experiments/hour — runs until manually stopped</text>
  </g>

  <!-- Step 1: Read code + past results -->
  <g class="node c-teal">
    <rect x="170" y="208" width="280" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="310" y="230" text-anchor="middle" dominant-baseline="central">Read code + past results</text>
  </g>

  <!-- Arrow: S1 → S2 -->
  <line x1="310" y1="252" x2="310" y2="274" class="arr" marker-end="url(#arrow)"/>

  <!-- Step 2: Propose + edit train.py -->
  <g class="node c-teal">
    <rect x="170" y="274" width="280" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="310" y="294" text-anchor="middle" dominant-baseline="central">Propose + edit train.py</text>
    <text class="ts" x="310" y="314" text-anchor="middle" dominant-baseline="central">Arch, optimizer, hyperparameters</text>
  </g>

  <!-- Arrow: S2 → S3 -->
  <line x1="310" y1="330" x2="310" y2="352" class="arr" marker-end="url(#arrow)"/>

  <!-- Step 3: Run training (highlighted — key step) -->
  <g class="node c-coral">
    <rect x="170" y="352" width="280" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="310" y="372" text-anchor="middle" dominant-baseline="central">Run training</text>
    <text class="ts" x="310" y="392" text-anchor="middle" dominant-baseline="central">uv run train.py (5 min budget)</text>
  </g>

  <!-- Arrow: S3 → S4 -->
  <line x1="310" y1="408" x2="310" y2="430" class="arr" marker-end="url(#arrow)"/>

  <!-- Step 4: Decision — val_bpb improved? -->
  <g class="node c-gray">
    <rect x="170" y="430" width="280" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="310" y="452" text-anchor="middle" dominant-baseline="central">val_bpb improved?</text>
  </g>

  <!-- Decision arrows to Keep / Discard -->
  <line x1="240" y1="474" x2="175" y2="508" class="arr" marker-end="url(#arrow)"/>
  <line x1="380" y1="474" x2="445" y2="508" class="arr" marker-end="url(#arrow)"/>

  <!-- Decision labels -->
  <text class="ts" x="195" y="496" opacity=".6">yes</text>
  <text class="ts" x="416" y="496" opacity=".6">no</text>

  <!-- Keep — advance branch -->
  <g class="node c-green">
    <rect x="70" y="508" width="210" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="175" y="528" text-anchor="middle" dominant-baseline="central">Keep</text>
    <text class="ts" x="175" y="548" text-anchor="middle" dominant-baseline="central">Advance git branch</text>
  </g>

  <!-- Discard — git reset -->
  <g class="node c-red">
    <rect x="340" y="508" width="210" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="445" y="528" text-anchor="middle" dominant-baseline="central">Discard</text>
    <text class="ts" x="445" y="548" text-anchor="middle" dominant-baseline="central">Git reset to previous</text>
  </g>

  <!-- Converge arrows: Keep → Log, Discard → Log -->
  <line x1="175" y1="564" x2="250" y2="590" class="arr" marker-end="url(#arrow)"/>
  <line x1="445" y1="564" x2="370" y2="590" class="arr" marker-end="url(#arrow)"/>

  <!-- Step 6: Log to results.tsv -->
  <g class="node c-teal">
    <rect x="170" y="590" width="280" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="310" y="612" text-anchor="middle" dominant-baseline="central">Log to results.tsv</text>
  </g>

  <!-- Loop-back arrow (dashed, right side) -->
  <path d="M 450 612 L 564 612 Q 576 612 576 600 L 576 242 Q 576 230 564 230 L 450 230"
        fill="none" class="arr" stroke-dasharray="4 3" marker-end="url(#arrow)"/>

  <!-- ========================================== -->
  <!-- SECTION 3: TRAINING PIPELINE DETAILS       -->
  <!-- ========================================== -->

  <!-- Connection arrow: Loop → Training details -->
  <line x1="310" y1="670" x2="310" y2="710" class="arr" marker-end="url(#arrow)"/>

  <!-- Training container (neutral dashed) -->
  <g>
    <rect x="40" y="710" width="600" height="170" rx="16"
          stroke-width="1" stroke-dasharray="6 4"
          fill="var(--bg-secondary)" stroke="var(--border)"/>
    <text class="th" x="66" y="738">train.py — modifiable training pipeline</text>
    <text class="ts" x="66" y="756">Runs during each training step — single GPU, single file</text>
  </g>

  <!-- GPT model -->
  <g class="node c-coral">
    <rect x="70" y="774" width="155" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="147" y="794" text-anchor="middle" dominant-baseline="central">GPT model</text>
    <text class="ts" x="147" y="814" text-anchor="middle" dominant-baseline="central">RoPE, FlashAttn3</text>
  </g>

  <!-- Arrow: GPT → MuonAdamW -->
  <line x1="225" y1="802" x2="260" y2="802" class="arr" marker-end="url(#arrow)"/>

  <!-- MuonAdamW optimizer -->
  <g class="node c-coral">
    <rect x="260" y="774" width="155" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="337" y="794" text-anchor="middle" dominant-baseline="central">MuonAdamW</text>
    <text class="ts" x="337" y="814" text-anchor="middle" dominant-baseline="central">Hybrid optimizer</text>
  </g>

  <!-- Arrow: MuonAdamW → Evaluation -->
  <line x1="415" y1="802" x2="450" y2="802" class="arr" marker-end="url(#arrow)"/>

  <!-- Evaluation -->
  <g class="node c-amber">
    <rect x="450" y="774" width="155" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="527" y="794" text-anchor="middle" dominant-baseline="central">Evaluation</text>
    <text class="ts" x="527" y="814" text-anchor="middle" dominant-baseline="central">val_bpb metric</text>
  </g>

  <!-- Footer: fixed constraints -->
  <text class="ts" x="340" y="856" text-anchor="middle" opacity=".5">climbmix-400b data · 8K BPE vocab · 300s budget · 2048 context</text>

  <!-- ========================================== -->
  <!-- LEGEND                                     -->
  <!-- ========================================== -->

  <g class="c-teal"><rect x="40" y="890" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="62" y="902">Agent actions</text>

  <g class="c-coral"><rect x="170" y="890" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="192" y="902">Training run</text>

  <g class="c-green"><rect x="300" y="890" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="322" y="902">Improvement</text>

  <g class="c-red"><rect x="430" y="890" width="14" height="14" rx="3" stroke-width="0.5"/></g>
  <text class="ts" x="452" y="902">No improvement</text>

</svg>
```

## 颜色分配规则

| 元素 | 颜色 | 原因 |
|------|------|------|
| Human, program.md | `c-gray` | 中性风格的设置/输入节点 |
| AI agent | `c-purple` | 主要的智能执行主体 |
| 循环操作步骤 | `c-teal` | 智能体的分析/编辑操作 |
| 运行训练 | `c-coral` | 强调关键步骤——5分钟的训练过程 |
| 决策检查 | `c-gray` | 中性的评估节点 |
| 保留（有改进） | `c-green` | 语义上成功——val_bpb值下降 |
| 抛弃（无改进） | `c-red` | 语义上失败——无任何改善 |
| 训练流程节点 | `c-coral` | 训练基础设施的组成部分 |
| 评估节点 | `c-amber` | 与训练部分区分开来，承担测量/指标功能 |
| 容器元素 | 中性色（虚线） | 用于柔和分组，不会掩盖内容主体 |

## 布局说明

- **视图框尺寸**：680×920（标准宽度，高度足以容纳3个区域）
- **三个区域划分**：设置区（y=30–98）、循环容器区（y=142–670）、训练详情区（y=710–880）
- **容器样式**：虚线边框（`stroke-dasharray="6 4"`），中性填充色（`var(--bg-secondary)`），边框宽度为1像素——由于无颜色填充，内部节点更为突出
- **循环回箭头**：由虚线 `<path>` 绘制，节点转角处采用二次曲线（`Q`）实现平滑的圆角过渡，从“日志”区域延伸至循环容器右侧的“读取代码”区域
- **决策流程结构**：一个问题节点（“val_bpb值有所改善吗？”），通过对角线箭头连接到“保留”/“抛弃”选项，随后再通过汇聚的对角线箭头回到“将结果写入results.tsv”节点
- **决策标签**：在对应对角线箭头上标注“是”/“否”，透明度设置为`.6`以保持低调
- **关键步骤突出显示**：“运行训练”步骤使用`c-coral`颜色，而周边步骤则采用`c-teal`颜色，从而将视线引向最关键的步骤
- **水平子流程**：训练流程中的各个节点通过从左到右的箭头依次连接（GPT模型 → MuonAdamW优化器 → 评估环节）
- **页脚元数据**：固定约束条件（数据量、词汇表大小、预算、上下文限制等）以居中显示的`ts`文本行形式呈现，透明度为`.5`
- **图例**：页面底部配有四种颜色样本，用于说明每种颜色所代表的含义
