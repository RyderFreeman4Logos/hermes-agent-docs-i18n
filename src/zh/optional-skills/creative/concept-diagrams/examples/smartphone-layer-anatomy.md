# 智能手机结构解析图

这是一张展开式视图图，展示了智能手机从前置玻璃到后置屏幕的所有内部结构层，通过左右交替标注的方式避免文字重叠。该图直观呈现了分层拆解后的产品结构及各个组件的详细信息。

## 主要设计手法

- **垂直分层展示**：将各层次在垂直方向上分开，以便清晰展现内部结构
- **交替标注**：通过左右交替放置标签，有效防止文字重叠
- **组件细节呈现**：芯片、线圈、镜头等组件均以逼真的形状进行渲染
- **厚度比例标尺**：在图侧设置测量参考线
- **渐进式深度效果**：各层次之间略有偏移，从而营造出三维堆叠的视觉效果

## 新型图形技术

### 电容式触摸网格
```xml
<rect class="digitizer" x="0" y="0" width="140" height="90" rx="14"/>
<g transform="translate(8, 8)">
  <!-- Horizontal lines -->
  <line class="digitizer-grid" x1="0" y1="15" x2="124" y2="15"/>
  <line class="digitizer-grid" x1="0" y1="37" x2="124" y2="37"/>
  <!-- Vertical lines -->
  <line class="digitizer-grid" x1="20" y1="0" x2="20" y2="74"/>
  <line class="digitizer-grid" x1="50" y1="0" x2="50" y2="74"/>
</g>
<!-- Touch point indicator -->
<circle cx="70" cy="45" r="12" fill="none" stroke="#7F77DD" stroke-width="2" opacity="0.6"/>
<circle cx="70" cy="45" r="5" fill="#7F77DD" opacity="0.4"/>
```

### OLED RGB子像素
```xml
<rect class="oled-panel" x="0" y="0" width="140" height="90" rx="12"/>
<g transform="translate(10, 10)">
  <!-- RGB pixel group -->
  <rect class="oled-subpixel-r" x="0" y="0" width="2" height="6"/>
  <rect class="oled-subpixel-g" x="3" y="0" width="2" height="6"/>
  <rect class="oled-subpixel-b" x="6" y="0" width="2" height="6"/>
  <!-- Repeat pattern -->
  <rect class="oled-subpixel-r" x="11" y="0" width="2" height="6"/>
  <rect class="oled-subpixel-g" x="14" y="0" width="2" height="6"/>
  <rect class="oled-subpixel-b" x="17" y="0" width="2" height="6"/>
</g>
```

### 带芯片的逻辑板
```xml
<rect class="pcb" x="0" y="0" width="116" height="106" rx="3"/>
<!-- PCB traces -->
<path class="pcb-trace" d="M 8 50 L 30 50 L 30 35"/>

<!-- CPU chip -->
<rect class="chip-cpu" x="30" y="20" width="55" height="35" rx="3"/>
<text class="chip-label" x="57" y="35" text-anchor="middle">A17 Pro</text>

<!-- RAM chip -->
<rect class="chip-ram" x="30" y="62" width="35" height="18" rx="2"/>
<text class="chip-label" x="47" y="74" text-anchor="middle">8GB RAM</text>

<!-- Storage chip -->
<rect class="chip-storage" x="30" y="85" width="55" height="16" rx="2"/>
<text class="chip-label" x="57" y="96" text-anchor="middle">256GB NAND</text>
```

### 相机镜头阵列
```xml
<!-- Main camera -->
<circle class="camera-lens" cx="20" cy="20" r="18"/>
<circle class="camera-lens-inner" cx="20" cy="20" r="13"/>
<circle class="camera-sensor" cx="20" cy="20" r="8"/>
<circle cx="20" cy="20" r="3" fill="#1a1a18"/>

<!-- Secondary camera (smaller) -->
<circle class="camera-lens" cx="15" cy="15" r="13"/>
<circle class="camera-lens-inner" cx="15" cy="15" r="9"/>
<circle class="camera-sensor" cx="15" cy="15" r="5"/>
```

### 带磁体的无线充电线圈
```xml
<!-- Concentric coil rings -->
<circle class="charging-coil-outer" cx="0" cy="0" r="30"/>
<circle class="charging-coil" cx="0" cy="0" r="23"/>
<circle class="charging-coil" cx="0" cy="0" r="16"/>
<circle class="charging-coil" cx="0" cy="0" r="9"/>

<!-- MagSafe magnet ring -->
<circle class="magnet" cx="0" cy="-35" r="3"/>
<circle class="magnet" cx="25" cy="-25" r="3"/>
<circle class="magnet" cx="35" cy="0" r="3"/>
<circle class="magnet" cx="25" cy="25" r="3"/>
<!-- ... continue around circle -->
```

### 电池单元
```xml
<rect class="battery" x="0" y="0" width="140" height="90" rx="10"/>
<rect class="battery-cell" x="10" y="12" width="120" height="60" rx="6"/>

<text x="70" y="38" text-anchor="middle" fill="#27500A" style="font-size:9px">Li-Ion Polymer</text>
<text x="70" y="52" text-anchor="middle" fill="#27500A" style="font-size:12px; font-weight:bold">4422 mAh</text>

<rect class="battery-connector" x="55" y="75" width="30" height="10" rx="2"/>
```

## CSS类名

```css
/* Glass */
.front-glass { fill: #E8E6DE; stroke: #888780; stroke-width: 1; opacity: 0.9; }
.back-glass { fill: #2C2C2A; stroke: #444441; stroke-width: 1; }

/* Touch digitizer */
.digitizer { fill: #EEEDFE; stroke: #534AB7; stroke-width: 1; }
.digitizer-grid { stroke: #AFA9EC; stroke-width: 0.3; fill: none; }

/* OLED */
.oled-panel { fill: #1a1a18; stroke: #444441; stroke-width: 1; }
.oled-subpixel-r { fill: #E24B4A; }
.oled-subpixel-g { fill: #97C459; }
.oled-subpixel-b { fill: #378ADD; }

/* Midframe */
.midframe { fill: #B4B2A9; stroke: #5F5E5A; stroke-width: 1.5; }

/* Logic board */
.pcb { fill: #0F6E56; stroke: #085041; stroke-width: 1; }
.pcb-trace { stroke: #5DCAA5; stroke-width: 0.3; fill: none; }
.chip-cpu { fill: #3C3489; stroke: #534AB7; stroke-width: 0.5; }
.chip-ram { fill: #185FA5; stroke: #378ADD; stroke-width: 0.5; }
.chip-storage { fill: #27500A; stroke: #3B6D11; stroke-width: 0.5; }

/* Battery */
.battery { fill: #EAF3DE; stroke: #3B6D11; stroke-width: 1.5; }
.battery-cell { fill: #97C459; stroke: #639922; stroke-width: 0.5; }

/* Camera */
.camera-lens { fill: #0C447C; stroke: #185FA5; stroke-width: 0.5; }
.camera-lens-inner { fill: #1a1a18; stroke: #378ADD; stroke-width: 0.3; }
.camera-sensor { fill: #3C3489; stroke: #534AB7; stroke-width: 0.3; }

/* Wireless charging */
.charging-coil { fill: none; stroke: #EF9F27; stroke-width: 1.5; }
.magnet { fill: #5F5E5A; stroke: #444441; stroke-width: 0.5; }
```

## 布局说明

- **视图框尺寸**：900×780（垂直排列时需设置较高的高度）
- **图层偏移**：为营造层次感，每层需向右及向下各偏移10像素
- **标签位置规则**：奇数层标签置于右侧，偶数层标签置于左侧
- **厚度刻度**：在左侧设置垂直方向的测量标尺
- **正反面标识**：在顶部和底部添加文字标签
- **芯片标签**：直接在芯片图形上使用6像素大小的白色小字标注
