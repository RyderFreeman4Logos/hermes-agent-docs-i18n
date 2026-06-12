# 粒子参考手册

TouchDesigner中的粒子系统——包括现代的POP（粒子运算符）以及传统的particleSOP路径。

如需实例化静态几何体（不支持每个实例独立的生命周期/速度设置），请参阅`geometry-comp.md`。对于基于GLSL的反馈模拟（无粒子抽象层），请参阅`operator-tips.md`中的“反馈TOP”部分。

在设置参数之前，务必先调用`td_get_par_info`获取运算符类型信息。下述参数名称基于TD 2025.32版本，实际使用时请先进行确认。

---

## 两种路径：POP与SOP

| | **POP系列**（现代版） | **particleSOP**（传统版） |
|---|---|---|
| 是否使用GPU？ | 是（计算型） | 否（CPU处理） |
| 粒子数量 | 可轻松支持10万以上 | 超过约5千后会开始变慢 |
| API风格 | 源节点/力场节点/求解器节点/渲染节点链 | 单一运算符搭配大量参数 |
| 适用场景 | 新项目及高负载场景 | 快速演示、少量粒子场景、TD 2023版本及更早版本 |

**优先使用POP系列。**仅当所需运算符的POP版本不存在时，才考虑使用particleSOP。

---

## POP处理流程概览

POP系统是由`geometryCOMP`内部的一系列运算符构成的链式结构：

```
popSourceTOP / popSourceSOP   ← spawn new particles
        ↓
popForceTOP (gravity, wind, etc.)
        ↓
popForceTOP (attractor, vortex, ...)
        ↓
popDeleteTOP (lifetime, bounds)
        ↓
popSolverTOP                  ← integrates velocity, updates positions
        ↓
[render via geometryCOMP / glslMAT instancing]
```

POP缓冲区用于存储标准通道数据：`P`（位置）、`v`（速度）、`life`、`id`、`Cd`（颜色），以及您自行添加的任何自定义通道。  

---  

## 最简POP配置

```python
# Create a geometry COMP to hold the POP network
geo = root.create(geometryCOMP, 'particles_geo')

# 1. Source — emit particles from a point
src = geo.create(popSourceTOP, 'src')
src.par.birthrate = 500          # per second
src.par.life = 4.0                # seconds

# 2. Gravity force
grav = geo.create(popForceTOP, 'gravity')
grav.par.forcetype = 'gravity'
grav.par.fy = -9.8

# 3. Lifetime cleanup
delp = geo.create(popDeleteTOP, 'cull')
delp.par.condition = 'lifeleq'    # delete when life <= 0
delp.par.value = 0

# 4. Solver
solv = geo.create(popSolverTOP, 'solver')
solv.par.timestep = 'frame'

# Wire: source → force → delete → solver
src.outputConnectors[0].connect(grav.inputConnectors[0])
grav.outputConnectors[0].connect(delp.inputConnectors[0])
delp.outputConnectors[0].connect(solv.inputConnectors[0])
```

`popSolverTOP`的输出即为实时的粒子缓冲区。可通过在小型SOP（球体、点）上使用`glslMAT`实例化技术来渲染它，以此作为每个粒子的“形状”。

---

## 常见力类型

| 力的类型 | 效果 | 常用参数 |
|---|---|---|
| `gravity` | 持续的定向拉力 | `fx`, `fy`, `fz` |
| `wind` | 持续的速度叠加 | `wx`, `wy`, `wz` |
| `drag` | 随时间衰减的速度 | `dragstrength` |
| `noise` | 拐流噪声产生的湍流效果 | `noiseamp`, `noisefreq`, `noiseseed` |
| `attractor` | 向某一点施加拉力 | `position`, `strength`, `falloff` |
| `vortex` | 围绕轴心旋转 | `axis`, `strength` |
| `point`（自定义） | 通过GLSL计算的任意力 | 通过`popforceadvancedTOP`实现 |

可以将多个`popForceTOP`串联使用——每种力都会以叠加的方式改变粒子的速度。

---

## 生命周期模式

### 持续发射（例如烟羽效果）

```python
src.par.birthrate = 800
src.par.life = 6.0       # variance via 'lifevariance'
src.par.lifevariance = 1.5
```

### 爆发式辐射（例如爆炸）

```python
src.par.birthrate = 0    # no continuous emission
src.par.burst.pulse()    # one burst on demand (verify param name)
src.par.burstcount = 5000
src.par.life = 1.5
```

### 基于节拍触发的突发模式

连接一个 `triggerCHOP`（来自音频或MIDI信号），用于触发突发模式的启动：

```python
op('/project1/audio_kick_trigger').outputConnectors[0].connect(...)
# Then via a chopExecuteDAT, on each kick:
def offToOn(channel, sampleIndex, val, prev):
    op('/project1/particles_geo/src').par.burst.pulse()
    return
```

## 粒子渲染

### 点精灵（最简单形式）

```python
# Inside the geometryCOMP, render the solver output directly
# The geo's first SOP child becomes the geometry
# But for POPs, we typically render via glslMAT on a small "shape"

# Simple billboard sphere per particle:
shape = geo.create(sphereSOP, 'shape')
shape.par.rad = 0.05
shape.par.rows = 6; shape.par.cols = 6   # low-poly to keep it fast

# Material that uses POP buffer for instancing
mat = root.create(glslMAT, 'particle_mat')
# Configure mat.par.instancingTOP = solver output (verify param name)
```

具体的实例化设置因TD版本而异——可以调用`td_get_hints(topic='popInstancing')`（或者尝试`popRender`/`instancing`，多试几个即可）。

### 通过glslcopyPOP实现GPU精灵效果

对于密集的烟雾或火焰类效果，可使用`glslcopyPOP`，该方式能从计算着色器中获取每个粒子的颜色与大小信息，随后在`renderTOP`中以点精灵的形式进行渲染，并采用加性混合模式。

---

## 碰撞检测

```python
# Collision detection against an SOP
coll = geo.create(popCollideTOP, 'ground_coll')
coll.par.collidewithsop = '/project1/ground_geo'  # path to colliding SOP
coll.par.bounce = 0.3
coll.par.friction = 0.1
# Insert between force and solver
```

仅针对平面与立方体之间的碰撞，可使用 `popPlaneCollideTOP`（成本更低）。 

---

## 自定义粒子级数据

可通过 `popAttribCreateTOP`（或通过 `glslcopyPOP` 编写代码）来添加自定义通道：

```python
# Add a "phase" attribute initialized random per-particle, used in render shader
attr = geo.create(popAttribCreateTOP, 'add_phase')
attr.par.attribname = 'phase'
attr.par.value0 = 'rand(@id)'   # expression in TD's POP attribute language
```

接着在渲染着色器中，使用 `texture(sTDPOPInputs[0].phase, ...)`（或您所使用的 TD 版本所采用的相应采样器写法——可通过 `td_get_docs(topic='pops')` 进行确认）。

---

## 旧版 particleSOP（请谨慎使用）

适用于快速演示或粒子数量较少的系统：

```python
# Inside a geo
psrc = geo.create(addSOP, 'point_src')      # source: a single point
psrc.par.points = '0 0 0'

part = geo.create(particleSOP, 'particles')
part.par.life = 3.0
part.par.birthrate = 100
part.par.gravityy = -9.8
part.par.windx = 0.5
part.inputConnectors[0].connect(psrc)
```

**CPU占用过高**。当活跃粒子数量超过约5,000个时，就会出现帧率下降的情况。

---

## 常见问题与解决方案

1. **粒子不显示** —— 通常是由于渲染端的问题。可通过在求解器输出上使用 `td_get_screenshot` 来查看（在较新版本的TD中，该功能可将缓冲区以类似TOP的视图呈现）。随后再检查 `geometryCOMP` 的渲染路径。
2. **“Burst”功能无法触发** —— 需确认 `burst` 参数设置为脉冲模式，而非开关模式。脉冲模式必须使用 `.pulse()` 函数，而不能直接赋值为 `True`。
3. **粒子在第一帧就瞬间移动** —— 原因是速度未被初始化。应设置 `popSourceTOP.par.initialvelocityX/Y/Z` 的值，或直接将其设为零。
4. **重力效果异常** —— TD中的“1单位”数值取决于场景的缩放比例。建议先从 `fy = -1.0` 开始调整，再逐步放大数值，而非直接使用现实世界中的9.8。
5. **粒子生成率过高会导致卡顿** —— 粒子生成率是按秒计算的，而非每帧。在60fps的帧率下，若 `birthrate = 6000`，则相当于每帧生成100个粒子，这是可以接受的；而若设置为 `600000`，则会导致严重卡顿。
6. **POP求解器的执行顺序很重要** —— 各种力的作用顺序与其在链中的出现顺序一致。如果将重力放在阻力之后，就会削弱重力的效果，这通常并非预期的结果。
7. **实例化参数的名称因版本而异** —— 不同版本的TD中，`mat.par.instancingTOP`、`mat.par.instanceop` 以及 `mat.par.instances` 这些参数名称可能有所不同。务必使用 `td_get_par_info(op_type='glslMAT')` 来确认当前版本的参数名称。
8. **“Cooking”过程中的依赖循环** —— POP求解器会生成隐式的时间循环。出现“Cooking dependency loop”警告在POP系统中是正常现象，且并无危害。
9. **由CHOP驱动的力值问题** —— 当某个力参数通过表达式与CHOP相关联时（例如随音频变化的重力），需确保CHOP在求解器之前完成计算。否则，力的作用将会延迟一帧。

---

## 性能目标参考

| 粒子数量 | 推荐设置 | 60fps下的帧率预算 |
|---|---|---|
| < 1k | 使用particleSOP | 几乎无压力 |
| 1k - 10k | 使用POP求解器及简单力场 | 约2-5毫秒 |
| 10k - 100k | 使用POP求解器及仅依赖GPU的力场 | 约5-15毫秒 |
| 100k+ | 使用`glslcopyPOP`及自定义计算代码 | 约10-25毫秒 |
| 1M+ | 使用自定义GPU缓冲区，不依赖POP框架 | 取决于着色器性能 |

可使用 `td_get_perf` 功能来检测POP处理链中哪个操作环节是性能瓶颈。

---

## 快速方案示例

| 目标效果 | 实现流程 |
|---|---|
| 烟雾羽流 | `popSourceTOP`（点源）→ 加入重力、风场及噪声效果 → `popDeleteTOP`（控制生命周期）→ 求解器处理 → 通过glslMAT实现实例化渲染 |
| 随节奏触发的粒子爆发 | `triggerCHOP`（音频触发）→ chopExecuteDAT函数触发 `popSourceTOP.par.burst` 的脉冲效果 |
| 烟花弹效果 | 在某一点生成粒子爆发 → 添加阻力与重力效果 → 当粒子生命周期达到阈值时再次触发爆发 |
| 雪/雨效果 | 在XZ平面上持续生成粒子（y坐标较高），施加重力与轻微风力，粒子生命周期结束后通过框删除处理 |
| 火花效果 | 粒子瞬间爆发，生命周期极短（约0.3秒），采用高亮度的叠加渲染方式，并通过反馈机制实现运动模糊效果 |
| 音频驱动的粒子效果 | 粒子生成率由音频波形幅度决定，颜色则根据频率带变化 |
