# Geometry COMP 参考手册

## 创建 Geometry COMPs

```python
geo = root.create(geometryCOMP, 'geo1')
# Remove default torus
for c in list(geo.children):
    if c.valid: c.destroy()
# Build your shape inside
```

## 正确模式（地理区域内的形状）

```python
# Create shape INSIDE the geo COMP
box = geo.create(boxSOP, 'cube')
box.par.sizex = 1.5; box.par.sizey = 1.5; box.par.sizez = 1.5

# For POP-based geometry (TD 099), POPs must be inside:
sph = geo.create(spherePOP, 'shape')
out1 = geo.create(outPOP, 'out1')
out1.inputConnectors[0].connect(sph.outputConnectors[0])
```

## 不要这样做：常见错误

```python
# BAD: Don't create geometry at parent level and wire into COMP
box = root.create(boxPOP, 'box1')  # ← outside geo, won't render

# BAD: Don't reference parent operators from inside COMP
choptopop1.par.chop = '../null1'  # ← hidden dependency, breaks on move
```

## 实例化

```python
geo.par.instancing = True
geo.par.instanceop = 'sopto1'    # relative path to CHOP/SOP with instance data
geo.par.instancetx = 'tx'
geo.par.instancety = 'ty'
geo.par.instancetz = 'tz'
```

### 按操作类型划分的实例属性名称

| 操作类型 | 属性名称 |
|---------|-----------------|
| CHOP | 通道名称：`tx`、`ty`、`tz` |
| SOP/POP | 位置相关属性：`P(0)`、`P(1)`、`P(2)` |
| DAT | 第一行的列标题名称 |
| TOP | 颜色通道：`r`、`g`、`b`、`a` |

### 混合数据源

```python
geo.par.instanceop = 'pos_chop'       # Position from CHOP
geo.par.instancetx = 'tx'
geo.par.instancecolorop = 'color_top' # Color from TOP
geo.par.instancecolorr = 'r'
```

## 渲染设置

```python
# Camera
cam = root.create(cameraCOMP, 'cam1')
cam.par.tx = 0; cam.par.ty = 0; cam.par.tz = 4

# Render TOP
render = root.create(renderTOP, 'render1')
render.par.outputresolution = 'custom'
render.par.resolutionw = 1280; render.par.resolutionh = 720
render.par.camera = cam.path
render.par.geometry = geo.path  # accepts path string
```

## 渲染时的 POPs 与 SOPs 对比

在 TD 099 中，`geometryCOMP` 能够渲染 **POPs**，但无法渲染 SOPs。位于 geometry COMP 内部的 `boxSOP` 将不会被显示——且不会引发任何错误。

```python
# WRONG — SOPs don't render (invisible, no errors)
box = geo.create(boxSOP, 'cube')       # ✗ invisible

# CORRECT — POPs render
box = geo.create(boxPOP, 'cube')       # ✓ visible
```

| SOP | POP | 备注 |
|-----|-----|-------|
| `boxSOP` | `boxPOP` | `sizex/y/z`, `surftype` |
| `sphereSOP` | `spherePOP` | `radx/y/z`, `freq`, `type`（几何面/网格面/共享极面/四面体面） |
| `torusSOP` | `torusPOP` | TD会自动在新几何组件中创建相关结构 |
| `circleSOP` | `circlePOP` |  |
| `gridSOP` | `gridPOP` |  |
| `tubeSOP` | `tubePOP` |  |

系统会自动创建新的几何组件：`in1`（用于inPOP）、`out1`（用于outPOP）、`torus1`（用于torusPOP）。在构建模型之前请务必先清理数据。 

## 形状之间的变形转换（switchPOP）

```python
sw = geo.create(switchPOP, 'shape_switch')
sw.par.index.expr = 'int(absTime.seconds / 3) % 4'
sw.inputConnectors[0].connect(tetra.outputConnectors[0])  # shape 0
sw.inputConnectors[1].connect(box.outputConnectors[0])    # shape 1
sw.inputConnectors[2].connect(octa.outputConnectors[0])   # shape 2
sw.inputConnectors[3].connect(sphere.outputConnectors[0]) # shape 3

out = geo.create(outPOP, 'out1')
out.inputConnectors[0].connect(sw.outputConnectors[0])
```

`spherePOP.par.type` 可选值：`geodesic`、`grid`、`sharedpoles`、`tetrahedron`。若需构建柏拉图立体多面体，请使用 `tetrahedron`。

## 其他说明

- `connect()` 函数会直接替换现有的连接关系，无需先断开连接
- `project.name` 用于返回 TOE 文件名，而 `project.folder` 则用于返回对应目录路径
