# 投影映射参考指南

适用于安装/活动场景的多窗口输出、表面映射、边缘融合以及投影仪校准图案相关内容。

关于平视显示器布局与屏幕面板网格的设置，请参阅 `layout-compositor.md`；如需生成线框图/测试图案，可参考 `operator-tips.md`。

---

## Window COMP — 输出至显示设备

`windowCOMP` 是 TD 用于将像素传输至真实显示设备的功能模块。

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

若要指定某个特定的物理显示器，请设置 `par.location` 参数：

```python
win.par.location = 'secondary'          # 'primary' | 'secondary' | 'monitor1' | 'monitor2' | ...
```

或者，您也可以使用与操作系统显示布局相匹配的 `winoffsetx/y` 来设置绝对坐标。

**务必调用 `winopen` 命令——仅设置参数是无法打开窗口的。**

---

## 多窗口输出

在多投影仪或多显示器环境中，应为每个输出创建一个 `windowCOMP`，且每个窗口应对应不同的 TOP 地址。

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

对于超宽单输出显示区域，可通过GPU的拼接/分屏功能（如Nvidia Mosaic、AMD Eyefinity）在5760×1080的分辨率下将内容分配到三台投影仪上，此时只需使用一个windowCOMP；随后可在TD中通过`cropTOP`指令为每块屏幕单独分割内容。

---

## 四点角定位（四边形变形）

最基础的投影映射功能——将矩形区域变形为四边形形状。

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

请使用 `td_get_par_info(op_type='cornerPinTOP')` 来确认 TD 2025.32 版本中的参数名称。

---

## 贝塞尔/网格变形（曲面）

对于非平面表面（如圆顶、圆柱、曲面墙），应采用细分网格并结合逐顶点位移技术。

### 方案：网格 + GLSL 位移

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

校准过程是迭代进行的：首先通过 `scene_out` 渲染棋盘格图案，对其进行投影，再拍摄该投影图像，最后手动调整角落/网格点的位置，直至其对齐。

---

## 边缘融合（多投影仪重叠场景）

当两个投影仪发生重叠时，重叠区域的亮度会提升一倍。可通过在重叠区域内逐步将每个投影仪的边缘透明度降低至 0 来实现融合效果。

### GLSL边缘融合着色器

该着色器为每个投影仪单独设置输出通道，将对应区域的内部边缘渐变变为黑色：

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

将该设置应用于每个存在重叠投影区域的投影仪的输出。通过调整 `uBlendLeft` / `uBlendRight` 的数值，使其与实际投影重叠情况相匹配。

对于上下混合投影或圆柱形布局，可使用 `uBlendTop` / `uBlendBottom` 对着色器功能进行扩展。

---

## 校准图案

用于调整投影仪对齐度的实用测试图案。可在设置阶段构建一个名为 `switchTOP` 的变量来选择这些图案之一，并将其路由到所有投影仪的显示窗口中。

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

或者，如果您的 TD 版本已包含该功能，可直接使用随附的 `testpatternTOP`。

---

## 投影显示审计工作流程

在调试多屏幕显示系统时，请按以下步骤操作：

1. 为每个输出端口渲染独特的颜色与标签（例如通过 `textTOP` 显示“LEFT”、“CENTER”、“RIGHT”）。
2. 确认每个窗口调用的路径正确：使用 `td_get_operator_info(path='/project1/win_0')` 进行检查。
3. 验证显示分配情况：亲自走到每台投影仪前进行目视确认。
4. 检查分辨率：对比物理投影仪的原始分辨率与 TD 系统输出的分辨率——两者不一致会导致图像缩放失真。
5. 检查内容渲染状态：通过 `td_get_perf` 查看。如果某个窗口的内容未完成渲染，投影仪将显示冻结的上一帧画面。

---

## 常见问题与解决方案

1. **窗口无法打开** —— 未调用 `winopen.pulse()` 函数。仅设置参数并不足以使窗口显示。
2. **显示错误** —— 参数 `par.location='secondary'` 的效果取决于操作系统的显示器排列顺序。为获得更可靠的解决方案，建议将 `winoffsetx/y` 设定为绝对坐标值。
3. **光标可见** —— 在打开窗口之前先设置 `par.cursor = False`，或直接关闭后重新打开窗口。
4. **投影画面全黑** —— 通常是由于内容未完成渲染所致。需通过 `td_get_perf` 确认 `final_out` 端口的内容是否已渲染完成。此外，还应从根目录开始递归检查 `td_get_errors` 中的错误信息。
5. **画面撕裂/垂直同步问题** —— `windowCOMP` 会遵循 `par.vsync` 的设置。对于投影显示，始终建议将 `vsync` 设为默认值 `vsync='vsync'`。出现画面撕裂现象通常意味着 GPU 处理负荷过重，可尝试降低渲染分辨率。
6. **宽高比不匹配** —— 物理投影仪的原始分辨率多为 1920×1200（16:10）而非 1080p。此时可选用 `justify='fitaspect'` 参数，或直接以投影仪的原始分辨率进行渲染。
7. **非商业许可限制** —— 此类许可将最大分辨率限制在 1280×1280。如需用于实际安装项目，必须使用商业许可版本；专业版则支持 4K 及更高分辨率。
8. **macOS 系统下的多显示器问题** —— `windowCOMP` 会识别 macOS 的“屏幕组”功能。在开始演示前，建议关闭屏幕组功能，或通过系统设置将 TD 应用固定到指定的显示器上。

---

## 快速解决方案指南

| 目标 | 实现方法 |
|---|---|
| 单屏全屏输出 | 使用一个 `windowCOMP`，设置 `justify='fillaspect'`，并调用 `winopen.pulse()` |
| 三台投影仪横向拼接显示 | 使用 3 个 `windowCOMP`，并为每个输出端口配置来自同一宽源的 `cropTOP` 参数 |
| 单个四边形显示区域 | 先使用 `cornerPinTOP` 定位角落，再结合 `windowCOMP` 实现显示 |
| 曲面/穹顶投影 | 通过顶点 GLSL 对网格进行细分处理，生成 `renderTOP`，最后通过 `windowCOMP` 显示 |
| 边缘融合效果 | 为每台投影仪配置独立的 GLSL 渐变着色器，再通过 `windowCOMP` 合并画面 |
| 校准模式 | 通过热键在场景显示与测试图案之间切换，实现快速校准 |
