# TouchDesigner Python API 参考手册

## td 模块

TouchDesigner 的 Python 环境会自动导入 `td` 模块。所有与 TD 相关的类、函数和常量均位于此处。TD 内部的脚本（Script DAT 文件、CHOP/DAT 执行回调函数以及扩展插件）均可完全访问这些内容。

在使用 MCP 的 `execute_python_script` 工具时，以下全局变量会预先加载：
- `op` — `td.op()` 的简写，用于通过路径查找操作符
- `ops` — `td.ops()` 的简写，用于根据模式查找多个操作符
- `me` — 执行脚本的操作符（通过 MCP，它实际上就是 twozero 内部执行器）
- `parent` — `me.parent()` 的简写
- `project` — 根项目组件
- `td` — 完整的 td 模块

## 查找操作符：op() 和 ops()

### op(path) — 查找单个操作符

```python
# Absolute path (always works from MCP)
node = op('/project1/noise1')

# Relative path (relative to current operator — only in Script DATs)
node = op('noise1')      # sibling
node = op('../noise1')   # parent's sibling

# Returns None if not found (does NOT raise)
node = op('/project1/nonexistent')  # None
```

### ops(pattern) — 查找多个操作符

```python
# Glob patterns
nodes = ops('/project1/noise*')       # all nodes starting with "noise"
nodes = ops('/project1/*')            # all direct children
nodes = ops('/project1/container1/*') # all children of container1

# Returns a tuple of operators (may be empty)
for n in ops('/project1/*'):
    print(n.name, n.OPType)
```

### 从节点进行导航

```python
node = op('/project1/noise1')

node.name        # 'noise1'
node.path        # '/project1/noise1'
node.OPType      # 'noiseTop'
node.type         # <class 'noiseTop'>
node.family       # 'TOP'

# Parent / children
node.parent()              # the parent COMP
node.parent().children     # all siblings + self
node.parent().findChildren(name='noise*')  # filtered

# Type checking
node.isTOP   # True
node.isCHOP  # False
node.isSOP   # False
node.isDAT   # False
node.isMAT   # False
node.isCOMP  # False
```

## 参数

每个操作符都拥有可通过 `.par` 属性访问的参数。

### 读取参数

```python
node = op('/project1/noise1')

# Direct access
node.par.seed.val        # current evaluated value (may be an expression result)
node.par.seed.eval()     # same as .val
node.par.seed.default    # default value
node.par.monochrome.val  # boolean parameters: True/False

# List all parameters
for p in node.pars():
    print(f"{p.name}: {p.val} (default: {p.default})")

# Filter by page (parameter group)
for p in node.pars('Noise'):  # page name
    print(f"{p.name}: {p.val}")
```

### 设置参数

```python
# Direct value setting
node.par.seed.val = 42
node.par.monochrome.val = True
node.par.resolutionw.val = 1920
node.par.resolutionh.val = 1080

# String parameters
op('/project1/text1').par.text.val = 'Hello World'

# File paths
op('/project1/moviefilein1').par.file.val = '/path/to/video.mp4'

# Reference another operator (for "dat", "chop", "top" type parameters)
op('/project1/glsl1').par.dat.val = '/project1/shader_code'
```

### 参数表达式

```python
# Python expressions that evaluate dynamically
node.par.seed.expr = "me.time.frame"
node.par.tx.expr = "math.sin(me.time.seconds * 2)"

# Reference another parameter
node.par.brightness1.expr = "op('/project1/constant1').par.value0.val"

# Export (one-way binding from CHOP to parameter)
# This makes the parameter follow a CHOP channel value
op('/project1/noise1').par.seed.val  # can also be driven by exports
```

### 参数类型

| 类型 | Python 类型 | 示例 |
|------|------------|---------|
| 浮点数 | `float` | `node.par.brightness1.val = 0.5` |
| 整数 | `int` | `node.par.seed.val = 42` |
| 开关 | `bool` | `node.par.monochrome.val = True` |
| 字符串 | `str` | `node.par.text.val = 'hello'` |
| 菜单 | `int`（索引）或 `str`（标签） | `node.par.type.val = 'sine'` |
| 文件 | `str`（路径） | `node.par.file.val = '/path/to/file'` |
| OP引用 | `str`（路径） | `node.par.dat.val = '/project1/text1'` |
| 颜色 | 分开的r/g/b/a浮点数 | `node.par.colorr.val = 1.0` |
| XY/XYZ坐标 | 分开的x/y/z浮点数 | `node.par.tx.val = 0.5` |

## 创建与删除运算符

```python
# Create via parent component
parent = op('/project1')
new_node = parent.create(noiseTop)         # using class reference
new_node = parent.create(noiseTop, 'my_noise')  # with custom name

# The MCP create_td_node tool handles this automatically:
# create_td_node(parentPath="/project1", nodeType="noiseTop", nodeName="my_noise")

# Delete
node = op('/project1/my_noise')
node.destroy()

# Copy
original = op('/project1/noise1')
copy = parent.copy(original, name='noise1_copy')
```

## 连接（连线操作符）

### 从输出连接到输入连接

```python
# Connect noise1's output to level1's input
op('/project1/noise1').outputConnectors[0].connect(op('/project1/level1'))

# Connect to specific input index (for multi-input operators like Composite)
op('/project1/noise1').outputConnectors[0].connect(op('/project1/composite1').inputConnectors[0])
op('/project1/text1').outputConnectors[0].connect(op('/project1/composite1').inputConnectors[1])

# Disconnect all outputs
op('/project1/noise1').outputConnectors[0].disconnect()

# Query connections
node = op('/project1/level1')
inputs = node.inputs          # list of connected input operators
outputs = node.outputs        # list of connected output operators
```

### 常见配置的连接模式

```python
# Linear chain: A -> B -> C -> D
ops_list = [op(f'/project1/{name}') for name in ['noise1', 'level1', 'blur1', 'null1']]
for i in range(len(ops_list) - 1):
    ops_list[i].outputConnectors[0].connect(ops_list[i+1])

# Fan-out: A -> B, A -> C, A -> D
source = op('/project1/noise1')
for target_name in ['level1', 'composite1', 'transform1']:
    source.outputConnectors[0].connect(op(f'/project1/{target_name}'))

# Merge: A + B + C -> Composite
comp = op('/project1/composite1')
for i, source_name in enumerate(['noise1', 'text1', 'ramp1']):
    op(f'/project1/{source_name}').outputConnectors[0].connect(comp.inputConnectors[i])
```

## DAT内容操作

### 文本型DAT

```python
dat = op('/project1/text1')

# Read
content = dat.text          # full text as string

# Write
dat.text = "new content"
dat.text = '''multi
line
content'''

# Append
dat.text += "\nnew line"
```

### DAT表格

```python
dat = op('/project1/table1')

# Read cell
val = dat[0, 0]         # row 0, col 0
val = dat[0, 'name']    # row 0, column named 'name'
val = dat['key', 1]     # row named 'key', col 1

# Write cell
dat[0, 0] = 'value'

# Read row/col
row = dat.row(0)         # list of Cell objects
col = dat.col('name')    # list of Cell objects

# Dimensions
rows = dat.numRows
cols = dat.numCols

# Append row
dat.appendRow(['col1_val', 'col2_val', 'col3_val'])

# Clear
dat.clear()

# Set entire table
dat.clear()
dat.appendRow(['name', 'value', 'type'])
dat.appendRow(['frequency', '440', 'float'])
dat.appendRow(['amplitude', '0.8', 'float'])
```

## 时间与动画功能

```python
# Global time
td.absTime.frame       # absolute frame number (never resets)
td.absTime.seconds     # absolute seconds

# Timeline time (affected by play/pause/loop)
me.time.frame          # current frame on timeline
me.time.seconds        # current seconds on timeline
me.time.rate           # FPS setting

# Timeline control (via execute_python_script)
project.play = True
project.play = False
project.frameRange = (1, 300)   # set timeline range

# Cook frame (when operator was last computed)
node.cookFrame
node.cookTime
```

## 扩展功能（组件上的自定义 Python 类）

扩展功能可为 COMPs 添加自定义的 Python 方法和属性。

```python
# Create extension on a Base COMP
base = op('/project1/myBase')

# The extension class is defined in a Text DAT inside the COMP
# Typically named 'ExtClass' with the extension code:

extension_code = '''
class MyExtension:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.counter = 0

    def Reset(self):
        self.counter = 0

    def Increment(self):
        self.counter += 1
        return self.counter

    @property
    def Count(self):
        return self.counter
'''

# Write extension code to DAT inside the COMP
op('/project1/myBase/extClass').text = extension_code

# Configure the extension on the COMP
base.par.extension1 = 'extClass'  # name of the DAT
base.par.promoteextension1 = True  # promote methods to parent

# Call extension methods
base.Increment()       # calls MyExtension.Increment()
count = base.Count     # accesses MyExtension.Count property
base.Reset()
```

## 实用的内置模块

### tdu — TouchDesigner 工具集

```python
import tdu

# Dependency tracking (reactive values)
dep = tdu.Dependency(initial_value)
dep.val = new_value   # triggers dependents to recook

# File path utilities
tdu.expandPath('$HOME/Desktop/output.mov')

# Math
tdu.clamp(value, min, max)
tdu.remap(value, from_min, from_max, to_min, to_max)
```

### TD函数

```python
from TDFunctions import *

# Commonly used utilities
clamp(value, low, high)
remap(value, inLow, inHigh, outLow, outHigh)
interp(value1, value2, t)  # linear interpolation
```

### TDStoreTools — 持久化存储

```python
from TDStoreTools import StorageManager

# Store data that survives project reload
me.store('myKey', 'myValue')
val = me.fetch('myKey', default='fallback')

# Storage dict
me.storage['key'] = value
```

## 通过 execute_python_script 实现常见模式

### 构建完整的处理链

```python
# Create a complete audio-reactive noise chain
parent = op('/project1')

# Create operators
audio_in = parent.create(audiofileinChop, 'audio_in')
spectrum = parent.create(audiospectrumChop, 'spectrum')
chop_to_top = parent.create(choptopTop, 'chop_to_top')
noise = parent.create(noiseTop, 'noise1')
level = parent.create(levelTop, 'level1')
null_out = parent.create(nullTop, 'out')

# Wire the chain
audio_in.outputConnectors[0].connect(spectrum)
spectrum.outputConnectors[0].connect(chop_to_top)
noise.outputConnectors[0].connect(level)
level.outputConnectors[0].connect(null_out)

# Set parameters
audio_in.par.file = '/path/to/music.wav'
audio_in.par.play = True
spectrum.par.size = 512
noise.par.type = 1  # Sparse
noise.par.monochrome = False
noise.par.resolutionw = 1920
noise.par.resolutionh = 1080
level.par.opacity = 0.8
level.par.gamma1 = 0.7
```

### 查询网络状态

```python
# Get all TOPs in the project
tops = [c for c in op('/project1').findChildren(type=TOP)]
for t in tops:
    print(f"{t.path}: {t.OPType} {'ERROR' if t.errors() else 'OK'}")

# Find all operators with errors
def find_errors(parent_path='/project1'):
    parent = op(parent_path)
    errors = []
    for child in parent.findChildren(depth=-1):
        if child.errors():
            errors.append((child.path, child.errors()))
    return errors

result = find_errors()
```

### 批量参数修改

```python
# Set parameters on multiple nodes at once
settings = {
    '/project1/noise1': {'seed': 42, 'monochrome': False, 'resolutionw': 1920},
    '/project1/level1': {'brightness1': 1.2, 'gamma1': 0.8},
    '/project1/blur1': {'sizex': 5, 'sizey': 5},
}

for path, params in settings.items():
    node = op(path)
    if node:
        for key, val in params.items():
            setattr(node.par, key, val)
```

## Python版本与相关包

TouchDesigner预装了Python 3.11+版本，其中包含以下常用包：
- **numpy** — 用于数组运算及快速数学计算
- **scipy** — 用于信号处理及FFT运算
- **OpenCV**（cv2）— 用于计算机视觉功能
- **PIL/Pillow** — 用于图像处理
- **requests** — 用于HTTP请求
- **json**、**re**、**os**、**sys** — 标准库模块

**重要提示：** 下方示例中的参数名称仅为示意用途。请务必执行检测功能（SKILL.md中的第0步），以获取与您所使用的TouchDesigner版本相匹配的实际参数名称。切勿直接复制示例中的参数名称。

用户还可以将自定义包安装到TouchDesigner的Python site-packages目录中。具体路径因操作系统而异，详情请参阅TouchDesigner官方文档。

## SOP顶点/点访问方式（TD 2025.32版本）

在TD 2025.32版本中，`td.Vertex`对象不包含`.x`、`.y`、`.z`这些属性。此时应通过索引方式来访问相关数据。

```python
# WRONG — crashes in TD 2025.32:
vertex.x, vertex.y, vertex.z

# CORRECT — index/attribute access:
pt = sop.points()[i]
pos = pt.P          # Position object
x, y, z = pos[0], pos[1], pos[2]

# Always introspect first:
dir(sop.points()[0])   # see what attributes actually exist
dir(sop.points()[0].P) # see Position object interface
```
