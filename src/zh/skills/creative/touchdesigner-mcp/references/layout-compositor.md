# 布局合成器参考手册

用于构建模块化多面板网格的模板——非常适合HUD界面、数据仪表板以及多源视觉合成场景。

## 布局方案

| 方案 | 适用场景 | 备注 |
|------|----------|------|
| `layoutTOP` | 固定网格、快速搭建 | 适用于GPU场景及简单平铺布局 |
| 容器COMP + `overTOP` | 需要完全控制、面板尺寸不统一的情况 | 设置步骤较多，但灵活性极高 |
| GLSL合成器 | 过程化/树状结构风格 | 功能最强大，但实现较为复杂 |

---

## layoutTOP

内置网格合成器——构建规则平铺网格的最快捷方案。

```python
layout = root.create(layoutTOP, 'layout1')
layout.par.resolutionw = 1920
layout.par.resolutionh = 1080
layout.par.cols = 3
layout.par.rows = 2
layout.par.gap = 4
```

连接输入数据（最多支持 cols×rows 的尺寸）：
```python
layout.inputConnectors[0].connect(op('panel_radar'))
layout.inputConnectors[1].connect(op('panel_wave'))
layout.inputConnectors[2].connect(op('panel_data'))
```

**可变宽度列：** 不直接支持。对于非均匀网格，请采用 overTOP 方法。  

---

## Container COMP 网格布局

将每个元素分别作为独立的 `containerCOMP` 来构建，并使用 `overTOP` 方法进行组合。  

请完整翻译输入内容，切勿提前终止。

```python
def create_panel(root, name, width, height, x=0, y=0):
    panel = root.create(containerCOMP, name)
    panel.par.w = width
    panel.par.h = height
    panel.viewer = True
    return panel

# Composite with overTOP chain
over1 = root.create(overTOP, 'over1')
over1.inputConnectors[0].connect(panel_radar)
over1.inputConnectors[1].connect(panel_wave)
over1.par.topx2 = 0
over1.par.topy2 = 512
```

**提示：** 如果面板尺寸不同，请在每个 `overTOP` 输入前添加一个 `resolutionTOP`。

```glsl
out vec4 fragColor;
uniform vec2 uGridDivisions;   // e.g. vec2(3, 2) for 3 cols, 2 rows
uniform float uLineWidth;      // pixels
uniform vec4 uLineColor;       // e.g. vec4(0.0, 1.0, 0.8, 0.6) for cyan

void main() {
    vec2 res = uTDOutputInfo.res.zw;
    vec2 uv = vUV.st;
    vec4 bg = texture(sTD2DInputs[0], uv);

    float lineW = uLineWidth / res.x;
    float lineH = uLineWidth / res.y;

    float vDiv = 0.0;
    for (float i = 1.0; i < uGridDivisions.x; i++) {
        float x = i / uGridDivisions.x;
        vDiv = max(vDiv, step(abs(uv.x - x), lineW));
    }

    float hDiv = 0.0;
    for (float i = 1.0; i < uGridDivisions.y; i++) {
        float y = i / uGridDivisions.y;
        hDiv = max(hDiv, step(abs(uv.y - y), lineH));
    }

    float line = max(vDiv, hDiv);
    vec4 result = mix(bg, uLineColor, line * uLineColor.a);
    fragColor = TDOutputSwizzle(result);
}
```

## 元素库模式

每个视觉元素都作为可复用的 `.tox` 文件，存在于独立的 `baseCOMP` 中：

### 标准接口
```
inputs:
  - in_audio   (CHOP)  — audio envelope / beat data
  - in_data    (CHOP)  — optional data stream
  - in_control (CHOP)  — intensity, color, speed params

outputs:
  - out_top    (TOP)   — rendered element
```

### 网络结构
```
/project1/
  audio_bus/          ← all audio analysis (see audio-reactive.md)
  elements/
    elem_radar/       ← baseCOMP with out_top
    elem_wave/
    elem_data/
  compositor/
    layout1           ← layoutTOP or overTOP chain
    dividers1         ← GLSL divider lines
    postfx/           ← bloom → chrom → CRT stack (see postfx.md)
      null_out        ← final output
  output/
    windowCOMP        ← full-screen output
```

**核心原则：** 各个组件之间互不知晓彼此的存在，由组合器负责将它们整合在一起。音频总线虽被所有组件引用，但实际上是独立存在的。
