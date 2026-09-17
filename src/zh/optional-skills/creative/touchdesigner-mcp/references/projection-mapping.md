# 投影映射参考指南

专为安装与活动场景设计的多窗口输出、表面映射、边缘融合以及投影仪校准图案功能。

有关 HUD 布局和屏幕面板网格的详细信息，请参阅 `layout-compositor.md`。关于线框图/测试图案的生成方法，请参阅 `operator-tips.md`。

---

## Window COMP — 输出至显示器

`windowCOMP` 是 TD 用于将像素输出到真实显示器的技术机制。

```python
win = root.create(windowCOMP, 'output_window')
win.par.winop = '/project1/final_out'   # path to the TOP being displayed
win.par.winw = 1920
win.par.winh = 1080
win.par.winoffsetx = 0                  # screen-space offset
win.par.winoffsety = 0
win.par.borders = False                 # no chrome
win.par.alwaysontop = True
win.par.cursor = False                  # hide cursor in fullscreen
win.par.justify = 'fillaspect'          # 'fill' | 'fitaspect' | 'fillaspect' | 'native'
win.par.winopen.pulse()                 # OPEN the window
```

若要指定特定的物理显示器，请设置 `par.location` 参数：

```python
win.par.location = 'secondary'          # 'primary' | 'secondary' | 'monitor1' | 'monitor2' | ...
```

或者，您也可以使用与操作系统显示布局相匹配的 `winoffsetx/y` 参数来设置绝对坐标。

**务必持续调用 `winopen` —— 仅设置参数是无法打开窗口的。**

---

## 多窗口输出

在多投影仪或多显示器环境中，应为每个输出创建一个 `windowCOMP`，且每个窗口需对应不同的 TOP 地址。

```python
for i, screen_top in enumerate(['out_left', 'out_center', 'out_right']):
    w = root.create(windowCOMP, f'win_{i}')
    w.par.winop = f'/project1/{screen_top}'
    w.par.winw = 1920; w.par.winh = 1080
    w.par.winoffsetx = i * 1920
    w.par.winoffsety = 0
    w.par.borders = False
    w.par.alwaysontop = True
    w.par.cursor = False
    w.par.winopen.pulse()
```

对于超宽单输出显示区域，可利用 GPU 的拼接/分屏功能（如 Nvidia Mosaic、AMD Eyefinity），在 5760×1080 的分辨率下通过一个 windowCOMP 将内容分配给三台投影仪，随后在 TD 内部使用 `cropTOP` 命令按屏幕对内容进行分割。

---

## 四点角定位（四边形变形）

最基础的投影映射功能——将矩形变形为四边形。

```python
# Source content
src = op('/project1/scene_out')

# Manual: cornerPinTOP (TD has this built-in)
cp = root.create(cornerPinTOP, 'corner_pin')
cp.par.tlx = 0.05; cp.par.tly = 0.10    # top-left (normalized 0-1)
cp.par.trx = 0.95; cp.par.try = 0.08    # top-right
cp.par.brx = 0.93; cp.par.bry = 0.92    # bottom-right
cp.par.blx = 0.07; cp.par.bly = 0.94    # bottom-left
cp.inputConnectors[0].connect(src)
```

**替代方案**：使用包含 `gridSOP` 的 `geometryCOMP`，并在顶点级 GLSL 代码中对顶点进行弯曲处理。此方法更具灵活性（可生成曲面），但需要更多的配置工作。

请通过 `td_get_par_info(op_type='cornerPinTOP')` 来确认 TD 2025.32 版本中的参数名称。

---

## 贝塞尔/网格变形（曲面）

对于非平面表面（如圆顶、圆柱、弯曲墙壁），可采用细分网格结合逐顶点位移的技术。

### 方案：网格网格 + GLSL 位移

```python
# Subdivided grid in a geo
geo = root.create(geometryCOMP, 'warp_geo')
grid = geo.create(gridSOP, 'warp_grid')
grid.par.rows = 32          # higher = smoother curve
grid.par.cols = 32
grid.par.sizex = 2; grid.par.sizey = 2

# Texture the source onto it
mat = root.create(constMAT, 'warp_mat')      # use constMAT for unlit projection
mat.par.maptop = '/project1/scene_out'        # source TOP

geo.par.material = mat.path

# Render to a TOP that goes to the projector window
cam = root.create(cameraCOMP, 'cam_proj')
cam.par.tz = 4

render = root.create(renderTOP, 'projection_out')
render.par.camera = cam.path
render.par.geometry = geo.path
render.par.outputresolution = 'custom'
render.par.resolutionw = 1920; render.par.resolutionh = 1080
```

对于每个顶点的偏移量，可在 constMAT 中编写顶点级 GLSL 代码（或使用 `glslMAT`），并通过统一变量从 CHOP 中读取位移值。

校准过程是迭代进行的：首先通过 `scene_out` 渲染棋盘格，对其进行投影，再拍摄该投影图像，随后手动调整角落或网格点，直至其对齐。

---

## 边缘融合（多投影仪重叠场景）

当两个投影仪发生重叠时，重叠区域的亮度会提升一倍。可通过在重叠区域内将每个投影仪的边缘透明度渐变至 0 来实现融合效果。

### GLSL边缘融合着色器

这是一种针对单个投影仪的输出通道着色器，可将该投影仪内部的边缘逐渐过渡为黑色：

```glsl
// edge_blend_pixel.glsl
out vec4 fragColor;
uniform float uBlendLeft;     // overlap width on left edge (0-0.5, 0=no blend)
uniform float uBlendRight;
uniform float uGamma;          // typically 2.2 — perceptual ramp

void main() {
    vec2 uv = vUV.st;
    vec4 col = texture(sTD2DInputs[0], uv);

    float aL = (uBlendLeft  > 0.0) ? smoothstep(0.0, uBlendLeft, uv.x) : 1.0;
    float aR = (uBlendRight > 0.0) ? smoothstep(0.0, uBlendRight, 1.0 - uv.x) : 1.0;
    float a = pow(aL * aR, uGamma);

    fragColor = TDOutputSwizzle(vec4(col.rgb * a, 1.0));
}
```

将该设置应用于每个存在重叠投影区域的投影仪的输出。根据实际的重叠程度调整 `uBlendLeft` / `uBlendRight` 的数值。

对于上下混合投影或圆柱形布局，可通过添加 `uBlendTop` / `uBlendBottom` 参数来扩展着色器功能。

---

## 校准图案

用于调整投影仪对齐度的实用测试图案。可在设置过程中构建一个名为 `switchTOP` 的开关，选中相应的图案并将其应用到所有投影仪窗口中。

```python
# Solid white — for brightness/uniformity check
white = root.create(constantTOP, 'cal_white')
white.par.colorr = 1.0; white.par.colorg = 1.0; white.par.colorb = 1.0

# Centered crosshair — for keystone alignment
gridcross = root.create(textTOP, 'cal_cross')
gridcross.par.text = '+'
gridcross.par.fontsizex = 200

# Fine grid — for warp/mesh alignment (use rampTOP + math + threshold, or build via GLSL)
# Color bars for projector color calibration
bars = root.create(rampTOP, 'cal_bars')
bars.par.type = 'horizontal'
```

或者，如果您的 TD 版本已包含该功能，可直接使用附带的 `testpatternTOP`。

---

## 投影校验工作流程

在调试多屏幕设置时：

1. 为每个输出端口生成独特的颜色与标签（通过 `textTOP` 显示“LEFT”、“CENTER”、“RIGHT”）。
2. 确认每个窗口调用的路径正确：使用 `td_get_operator_info(path='/project1/win_0')` 进行检查。
3. 验证显示分配情况：亲自走到每台投影仪前进行目视确认。
4. 检查分辨率：对比物理投影仪的原始分辨率与 TD 的输出分辨率——两者不一致会导致缩放伪影。
5. 检查渲染状态：通过 `td_get_perf` 查看，如果某个窗口的源内容未完成渲染，投影仪将显示冻结的上一帧画面。

---

## 常见问题与陷阱

1. **窗口无法打开** —— 您忘记了调用 `winopen.pulse()`。仅设置参数是无法打开窗口的。  
2. **显示错误** —— 参数 `par.location='secondary'` 的效果取决于操作系统的显示器顺序。为获得更可靠的解决方案，建议将 `winoffsetx/y` 设置为绝对坐标。  
3. **光标可见** —— 在打开窗口之前设置 `par.cursor = False`，或直接关闭后重新打开窗口。  
4. **画面呈黑色** —— 通常是由于渲染问题所致。可通过 `td_get_perf` 检查 `final_out` 的输出是否正常。还需从根目录开始递归查看 `td_get_errors` 的输出信息。  
5. **画面撕裂/缺少垂直同步** —— `windowCOMP` 会遵循 `par.vsync` 的设置。对于投影显示，始终建议将 `vsync` 设置为默认值 `vsync='vsync'`。出现画面撕裂现象通常意味着GPU负载过高，可尝试降低渲染分辨率。  
6. **宽高比不匹配** —— 投影仪的原始分辨率多为1920×1200（16:10）而非1080分辨率。此时可使用 `justify='fitaspect'` 参数，或按投影仪的原始分辨率进行渲染。  
7. **非商业许可限制** —— 此类许可将最高分辨率限制在1280×1280。如需用于实际安装项目，必须使用商业许可；专业版许可则支持4K及以上分辨率。  
8. **macOS系统下的多显示器环境** —— `windowCOMP` 会识别macOS的“屏幕组”功能。在开始演示前，请关闭“屏幕组”功能，或通过系统设置将TD应用固定到指定的显示器上。  

---

## 快速解决方案指南

| 目标 | 实现方案 |
|---|---|
| 单一全屏输出 | 使用一个 `windowCOMP`，设置 `justify='fillaspect'`，并调用 `winopen.pulse()` |
| 三投影仪宽幅显示 | 使用3个 `windowCOMP`，从同一宽源图像为每个输出分别设置 `cropTOP` 参数 |
| 单一四边形表面显示 | 通过 `cornerPinTOP` 设置后传递至 `windowCOMP` |
| 弧形/穹顶形状显示 | 先使用带有顶点GLSL脚本的细分网格SOP，再经过 `renderTOP` 处理，最后输出到 `windowCOMP` |
| 边缘融合效果 | 为每个投影仪单独设置GLSL渐变着色器，最终整合到 `windowCOMP` 中 |
| 校准模式 | 通过热键在场景图像与测试图案之间切换，由 `switchTOP` 控制 |
