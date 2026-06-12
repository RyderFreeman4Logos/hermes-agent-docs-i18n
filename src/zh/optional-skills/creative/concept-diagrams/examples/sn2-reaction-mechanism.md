# SN2反应机理

该化学图展示了氢氧根离子与溴甲烷之间的双分子亲核取代（SN2）反应机理。图中包含分子结构渲染、电子运动箭头、过渡态表示法以及反应能量曲线。

## 使用的关键元素样式

- **分子结构**：带有键的球棒式原子模型
- **电子运动**：表示亲核进攻的曲线箭头
- **过渡态**：带部分电荷的五配位中间体，用括号标出
- **立体化学**：用于表示三维构型的楔形/虚线键
- **能量曲线**：势能与反应坐标的关系图
- **注释框**：关键特征及机理说明

## 图表类型

这是一张**化学机理图**，具有以下特点：
- **分子渲染**：原子以带有元素符号的彩色圆圈表示
- **键的表示方式**：实线、楔形线、虚线以及部分带电的虚线键
- **反应箭头**：电子运动用曲线表示，反应进程用直线表示
- **能量景观**：机理图下方为定量能量曲线

## 分子结构元素

### 原子渲染方式

```xml
<!-- Carbon atom (dark) -->
<circle cx="0" cy="0" r="14" class="carbon"/>
<text class="chem" x="0" y="5" text-anchor="middle" fill="white" font-weight="500">C</text>

<!-- Oxygen atom (red) -->
<circle cx="0" cy="0" r="14" class="oxygen"/>
<text class="chem" x="0" y="5" text-anchor="middle" fill="white" font-weight="500">O</text>

<!-- Hydrogen atom (light with border) -->
<circle cx="38" cy="0" r="8" class="hydrogen"/>
<text class="chem-sm" x="38" y="4" text-anchor="middle">H</text>

<!-- Bromine atom (brown) -->
<circle cx="52" cy="0" r="16" class="bromine"/>
<text class="chem" x="52" y="5" text-anchor="middle" fill="white" font-weight="500">Br</text>
```

```css
.carbon { fill: #2C2C2A; }
.hydrogen { fill: #F1EFE8; stroke: #888780; stroke-width: 1; }
.oxygen { fill: #E24B4A; }
.bromine { fill: #993C1D; }
.nitrogen { fill: #378ADD; }  /* for other reactions */
```

### 绑定类型

```xml
<!-- Single bond (solid) -->
<line x1="14" y1="0" x2="38" y2="0" class="bond"/>

<!-- Wedge bond (coming toward viewer) -->
<polygon class="bond-wedge" points="0,-14 -6,-35 6,-35"/>

<!-- Dash bond (going away from viewer) -->
<line x1="-10" y1="10" x2="-28" y2="28" class="bond-dash"/>

<!-- Partial bond (forming/breaking) -->
<line x1="-40" y1="0" x2="-14" y2="0" class="bond-partial"/>
```

```css
.bond { stroke: var(--text-primary); stroke-width: 2.5; fill: none; stroke-linecap: round; }
.bond-thin { stroke: var(--text-primary); stroke-width: 1.5; fill: none; }
.bond-partial { stroke: var(--text-primary); stroke-width: 2; fill: none; stroke-dasharray: 4 3; }
.bond-wedge { fill: var(--text-primary); stroke: none; }
.bond-dash { stroke: var(--text-primary); stroke-width: 2; fill: none; stroke-dasharray: 2 2; }
```

### 单电子对与电荷

```xml
<!-- Lone pair electrons (dots) -->
<circle cx="-8" cy="-18" r="2" fill="var(--text-primary)"/>
<circle cx="0" cy="-18" r="2" fill="var(--text-primary)"/>

<!-- Formal negative charge -->
<text class="charge" x="12" y="-12" fill="#A32D2D" font-weight="bold">⊖</text>

<!-- Partial charges (delta notation) -->
<text class="partial" x="0" y="-18" text-anchor="middle" fill="#A32D2D">δ⁻</text>
<text class="partial" x="0" y="-22" text-anchor="middle" fill="#3B6D11">δ⁺</text>
```

```css
.charge { font-family: "Times New Roman", Georgia, serif; font-size: 12px; }
.partial { font-family: "Times New Roman", Georgia, serif; font-size: 11px; font-style: italic; }
```

### 弧形箭头（电子运动）

```xml
<defs>
  <marker id="curved-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0,0 L10,5 L0,10 L3,5 Z" class="arrow-fill"/>
  </marker>
</defs>

<!-- Nucleophilic attack arrow -->
<path d="M -5,15 Q 30,60 70,25" class="arrow-curved" marker-end="url(#curved-arrow)"/>
```

```css
.arrow-curved { stroke: #534AB7; stroke-width: 2; fill: none; }
.arrow-fill { fill: #534AB7; }
```

### 过渡态括号

```xml
<!-- Left bracket -->
<path d="M -75,-70 L -85,-70 L -85,75 L -75,75" class="ts-bracket"/>

<!-- Right bracket -->
<path d="M 95,-70 L 105,-70 L 105,75 L 95,75" class="ts-bracket"/>

<!-- Double dagger symbol -->
<text class="chem" x="115" y="-60" fill="var(--text-primary)">‡</text>
```

```css
.ts-bracket { stroke: var(--text-primary); stroke-width: 1.5; fill: none; }
```

## 能源概况图

### 坐标轴

```xml
<!-- Y-axis (Energy) -->
<line x1="0" y1="280" x2="0" y2="0" class="axis" marker-end="url(#straight-arrow)"/>
<text class="t" x="-15" y="-10" text-anchor="middle" transform="rotate(-90 -15 140)">Potential Energy</text>

<!-- X-axis (Reaction Coordinate) -->
<line x1="0" y1="280" x2="600" y2="280" class="axis" marker-end="url(#straight-arrow)"/>
<text class="t" x="580" y="305" text-anchor="middle">Reaction Coordinate</text>
```

### 能量曲线

```xml
<!-- Filled area under curve -->
<path class="energy-fill" d="
  M 40,200 
  Q 150,200 250,50 
  Q 350,200 500,220 
  L 500,280 L 40,280 Z
"/>

<!-- Curve line -->
<path class="energy-curve" d="
  M 40,200 
  Q 100,200 150,150
  Q 200,80 250,50 
  Q 300,80 350,150
  Q 400,210 500,220
"/>
```

```css
.energy-curve { stroke: #534AB7; stroke-width: 2.5; fill: none; }
.energy-fill { fill: rgba(83, 74, 183, 0.1); }
```

### 能量层级与标注功能

```xml
<!-- Reactants level -->
<line x1="20" y1="200" x2="80" y2="200" stroke="#3B6D11" stroke-width="2"/>
<text class="ts" x="50" y="218" text-anchor="middle">Reactants</text>

<!-- Transition state peak -->
<circle cx="250" cy="50" r="5" fill="#534AB7"/>
<line x1="250" y1="50" x2="250" y2="280" class="energy-level"/>
<text class="ts" x="250" y="30" text-anchor="middle" fill="#534AB7" font-weight="500">Transition State [‡]</text>

<!-- Products level (lower = exergonic) -->
<line x1="470" y1="220" x2="530" y2="220" stroke="#3B6D11" stroke-width="2"/>

<!-- Activation energy arrow -->
<line x1="100" y1="200" x2="100" y2="55" class="delta-arrow" marker-end="url(#delta-arrow)"/>
<text class="ts" x="85" y="125" text-anchor="end" fill="#3B6D11">E<tspan baseline-shift="sub" font-size="8">a</tspan></text>
```

```css
.energy-level { stroke: var(--text-secondary); stroke-width: 1; stroke-dasharray: 4 2; fill: none; }
.delta-arrow { stroke: #3B6D11; stroke-width: 1.5; fill: none; }
.delta-fill { fill: #3B6D11; }
```

## 化学学科文本样式

```css
/* Chemistry notation (serif font for formulas) */
.chem { font-family: "Times New Roman", Georgia, serif; font-size: 16px; fill: var(--text-primary); }
.chem-sm { font-family: "Times New Roman", Georgia, serif; font-size: 12px; fill: var(--text-primary); }
.chem-lg { font-family: "Times New Roman", Georgia, serif; font-size: 18px; fill: var(--text-primary); }
```

## SVG中的下标/上标功能

```xml
<!-- Subscript using tspan -->
<text class="ts">E<tspan baseline-shift="sub" font-size="8">a</tspan></text>

<!-- Superscript for charges -->
<text class="chem-sm">OH⁻</text>  <!-- Using Unicode superscript minus -->
<text class="chem-sm">CH₃Br</text>  <!-- Using Unicode subscript 3 -->
```

## 颜色编码

| 元素 | 颜色 | 十六进制值 |
|------|------|-----------|
| 碳   | 深灰色 | #2C2C2A |
| 氢   | 浅奶油色 | #F1EFE8 |
| 氧   | 红色   | #E24B4A |
| 溴   | 棕色   | #993C1D |
| 氮   | 蓝色   | #378ADD |
| 电子箭头 | 紫色 | #534AB7 |
| 正电荷 | 绿色   | #3B6D11 |
| 负电荷 | 红色   | #A32D2D |

## 布局说明

- **视图框尺寸**：800×680（横向布局，用于展示反应机理与能量曲线）
- **反应机理部分**：y轴范围为60-300，依次显示反应物 → 过渡态 → 产物
- **能量曲线部分**：y轴范围为320-630，包含坐标轴与能量曲线
- **原子大小**：碳/氧/溴的半径约为12-16像素，氢的半径约为7-8像素
- **键长**：原子中心之间的距离约为25-40像素
- **阶段间距**：不同反应机理步骤之间的间距约为140像素

## 适用场景

此图表风格适用于以下情况：
- 有机反应机理（SN1、SN2、E1、E2、加成反应、消除反应）
- 反应能量曲线与动力学分析
- 立体化学示意图
- 酶的催化机理图解
- 过渡态理论可视化展示
- 任何需要分子结构呈现的化学概念
