# Replicator COMP 参考文档

`replicatorCOMP` 能够根据数据表驱动，将某个模板操作符复制 N 次。这是数据驱动型网络中的基本 TD 模式应用场景，包括按钮网格、场景角色列表、动态用户界面以及针对每个通道的参数面板。

如需了解基于像素/每次渲染进行视觉实例化的方法，请参阅 `geometry-comp.md`。Replicator 负责构建网络节点，而实例化则用于生成渲染副本——二者属于不同的处理层面。

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

只需编辑一次模板，所有克隆体都会继承该更改；修改表格后，克隆体会动态地增加或删除相应行。同时，还可为每一行单独设置参数覆盖值。

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

## 每行参数覆盖功能

复制器自带的`replicator1_callbacks` DAT文件允许你对每个克隆对象进行个性化定制：

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

或者使用引用 `digits` 的参数表达式（即每个克隆分支的索引，可作为内置表达式标记存在于克隆后的子树中）：

```python
# Inside the template, set a param expression like:
# par.value0.expr = "op('../scene_data')[me.digits + 1, 'value']"
```

`me.digits` 的值即为当前克隆体的行索引。对于静态引用场景而言，这是最为简洁的实现方式——无需使用回调函数。

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

每个克隆体都是复制器的子节点（而复制器本身又是面板的子节点）。面板会自动对所有元素进行排列。

对于二维网格，需在容器上设置 `par.align = 'fillresize'`，然后根据行号/列号在回调函数中为每个克隆体分别覆盖 `par.x` / `par.y` 的值。---

## 无需重新构建即可更新

当数据表发生变化时，复制器会重新生成这些克隆体。默认情况下，它会销毁并重新创建所有元素。若要保留现有状态，请设置：

```python
rep.par.recreatemissing = True       # only add/remove changed rows
rep.par.recreateallonchange = False
```

该模式对于实时编辑场景至关重要（即设计师可调整表格，而网络连接始终保持畅通）。

对于增量数据导入场景（例如通过 `webDAT` 定期轮询 API），可让 `datExecuteDAT` 负责监控响应、解析数据并将其写入数据表，随后由复制器自动完成更新。

---

## 常见模式

### 场景编排（数据 → 按钮 + 逻辑）

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

可单独查看多通道CHOP中的每个通道：

```python
# Data table: one row per channel (auto-extracted via choptodatDAT)
# Template: a small chopVis COMP showing one channel
# Replicator generates N visualizers stacked vertically
```

---

## 复制器模式与纯 Python 循环模式对比

| 方案 | 适用场景 |
|---|---|
| **replicatorCOMP** | 克隆集合会动态变化（实时添加/删除行）。适用于需要可视化编辑的场景，且该模式可在不同项目中重复使用。 |
| **Python 循环**（通过 `td_execute_python` 实现） | 一次性生成数据，克隆集合为静态。逻辑更简单，无需处理模板开销，编写速度更快。 |

如果仅需构建一次网络结构，建议使用 `td_execute_python` 配合 Python 循环模式。而当数据是实时变化的场景下，复制器模式的优势才会显现。

---

## 常见陷阱

1. **表头行问题** —— `tableDAT` 的行是按 0 开始索引的。如果存在表头，第一行数据的索引为 1。在回调函数中很容易出现索引错误。
2. **缺少 `namefromdatname` 列** —— 复制器会默认使用基于数字的后缀作为名称。这样一来，按钮的名称就会变成 `1`、`2`、`3` 等，而非有意义的名称。建议显式设置 `par.namefromdatname`。
3. **模板本身也是网络节点** —— 模板操作本身即为一个真实的网络节点。不要直接在其下游连接其他元素，而应连接到克隆节点（或在此处使用 `nullCOMP` 作为中间节点）。
4. **“更改时重新生成”会清除状态** —— 每次重新生成时，切换开关、滑块位置以及克隆节点内的未缓存数据都会丢失。如需保留这些状态，可使用 `recreatemissing` 参数。
5. **编辑操作不会触发 `onReplicate` 事件** —— 该事件仅在克隆集合发生变化时触发。对现有行中的数值进行修改不会再次触发该事件。如需实现单元格级的实时更新，可使用 `parameterExecuteDAT` 或表达式。
6. **克隆节点上的自定义参数** —— 在模板中添加的页面会被同步到所有克隆节点。而在 `onReplicate` 事件中添加的页面则会在下一次重新生成时丢失。务必在模板中添加自定义页面，而非在克隆节点中。
7. **大量数据快速添加带来的问题** —— 迅速添加大量行会触发大量克隆事件。建议通过 Python 批量添加数据，最后再调用 `data.cook(force=True)` 一次性处理。
8. **`me.digits` 仅在复制器子节点中有效** —— `me.digits` 仅能在复制器的后代操作节点中生效。不要在无关的网络节点中引用它。
9. **跨克隆节点的引用问题** —— 虽然可以在克隆节点内部通过相对路径引用其他克隆节点（如 `op('../OtherClone/x')`），但若节点名称发生变化，该引用就会失效。建议使用数据表中的绝对路径进行引用。

---

## 快速实现方案

| 需求 | 实现方式 |
|---|---|
| 8 按钮场景选择器 | `tableDAT`（8 行）+ `buttonCOMP` 模板 + `replicatorCOMP` |
| 各频段均衡器控制面板 | `tableDAT`（存储频段名称）+ 容器模板（包含标签和滑块）+ 复制器 |
| 数据驱动的可视化场景 | `tableDAT`（存储场景配置）+ `baseCOMP` 模板（构建可视化链条）+ 复制器 |
| 实时更新的克隆集合 | 与上述方案相同 + 设置 `par.recreatemissing = True` |
| 每行不同颜色的 UI | 使用包含颜色列的数据表，通过 `onReplicate` 回调为每个克隆节点设置不同颜色 |
| 从 API 响应中获取列表数据 | 先通过 `webDAT` → `datExecuteDAT` 解析 JSON 数据 → 写入数据表 → 再由复制器更新界面 |
