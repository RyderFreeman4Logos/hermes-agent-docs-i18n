# 乱序CPU核心微架构

该图为现代超标量乱序CPU核心内部流水线阶段的结构示意图。它展示了具有并行路径的多级垂直流程、执行端口的扩展模式，以及独立的存储层次结构侧边栏。

## 主要设计元素

- **多级垂直流程**：包含六个流水线阶段（前端处理 → 重命名 → 调度 → 执行 → 取出）
- **并行解码路径**：主解码路径与微操作缓存旁路路径（缓存命中时用虚线表示）
- **容器分组**：按功能对逻辑阶段进行彩色容器分组
- **扩展模式**：单个调度器向6个执行端口分发指令
- **侧边栏布局**：存储层次结构置于右侧独立列中
- **阶段标签**：左对齐的标签用于标识当前流水线阶段
- **颜色编码语义**：不同功能单元类别采用不同颜色标识

## 图表类型

这是一张**结构/流程混合型**图表：
- **流程特性**：指令从上至下依次经过各个流水线阶段
- **结构特性**：各组件按功能进行分组（如重命名单元、执行集群）
- **侧边栏设计**：存储层次结构在架构上独立存在，但通过数据路径相互连接

## 流水线阶段详解

### 前端处理阶段（紫色）
```xml
<!-- Fetch Unit -->
<g class="node c-purple">
  <rect x="40" y="70" width="140" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="110" y="90" text-anchor="middle" dominant-baseline="central">Fetch unit</text>
  <text class="ts" x="110" y="110" text-anchor="middle" dominant-baseline="central">6-wide, 32B/cycle</text>
</g>

<!-- Branch Predictor (subordinate) -->
<g class="node c-purple">
  <rect x="40" y="140" width="140" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="110" y="162" text-anchor="middle" dominant-baseline="central">Branch predictor</text>
</g>

<!-- Decode -->
<g class="node c-purple">
  <rect x="230" y="70" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="310" y="90" text-anchor="middle" dominant-baseline="central">Decode</text>
  <text class="ts" x="310" y="110" text-anchor="middle" dominant-baseline="central">x86 → µops, 6-wide</text>
</g>
```

### µop缓存旁路路径（Teal）
µop缓存（解码流缓冲区）提供了一条可绕过复杂解码器的替代路径：

```xml
<!-- µop Cache parallel to decode -->
<g class="node c-teal">
  <rect x="230" y="150" width="160" height="50" rx="8" stroke-width="0.5"/>
  <text class="th" x="310" y="168" text-anchor="middle" dominant-baseline="central">µop cache (DSB)</text>
  <text class="ts" x="310" y="186" text-anchor="middle" dominant-baseline="central">4K entries, 8-wide</text>
</g>

<!-- Dashed bypass path indicating cache hit -->
<path d="M180 110 L205 110 L205 175 L230 175" fill="none" class="arr" 
      stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<text class="tx" x="164" y="148" opacity=".6">hit</text>
```

### 重命名/分配容器（Coral）
用于对容器内的相关重命名组件进行分组管理：

```xml
<!-- Outer container -->
<g class="c-coral">
  <rect x="40" y="250" width="530" height="130" rx="12" stroke-width="0.5"/>
  <text class="th" x="60" y="274">Rename / allocate</text>
  <text class="ts" x="60" y="292">Map architectural → physical registers</text>
</g>

<!-- Inner components -->
<g class="node c-coral">
  <rect x="60" y="310" width="180" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="150" y="330" text-anchor="middle" dominant-baseline="central">Register alias table</text>
  <text class="ts" x="150" y="350" text-anchor="middle" dominant-baseline="central">180 physical regs</text>
</g>
```

### 调度器分发模式（琥珀色 → 青绿色）
通过单个统一调度器将任务分配至多个执行端口：

```xml
<!-- Unified Scheduler -->
<g class="node c-amber">
  <rect x="140" y="420" width="330" height="50" rx="8" stroke-width="0.5"/>
  <text class="th" x="305" y="438" text-anchor="middle" dominant-baseline="central">Unified scheduler</text>
  <text class="ts" x="305" y="456" text-anchor="middle" dominant-baseline="central">97 entries, out-of-order dispatch</text>
</g>

<!-- Fan-out arrows to 6 ports -->
<line x1="170" y1="470" x2="90" y2="540" class="arr" marker-end="url(#arrow)"/>
<line x1="215" y1="470" x2="170" y2="540" class="arr" marker-end="url(#arrow)"/>
<line x1="265" y1="470" x2="250" y2="540" class="arr" marker-end="url(#arrow)"/>
<line x1="305" y1="470" x2="330" y2="540" class="arr" marker-end="url(#arrow)"/>
<line x1="355" y1="470" x2="410" y2="540" class="arr" marker-end="url(#arrow)"/>
<line x1="420" y1="470" x2="490" y2="540" class="arr" marker-end="url(#arrow)"/>
```

### 执行端口框模式
用于显示端口号及功能的紧凑型框体：

```xml
<!-- Execution port with multi-line capability -->
<g class="node c-teal">
  <rect x="55" y="540" width="70" height="64" rx="6" stroke-width="0.5"/>
  <text class="th" x="90" y="560" text-anchor="middle" dominant-baseline="central">Port 0</text>
  <text class="tx" x="90" y="576" text-anchor="middle" dominant-baseline="central">ALU</text>
  <text class="tx" x="90" y="590" text-anchor="middle" dominant-baseline="central">DIV</text>
</g>
```

### 重排缓冲区（粉色）
底部显示已淘汰任务的宽水平条：

```xml
<g class="c-pink">
  <rect x="40" y="670" width="530" height="40" rx="10" stroke-width="0.5"/>
  <text class="th" x="305" y="694" text-anchor="middle" dominant-baseline="central">Reorder buffer (ROB) — 512 entries, 8-wide retire</text>
</g>
```

### 内存层次结构侧边栏（蓝色）
用于显示不同缓存级别的独立列：

```xml
<!-- Container -->
<g class="c-blue">
  <rect x="600" y="30" width="190" height="360" rx="16" stroke-width="0.5"/>
  <text class="th" x="695" y="54" text-anchor="middle">Memory hierarchy</text>
</g>

<!-- Cache levels stacked vertically -->
<g class="node c-blue">
  <rect x="620" y="70" width="150" height="50" rx="8" stroke-width="0.5"/>
  <text class="th" x="695" y="88" text-anchor="middle" dominant-baseline="central">L1-I cache</text>
  <text class="ts" x="695" y="106" text-anchor="middle" dominant-baseline="central">32 KB, 8-way</text>
</g>
<!-- Additional levels follow same pattern -->
```

## 连接模式

### 指令获取路径
从L1-I缓存指向获取单元的横向箭头：
```xml
<path d="M620 95 L200 95" fill="none" class="arr" marker-end="url(#arrow)"/>
<text class="tx" x="410" y="88" text-anchor="middle" opacity=".6">instruction fetch</text>
```

### 加载/存储路径
从执行端口到L1缓存之间的复杂路径：
```xml
<path d="M250 604 L250 640 L580 640 L580 160 L620 160" fill="none" class="arr" marker-end="url(#arrow)"/>
<text class="tx" x="415" y="652" text-anchor="middle" opacity=".6">load / store</text>
```

### 提交路径（虚线）
用于显示从ROB回写至寄存器文件的路径的虚线：
```xml
<path d="M550 690 L580 690 L580 445 L595 445" fill="none" class="arr" stroke-dasharray="4 3"/>
<text class="tx" x="590" y="578" opacity=".6" transform="rotate(-90 590 578)">commit</text>
```

### 路径合并（解码 + 微操作缓存）
在重命名之前，两条路径会先进行合并：
```xml
<line x1="390" y1="98" x2="430" y2="98" class="arr"/>
<line x1="390" y1="175" x2="430" y2="175" class="arr"/>
<path d="M430 98 L430 175" fill="none" stroke="var(--text-secondary)" stroke-width="1.5"/>
<line x1="430" y1="136" x2="470" y2="136" class="arr" marker-end="url(#arrow)"/>
```

## 文本类别

该图表为极小的标签额外定义了一种文本类别：

```css
.tx { font-family: system-ui, -apple-system, sans-serif; font-size: 10px; fill: var(--text-secondary); }
```

**用途：**  
- 执行端口功能标签（ALU、分支处理、加载操作等）  
- 连接节点标签（指令获取、加载/存储、写回操作）  
- DRAM延迟标注  

## 颜色语义映射  

| 颜色 | 阶段 | 组件 |
|------|------|------|
| `c-purple` | 前端阶段 | 指令获取、分支预测器、指令解码 |
| `c-teal` | 执行阶段 | 微操作缓存、执行端口 |
| `c-coral` | 重命名阶段 | 注册地址转换器、物理寄存器文件、空闲列表 |
| `c-amber` | 调度阶段 | 统一调度器 |
| `c-pink` | 撤销阶段 | 重排序缓冲区 |
| `c-blue` | 内存阶段 | L1指令缓存、L1数据缓存、L2缓存、DRAM |
| `c-gray` | 外部接口 | 芯片外DRAM |

## 布局说明  

- **视图框尺寸**：820×720（为体现垂直流水线结构，高度大于宽度）  
- **主流水线区域**：x=40 至 x=570（宽度为530像素）  
- **内存侧边栏区域**：x=600 至 x=790（宽度为190像素）  
- **阶段标签**：位于x=30位置，左对齐，透明度为50%  
- **垂直间距**：各主要阶段之间间距约为80–100像素  
- **容器内边距**：容器内部留有20像素的边距  
- **端口间距**：各执行端口中心之间的间距为80像素  
- **图例**：位于内存侧边栏的右下角，用于说明颜色编码规则  

## 所展示的架构细节  

| 组件 | 规格参数 | 备注 |
|------|----------|------|
| 指令获取阶段 | 6路并行，每周期处理32字节 | 典型的现代Intel/AMD架构 |
| 指令解码阶段 | 6路并行，将x86指令转换为微操作 | 解码逻辑较为复杂 |
| 微操作缓存 | 4K条目，8路并行访问 | 用于加速高频访问的代码路径 |
| 注册地址转换器 | 支持180个物理寄存器 | 可实现深度重命名优化 |
| 调度器 | 97个调度单元 | 采用统一寄存器文件结构 |
| 执行阶段 | 6个执行端口 | 包含2个ALU、2个加载/存储端口以及1个向量处理端口 |
| 撤销队列 | 512个条目，8路并行访问 | 采用顺序撤销机制 |
| L1指令缓存 | 容量32 KB，8路并行访问 | 用于存储指令 |
| L1数据缓存 | 容量48 KB，12路并行访问 | 用于存储数据 |
| L2缓存 | 容量1.25 MB，20路并行访问 | 统一结构设计 |
| DRAM | DDR5-6400频率，延迟约80纳秒 | 位于芯片外部 |

## 何时使用此图表风格  

适用于以下场景：  
- CPU/GPU微架构的可视化展示  
- 编译器流水线各阶段的演示  
- 网络数据包处理流程的可视化  
- 任何由调度器驱动、包含多个并行执行单元的系统  
- 具有多个功能单元的硬件设计
