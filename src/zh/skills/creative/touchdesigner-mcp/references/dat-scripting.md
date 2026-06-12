# 基于DAT的脚本编写参考

TD的事件/回调模型——一种可响应网络事件而运行的Python代码。涵盖了完整的“执行DAT”功能集及其常用实现模式。

如需进行任意形式的Python代码执行（非基于回调的方式），请参阅`python-api.md`。关于MCP中的`td_execute_python`工具，可参考`mcp-tools.md`。

---

## 执行DAT系列

每种类型的DAT都会监控某一类事件源，并在数据发生变化时触发Python代码执行。

| DAT | 监控内容 | 适用场景 |
|---|---|---|
| `chopExecuteDAT` | CHOP的通道数值 | 音频触发、阈值回调、基于数值输入的状态机逻辑 |
| `datExecuteDAT` | DAT的内容（表格单元格、文本） | 对API数据更新的响应、解析webDAT响应内容 |
| `parameterExecuteDAT` | 参数的值或脉冲信号 | 对用户修改参数的响应、自定义脉冲按钮功能 |
| `panelExecuteDAT` | 面板COMP的交互操作 | 按钮点击、滑块拖动、字段提交等操作 |
| `opExecuteDAT` | 操作员生命周期事件 | 新操作员创建、删除或名称更改时触发 |
| `executeDAT` | 项目生命周期及帧级事件 | 一次性设置任务、每帧逻辑处理、保存/加载钩子功能 |

所有这些DAT都包含一个带有预定义回调函数的配套DAT文件，您只需填写自己需要的回调函数内容即可。

---

## chopExecuteDAT — 数值触发器

```python
ce = root.create(chopExecuteDAT, 'kick_handler')
ce.par.chop = '/project1/audio/out_kick'      # source CHOP
ce.par.offtoon = True                          # fire when channel rises above 0
ce.par.ontooff = False
ce.par.whileon = False
ce.par.valuechange = False
```

在已停靠的回调 DAT 中：

```python
def offToOn(channel, sampleIndex, val, prev):
    """Channel went from 0 to non-zero. Classic beat trigger."""
    op('/project1/strobe').par.flash.pulse()
    op('/project1/scene').par.index = (op('/project1/scene').par.index + 1) % 8
    return

def onToOff(channel, sampleIndex, val, prev):
    """Channel went from non-zero to 0."""
    return

def whileOn(channel, sampleIndex, val, prev):
    """Fires every frame while channel is non-zero. Use sparingly."""
    return

def valueChange(channel, sampleIndex, val, prev):
    """Fires every frame the value changes (continuous). Heavy."""
    return
```

`channel` 是一个 `Channel` 对象，包含 `.name`、`.owner`、`.vals[]` 等属性。可使用 `channel.name == 'chan1'` 来进行过滤。

**基于阈值的自定义触发器：** 首先通过 `triggerCHOP` 将输入的 CHOP 信号处理为纯净的 0/1 脉冲，然后再使用 `offtoon` 进行监测。

---

## datExecuteDAT — 表格/文本内容变化检测

```python
de = root.create(datExecuteDAT, 'api_response')
de.par.dat = '/project1/api/web1'              # source DAT
de.par.tablechange = True                      # any cell change
de.par.cellchange = False
de.par.rowchange = False
de.par.colchange = False
```

```python
def onTableChange(dat):
    """Whole table changed (including text DAT content updates)."""
    if dat.numRows == 0:
        return
    # If it's a webDAT response, parse JSON
    import json
    try:
        data = json.loads(dat.text)
    except json.JSONDecodeError:
        debug(f'Bad JSON: {dat.text[:100]}')
        return
    # Write to a CHOP
    op('/project1/api_value').par.value0 = float(data.get('count', 0))
    return

def onCellChange(dat, cells, prev):
    """Specific cells changed."""
    for cell in cells:
        # cell.row, cell.col, cell.val
        pass
    return
```

`debug()` 会将输出打印到文本端口中，可通过 `td_read_textport` 查看该内容。

---

## parameterExecuteDAT — 参数变更与脉冲信号

```python
pe = root.create(parameterExecuteDAT, 'comp_params')
pe.par.op = '/project1/my_component'           # COMP whose params to watch
pe.par.parameters = '*'                         # or specific names like 'Intensity Reset'
pe.par.valuechange = True
pe.par.pulse = True
```

```python
def onValueChange(par, prev):
    """par is a Par object. par.name, par.eval(), par.owner."""
    if par.name == 'Intensity':
        op('/project1/bloom').par.threshold = par.eval()
    return

def onPulse(par):
    """Pulse param was triggered."""
    if par.name == 'Reset':
        op('/project1/scene').par.index = 0
        op('/project1/audio_player').par.cuepoint = 0
        op('/project1/audio_player').par.cuepulse.pulse()
    return

def onExpressionChange(par, val, prev):
    """User changed the expression on a param."""
    return

def onExportChange(par, val, prev):
    """Export source changed."""
    return

def onModeChange(par, val, prev):
    """Param mode changed (CONSTANT / EXPRESSION / EXPORT / etc)."""
    return
```

## panelExecuteDAT — UI事件

用于交互式控制界面。有关完整的面板COMP上下文信息，请参阅`panel-ui.md`文档。

```python
pe = root.create(panelExecuteDAT, 'btn_handler')
pe.par.panel = '/project1/play_btn'
pe.par.click = True              # mouse click events
pe.par.value = True              # state changes (toggle)
pe.par.lockedchange = False
```

```python
def onOffToOn(panelValue):
    """Panel value rose to 1 (button pressed, slider crossed threshold)."""
    op('/project1/scene_timer').par.start.pulse()
    return

def onOnToOff(panelValue):
    """Panel value dropped to 0."""
    return

def onValueChange(panelValue):
    """Continuous: every frame the value changes."""
    val = panelValue.eval()
    op('/project1/master').par.opacity = val
    return

def onClick(panelValue):
    """Discrete click event, fires once per click."""
    return
```

`panelValue` 是 COMP 面板上的一个 `Par` 对象。

---

## opExecuteDAT — 操作符生命周期

用于监控父级 COMP 中操作符的创建、删除及重命名操作。

```python
oe = root.create(opExecuteDAT, 'lifecycle')
oe.par.op = '/project1'
oe.par.create = True
oe.par.destroy = True
oe.par.namechange = True
oe.par.flagchange = False
```

```python
def onCreate(opCreated):
    """A new operator was created. Useful for auto-applying conventions."""
    if opCreated.OPType == 'glslTOP':
        # Always wrap with a null
        n = opCreated.parent().create(nullTOP, opCreated.name + '_out')
        n.inputConnectors[0].connect(opCreated)
    return

def onDestroy(opDestroyed):
    """Operator was deleted. opDestroyed.path is still valid for one frame."""
    return

def onNameChange(opChanged):
    """Operator was renamed."""
    return
```

适用于开发阶段的代码框架搭建（自动创建下游的nullTOP对象、统一自动命名规则）。为避免出现意外副作用，建议在正式项目中将其禁用。

---

## executeDAT — 项目生命周期与每帧处理

一款功能全面的工具，可让您在项目启动、保存、加载以及每一帧的开始和结束时插入自定义操作。

```python
exec_dat = root.create(executeDAT, 'lifecycle')
exec_dat.par.start = True
exec_dat.par.create = True
exec_dat.par.framestart = True
exec_dat.par.frameend = False
```

```python
def onStart():
    """Project just started cooking. Run once."""
    op('/project1/scene').par.index = 0
    debug('Project started')
    return

def onCreate():
    """Component was just created (only fires for component executeDATs, not project root)."""
    return

def onFrameStart(frame):
    """Per-frame, BEFORE network cooks. Heavy logic here = bottleneck."""
    return

def onFrameEnd(frame):
    """Per-frame, AFTER network cooks. Use for capture, recording, post-network logic."""
    return

def onPlayStateChange(playing):
    """Project play/pause toggled."""
    return

def onProjectPreSave():
    """Right before saving the .toe file."""
    return

def onProjectPostSave():
    return
```

在 `onFrameStart` 函数中加入复杂的逐帧逻辑，是导致 TD 项目性能下降的最常见原因之一。建议将逐帧计算任务交由 CHOPs 处理，而将事件处理逻辑用脚本实现。

---

## 模式：根据节奏触发动画序列

```python
# Source: a kick trigger CHOP
# Goal: on each kick, run a 1.5s scale pulse + color flash

# Setup (create once)
animator = root.create(timerCHOP, 'pulse_anim')
animator.par.length = 1.5
animator.par.cycle = False

# Param expressions on visual targets:
op('logo').par.sx.expr = "1.0 + (1 - op('pulse_anim')['timer_fraction']) * 0.3"
op('logo').par.sx.mode = ParMode.EXPRESSION
op('logo').par.sy.expr = "1.0 + (1 - op('pulse_anim')['timer_fraction']) * 0.3"
op('logo').par.sy.mode = ParMode.EXPRESSION

# In a chopExecuteDAT watching the kick CHOP:
def offToOn(channel, sampleIndex, val, prev):
    op('pulse_anim').par.start.pulse()
    return
```

## 模式：基于 API 数据实时编辑 CHOP 内容

```python
# webDAT polls an API every 5 seconds
# datExecuteDAT parses the response and writes to a constantCHOP

def onTableChange(dat):
    import json
    try:
        data = json.loads(dat.text)
    except:
        return
    target = op('/project1/external_state')
    target.par.name0 = 'temperature'
    target.par.value0 = float(data['temp_c'])
    target.par.name1 = 'humidity'
    target.par.value1 = float(data['humidity'])
    return
```

可视化界面仅引用 `op('external_state')['temperature']` —— 其数据会实时更新。  

## 模式：自清洁网络

```python
# An opExecuteDAT watching for orphaned helper ops, deleting them after their parent disappears

def onDestroy(opDestroyed):
    parent_name = opDestroyed.name
    helper = op(f'/project1/{parent_name}_helper')
    if helper:
        helper.destroy()
    return
```

## 常见陷阱

1. **回调函数会静默崩溃** — 异常信息虽会输出到文本端口，但不会显示在用户界面中。调试前务必先调用 `td_clear_textport` 清空内容，调试后再使用 `td_read_textport` 读取。
2. **`debug()` 与 `print()` 的区别** — 两者都会将内容写入文本端口，但 `debug()` 还会标注出调用该函数的 DAT 文件名及行号。编写脚本时建议优先使用 `debug()`。
3. **`val` 表示新值，`prev` 表示旧值** — 容易搞混这两个参数的用途。建议始终使用如下函数定义：`def offToOn(channel, sampleIndex, val, prev)`。若感到困惑，可查阅 TD 文档中的参数顺序说明。
4. **`whileOn` 与 `valueChange` 每帧触发一次** — 这种方式计算开销较大，除非确实必要否则应避免使用。建议改用表达式来驱动相关逻辑。
5. **在烹饪暂停状态下回调函数不会执行** — 如果父级 COMP 的 `allowCooking=False`，回调函数将会停止运行。这一特性可用于实现“禁用自身”的切换功能。
6. **`par` 与 `panelValue` 的差异** — `parameterExecuteDAT` 返回的是 `par` 对象，而 `panelExecuteDAT` 返回的是 `panelValue` 对象（两者均为类似 Par 的对象）。二者都具备 `.name` 和 `.eval()` 方法，但其作用上下文不同。
7. **`opExecuteDAT` 会自动触发自身** — 当创建一个 `opExecuteDAT` 对象时，若设置 `par.create=True` 且父级条件满足，该对象会自动触发自身的 `onCreate` 方法。可通过 `if opCreated == me: return` 来过滤此类自动触发。
8. **重新加载时的行为变化** — 当重新加载扩展模块（使用 `td_reinit_extension`）时，所有回调 DAT 对象的内部状态都会被重置，模块级别的变量也会丢失。建议将状态信息保存在 tableDAT 对象或嵌入式的 DAT 对象中，而非模块的全局变量中。
9. **烹饪过程中的依赖关系问题** — 如果某个回调函数向位于其数据源上游的操作对象写入数据，就可能导致烹饪循环。TD 会对此发出警告，但并不总是会阻止操作。应确保数据流为单向传递。
10. **活动状态标志** — 每个 Execute DAT 对象都包含 `par.active` 属性，值为 False 时表示处于静默状态。这样无需删除连接线即可轻松切换测试模式。

---

## 快速用法示例

| 目标 | 设置方式 |
|---|---|
| 触发节奏变化 | 设置 `chopExecuteDAT.par.offtoon=True`，并监控 `triggerCHOP` 信号 |
| 处理 API 返回响应 | 设置 `datExecuteDAT.par.tablechange=True`，并监控 `webDAT` 信号 |
| 自定义按钮触发动作 | 设置 `parameterExecuteDAT.par.pulse=True`，并监控自定义的脉冲参数 |
| 滑块控制连续参数 | 设置 `panelExecuteDAT.par.value=True`，并监控 `sliderCOMP` 信号 |
| 仅执行一次的初始化操作 | 设置 `executeDAT.par.start=True`，并在 `onStart()` 方法中编写相关逻辑 |
| 每帧记录指标数据 | 设置 `executeDAT.par.frameend=True`，将数值记录到 CHOP 对象中 |
| 自动为新操作命名 | 设置 `opExecuteDAT.par.create=True`，强制遵循命名规范 |
