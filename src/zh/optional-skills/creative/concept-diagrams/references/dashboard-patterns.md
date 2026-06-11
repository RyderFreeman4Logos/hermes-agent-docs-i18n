# 仪表板设计模式

用于在概念图中构建用户界面/仪表板原型的基础组件——管理面板、监控仪表板、控制界面以及状态显示区域。

## 设计模式说明

“屏幕”指的是位于较浅色“框架”矩形内的圆形深色区域，其上方还会嵌套图表、计量表或指示器等元素。

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
<circle cx="35" cy="74" r="6" fill="#97C459"/> <!-- green = ok -->
<circle cx="75" cy="74" r="6" fill="#EF9F27"/> <!-- amber = warning -->
<circle cx="115" cy="74" r="6" fill="#E24B4A"/> <!-- red = alert -->
```

## CSS

```css
.dashboard      { fill: #F1EFE8; stroke: #5F5E5A; stroke-width: 1.5; }
.screen         { fill: #1a1a18; }
.screen-content { fill: #2C2C2A; }
.screen-chart   { fill: #5DCAA5; }
.screen-bar     { fill: #7F77DD; }
.screen-alert   { fill: #E24B4A; }
```

## 小贴士

- 无论在浅色模式还是深色模式下，控制面板界面均保持暗色显示——这模拟了实际显示器的屏幕效果。
- 请将屏幕上的文字尺寸设置得较小（`font-size:8px` 或 `10px`），并确保对比度足够高（深色背景上使用接近白色的文字颜色）。
- 一致地使用绿色/琥珀色/红色三种颜色来表示不同状态——分别对应正常、警告和警报。
- 通常，单个控制面板会叠加在基础设施架构图之上，以实现统一的视图展示（参见 `examples/smart-city-infrastructure.md`）。
