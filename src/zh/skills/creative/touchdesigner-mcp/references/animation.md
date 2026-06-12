# 动画参考

基于时间的运动模式——关键帧、LFO、计时器、缓动函数以及表达式驱动的动画。

在设置参数之前，务必先调用 `td_get_par_info` 获取操作类型的参数信息。下述参数名称基于 TD 2025.32 版本，实际使用时请注意检查是否会出现错误。

---

## 时间源

TD 提供三种时间参考方式——请选择合适的一种。

| 表达式 | 行为描述 | 适用场景 |
|---|---|---|
| `absTime.seconds` | 自 TD 启动以来的实时时钟秒数，永不重置。 | 连续运动、GLSL 中的 `uTime` 变量、无限循环动画 |
| `absTime.frame` | 实时时钟的帧计数。 | 需要精确到帧的触发操作 |
| `me.time.frame` | 组件自身的帧计数（在播放/停止时会重置）。 | 组件级的动画时间轴 |
| `me.time.seconds` | 组件自身的秒数表示。 | 与上同，以秒为单位 |

**规则：** 对于着色器及连续运动效果，建议使用 `absTime.seconds`；而对于组件内的触发型或循环动画，则应使用 `me.time.*` 系列表达式。

---

## LFO CHOP — 循环运动

最简单的周期性驱动方式。响应速度快、对 GPU 资源占用低，且兼容表达式功能。

```python
lfo = root.create(lfoCHOP, 'rot_driver')
lfo.par.type = 'sin'        # 'sin' | 'cos' | 'ramp' | 'square' | 'triangle' | 'pulse'
lfo.par.frequency = 0.25    # cycles per second
lfo.par.amplitude = 1.0
lfo.par.offset = 0.0
lfo.par.phase = 0.0         # 0-1, useful for offsetting parallel LFOs
```

**通过导出方式设置参数：**

```python
op('/project1/geo1').par.rx.mode = ParMode.EXPRESSION
op('/project1/geo1').par.rx.expr = "op('rot_driver')['chan1'] * 360"
```

**多个同步的LFO（带相位偏移的X/Y/Z旋转）：**
您可以创建一个包含三个通道且每个通道均带有相位偏移的LFO，或者使用三个独立的LFO，并分别设置其`phase`参数值（0.0、0.33、0.66）。**

---

## Timer CHOP — 触发型序列

适用于仅需执行一次的动画、与节拍同步的序列，或基于舞台场景的逻辑控制。

```python
timer = root.create(timerCHOP, 'fade_timer')
timer.par.length = 4.0       # cycle length in seconds
timer.par.cycle = False      # run once vs. loop
timer.par.outputseconds = True
```

输出通道包括：`timer_fraction`（在完整周期内取值范围为 0 到 1）、`running`、`done` 以及 `cycles`。

**启动计时器：**
```python
timer.par.start.pulse()
```

**实现渐隐效果：**
```python
op('/project1/level1').par.opacity.mode = ParMode.EXPRESSION
op('/project1/level1').par.opacity.expr = "op('fade_timer')['timer_fraction']"
```

**调整计时器比例**——可直接在表达式中设置：

```python
# Smoothstep: ease in/out
expr = "smoothstep(0, 1, op('fade_timer')['timer_fraction'])"
# Cubic ease-out: 1 - (1-t)^3
expr = "1 - pow(1 - op('fade_timer')['timer_fraction'], 3)"
```

## CHOP 模式——自定义曲线

适用于任意波形（锯齿渐变、缓动曲线及自定义包络）。

```python
pat = root.create(patternCHOP, 'envelope')
pat.par.type = 'gaussian'    # 'gaussian' | 'ramp' | 'square' | 'sin' | etc.
pat.par.length = 60          # samples
pat.par.cyclelength = 1.0    # seconds at TD framerate
```

可与 `lookupCHOP` 结合使用，通过自定义曲线对 0-1 值的驱动参数进行重新映射。

---

## Animation COMP — 基于关键帧

适用于多关键帧动态图形。每个 animationCOMP 都包含可在动画编辑器中编辑关键帧的通道。

```python
anim = root.create(animationCOMP, 'intro_anim')
# By default has channels chan1..chanN; access via:
# op('intro_anim').par.length, .par.play, .par.cue, etc.

# Drive a parameter from a channel
op('/project1/text1').par.tx.mode = ParMode.EXPRESSION
op('/project1/text1').par.tx.expr = "op('intro_anim/out1')['chan1']"
```

关键帧通常在用户界面（动画编辑器）中进行编辑，但也可以通过内部的 `keyframes` 表来设置。若需通过编程方式创建关键帧，则应使用 `td_execute_python`：

```python
# Get the channel CHOP inside an animationCOMP
ch = op('/project1/intro_anim/chans')
# Insert a key (advanced API — verify with td_get_par_info(op_type='animationCOMP'))
ch.appendKey('chan1', frame=0, value=0.0, expression=None)
ch.appendKey('chan1', frame=120, value=1.0)
```

在大多数使用场景中，建议改用 LFO/计时器/模式切分功能来控制参数——这样更为简单且便于脚本化处理。

---

## 表达式中的缓动功能

TD 的表达式求值器支持 Python 数学运算。常见的缓动形式包括：

```python
# Linear
"t"

# Smoothstep (classic ease-in-out)
"smoothstep(0, 1, t)"

# Ease-out cubic
"1 - pow(1 - t, 3)"

# Ease-in cubic
"pow(t, 3)"

# Ease-in-out cubic
"3*t*t - 2*t*t*t"

# Bounce (manual, simplified)
"abs(sin(t * 6.28 * 3) * (1 - t))"
```

其中，`t` 可以是 `op('fade_timer')['timer_fraction']`，也可以是任何介于 0 到 1 之间的数值。  

---

## Filter CHOP — 平滑现有通道数据

在用于驱动可视化效果之前，先对存在抖动现象的数值（如音频分析结果、传感器数据等）进行平滑处理。

```python
filt = root.create(filterCHOP, 'smooth')
filt.par.filter = 'gaussian'   # or 'lowpass'
filt.par.width = 0.5            # smoothing window in seconds
filt.inputConnectors[0].connect(op('raw_signal'))
```

**警告：** 在时间切片模式下，切勿对 AudioSpectrum 的输出使用 Filter CHOP 功能——该功能会大幅增加采样点数量，并将各频段值平均至接近零的水平。详情请参阅 `audio-reactive.md` 文档。

---

## Lag CHOP — 非对称上升/下降特性

上升与下降过程的速率不同，这是用于可视化音频包络线的标准方式。

```python
lag = root.create(lagCHOP, 'env_smooth')
lag.par.lag1 = 0.02   # attack (rise time, seconds)
lag.par.lag2 = 0.30   # release (fall time, seconds)
lag.inputConnectors[0].connect(op('raw_envelope'))
```

快速响应、缓慢释放——营造出经典的电压表视觉效果。

```python
# In an executeDAT (frameStart):
def onFrameStart(frame):
    t = absTime.seconds
    op('/project1/circle').par.tx = math.sin(t * 2.0) * 3.0
    op('/project1/circle').par.ty = math.cos(t * 2.0) * 3.0
    return
```

复杂的逻辑仍应处理在 CHOP 中（这类操作对 CPU 的消耗较低，且结果具有确定性）。脚本则适用于一次性任务或非实时的分支逻辑。

---

## 常见陷阱

1. **帧率依赖问题** — `me.time.frame` 的单位为 TD 项目中的帧数（默认为 60 帧/秒）。如果项目的帧率发生变化，物体的运动速度也会随之改变。如需实现与帧率无关的时间控制，请使用 `seconds` 单位。
2. **计算开销问题** — 每个用于驱动参数的 CHOP 都会在每一帧进行计算。因此应尽量合并驱动逻辑（使用一个大型 mathCHOP 替代多个小型 CHOP）。
3. **表达式模式问题** — 参数的默认值为 `CONSTANT` 模式。除非将 `par.X.mode` 设置为 `ParMode.EXPRESSION`，否则 `par.X.expr = ...` 的设置将被忽略。
4. **动画编辑器的修改** — 通过用户界面设置的关键帧会保存在 animationCOMP 的内部关键帧表中，因此即使保存后重新打开文件，这些关键帧依然存在。虽然可以通过 `appendKey()` 方法以编程方式设置关键帧，但建议先使用 `td_get_docs(topic='animation')` 查阅相关 API 文档以确认用法。
5. **循环动画问题** — 若要实现无缝循环，`length` 的值必须与 `cyclelength` 相同，且起始值和结束值也必须一致。否则动画会出现明显的跳跃现象。

---

## 快速方案

| 目标 | 最简实现方式 |
|---|---|
| 持续旋转 | 使用 LFO CHOP，设置 `type='ramp'`，并将表达式绑定到 `geo.par.rx` |
| 2 秒内渐显 | 使用计时器 CHOP，设置 `length=2`，再将平滑过渡表达式绑定到 `level.par.opacity` |
| 每拍产生脉冲效果 | 通过音频触发 `triggerCHOP`，再利用表达式驱动缩放比例 |
| 3D 利萨如曲线轨道 | 使用两个频率不同的 LFO，分别驱动 `tx`/`ty`/`tz` 参数 |
| 随机抖动效果 | 在位置参数中加入低频的 `noiseCHOP` |
| 定时切换场景 | 使用计时器 CHOP，再通过它来切换 TOP 或 CHOP 的 `index` 值 |
