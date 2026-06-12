# 公寓平面图：3室到4室的改造方案

该平面图展示了一处面积为1,500平方英尺的公寓，以及将其从3室结构改造为4室结构的规划方案。图中体现了建筑制图规范、房间布局、用虚线标示的拟议改动内容，以及面积对比表。

## 主要设计元素

- **建筑平面图**：展示墙体、门和窗的俯视视图
- **拟议改动**：新墙体以红色虚线标出
- **房间颜色编码**：通过不同浅色填充区分不同类型的房间
- **动线路径**：箭头标识新的通行路线
- **数据表格**：突出显示改造前后的面积对比数据
- **建筑符号**：北向箭头、比例尺、门开向指示

## 图表类型

这是一份**建筑平面图**，包含以下特点：
- **平面视图**：俯视的正投影
- **叠加展示法**：现有结构与拟议改动内容同时呈现
- **定量数据**：面积测量值及对比表格

## 建筑制图元素

### 墙体样式

```xml
<!-- Outer walls (thick) -->
<line class="wall" x1="0" y1="0" x2="560" y2="0"/>

<!-- Internal walls (thinner) -->
<line class="wall-thin" x1="180" y1="0" x2="180" y2="140"/>

<!-- Proposed new walls (dotted red) -->
<line class="proposed-wall" x1="125" y1="170" x2="125" y2="330"/>
```

```css
.wall { stroke: var(--text-primary); stroke-width: 6; fill: none; stroke-linecap: square; }
.wall-thin { stroke: var(--text-primary); stroke-width: 3; fill: none; }
.proposed-wall { stroke: #A32D2D; stroke-width: 4; fill: none; stroke-dasharray: 8 4; }
```

### 门符号

```xml
<!-- Door opening with swing arc -->
<rect x="150" y="137" width="25" height="6" fill="var(--bg-primary)"/>
<path class="door" d="M150,140 L150,165"/>
<path class="door-swing" d="M150,140 A25,25 0 0,0 175,140"/>

<!-- Sliding door (balcony) -->
<rect x="60" y="327" width="60" height="6" fill="var(--bg-primary)" stroke="var(--text-secondary)" stroke-width="1"/>
<line x1="60" y1="330" x2="90" y2="330" stroke="var(--text-secondary)" stroke-width="2"/>
<line x1="90" y1="330" x2="120" y2="330" stroke="var(--text-secondary)" stroke-width="2" stroke-dasharray="3 3"/>

<!-- Proposed door (dotted) -->
<rect x="143" y="292" width="22" height="6" fill="var(--bg-primary)" stroke="#A32D2D" stroke-width="1" stroke-dasharray="3 2"/>
<path d="M165,295 A22,22 0 0,0 165,273" stroke="#A32D2D" stroke-width="1" stroke-dasharray="3 2" fill="none"/>
```

```css
.door { stroke: var(--text-secondary); stroke-width: 1.5; fill: none; }
.door-swing { stroke: var(--text-tertiary); stroke-width: 1; fill: none; stroke-dasharray: 3 2; }
```

### 窗口符号

```xml
<!-- Window with glass indication -->
<rect class="window" x="-3" y="30" width="6" height="50"/>
<line class="window-glass" x1="0" y1="35" x2="0" y2="75"/>

<!-- Horizontal window (top wall) -->
<rect class="window" x="220" y="-3" width="60" height="6"/>
<line class="window-glass" x1="225" y1="0" x2="275" y2="0"/>
```

```css
.window { stroke: var(--text-primary); stroke-width: 1; fill: var(--bg-primary); }
.window-glass { stroke: #378ADD; stroke-width: 2; fill: none; }
```

### 房间填充功能

```xml
<!-- Different colors for room types -->
<rect class="room-master" x="3" y="3" width="174" height="134" rx="2"/>
<rect class="room-bed2" x="183" y="3" width="134" height="104" rx="2"/>
<rect class="room-living" x="3" y="173" width="554" height="154" rx="2"/>
<rect class="room-kitchen" x="443" y="3" width="114" height="104" rx="2"/>
<rect class="room-bath" x="183" y="113" width="54" height="54" rx="2"/>

<!-- Proposed new room (highlighted) -->
<rect class="room-new" x="3" y="223" width="120" height="104"/>
```

```css
.room-master { fill: rgba(206, 203, 246, 0.3); }  /* purple tint */
.room-bed2 { fill: rgba(159, 225, 203, 0.3); }    /* teal tint */
.room-bed3 { fill: rgba(250, 199, 117, 0.3); }    /* amber tint */
.room-living { fill: rgba(245, 196, 179, 0.3); }  /* coral tint */
.room-kitchen { fill: rgba(237, 147, 177, 0.3); } /* pink tint */
.room-bath { fill: rgba(133, 183, 235, 0.3); }    /* blue tint */
.room-new { fill: rgba(163, 45, 45, 0.15); }      /* red tint for proposed */
```

### 支持用例

```xml
<!-- Kitchen counter hint -->
<rect x="450" y="15" width="50" height="25" fill="none" stroke="var(--text-tertiary)" stroke-width="0.5" rx="2"/>
<text class="tx" x="475" y="30" text-anchor="middle">Counter</text>

<!-- Balcony (dashed outline) -->
<rect class="balcony-fill" x="3" y="333" width="200" height="50"/>
```

```css
.balcony { fill: none; stroke: var(--text-secondary); stroke-width: 2; stroke-dasharray: 6 3; }
.balcony-fill { fill: rgba(93, 202, 165, 0.1); }
```

### 房间标签

```xml
<!-- Room name and area -->
<text class="room-label" x="90" y="65" text-anchor="middle">MASTER</text>
<text class="room-label" x="90" y="78" text-anchor="middle">BEDROOM</text>
<text class="area-label" x="90" y="95" text-anchor="middle">195 sq ft</text>

<!-- Proposed room (in red) -->
<text class="room-label" x="63" y="268" text-anchor="middle" fill="#A32D2D">BEDROOM 4</text>
<text class="tx" x="63" y="282" text-anchor="middle" fill="#A32D2D">(NEW)</text>
```

```css
.room-label { font-family: system-ui; font-size: 11px; fill: var(--text-primary); font-weight: 500; }
.area-label { font-family: system-ui; font-size: 9px; fill: var(--text-tertiary); }
```

### 流动箭头

```xml
<defs>
  <marker id="circ-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0,0 L10,5 L0,10 Z" class="circulation-fill"/>
  </marker>
</defs>

<path class="circulation" d="M300,250 L200,250 L145,250 L145,280" marker-end="url(#circ-arrow)"/>
<text class="tx" x="250" y="242" fill="#3B6D11" font-weight="500">New corridor access</text>
```

```css
.circulation { stroke: #3B6D11; stroke-width: 2; fill: none; }
.circulation-fill { fill: #3B6D11; }
```

### 北箭头与比例尺

```xml
<!-- North arrow -->
<g transform="translate(520, 260)">
  <circle cx="0" cy="0" r="20" fill="none" stroke="var(--text-tertiary)" stroke-width="0.5"/>
  <polygon points="0,-18 -5,5 0,0 5,5" fill="var(--text-primary)"/>
  <text class="tx" x="0" y="-22" text-anchor="middle">N</text>
</g>

<!-- Scale bar -->
<g transform="translate(420, 300)">
  <line x1="0" y1="0" x2="100" y2="0" stroke="var(--text-primary)" stroke-width="2"/>
  <line x1="0" y1="-5" x2="0" y2="5" stroke="var(--text-primary)" stroke-width="1"/>
  <line x1="50" y1="-3" x2="50" y2="3" stroke="var(--text-primary)" stroke-width="1"/>
  <line x1="100" y1="-5" x2="100" y2="5" stroke="var(--text-primary)" stroke-width="1"/>
  <text class="tx" x="0" y="15" text-anchor="middle">0</text>
  <text class="tx" x="50" y="15" text-anchor="middle">5'</text>
  <text class="tx" x="100" y="15" text-anchor="middle">10'</text>
</g>
```

## 区域对比表

### 表结构

```xml
<!-- Header row -->
<rect class="table-header" x="0" y="0" width="180" height="28" rx="4 4 0 0"/>
<text class="ts" x="90" y="18" text-anchor="middle" font-weight="500">Room</text>

<!-- Normal row -->
<rect class="table-row" x="0" y="28" width="180" height="24"/>
<text class="tx" x="10" y="44">Master Bedroom</text>
<text class="tx" x="230" y="44" text-anchor="middle">195</text>

<!-- Alternating row -->
<rect class="table-row-alt" x="0" y="52" width="180" height="24"/>

<!-- Highlighted row (for changes) -->
<rect class="table-highlight" x="0" y="100" width="180" height="24"/>
<text class="tx" x="10" y="116" fill="#A32D2D" font-weight="500">Bedroom 4 (NEW)</text>
<text class="tx" x="430" y="116" text-anchor="middle" fill="#3B6D11">+100</text>

<!-- Total row -->
<rect x="0" y="268" width="180" height="28" fill="var(--bg-secondary)" stroke="var(--border)" stroke-width="1"/>
<text class="ts" x="10" y="286" font-weight="500">TOTAL CARPET AREA</text>
```

```css
.table-header { fill: var(--bg-secondary); }
.table-row { fill: var(--bg-primary); stroke: var(--border); stroke-width: 0.5; }
.table-row-alt { fill: var(--bg-tertiary); stroke: var(--border); stroke-width: 0.5; }
.table-highlight { fill: rgba(163, 45, 45, 0.1); stroke: #A32D2D; stroke-width: 0.5; }
```

## 布局说明

- **视图框尺寸**：800×780（纵向布局，适用于平面图与表格）
- **比例尺**：10像素 = 1英尺（公寓大小约为50英尺 × 33英尺）
- **平面图原点**：为预留边距，设定在(50, 60)位置
- **墙体厚度**：外墙6像素，内墙3像素（对应约6英寸厚的墙体）
- **房间标签**：位于每个房间中央，下方标注面积
- **表格位置**：置于平面图下方，占据整个宽度

## 颜色编码

| 元素 | 颜色 | 用途 |
|------|------|------|
| 待建墙体 | 红色（#A32D2D），点状线 | 新建结构 |
| 新增房间区域填充色 | 15%透明度的红色 | 第4卧室区域 |
| 通道区域 | 绿色（#3B6D11） | 新建通行路径 |
| 窗户玻璃 | 蓝色（#378ADD） | 标示玻璃部分 |
| 卧室 | 紫色/青绿色/琥珀色系 | 区分不同类型的卧室 |
| 湿区 | 蓝色色调 | 浴室区域 |
| 客厅区域 | 珊瑚色色调 | 公共活动区域 |

## 适用场景

此图表风格适用于：
- 公寓/住宅平面图
- 办公空间布局规划
- 展示改造前后的方案
- 需要计算面积的空间规划
- 房地产营销材料
- 室内设计展示
- 建筑审批相关文件
