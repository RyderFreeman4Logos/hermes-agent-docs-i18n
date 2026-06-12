# 智慧城市基础设施

该图展示了一个多系统集成方案，呈现了通过中央物联网平台相互连接的各类城市基础设施（电力、水务、交通系统），并在其上方设置了面向市民的仪表盘界面。图中展示了中心辐射式布局、多样化的实体形状以及用户界面原型。

## 主要设计模式

- **中心辐射式布局**：以中央物联网平台为核心，向各子系统延伸数据连接
- **连接点**：用于标识数据线路与中央枢纽相连位置的视觉标记
- **仪表盘/界面原型**：包含迷你图表、计量仪表及状态指示器的屏幕界面
- **多系统集成**：通过中央平台将三个独立的系统整合为一体
- **语义化线条样式**：为不同类型的数据（虚线）、电力、水务、道路等设置不同的线条风格
- **实体基础设施图形**：太阳能板、风力涡轮机、水坝、管道、道路、车辆等

## 新型图形绘制技术

### 太阳能板（带网格线的倾斜多边形）
```xml
<polygon class="solar-panel" points="0,25 35,8 38,12 3,29"/>
<line class="solar-frame" x1="12" y1="22" x2="24" y2="13"/>
<line x1="19" y1="29" x2="19" y2="40" stroke="#5F5E5A" stroke-width="2"/>
```

### 风力涡轮机（塔架 + 机舱 + 叶片）
```xml
<!-- Tapered tower -->
<polygon class="wind-tower" points="20,70 30,70 28,25 22,25"/>
<!-- Nacelle -->
<rect class="wind-hub" x="18" y="20" width="14" height="8" rx="2"/>
<!-- Hub -->
<circle class="wind-hub" cx="25" cy="18" r="5"/>
<!-- Blades (rotated ellipses) -->
<ellipse class="wind-blade" cx="25" cy="5" rx="3" ry="13"/>
<ellipse class="wind-blade" cx="14" cy="26" rx="3" ry="13" transform="rotate(-120, 25, 18)"/>
<ellipse class="wind-blade" cx="36" cy="26" rx="3" ry="13" transform="rotate(120, 25, 18)"/>
```

### 带电量显示的电池状态
```xml
<rect class="battery" x="0" y="0" width="45" height="65" rx="5"/>
<!-- Terminals -->
<rect x="10" y="-6" width="10" height="8" rx="2" fill="#27500A"/>
<rect x="25" y="-6" width="10" height="8" rx="2" fill="#27500A"/>
<!-- Charge level fill -->
<rect class="battery-level" x="5" y="12" width="35" height="48" rx="3"/>
<text x="22" y="42" text-anchor="middle" fill="#173404" style="font-size:10px">85%</text>
```

### 带有水波的坝体/水库
```xml
<!-- Dam wall -->
<polygon class="reservoir-wall" points="0,60 10,0 70,0 80,60"/>
<!-- Water behind dam -->
<polygon class="water" points="12,10 68,10 68,55 75,55 75,58 5,58 5,55 12,55"/>
<!-- Wave effect -->
<path d="M 15 25 Q 25 22 35 25 Q 45 28 55 25" fill="none" stroke="#378ADD" stroke-width="1" opacity="0.5"/>
```

### 带有接头与阀门的管道网络
```xml
<path class="pipe" d="M 80 85 L 110 85"/>
<circle class="pipe-joint" cx="10" cy="30" r="8"/>
<circle class="valve" cx="190" cy="85" r="6"/>
<!-- Distribution branches -->
<path class="pipe-thin" d="M 18 30 L 50 30"/>
<path class="pipe-thin" d="M 10 22 L 10 5 L 50 5"/>
```

### 带车道标线的道路交叉口
```xml
<!-- Road surface -->
<line class="road" x1="0" y1="50" x2="170" y2="50"/>
<line class="road-mark" x1="10" y1="50" x2="160" y2="50"/>
<!-- Cross road -->
<line class="road" x1="85" y1="0" x2="85" y2="100"/>
<line class="road-mark" x1="85" y1="10" x2="85" y2="90"/>
<!-- Embedded sensors -->
<circle class="sensor" cx="40" cy="50" r="5"/>
```

### 带信号状态的交通灯系统
```xml
<rect class="traffic-light" x="0" y="0" width="14" height="32" rx="3"/>
<circle class="light-red" cx="7" cy="8" r="4"/>
<circle class="light-off" cx="7" cy="16" r="4"/>
<circle class="light-off" cx="7" cy="24" r="4"/>
```

### 带有窗口与轮子的总线
```xml
<rect class="bus" x="0" y="0" width="55" height="28" rx="6"/>
<!-- Windows -->
<rect class="bus-window" x="5" y="5" width="12" height="12" rx="2"/>
<rect class="bus-window" x="20" y="5" width="12" height="12" rx="2"/>
<!-- Wheels with hubcaps -->
<circle cx="14" cy="30" r="6" fill="#2C2C2A"/>
<circle cx="14" cy="30" r="3" fill="#5F5E5A"/>
```

### 仪表板界面原型图
```xml
<!-- Monitor frame -->
<rect class="dashboard" x="0" y="0" width="200" height="120" rx="8"/>
<!-- Screen -->
<rect class="screen" x="10" y="10" width="180" height="85" rx="4"/>
<!-- Mini bar chart -->
<rect class="screen-content" x="18" y="18" width="50" height="35" rx="2"/>
<rect class="screen-chart" x="22" y="38" width="8" height="12"/>
<rect class="screen-chart" x="33" y="32" width="8" height="18"/>
<!-- Gauge -->
<circle class="screen-bar" cx="100" cy="35" r="12"/>
<text x="100" y="39" text-anchor="middle" fill="#E8E6DE" style="font-size:8px">78%</text>
<!-- Status indicators -->
<circle cx="35" cy="74" r="6" fill="#97C459"/>
<circle cx="75" cy="74" r="6" fill="#97C459"/>
<circle cx="115" cy="74" r="6" fill="#EF9F27"/>
```

### 具有连接点的六边形物联网中心
```xml
<!-- Outer hexagon -->
<polygon class="iot-hex" points="0,-45 39,-22 39,22 0,45 -39,22 -39,-22"/>
<!-- Inner hexagon -->
<polygon class="iot-inner" points="0,-20 17,-10 17,10 0,20 -17,10 -17,-10"/>
<!-- Connection dots on data lines -->
<circle cx="321" cy="248" r="4" fill="#7F77DD"/>
```

## 基础设施相关的 CSS 类名

```css
/* Power system */
.solar-panel { fill: #3C3489; stroke: #534AB7; stroke-width: 0.5; }
.solar-frame { fill: none; stroke: #EEEDFE; stroke-width: 0.5; }
.wind-tower { fill: #B4B2A9; stroke: #5F5E5A; stroke-width: 1; }
.wind-blade { fill: #F1EFE8; stroke: #888780; stroke-width: 0.5; }
.battery { fill: #27500A; stroke: #3B6D11; stroke-width: 1.5; }
.battery-level { fill: #97C459; }
.power-line { stroke: #EF9F27; stroke-width: 2; fill: none; }

/* Water system */
.reservoir-wall { fill: #B4B2A9; stroke: #5F5E5A; stroke-width: 1; }
.water { fill: #85B7EB; stroke: #378ADD; stroke-width: 0.5; }
.pipe { fill: none; stroke: #378ADD; stroke-width: 4; stroke-linecap: round; }
.pipe-joint { fill: #185FA5; stroke: #0C447C; stroke-width: 1; }
.valve { fill: #0C447C; stroke: #185FA5; stroke-width: 1; }

/* Transport */
.road { stroke: #888780; stroke-width: 8; fill: none; stroke-linecap: round; }
.road-mark { stroke: #F1EFE8; stroke-width: 1; fill: none; stroke-dasharray: 6 4; }
.traffic-light { fill: #444441; stroke: #2C2C2A; stroke-width: 0.5; }
.light-red { fill: #E24B4A; }
.light-green { fill: #97C459; }
.light-off { fill: #2C2C2A; }
.bus { fill: #E1F5EE; stroke: #0F6E56; stroke-width: 1.5; }

/* Data/IoT */
.data-line { stroke: #7F77DD; stroke-width: 2; fill: none; stroke-dasharray: 4 3; }
.iot-hex { fill: #EEEDFE; stroke: #534AB7; stroke-width: 2; }

/* Dashboard */
.dashboard { fill: #F1EFE8; stroke: #5F5E5A; stroke-width: 1.5; }
.screen { fill: #1a1a18; }
.screen-chart { fill: #5DCAA5; }
```

## 布局说明

- **视图框尺寸**：720×620（三列布局时宽度更大）
- **物联网中心位置**：位于几何中心点 (360, 270)
- **数据线路**：建议采用二次曲线或L形路径，并在连接物联网中心的节点处添加连接点
- **各系统区间间距**：每个系统板块的宽度约为200像素
- **垂直层次结构**：仪表板（顶部）→ 物联网中心（中部）→ 各系统（底部）
- **组件分组**：为便于定位，每个主要组件都应使用 `<g transform="translate(x,y)">` 进行封装
