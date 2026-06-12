# 3D场景参考

包括光照系统、阴影效果、IBL/立方体贴图、多摄像机设置以及PBR材质相关内容。关于线框渲染及反馈技巧，请参阅`operator-tips.md`；涉及几何体实例化的相关信息可在`geometry-comp.md`中找到；着色器代码的详细说明则见`glsl.md`。

---

## 3D场景的结构组成

```
[Geometry COMP]    ← contains SOPs (the shapes)
[Material]         ← Phong/PBR/GLSL/Constant MAT
[Light COMPs]      ← point/directional/spot/area/environment
[Camera COMP]      ← view position, FOV
        │
        ▼
   [Render TOP]    ← combines geo + lights + camera into a 2D image
        │
        ▼
   [post-FX chain] ← bloomTOP, glsl shaders, etc.
        │
        ▼
   [windowCOMP]    ← actual display
```

Render TOP 是整个系统的核心组件。它需要明确的 `geometry` 路径、明确的 `camera` 路径，以及通过灯光表或环境光引用指定的光源。  

---

## 最简场景

```python
# Geometry
geo = root.create(geometryCOMP, 'scene_geo')
sphere = geo.create(sphereSOP, 'shape')
sphere.par.rad = 1.0; sphere.par.rows = 64; sphere.par.cols = 64

# Material — start with PBR
mat = root.create(pbrMAT, 'mat')
mat.par.basecolorr = 0.7; mat.par.basecolorg = 0.7; mat.par.basecolorb = 0.7
mat.par.metallic = 0.0
mat.par.roughness = 0.4

geo.par.material = mat.path

# Camera
cam = root.create(cameraCOMP, 'cam1')
cam.par.tx = 0; cam.par.ty = 0; cam.par.tz = 4
cam.par.fov = 45
cam.par.near = 0.1; cam.par.far = 100

# Key light
key = root.create(lightCOMP, 'key_light')
key.par.lighttype = 'point'
key.par.tx = 3; key.par.ty = 3; key.par.tz = 3
key.par.dimmer = 1.5

# Render
render = root.create(renderTOP, 'render1')
render.par.outputresolution = 'custom'
render.par.resolutionw = 1920; render.par.resolutionh = 1080
render.par.camera = cam.path
render.par.geometry = geo.path
render.par.lights = key.path                 # single light path; for multi, see below
render.par.bgcolorr = 0; render.par.bgcolorg = 0; render.par.bgcolorb = 0
```

对于多个灯光，可保留 `par.lights` 为空——Render TOP 会默认在网络中搜索所有的 `lightCOMP` 和 `envlightCOMP` 操作。若需限定为特定灯光，则需设置 `par.lights = '/project1/key_light /project1/fill_light'`（以空格分隔的路径）。

---

## 灯光类型

| 类型 | 特点 | 常见参数 |
|---|---|---|
| `point` | 全向发光，亮度随距离衰减 | `dimmer`、`coneangle`（不适用）、`attenuation` |
| `directional` | 平行光束，无限远距离（如太阳光） | `dimmer`，仅灯光的旋转角度有影响 |
| `spot` | 圆锥形发光，亮度随距离和角度双重衰减 | `coneangle`、`conedelta`、`dimmer` |
| `cone` | 与 spot 类似，但边缘更锐利 | 同上 |
| `area` | 矩形形状的柔和光源 | `sizex`、`sizey` |

所有类型均支持：`colorr`、`colorg`、`colorb`、`tx/ty/tz`、`rx/ry/rz`、`dimmer`。

### 三点布光（摄影棚场景）

```python
# Key — main light, ~45° front
key = root.create(lightCOMP, 'key')
key.par.lighttype = 'point'
key.par.tx = 4; key.par.ty = 3; key.par.tz = 4
key.par.dimmer = 1.5
key.par.colorr = 1.0; key.par.colorg = 0.95; key.par.colorb = 0.85

# Fill — softer, opposite side
fill = root.create(lightCOMP, 'fill')
fill.par.lighttype = 'area'
fill.par.tx = -4; fill.par.ty = 2; fill.par.tz = 3
fill.par.dimmer = 0.5
fill.par.colorr = 0.7; fill.par.colorg = 0.8; fill.par.colorb = 1.0
fill.par.sizex = 4; fill.par.sizey = 4

# Rim/back — outline from behind
rim = root.create(lightCOMP, 'rim')
rim.par.lighttype = 'spot'
rim.par.tx = 0; rim.par.ty = 4; rim.par.tz = -4
rim.par.coneangle = 30
rim.par.dimmer = 1.0

# Optional: ambient lift to prevent pure-black shadows
amb = root.create(ambientlightCOMP, 'ambient')
amb.par.dimmer = 0.15
```

## 阴影

当 `par.shadowtype != 'none'` 时，点光源和定向光都会投射阴影。

```python
key.par.shadowtype = 'softshadow'        # 'none' | 'hardshadow' | 'softshadow'
key.par.shadowsize = 1024                # shadow map resolution
key.par.shadowsoftness = 0.02            # softshadow only
```

**提示：**
- 柔和阴影会耗费大量 GPU 资源。建议先设置 `shadowsize = 1024`，只有当在当前分辨率下阴影边缘出现像素化现象时，再逐步提高该值至 2048/4096。
- 设置聚光灯的 `near`/`far` 范围时应恰好覆盖整个场景。范围过宽会导致阴影贴图精度浪费。
- 多个能投射阴影的光源会进一步增加成本。在实时渲染场景中建议仅使用 1-2 个此类光源，其余光源则应预先烘焙到材质中。

---

## 基于图像的照明（IBL）/ 环境光

若要实现逼真的 PBR 材质，就需要使用立方体贴图来处理反射效果。

```python
# Environment light from an HDR
env = root.create(envlightCOMP, 'env')
env.par.envmap = '/project1/cube_in'         # path to a TOP that produces a cubemap
env.par.envlightmap = ...                    # diffuse irradiance map (often same as envmap)
env.par.dimmer = 1.0

# Cubemap source — option A: built-in cubeTOP from 6 faces
cube = root.create(cubeTOP, 'cube_in')
# (assign 6 face TOPs)

# Option B: HDR equirectangular → cubemap conversion
# Use a moviefileinTOP loading .hdr or .exr, then projectTOP type='cubemapfromequirect'
hdr = root.create(moviefileinTOP, 'hdr_src')
hdr.par.file = '/path/to/environment.hdr'

proj = root.create(projectTOP, 'cube_proj')
proj.par.projecttype = 'cubemapfromequirect'
proj.inputConnectors[0].connect(hdr)
```

当场景中存在 `envlightCOMP` 时，PBR 材质会自动采样环境光。由于不同版本的 TD 可能存在差异，请使用 `td_get_par_info(op_type='envlightCOMP')` 来确认参数名称。

---

## PBR 材质设置

```python
mat = root.create(pbrMAT, 'pbr_metal')
mat.par.basecolorr = 0.95; mat.par.basecolorg = 0.65; mat.par.basecolorb = 0.4
mat.par.metallic = 1.0
mat.par.roughness = 0.25
mat.par.specularlevel = 0.5
mat.par.emitcolorr = 0; mat.par.emitcolorg = 0; mat.par.emitcolorb = 0

# Texture maps
mat.par.basecolormap = '/project1/textures/albedo'         # TOP path
mat.par.metallicroughnessmap = '/project1/textures/mr'      # G=roughness, B=metallic (glTF convention)
mat.par.normalmap = '/project1/textures/normal'
mat.par.emitmap = '/project1/textures/emit'
mat.par.occlusionmap = '/project1/textures/ao'
```

**材质常用表达：**

| 类型 | 金属感 | 粗糙度 | 基础颜色 |
|---|---|---|---|
| 拉丝钢 | 1.0 | 0.4 | (0.7, 0.7, 0.7) |
| 抛光金 | 1.0 | 0.1 | (1.0, 0.85, 0.4) |
| 塑料 | 0.0 | 0.5 | 中等饱和度 |
| 橡胶 | 0.0 | 0.9 | 深色 |
| 玻璃 | 0.0 | 0.05 | (1, 1, 1)，低透明度及透光效果 |
| 发光源 | 0.0 | 1.0 | 深色，高 `emitcolor` 值 |

对于玻璃/透光效果，较新版本的 TD 支持在 PBR 中使用 `transmission` 参数；旧版本则需要使用 glslMAT。

---

## 多摄像头设置

适用于对比查看、回放、多屏映射等功能。

```python
# Camera A — main scene
cam_a = root.create(cameraCOMP, 'cam_main')
cam_a.par.tz = 5

# Camera B — orbiting top-down
cam_b = root.create(cameraCOMP, 'cam_top')
cam_b.par.ty = 6; cam_b.par.rx = -90

# Render each via separate Render TOPs
render_a = root.create(renderTOP, 'render_main')
render_a.par.camera = cam_a.path
render_a.par.geometry = geo.path

render_b = root.create(renderTOP, 'render_top')
render_b.par.camera = cam_b.path
render_b.par.geometry = geo.path
```

若需实现画中画效果，可使用 `multiplyTOP`/`compositeTOP` 对两者进行合成；而对于多显示器场景，则可分别将它们路由至独立的 `windowCOMP` 中。

### 相机动画

可通过表达式（轨道运动）、animationCOMP（路径点）或 LFO（振荡）来控制相机参数：

```python
# Orbiting camera
cam_a.par.tx.mode = ParMode.EXPRESSION
cam_a.par.tx.expr = "cos(absTime.seconds * 0.3) * 6"
cam_a.par.tz.mode = ParMode.EXPRESSION
cam_a.par.tz.expr = "sin(absTime.seconds * 0.3) * 6"
cam_a.par.lookat = '/project1/scene_geo'        # auto-aim at target
```

`par.lookat` 是最简单的“始终注视目标”机制。

### 景深效果

当 `par.dof = 'on'` 时，PBR + Render TOP 版本便支持景深效果。

```python
render.par.dof = 'on'
render.par.focusdistance = 5.0
render.par.aperture = 0.05         # blur strength
render.par.bokehshape = 'hexagon'
```

DOF效果对GPU性能要求很高。为提升运行效率，建议先以较低分辨率进行渲染，再进行放大处理。

---

## 常见问题与解决方案

1. **渲染结果全黑** —— 最常见原因在于没有光源。即便使用了PBR材质，也至少需要一个`lightCOMP`或`envlightCOMP`。为保险起见，可添加一个亮度较低的`ambientlightCOMP`。
2. **材质无法显示** —— `geo.par.material`必须是一个字符串形式的路径，而非材质对象本身。应使用`mat.path`而非`mat`。
3. **光源被忽略** —— 默认情况下，Render TOP会自动识别网络中的所有`lightCOMP`。如果存在来自其他场景的多余光源，它们也会被一并加载。此时需明确指定`par.lights`。
4. **PBR材质显得单调** —— 若没有`envlightCOMP`提供反射效果，PBR材质会呈现出类似Phong模型的外观。即便没有HDR文件，也应添加一个`envlightCOMP`（可临时使用`constantTOP`立方体贴图作为替代）。
5. **阴影出现瑕疵或条纹** —— 可适当提高`par.shadowbias`的值。针对不同光源可分别进行调整。
6. **相机位于几何体内部** —— 如果`cam.par.tz`值位于球体内部，就会看到几何体内部场景（若启用了背面剔除则可能什么也看不到）。此时需将相机移至更外侧的位置。
7. **光源照射范围过小** —— 点光源具有固有的衰减效果，因此远处的几何体会接收到很少的光线。可提高`par.dimmer`的值或将光源移近一些。
8. **多个相机冲突** —— 每次运行Render TOP只能对应一个相机，无法共享同一个相机。如需使用多个相机，需分别运行多个Render TOP。
9. **坐标系方向错误** —— TD引擎采用右手坐标系，Y轴向上。从Z轴向上的软件（如Blender、Z轴向上的Maya）导入的资产，需要在几何体COMP上执行90°的X轴旋转。
10. **渲染性能不足** —— 在现代GPU上，1080p60分辨率下使用PBR材质、IBL效果、阴影及DOF效果通常可以正常运行，但若同时启用4K分辨率、4个光源、软阴影及DOF效果，则很容易导致性能崩溃。可通过`td_get_perf`工具进行性能分析，在增加更多效果前适当降低设置强度。

---

## 快速方案指南

| 需求场景 | 推荐配置 |
|---|---|
| 影室人像摄影 | 三点照明系统（主光+补光+轮廓光）+ 环境光 + PBR材质 + DOF效果 |
| 户外日光场景 | 一个定向光源`lightCOMP`（模拟太阳）+ 天空HDR环境光 + 软阴影 |
| 戏剧性/黑色电影风格 | 从上方照射的单一聚光灯、硬阴影，环境光强度设为0.05 |
| 抽象/梦幻风格 | 多个低亮度的区域光源，不使用阴影，后期添加`bloomTOP`效果 |
| 产品渲染 | 三点照明系统 + IBL效果 + 中性色PBR材质 + 设置`bgcolorr=g=b=1`（纯白色无缝背景） |
| 游戏风格渲染 | Phong材质模型 + 1-2个光源 + 不使用IBL效果 + 平坦的环境光（成本低且风格化） |
| 线框图与实色渲染结合 | 使用两个Render TOP，一个应用线框图材质，另一个应用PBR材质，最后通过`addTOP`功能进行合成 |
| 盘旋摄像机效果 | 设置`par.lookat`，并使用正弦/余弦函数为tx/tz参数生成动态变化值 |
