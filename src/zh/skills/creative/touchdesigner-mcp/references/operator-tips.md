# 操作员指南

## 线框渲染模式

用于在黑色背景上渲染线框几何体的可复用配置：

```python
# 1. Material
mat = root.create(wireframeMAT, 'wire_mat')
mat.par.colorr = 1.0; mat.par.colorg = 0.0; mat.par.colorb = 0.0
mat.par.linewidth = 3

# 2. Geometry COMP
geo = root.create(geometryCOMP, 'my_geo')
geo.par.rx.expr = 'absTime.seconds * 30'
geo.par.ry.expr = 'absTime.seconds * 45'
geo.par.material = mat.path  # NOTE: 'material' not 'mat'

# 3. Shape inside the geo
box = geo.create(boxSOP, 'cube')
box.par.sizex = 1.5; box.par.sizey = 1.5; box.par.sizez = 1.5

# 4. Camera
cam = root.create(cameraCOMP, 'cam1')
cam.par.tx = 0; cam.par.ty = 0; cam.par.tz = 4; cam.par.fov = 45

# 5. Render TOP
render = root.create(renderTOP, 'render1')
render.par.outputresolution = 'custom'
render.par.resolutionw = 1280; render.par.resolutionh = 720
render.par.bgcolorr = 0; render.par.bgcolorg = 0; render.par.bgcolorb = 0
render.par.camera = cam.path
render.par.geometry = geo.path

# 6. Output null
out = root.create(nullTOP, 'out1')
out.inputConnectors[0].connect(render.outputConnectors[0])
```

**核心规则：**
- 类名格式：必须为 `wireframeMAT`，不可使用小写的 `wireframeMat`（后缀需全大写）
- 几何体 SOP/POP 需放置于几何体组件内部
- 材质路径应为 `geo.par.material`，而非 `geo.par.mat`
- 渲染几何体时，需设置 `render.par.geometry = geo.path`（路径为字符串格式）
- 若需清晰的线框效果，请将 `wireframeMAT.par.wireframemode` 设定为 `'topology'`；若需显示三角形边缘，则设为 `'tesselated'`
- 备选方案：可直接使用 `renderTOP.par.overridemat`，无需为每个几何体单独设置材质

## 反馈入口 TOP

### 基本结构

```
input (initial state) ──┐
                        ├──→ feedback_top ──→ processing ──→ null_out
                        │                                        ↑
                        └── par.top = 'null_out' ────────────────┘
```

### 设置模式

```python
# 1. Processing chain
glsl = root.create(glslTOP, 'sim')
null_out = root.create(nullTOP, 'null_out')
glsl.outputConnectors[0].connect(null_out.inputConnectors[0])

# 2. Feedback referencing null_out
feedback = root.create(feedbackTOP, 'feedback')
feedback.par.top = 'null_out'

# 3. Black initial state
const_init = root.create(constantTOP, 'const_init')
const_init.par.colorr = 0; const_init.par.colorg = 0; const_init.par.colorb = 0

# 4. Wire: initial → feedback, feedback → processing
feedback.inputConnectors[0].connect(const_init)
glsl.inputConnectors[0].connect(feedback)

# 5. Reset to apply initial state
feedback.par.resetpulse.pulse()
```

### 常见错误

| 错误信息 | 成因 | 解决方案 |
|---------|------|----------|
| “指定的数据源不足” | 未连接任何输入源 | 连接初始状态 TOP |
| 出现异常的初始模式 | 初始状态设置错误 | 使用恒定值 TOP（黑色） |

### 实用提示

1. 模拟时请使用浮点格式：`glsl.par.format = 'rgba32float'`
2. 设置完成后进行重置：`feedback.par.resetpulse.pulse()`
3. 确保分辨率一致——反馈、处理及初始状态的分辨率必须相同
4. 使用软边界可避免边缘伪影：
   ```glsl
   float edge = 3.0 * texel.x;
   float bx = smoothstep(0.0, edge, uv.x) * smoothstep(0.0, edge, 1.0 - uv.x);
   float by = smoothstep(0.0, edge, uv.y) * smoothstep(0.0, edge, 1.0 - uv.y);
   value *= bx * by;
   ```

### 应用场景
- **波浪模拟** — R表示高度，G表示速度，初始状态为黑色
- **元胞自动机** — 白色代表存活，黑色代表死亡，初始状态为随机噪声
- **拖尾/运动模糊** — 将当前帧与反馈值进行混合处理，初始状态为黑色
