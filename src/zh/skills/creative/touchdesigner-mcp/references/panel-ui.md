# 面板与用户界面参考

TouchDesigner 内部的交互式控制界面——包括按钮、滑块、输入框、自定义参数页面以及面板回调功能。关于 HUD 叠加层（显示在视觉内容上的文字），请参阅 `layout-compositor.md` 文档。

典型应用场景：
- VJ 控制台（主推子器、场景切换按钮、效果开关）
- 安装操作员控制台
- 具有独立参数用户界面的独立 TOX 组件
- 在平板电脑上显示的类似手机的操作界面

---

## 两层用户界面结构

| 层级 | 含义 | 用途 |
|---|---|---|
| **自定义参数** | 任何 COMP 中的参数，其编辑方式与内置的 TD 参数相同 | 用于配置组件、预设以及“设置”面板 |
| **面板 COMP** | 容器 COMP 内部可见的控件（按钮、滑块、输入框） | 构建交互式控制界面和实时用户界面 |

两者可结合使用：创建一个包含面板控件的容器 COMP，使其能够读取/写入父组件中的自定义参数。

---

## 自定义参数

可为任何 COMP 添加可由用户编辑的参数。这些参数会随 COMP 一同保存，可用于驱动表达式，并在保存/重新加载后依然存在。

```python
# Add a custom page to a baseCOMP
comp = op('/project1/my_component')
page = comp.appendCustomPage('Controls')

# Add typed params
page.appendFloat('Intensity', label='Intensity')[0]   # returns a Par
page.appendInt('Count', label='Count')[0]
page.appendToggle('Enabled', label='Enabled')[0]
page.appendMenu('Mode', menuNames=['off', 'soft', 'hard'], menuLabels=['Off', 'Soft', 'Hard'])[0]
page.appendStr('Title', label='Title')[0]
page.appendRGB('Color', label='Color')                # returns 3 pars
page.appendXY('Offset', label='Offset')               # returns 2 pars
page.appendPulse('Reset', label='Reset')[0]
page.appendFile('TextureFile', label='Texture')[0]
```

**随时随地读写数据：**

```python
val = op('/project1/my_component').par.Intensity.eval()
op('/project1/my_component').par.Intensity = 0.7
```

**通过表达式驱动其他参数：**

```python
op('bloom1').par.threshold.mode = ParMode.EXPRESSION
op('bloom1').par.threshold.expr = "op('/project1/my_component').par.Intensity"
```

**脉冲处理器（重置按钮）：**

通过使用监听 COMP 脉冲参数的 `parameterExecuteDAT` 来实现相关功能。详情请参阅 `dat-scripting.md`。

---

## 面板 COMPs —— 小部件

它们均为 COMP，会在 `containerCOMP` 内以可点击/可拖动的形式呈现为小部件。

| 类型 | 类型名称 | 用途 |
|---|---|---|
| 按钮 | `buttonCOMP` | 执行点击操作——瞬时触发或切换状态 |
| 滑块 | `sliderCOMP` | 通过拖动设置 0-1 的数值（一维或二维） |
| 输入框 | `fieldCOMP` | 文本输入 |
| 容器 | `containerCOMP` | 负责布局与视觉样式设计，用于容纳子元素 |
| 下拉选择 | `selectCOMP` | 引用并显示来自其他 COMP 的内容 |
| 列表 | `listCOMP` | 支持滚动的列表，每行可设置回调函数 |

### 按钮

```python
btn = root.create(buttonCOMP, 'play_btn')
btn.par.w = 120; btn.par.h = 40
btn.par.buttontype = 'momentary'    # 'momentary' | 'toggleup' | 'togglepress' | 'radio'
btn.par.bgcolorr = 0.1; btn.par.bgcolorg = 0.1; btn.par.bgcolorb = 0.1
btn.par.text = 'Play'

# Read state
state = btn.panel.state          # 1 when active
```

### 滑块控件

```python
sld = root.create(sliderCOMP, 'master_fader')
sld.par.w = 60; sld.par.h = 300
sld.par.style = 'vertical'        # 'vertical' | 'horizontal' | 'xy'
sld.par.value0min = 0.0
sld.par.value0max = 1.0

# Drive a parameter via expression (always-on, no callback needed)
op('/project1/master_level').par.opacity.mode = ParMode.EXPRESSION
op('/project1/master_level').par.opacity.expr = "op('master_fader').panel.u"
```

`panel.u` 和 `panel.v` 用于显示经过归一化处理后的 0-1 值。对于二维滑块，这两个字段都会被填充数据。

### 字段（文本输入）

```python
fld = root.create(fieldCOMP, 'scene_name')
fld.par.w = 200; fld.par.h = 30
fld.par.fieldtype = 'string'      # 'string' | 'integer' | 'float'

# Read current text
text = fld.panel.field            # the text content
```

### 列表

对于需要支持滚动且可选中行的列表，可使用嵌入式的 `list1_callbacks` DAT 来处理行级交互操作。可通过 `list_definition` 表 DAT 来定义单元格内容。

---

## 容器 COMP — 布局与样式

`containerCOMP` 是用于对小部件进行分组以及布局安排的主要父容器。

```python
panel = root.create(containerCOMP, 'control_panel')
panel.par.w = 400; panel.par.h = 600
panel.par.bgcolorr = 0.05
panel.par.bgcolorg = 0.05
panel.par.bgcolorb = 0.05
panel.par.bgalpha = 1.0

# Layout child panels in vertical stack
panel.par.align = 'lefttoright'   # 'lefttoright' | 'toptobottom' | etc.
```

子元素会根据 `par.align` 参数自动定位。如需绝对定位，请将 `par.align` 设置为 `'fillresize'`，并分别指定每个子元素的 `par.x` / `par.y` 值。

### 布局策略

| `par.align` | 行为描述 |
|---|---|
| `lefttoright` | 子元素水平堆叠 |
| `toptobottom` | 子元素垂直堆叠 |
| `righttoleft` / `bottomtotop` | 反向堆叠 |
| `fillresize` | 子元素按需调整大小以填满空间，需手动定位 |
| `top` / `bottom` / `left` / `right` | 固定定位 |

对于复杂的网格布局：可采用嵌套容器的方式——即使用垂直容器来容纳多个水平容器。

---

## 面板回调函数 —— 事件响应机制

`panelExecuteDAT` 会持续监控面板，并在用户发生交互时触发相应的 Python 回调函数。

```python
pe = root.create(panelExecuteDAT, 'btn_handler')
pe.par.panel = '/project1/play_btn'
pe.par.click = True              # respond to clicks
pe.par.value = True              # respond to value changes
```

在其已停靠的 DAT 中：

```python
def onOffToOn(panelValue):
    # Click pressed
    op('/project1/scene_timer').par.start.pulse()
    return

def onOnToOff(panelValue):
    # Click released
    return

def onValueChange(panelValue):
    # Slider drag, field change, etc.
    new_val = panelValue.eval()
    op('/project1/master').par.opacity = new_val
    return
```

在自定义参数页面中设置脉冲参数时，请改用 `parameterExecuteDAT`。  

---

## 构建功能完备的 VJ 控制面板

端到端实现方案：

```python
# 1. Top-level container
panel = root.create(containerCOMP, 'vj_control')
panel.par.w = 800; panel.par.h = 200
panel.par.align = 'lefttoright'

# 2. Master fader column
master_col = panel.create(containerCOMP, 'master')
master_col.par.w = 120; master_col.par.h = 200
master_col.par.align = 'toptobottom'

master_label = master_col.create(textTOP, 'lbl')
master_label.par.text = 'MASTER'

master_sld = master_col.create(sliderCOMP, 'fader')
master_sld.par.w = 60; master_sld.par.h = 150
master_sld.par.style = 'vertical'

# 3. Scene buttons row
scene_col = panel.create(containerCOMP, 'scenes')
scene_col.par.w = 400; scene_col.par.h = 200
scene_col.par.align = 'lefttoright'
for i in range(8):
    b = scene_col.create(buttonCOMP, f'scene_{i+1}')
    b.par.w = 50; b.par.h = 50
    b.par.text = str(i+1)
    b.par.buttontype = 'radio'      # only one active at a time

# 4. FX toggle column
fx_col = panel.create(containerCOMP, 'fx')
fx_col.par.w = 280; fx_col.par.h = 200
fx_col.par.align = 'toptobottom'
for fx in ['Bloom', 'CRT', 'Glitch', 'Strobe']:
    t = fx_col.create(buttonCOMP, fx.lower())
    t.par.w = 220; t.par.h = 35
    t.par.text = fx
    t.par.buttontype = 'toggleup'

# 5. Display in a window
win = root.create(windowCOMP, 'control_win')
win.par.winop = panel.path
win.par.winw = 800; win.par.winh = 200
win.par.borders = True
win.par.winopen.pulse()
```

随后，可通过表达式或 panelExecuteDATs 将面板参数值传递给操作模块。

---

## 面板的展示方式——独立窗口或嵌入式显示

| 方式 | 适用场景 |
|---|---|
| 使用指向面板的 `windowCOMP` | 独立的控制界面，单独的显示区域 |
| 通过 `renderTOP` 渲染容器COMP | 在可视化内容之上叠加复合UI（类似HUD界面） |
| 直接在网络编辑器面板中使用 `panelCOMP` | 仅限设计师/开发者预览——此时面板具备完全交互功能 |

对于触摸屏平板电脑，可在第二台显示器上使用 `windowCOMP`，并将其信号路由至平板电脑的HDMI输入端口。

---

## 常见问题与解决方案

1. **面板无法响应点击操作** —— 可能是因为设置了 `par.disabled = True`，或父容器中存在 `par.disableinputs = True`。请检查面板的层级结构。
2. **滑块数值不更新** —— `panel.u/v` 读取的是可视化元素的位置。若直接设置 `par.value0`，会导致可视化元素出现延迟。应让 `par.value0` 成为真实数值来源，再由滑块随之更新。
3. **自定义参数不显示** —— 必须先调用 `appendCustomPage`，然后再添加参数。没有参数的页面将不会显示。
4. **重新加载后自定义参数消失** —— 通过Python在运行时添加的参数，只有在其对应的COMP被保存之后才会保留。建议使用 `tox` 格式保存（`comp.save('mycomp.tox')`），或通过 `td_execute_python` 执行代码后再保存项目。
5. **事件回调触发两次** —— 单次按钮点击可能会同时触发 `onOffToOn` 和 `onValueChange` 两个回调。请选择其中一个来处理相应操作，避免重复触发。
6. **脉冲参数需使用 `.pulse()` 方法** —— 直接为脉冲参数设置 `par.X = True` 是无效的。务必使用 `.pulse()` 方法。
7. **字段文本需按 Tab/Enter 键才会生效** —— 在输入过程中字段不会触发回调。若需在每次按键时都触发回调，可设置 `par.committemode = 'all'`（但此方式性能开销较大）。
8. **`par.text` 与面板内容的区别** —— `buttonCOMP.par.text` 是按钮上的标签文字，而按钮的当前状态则由 `panel.state`（0/1）决定。两者不可混淆。
9. **macOS系统下的触摸输入** —— 直接通过触摸面板实现多点触控功能是可行的，但TD的触摸手势处理能力较为基础。对于复杂的缩放/旋转等多点触控操作，建议在平板电脑上使用TouchOSC。
10. **布局未及时更新** —— 更改 `par.align` 属性时，容器需要重新计算布局。可通过点击子元素或对容器进行脉冲操作来触发重新计算。

---

## 快速实现方案

| 需求 | 实现方式 |
|---|---|
| 控制主推子器 | 使用垂直方向的 `sliderCOMP`，并通过表达式控制 `level.par.opacity` 的值 |
| 场景选择器 | 使用8个单选按钮型的 `buttonCOMP`，根据其状态调用 `selectCHOP` 函数，进而控制 `switchTOP.par.index` |
| 效果开关控制 | 使用上下切换型 `buttonCOMP`，通过表达式控制某个效果运算单元的旁路开关 |
| 数值输入 | 使用浮点数类型的 `fieldCOMP`，并通过表达式将其值赋给目标参数 |
| 组件参数设置 | 在对应组件的COMP上定义自定义参数，由面板内的控件来驱动这些参数的变化 |
| 触摸屏界面 | 使用包含各种控件的 `containerCOMP`，再通过 `windowCOMP` 将其显示在第二台显示器上 |
| 状态显示 | 通过 `selectCOMP` 方法将 `textTOP` 渲染到面板中以实现状态展示 |
