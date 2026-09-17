# Replicator COMP 参考文档

`replicatorCOMP` 能够根据数据表的要求，将某个模板操作符复制 N 次。这是数据驱动型网络的基本结构模式，常见应用包括按钮网格、场景角色列表、动态用户界面以及针对每个通道的参数面板。

如需了解基于像素/每次渲染进行实例化的方法，请参阅 `geometry-comp.md`。Replicator 负责构建网络节点，而实例化则用于生成渲染副本——二者属于不同的处理层面。

---

## 概念说明

```
[Template OP]                  [Data tableDAT]
       │                              │
       └─────→ replicatorCOMP ←───────┘
                     │
                     ▼
        [N clones], one per data row
        Each clone gets per-row params
```

修改一次模板 → 所有克隆体都会继承该更改。修改表格 → 克隆体会动态地新增或删除行。可针对每一行单独推送参数覆盖值。

---

## 最简配置流程

```python
# 1. Make a template (the thing to clone)
template = root.create(buttonCOMP, 'btn_template')
template.par.w = 80; template.par.h = 80
template.par.text = 'X'
template.par.bgcolorr = 0.2

# 2. Make a data table (one row per clone)
data = root.create(tableDAT, 'scene_data')
data.appendRow(['name', 'color_r', 'color_g', 'color_b'])
data.appendRow(['Sunset', 1.0, 0.4, 0.0])
data.appendRow(['Midnight', 0.0, 0.1, 0.4])
data.appendRow(['Storm', 0.3, 0.3, 0.5])
data.appendRow(['Forest', 0.0, 0.5, 0.2])

# 3. Replicator — points at template + data
rep = root.create(replicatorCOMP, 'scene_buttons')
rep.par.template = template.path
rep.par.opfromdat = data.path
rep.par.namefromdatname = 'name'        # use 'name' column for clone names
rep.par.incrementalnumbering = False
```

烹饪完成后，复制器会生成4个名为“Sunset”、“Midnight”、“Storm”和“Forest”的子COMP（每行非标题行对应一个），它们均是从“btn_template”克隆而来的。

---

## 每行参数覆盖设置

复制器中预置的“replicator1_callbacks”DAT文件允许你对每个克隆对象进行自定义配置：

```python
def onReplicate(comp, allOps, newOps, template, master):
    """Called once per replicate cycle. newOps is the list of just-created clones."""
    data = op('scene_data')
    for i, clone in enumerate(newOps):
        row = i + 1                 # +1 to skip header
        clone.par.text = data[row, 'name'].val
        clone.par.bgcolorr = float(data[row, 'color_r'].val)
        clone.par.bgcolorg = float(data[row, 'color_g'].val)
        clone.par.bgcolorb = float(data[row, 'color_b'].val)
    return
```

或者使用引用 `digits` 的参数表达式（即每个克隆分支的索引，作为内置表达式标记存在于克隆后的子树中）：

```python
# Inside the template, set a param expression like:
# par.value0.expr = "op('../scene_data')[me.digits + 1, 'value']"
```

`me.digits` 的值即为当前克隆体的行索引。这是实现静态引用模式的最简洁方式——无需使用回调函数。

---

## 布局：网格中的按钮

将复制器放入具有自动布局功能的 `containerCOMP` 中即可：

```python
panel = root.create(containerCOMP, 'scene_panel')
panel.par.w = 400; panel.par.h = 100
panel.par.align = 'lefttoright'

# Move the replicator inside
rep.parent = panel.path           # or create rep as a child of panel directly
```

每个克隆对象都是复制器的子对象（而复制器本身又是面板的子对象）。面板会自动对所有元素进行排列。

对于二维网格，需在容器上设置 `par.align = 'fillresize'`，然后根据行号/列号在回调函数中为每个克隆对象分别覆盖 `par.x` / `par.y` 的值。---

## 无需重建即可更新

当数据表发生变化时，复制器会重新生成这些克隆对象。默认情况下，它会销毁并重新创建所有内容。若要保留现有状态，请设置：

```python
rep.par.recreatemissing = True       # only add/remove changed rows
rep.par.recreateallonchange = False
```

该模式对于实时编辑场景至关重要（即设计人员调整表格时，网络连接仍需保持稳定）。

而对于增量数据导入场景（例如通过 `webDAT` 定期轮询 API 获取数据），则可由 `datExecuteDAT` 负责监控响应、解析数据并将其写入数据表，进而实现复制器的自动更新。

---

## 常见模式

### 场景角色分配（数据 → 按钮 + 逻辑）

```python
# Data per scene: name, file path, audio track, BPM
scene_data.appendRow(['name', 'file', 'audio', 'bpm'])
scene_data.appendRow(['Intro', '/scenes/intro.tox', '/audio/intro.wav', 110])
scene_data.appendRow(['Main', '/scenes/main.tox', '/audio/main.wav', 128])

# Replicator clones a buttonCOMP per scene
# Each button's onClick callback loads the corresponding tox + cues audio
```

### 动态参数面板

针对各个音频频段，会为每个频段生成一个推子条：

```python
# Data: band names (sub, low, mid, hi-mid, high, air)
# Template: containerCOMP with label + sliderCOMP
# Replicator clones N strips
# Each slider's value is read at /audio_eq/{band_name}/fader
```

### 过程化视觉网络

根据配置文件构建多通道视觉网络：

```python
# Data: which TOPs to chain, per "scene"
# Template: a baseCOMP with placeholder children
# Replicator builds one baseCOMP per scene; each scene contains a custom chain
# Switch between scenes via switchTOP.par.index driven by panel
```

### 每通道独立显示的CHOP功能

可分别查看多通道CHOP中的各个通道状态：

```python
# Data table: one row per channel (auto-extracted via choptodatDAT)
# Template: a small chopVis COMP showing one channel
# Replicator generates N visualizers stacked vertically
```

---

## 复制器模式与纯 Python 循环模式对比

| 方式 | 适用场景 |
|---|---|
| **replicatorCOMP** | 克隆集合会动态变化（实时添加/删除行）。适用于需要可视化编辑的场景，且该模式可在不同项目中重复使用。 |
| **Python 循环**（通过 `td_execute_python` 实现） | 用于一次性生成数据。数据集为静态，逻辑更简单，无需处理模板开销，代码编写速度更快。 |

如果仅需构建一次网络结构，建议使用 `td_execute_python` 配合 Python 循环模式。而当数据是实时变化的时，复制器模式才能发挥其优势。

---

## 常见问题与注意事项

1. **表头行问题** —— `tableDAT` 中的行采用 0 索引制。若存在表头，则第一行数据对应的索引为 1。在回调函数中，由于索引处理不当而导致的错误十分常见。
2. **缺少 `namefromdatname` 列** —— 复制器模式会默认使用基于数字的后缀作为名称。这样一来，按钮的名称就会变为 `1`、`2`、`3` 等，缺乏实际意义。建议明确设置 `par.namefromdatname` 参数。
3. **模板作为网络节点存在** —— 模板操作本身也是一个真实的网络节点。切勿直接将其下游的其他组件与之相连，而应连接到克隆节点上（或在其之间使用 `nullCOMP` 作为中间节点）。
4. **“更改时重新生成”功能会清除状态** —— 每次重新生成数据时，切换开关的状态、滑块位置以及克隆节点内的未缓存数据都会丢失。如需保留这些信息，可使用 `recreatemissing` 参数。
5. **编辑操作不会触发 `onReplicate` 事件** —— 该事件仅在克隆集合发生变化时才会触发。对现有行中的数值进行修改不会再次触发该事件。如需实现单元格级的实时更新，可使用 `parameterExecuteDAT` 或表达式功能。
6. **克隆体上的自定义参数**——在模板中添加的页面会同步到克隆体中，而在 `onReplicate` 函数中添加的页面则会在下一次重新生成时丢失。务必在模板上而非克隆体上添加自定义页面。

7. **批量处理带来的问题**——快速添加大量数据行会触发大量克隆事件。建议通过 Python 批量添加数据，并在最后调用一次 `data.cook(force=True)`。

8. **复制器子节点之外的 `me.digits`**——`me.digits` 仅在作为复制器子节点的操作中有效。请勿在无关的网络结构中引用它。

9. **跨克隆体引用**——虽然可以通过相对路径从某个克隆体内部引用另一个兄弟克隆体（如 `op('../OtherClone/x')`），但若克隆体名称发生变化，此方式将失效。建议通过数据表使用绝对路径进行引用。

---

## 快速方案

| 需求 | 设置方式 |
|---|---|
| 8按钮场景选择器 | `tableDAT`（8行数据）+ `buttonCOMP`模板 + `replicatorCOMP` |
| 每个频段的EQ控制面板 | `tableDAT`（频段名称）+ 容器模板（标签+滑块）+ 复制器 |
| 数据驱动的视觉场景 | `tableDAT`（场景配置）+ `baseCOMP`模板（视觉元素链）+ 复制器 |
| 实时更新的克隆体集合 | 上述设置 + 设置 `par.recreatemissing = True` |
| 每行不同颜色的UI | 包含颜色列的数据表，通过 `onReplicate` 回调为每个克隆体设置不同颜色 |
| 从API响应获取列表 | `webDAT` → `datExecuteDAT`解析JSON → 写入数据表 → 复制器更新数据 |
