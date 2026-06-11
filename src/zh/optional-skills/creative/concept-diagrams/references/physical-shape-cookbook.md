# 实体物体绘制指南

当矩形形状无法满足需求时，用于绘制各类实体对象（车辆、建筑物、硬件设备、机械系统、人体结构）的指导方案。

## 形状选择

| 实体形态 | SVG元素 | 典型应用场景 |
|---------|----------|--------------|
| 曲面物体 | 带有Q/C曲线的`<path>` | 机身、油箱、管道 |
| 锥形/角度状物体 | `<polygon>` | 翼片、尾翼、楔形物 |
| 圆柱形/圆形物体 | `<ellipse>`、`<circle>` | 发动机、轮子、按钮 |
| 线性结构 | `<line>` | 支架、梁、连接件 |
| 内部分隔区域 | 父元素内的`<rect>` | 舱室、房间 |
| 虚线边界 | `stroke-dasharray`属性 | 隐藏部分、油箱 |

## 分层绘制方法

1. 先绘制外部结构（机身、框架、船体）
2. 在其上添加内部分隔区域（驾驶舱、舱室）
3. 添加细节元素（发动机、轮子、控制装置）
4. 添加带标签的指引线

## 使用语义化CSS类（替代c-*颜色类）

在绘制实体图时，建议直接定义针对特定组件的CSS类，而非使用`c-*`格式的颜色类。这种方式能让每个部件具备自解释性，同时有助于控制色彩方案的使用范围：

```css
.fuselage { fill: #F1EFE8; stroke: #5F5E5A; stroke-width: 1; }
.wing     { fill: #E6F1FB; stroke: #185FA5; stroke-width: 1; }
.engine   { fill: #FAECE7; stroke: #993C1D; stroke-width: 1; }
```

将这些内容添加到 SVG 文件内的本地 `<style>` 标签中（或扩展主机页面的 `<style>` 块）。亮色/暗色模式功能依然有效——若需实现暗色模式自适应，可使用模板中的 CSS 变量（如 `var(--bg-secondary)`、`var(--border)`、`var(--text-primary)`）。

## 参考示例

可通过以下示例文件了解可正常使用的实物结构展示方案：

- `examples/commercial-aircraft-structure.md` —— 机身曲线 + 锥形机翼 + 椭圆形发动机
- `examples/wind-turbine-structure.md` —— 地下基础、管状塔架及风机舱剖面图
- `examples/smartphone-layer-anatomy.md` —— 带有交替标注的爆炸视图结构图
- `examples/apartment-floor-plan-conversion.md` —— 墙壁、门、窗以及拟进行的改动
