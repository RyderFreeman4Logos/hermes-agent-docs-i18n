# TouchDesigner MCP — 常见问题与经验总结

这些经验来自实际的使用案例，是经过实践检验的宝贵知识。在开始开发之前，请务必先阅读本文。

## 参数名称

### 1. 绝对不要硬编码参数名称——始终通过程序动态获取

不同版本的 TouchDesigner 中，参数名称可能会发生变化。在某个版本中有效的参数，在另一个版本中可能无效。因此，务必使用 `td_get_par_info` 函数从 TouchDesigner 中获取真实的参数名称。

Agent 的大语言模型训练数据中可能包含错误的参数名称，切勿依赖这些数据。

以下是已知的历史差异（实际情况可能还会有变化——请务必自行验证）：
| 文档/训练资料中的名称 | 某些版本中的实际名称 | 备注 |
|-------------------|----------------------|------|
| `dat` | `pixeldat` | GLSL TOP像素着色器中的DAT数据 |
| `colora` | `alpha` | TOP区域的恒定透明度值 |
| `sizex` / `sizey` | `size` | TOP区域的模糊强度（单个数值） |
| `fontr/g/b/a` | `fontcolorr/g/b/a` | TEXT TOP区域文字的颜色值（红/绿/蓝） |
| `fontcolora` | `fontalpha` | TEXT TOP区域文字的透明度值（并非`fontcolora`） |
| `bgcolora` | `bgalpha` | TEXT TOP区域背景的透明度值 |
| `value1name` | `vec0name` | GLSL TOP统一变量的名称 |

### 2. twozero td_execute_python 的响应格式

通过 twozero MCP 调用 `td_execute_python` 时，成功的响应会以 `(ok)` 开头，后跟帧率/错误统计信息（例如 `[fps 60.0/60] [0 err/0 warn]`），而非原始的 Python `result` 字典。如果需要通过程序解析响应，请先检查是否以 `(ok)` 开头——不要直接根据脚本中的 Python 变量名进行匹配。应使用 `td_get_operator_info` 函数或单独的查询方式来获取实际数值。

### 3. 使用 td_set_operator_pars 时，参数名称必须完全一致

建议先使用 td_get_par_info 函数来查询参数名称。与直接使用 Python 会导致整个脚本因 tdAttributeError 而崩溃并终止执行不同，MCP 工具会验证参数名称，并给出明确的错误提示说明问题所在。因此，请务必在设置参数之前先进行确认。

### 4. 为确保跨版本兼容性，请使用 `safe_par()` 模式

```python
def safe_par(node, name, value):
    p = getattr(node.par, name, None)
    if p is not None:
        p.val = value
        return True
    return False
```

### 5. `td.tdAttributeError` 会导致整个脚本崩溃——请采用防御性访问方式

如果执行 `node.par.nonexistent = value`，TD 会抛出 `tdAttributeError` 错误，从而使整个脚本停止运行。预防胜于补救：
- 使用 `op()` 而非 `opex()`——失败时 `op()` 会返回 None，而 `opex()` 会直接抛出异常
- 在访问任何参数之前先使用 `hasattr(node.par, 'name')` 进行检查
- 使用带有默认值的 `getattr(node.par, 'name', None)` 方法
- 采用第 3 个常见陷阱中介绍的 `safe_par()` 模式

```python
# WRONG — crashes if param doesn't exist:
node.par.nonexistent = value

# CORRECT — defensive access:
if hasattr(node.par, 'nonexistent'):
    node.par.nonexistent = value
```

### 6. `outputresolution`为字符串类型选项，而非整数。

```
menuNames: ['useinput','eighth','quarter','half','2x','4x','8x','fit','limit','custom','parpanel']
```
请始终使用字符串格式进行设置。若将 `outputresolution` 设置为 `9`，该操作很可能会在无声无息中失败。
```python
node.par.outputresolution = 'custom'  # correct
node.par.resolutionw = 1280; node.par.resolutionh = 720
```
查询有效值：`list(node.par.outputresolution.menuNames)`

## GLSL着色器

### 7. GLSL TOP中不存在`uTDCurrentTime`

GLSL TOP并不提供内置的时间统一变量。虽然GLSL MAT包含`uTDGeneral.seconds`，但该变量在GLSL TOP环境中不可用。

**主要参考——GLSL TOP向量/值页面：**
```python
gl.par.value0name = 'uTime'
gl.par.value0.expr = "absTime.seconds"
# In GLSL: uniform float uTime;
```

**回退方案——恒定TOP纹理（适用于复杂时间数据）：**

重要提示：必须将格式设置为`rgba32float`——默认的8位格式会将数值限制在0到1之间：
```python
t = root.create(constantTOP, 'time_driver')
t.par.format = 'rgba32float'
t.par.outputresolution = 'custom'
t.par.resolutionw = 1; t.par.resolutionh = 1
t.par.colorr.expr = "absTime.seconds % 1000.0"
t.outputConnectors[0].connect(glsl.inputConnectors[0])
```

### 8. API中GLSL编译错误不会产生任何提示

虽然UI上的GLSL TOP会显示黄色警告三角形，但`node.errors()`函数可能返回空字符串。建议同时查看`node.warnings()`的输出，并创建一个指向GLSL TOP的Info DAT文件，以便获取实际的编译器输出信息。

### 9. TD GLSL使用`vUV.st`而非`gl_FragCoord`——且在macOS上必须调用`TDOutputSwizzle()`函数

标准的GLSL语法在此处无效。TD框架提供了以下专用变量：
- `vUV.st` — UV坐标（范围为0-1）
- `uTDOutputInfo.res.zw` — 分辨率信息
- `sTD2DInputs[0]` — 输入纹理
- `layout(location = 0) out vec4 fragColor` — 输出颜色

在macOS平台上需特别注意：必须始终使用`TDOutputSwizzle()`函数来封装输出结果。
```glsl
fragColor = TDOutputSwizzle(color);
```
TD支持GLSL 4.60版本（基于Vulkan后端），已不再支持GLSL 3.30及更早的版本。

### 10. 大型GLSL着色器——写入临时文件

包含特殊字符的GLSL代码可能会损坏JSON数据。建议将此类着色器先写入临时文件，再在TD中加载使用。
```python
# Agent side: write shader to /tmp/shader.glsl via write_file
# TD side:
sd = root.create(textDAT, 'shader_code')
with open('/tmp/shader.glsl', 'r') as f:
    sd.text = f.read()
```

## 节点管理

### 11. 在遍历 `root.children` 时销毁节点会导致 `tdError` 错误

当某个子节点被销毁时，迭代器将会失效。因此务必先创建快照：
```python
kids = list(root.children)  # snapshot
for child in kids:
    if child.valid:  # check — earlier destroys may cascade
        child.destroy()
```

### 11b. 将节点的清理与创建操作拆分为独立的 td_execute_python 调用

在同一个脚本中创建与刚刚被销毁的节点具有相同名称的新节点，会引发“无效的操作对象”错误——即便使用了 `list()` 快照功能也是如此。TD 的内部引用在单个执行上下文内就可能会失效。

**错误做法（单次调用）：**
```python
# td_execute_python:
for c in list(root.children):
    if c.valid and c.name.startswith('my_'):
        c.destroy()
# ... then create my_audio, my_shader etc. in same script → CRASHES
```

**正确（两次独立调用）：**
```python
# Call 1: td_execute_python — clean only
for c in list(root.children):
    if c.valid and c.name.startswith('my_'):
        c.destroy()

# Call 2: td_execute_python — build (separate MCP call)
audio = root.create(audiofileinCHOP, 'my_audio')
# ... rest of build
```

### 12. Feedback TOP：应使用 `top` 参数，而非直接连接输入线

feedbackTOP 的 `top` 参数用于指定需要延迟的 TOP。切勿将该 TOP 直接连接到反馈功能的输入端——否则会形成真正的循环依赖关系。

正确设置方式：
```python
fb = root.create(feedbackTOP, 'fb_delay')
fb.par.top = comp.path          # reference only — no wire to fb input
fb.outputConnectors[0].connect(xf)  # fb output -> transform -> fade -> comp
```

在变换/渐变链中出现“检测到Cook依赖循环”警告属于正常现象。

### 13. GLSL TOP会自动创建关联节点

创建`glslTOP`时，系统还会同时生成`name_pixel`（文本DAT）、`name_info`（信息DAT）以及`name_compute`（文本DAT）这些节点。它们都会显示在网络图中。无需为这些“额外”的节点感到担忧。

### 14. 默认项目根目录为/project1

新的TD文件都以/project1作为主要容器来创建。系统节点则位于/、/ui、/sys、/local、/perform路径下。请勿在/project1之外创建用户节点。

### 15. 非商业许可版本的分辨率上限为1280x1280

即使将`resolutionw=1920`设置，实际分辨率也会被强制限制在1280。因此，请务必在创建后检查实际分辨率。
```python
n.cook(force=True)
actual = str(n.width) + 'x' + str(n.height)
```

## 录制与编解码器

### 16. MovieFileOut TOP：H.264/H.265/AV1 需要商业许可证

在非商业用途下，这些编解码器会引发错误。推荐的替代方案包括：
- `prores` — Apple ProRes格式，**在macOS上表现最佳**，支持硬件加速，且无需许可证。在1280x720分辨率下传输速度约为55MB/s，同时保持无损质量。**建议在macOS上将其设为默认选项。**
- `cineform` — GoPro Cineform格式，支持阿尔法通道
- `hap` — 支持硬件加速播放，适用于大文件处理
- `notchlc` — 支持硬件加速，图像质量良好
- `mjpa` — Motion JPEG格式，作为传统备用方案（有损压缩，仅当ProRes不可用时使用）

对于图像序列：需设置 `rec.par.type = 'imagesequence'` 以及 `rec.par.imagefiletype = 'png'`

### 17. MovieFileOut 可能不存在 `.record()` 方法

建议改用切换参数来实现相同功能：
```python
rec.par.record = True   # start recording
rec.par.record = False  # stop recording
```

在同一个脚本中同时设置文件路径并开始录制时，请使用delayFrames功能：
```python
rec.par.file = '/tmp/new_output.mov'
run("op('/project1/recorder').par.record = True", delayFrames=2)
```

### 18. 迅速调用 TOP.save() 时会捕获同一帧画面

如需进行实时录制，请使用 MovieFileOut；若希望获得精确到单帧的输出效果，则需将 `project.realTime` 设置为 False。

### 19. AudioFileIn 的 CHOP 功能：触发时机与录制顺序至关重要

必须严格按指定顺序执行录制操作，否则会导致录音文件为空、音频从文件中间开始播放，或根本无法生成文件。

**推荐的录制顺序如下：**

```python
# Step 1: Stop any existing recording
rec.par.record = False

# Step 2: Reset audio to beginning
audio.par.play = False
audio.par.cue = True
audio.par.cuepoint = 0      # may need cuepointunit=0 too
# Verify: audio.par.cue.eval() should be True

# Step 3: Set output file path
rec.par.file = '/tmp/output.mov'

# Step 4: Release cue + start playing + start recording (with frame delay)
audio.par.cue = False
audio.par.play = True
audio.par.playmode = 2      # Sequential — plays once through
run("op('/project1/recorder').par.record = True", delayFrames=3)
```

**为何每一步都很重要：**
- 首先设置 `rec.par.record = False` —— 如果之前仍有正在进行的录制，设置 `par.file` 可能会无声失败
- 设置 `audio.par.cue = True` + `cuepoint = 0` —— 这样可确保音频从开头开始播放，否则频谱图在最初几秒内可能处于静音状态
- 在开始录制时设置 `delayFrames=3` —— 在同一脚本中同时设置 `par.file` 和 `par.record = True` 可能会导致竞争条件；文件路径需要在录制开始前有一帧的时间来完成注册
- 设置 `playmode = 2`（顺序播放）—— 该模式会一次性播放文件。若希望让 TD 的时间轴控制播放位置，则请使用 `playmode = 0`（锁定到时间轴）

## TD Python API 使用模式

### 20. COMP 扩展配置：ext0object 格式至关重要

`ext0object` 要求使用常量字符串（而非表达式形式）：
```python
comp.par.ext0object = "op('./myExtensionDat').module.MyClassName(me)"
```
绝不可仅将参数设置为 DAT 名称。严禁使用 ParMode.EXPRESSION 模式。务必确保该 DAT 文件中包含 `par.language='python'` 这一配置。

### 21. td.Panel 不支持下标访问——应通过属性方式来调用其功能

```python
comp.panel.select      # correct (attribute access, returns float)
comp.panel['select']   # WRONG — 'td.Panel' object is not subscriptable
```

### 22. 在脚本回调中始终使用相对路径

在 scriptTOP/CHOP/SOP/DAT 回调中，应使用相对于 `scriptOp` 或 `me` 的路径：
```python
root = scriptOp.parent().parent()
dat = root.op('pixel_data')
```
绝不要硬编码诸如 `op('/project1/myComp/child')` 这样的绝对路径——当容器被重命名或复制时，这类路径就会失效。

### 23. keyboardinCHOP 频道名称均以“k”开头

这些频道名称分别为 `kup`、`kdown`、`kleft`、`kright`、`ka`、`kb` 等——而非 `up`、`down`、`a`、`b`。请务必通过以下方式进行确认：
```python
channels = [c.name for c in op('/project1/keyboard1').chans()]
```

### 24. expressCHOP 仅限烹饪上下文使用的属性——误报问题

`me.inputVal`、`me.chanIndex` 和 `me.sampleIndex` 仅在烹饪上下文中有效。从外部调用 `par.expr0expr.eval()` 总会引发错误——但这并非真正的运算符错误。在错误检测时可忽略这些错误。

### 25. td.Vertex 属性——应使用索引访问而非命名属性

在 TD 2025.32 版本中，`td.Vertex` 对象并不具备 `.x`、`.y`、`.z` 这类属性：
```python
# WRONG — crashes:
vertex.x, vertex.y, vertex.z

# CORRECT — index-based:
vertex.point.P[0], vertex.point.P[1], vertex.point.P[2]
# Or for SOP point positions:
pt = sop.points()[i]
pos = pt.P    # use P[0], P[1], P[2]
```

## 音频处理

### 26. Audio Spectrum CHOP 的输出信号较弱——如何增强它？

原始输出值非常小（0.001–0.05）。可使用内置的增强功能：`spectrum.par.highfrequencyboost = 3.0`。

如果信号依然较弱，可加入处于“范围模式”下的 Math CHOP 模块：`fromrangehi=0.05, torangehi=1.0`。

### 27. AudioSpectrum CHOP：时间切片与采样数量是最大的陷阱

当音频频率为 44100Hz 且设置 `timeslice=False` 时，该工具会将整个音频文件的所有样本都输出出来（约 24000 样本以上）。此时若再使用 CHOP-to-TOP 功能，会导致纹理分辨率超出上限，从而引发警告甚至操作失败。

**解决方案：** 为实现实时逐帧 FFT，请保持 `timeslice = True`（默认值）。可通过设置 `fftsize` 来控制频谱bin的数量（该参数为字符串类型，需使用 `'256'` 而非数字 `256`）。

如果使用 CHOP-to-TOP 后样本数量仍过多，可在 choptoTOP 参数中设置 `layout = 'rowscropped'`。

```python
spectrum.par.fftsize = '256'      # STRING, not int — enum values
spectrum.par.timeslice = True     # MUST be True for real-time audio reactivity
spectex.par.layout = 'rowscropped'  # handles oversized CHOP inputs
```

**resampleCHOP 没有 `numsamples` 参数。** 它使用的是 `rate`、`start`、`end` 和 `method` 这些参数。切勿凭猜测行事——务必先调用 `td_get_par_info('resampleCHOP')` 来查询参数信息。

### 28. CHOP To TOP 没有输入连接器——请使用 par.chop 引用方式

```python
spec_tex = root.create(choptoTOP, 'spectrum_tex')
spec_tex.par.chop = resample  # correct: parameter reference
# NOT: resample.outputConnectors[0].connect(spec_tex.inputConnectors[0])  # WRONG
```

## 工作流

### 29. 构建完成后务必进行验证——错误往往毫无征兆

节点错误与连接中断不会产生任何输出。务必进行检查：
```python
for c in list(root.children):
    e = c.errors()
    w = c.warnings()
    if e: print(c.name, 'ERR:', e)
    if w: print(c.name, 'WARN:', w)
```

### 30. 用于指定显示目标的窗口 COMP 参数为 `winop`

```python
win = root.create(windowCOMP, 'display')
win.par.winop = '/project1/logo_out'
win.par.winw = 1280; win.par.winh = 720
win.par.winopen.pulse()
```

### 31. 在高频调用中，`sample()` 会返回已冻结的像素数据

`out.sample(x, y)` 会从单次 Cook 快照中获取像素数据。建议通过设置 2 秒以上的延迟来采集样本，或直接对显示窗口进行截屏。

### 32. 基于音频的 GLSL：时间域处理流程

对于需要与音频同步的视觉效果，其处理流程如下：AudioFileIn → AudioSpectrum(timeslice=True, fftsize='256') → Math(gain=5) → choptoTOP(par.chop=math, layout='rowscropped') → GLSL 输入。着色器会在不同的 x 坐标处采样 `sTD2DInputs[1]`，以分别处理低频、中频和高频信号。最后可使用 MovieFileOut 功能录制时间域处理后的输出结果。

**重要注意事项：** 在开始录制之前，必须先对 AudioFileIn 设置触发信号（设置 `par.cue=True` 并调用 `par.cuepulse.pulse()`），之后再取消触发（设置 `par.cue=False` 且 `par.play=True`）。否则，在最初的几秒内，频谱数据将呈现静音状态。

### 33. twozero MCP：优先使用原生工具

**始终优先选择原生 MCP 工具，而非 td_execute_python：**
- 使用 `td_create_operator` 而非 `root.create()` 脚本（可自动处理视图窗口的定位）
- 使用 `td_set_operator_pars` 而非 `node.par.X = Y` 脚本（能自动验证参数名称的正确性）
- 使用 `td_get_par_info` 而非通过临时节点查找的方式（响应迅速且无需后续清理工作）
- 使用 `td_get_errors` 而非手动循环调用 `c.errors()` 函数
- 使用 `td_get_focus` 来获取当前操作上下文信息（旧方法中无此功能）

仅当需要处理多步骤逻辑（如节点连接链、条件构建、循环结构）时，才考虑使用 `td_execute_python`。

### 34. twozero 中 td_execute_python 的响应封装方式

twozero会为`td_execute_python`的响应添加状态信息，格式如下：`(ok)\n\n[fps 60.0/60] [0 err/0 warn]`。您的Python代码中的`result`变量值可能不会以原样出现在响应文本中。如果需要通过编程方式检查结果，请在脚本中使用`print()`语句——这些输出会显示在响应中，切勿尝试通过字符串匹配来获取`result`字典的内容。

### 35. 音频响应链：切勿使用Lag CHOP或Filter CHOP进行频谱平滑处理

Derivative的文档和教程建议在将原始FFT输出传递给着色器之前，使用Lag CHOP（lag1=0.2，lag2=0.5）对其进行平滑处理。**但这种方法不适用于“AudioSpectrum → CHOP to TOP → GLSL”这条处理链。**

问题所在：Lag CHOP以时间切片模式运行。256个样本的频谱输入会被扩展为1600至2400个样本。由于滞后平均的作用，所有数值都会被拉近至接近零的水平（约1e-06）。随后通过CHOP to TOP操作生成的纹理尺寸为2400×2，而非原有的256×2。这样一来，着色器实际接收到的音频数据几乎为零。

**正确的处理链应为：Spectrum(outlength=256) → Math(gain=10) → CHOPtoTOP → GLSL**，全程无需使用CHOP进行平滑处理。如果需要平滑效果，可在GLSL着色器中通过带有反馈纹理的时间插值来实现。

经实际音频测试验证的数值如下：
- 未使用Lag CHOP时：低频段数值为5.0-5.4，中频段数值为1.0-1.7（信号强劲，可正常使用）
- 使用Lag CHOP后：所有频段数值均为0.000001-0.00004（信号完全消失，无任何音频响应）

### 36. AudioSpectrum的输出长度：需手动设置以避免CHOP to TOP操作导致的数据溢出

在可视化模式下，若使用FFT 8192算法，AudioSpectrum默认会生成22,050个采样点（即每赫兹一个样本，范围从0到22050）。CHOP to TOP无法处理如此大量的数据，此时会出现“采样点数量超过纹理分辨率上限”的错误。

解决方案为：将`spectrum.par.outputmenu`设置为‘setmanually’，并将`spectrum.par.outlength`设为256。这样即可得到256个频率区间，足以满足可视化FFT的需求。

请勿通过将`timeslice`设为False来临时解决此问题——因为那样会一次性处理整个音频文件，从而产生更多采样点。

### 37. CHOP to TOP生成的GLSL频谱纹理为256x2，而非256x1

AudioSpectrum输出两个通道的数据（立体声：chan1和chan2）。当CHOP to TOP使用`dataformat='r'`时，会生成一个256x2的纹理——每行对应一个通道。应在该纹理的`y=0.25`位置采样第一个通道（即第一行的中间位置），而非`y=0.5`位置（即行与行之间的边界）。

```glsl
float bass = texture(sTD2DInputs[1], vec2(0.05, 0.25)).r;  // correct
float bass = texture(sTD2DInputs[1], vec2(0.05, 0.5)).r;   // WRONG — samples between rows
```

### 38. FPS显示为0并不意味着渲染过程已停止——请检查播放状态

即便渲染仍在正常进行，`TOP.save()`仍能生成有效的截图，但TD在调用`td_get_perf`时仍可能显示`fps:0`。造成这一现象的最常见原因有两大类：

**a) 项目处于暂停状态（播放条已停止）。** 可使用空格键切换TD的播放条状态。位于`/`路径下的`root`元素并不包含`.playbar`属性（该属性存在于执行COMP的节点上）。最简单的解决方法是通过`td_input_execute`发送空格键输入，不过该工具有时会出现故障。作为临时解决方案，无论播放状态如何，`TOP.save()`始终能正常工作——建议先使用它确认渲染确实正在运行，再花费时间调试FPS问题。

**b) 音频设备CHOP阻塞了主线程（最常见原因）。** 当`audiodeviceoutCHOP`的`active=True`时，其会占用300-400毫秒/帧的处理时间（占帧处理预算的2000%以上），从而导致渲染循环停滞，使FPS显示为0。**仅将音量设置为0是远远不够的**——音频驱动程序仍会被阻塞。解决方案是设置`par.active = False`，这样就能完全阻止CHOP与音频驱动程序发生交互。如果需要监控音频输出，建议仅在短暂的播放测试期间启用该功能，录制前务必将其关闭。

2026年4月验证结果：将`audiodeviceoutCHOP`的`active`属性设置为`False`后，FPS可立即从0恢复至60，帧处理预算占用率也从2348%降至0.1%。

当FPS显示为0时的诊断步骤：
1. `td_get_perf` — 检查是否有操作会导致CPU使用率/频率异常升高（通常为audiodeviceoutCHOP问题）  
2. 若audiodeviceoutCHOP的数值超过100ms/s，应立即将`par.active`设置为`False`  
3. 对输出结果调用`TOP.save()`——若能生成有效图像，则说明流程正常运行，只是无法达到实时处理速度  
4. 检查是否存在其他会导致阻塞的CHOP操作（如audiodevin等）  
5. 切换播放状态（使用空格键），或确认absTime.seconds是否在持续递增  

### 39. 在FPS为0时进行录制会生成空白或几乎为空的文件  

这是导致“我录制了30秒，却只得到2帧视频”这一问题的首要原因。当TD的处理循环陷入停滞（FPS为0或极低）时，MovieFileOut就没有任何内容可记录。与无论何种情况下都会捕获最后处理完成的帧的`TOP.save()`不同，MovieFileOut仅会写入真正被处理完成的帧。  

**在开始录制之前，请务必先确认FPS数值：**
```python
# Check via td_get_perf first
# If FPS < 30, do NOT start recording — fix the performance issue first
# If FPS=0, the playbar is likely paused — see pitfall #37
```

录制到空白视频的常见原因：
- Playbar处于暂停状态（FPS=0）——请参阅故障案例#37
- 音频设备CHOP阻塞了主线程——请参阅故障案例#37b
- 在音频信号未准备好之前就开始录制——此时音频无声，GLSL着色器输出黑色画面，MovieFileOut会记录下看似空白的黑色帧
- 在同一脚本中同时设置了`par.file`和`par.record = True`——请参阅故障案例#18

### 40. GLSL着色器生成黑色输出——在开始长时间渲染前务必进行测试

新的GLSL着色器可能会在后台静默出错（参见故障案例#7）。在录制长时镜头之前，务必先：

1. **先编写一个最简单的测试着色器**，使其仅输出纯色或透明画面：
```glsl
void main() {
    vec2 uv = vUV.st;
    fragColor = TDOutputSwizzle(vec4(uv, 0.0, 1.0));
}
```

2. 通过 `td_get_screenshot` 对 GLSL TOP 的输出结果进行查看，**确认测试渲染正确**。

3. 立即更换为真实的着色器并再次截屏。如果画面为黑色，说明该着色器存在编译错误或逻辑问题。

4. **只有确认无误后，才开始录制**。90秒的 ProRes 视频文件大小约为5GB，录制全黑画面只会浪费磁盘空间和时间。

GLSL 输出呈现黑色的常见原因：
- 在 macOS 系统上缺少 `TDOutputSwizzle()` 函数（错误编号#8）
- 时间统一变量未连接——着色器会使用默认值 0.0，导致分形图案始终停留在原点
- 颜谱纹理未连接——音频数值全部为 0.0，从而使所有内容变为黑色
- 应该进行浮点数除法却使用了整数除法（`1/2 = 0` 而非 `0.5`）
- `absTime.seconds % 1000.0` 的计算结果在超过1000后发生循环，从而导致异常数值

### 41. `td_write_dat` 函数使用的是 `text` 参数，而非 `content`

MCP 工具 `td_write_dat` 在执行完全替换操作时需要 `text` 参数。如果传入 `content` 参数，将会出现错误提示：“如需完全替换，请提供 ‘text’ 参数；如需局部修补，则需提供 ‘old_text’+‘new_text’ 参数”。

如果 `td_write_dat` 操作失败，可改用 `td_execute_python` 作为替代方案：
```python
op("/project1/shader_code").text = shader_string
```

### 42. td_execute_python 确实会返回 print() 的输出内容——可用于调试

在 `td_execute_python` 脚本中的 `print()` 语句会显示在 MCP 响应文本中。这是从脚本中读取值的正确方式。响应格式为：首先输出打印的内容，然后在单独的一行显示 `[fps X.X/X] [N err/N warn]`。

不过，`result` 变量（如果您设置了该变量）不会以原样呈现——凡是需要读取的内容，请使用 `print()` 函数来实现。
```python
# CORRECT — appears in response:
print('value:', some_value)

# WRONG — not reliably in response:
result = some_value
```

对于结构化数据，建议使用专门的检测工具（如 `td_get_operator_info` 和 `td_read_chop`），这些工具能够返回格式规范的 JSON 数据。

### 43. `td_get_operator_info` 返回的 JSON 数据后会附加 `[fps X.X/X]` 字符串——会导致 `json.loads()` 失败

`td_get_operator_info` 函数返回的文本在 JSON 对象之后会附带 `[fps 60.0/60]` 这样的字符串。这会导致 `json.loads()` 解析时出现“存在多余数据”的错误。在解析之前，请先移除该字符串。
```python
clean = response_text.rsplit('[fps', 1)[0]
data = json.loads(clean)
```

### 44. td_get_screenshot 不可靠——会返回 `{"status": "pending"}`，且可能永远无法生成截图

截图并非能立即完成。该工具会返回 `{"status": "pending", "requestId": "..."}`，实际文件可能会稍后出现，但也有可能根本不会生成。在2026年4月的测试中，即便着色器以8-30帧/秒的速度运行，截图状态仍会永久处于“待处理”状态，且磁盘上也不会有任何文件生成。

**切勿依赖 `td_get_screenshot` 进行帧捕获。** 如需可靠的帧捕获方式，请使用 MovieFileOut 录制功能结合 ffmpeg 进行帧提取：
```bash
# Record in TD first, then extract frames:
ffmpeg -y -i /tmp/td_output.mov -t 25 -vf 'fps=24' /tmp/td_frames/frame_%06d.png
```

如果需要快速进行视觉检查，可以尝试使用 `td_get_screenshot`（该方法有时有效），但务必以录制作为备用方案。该功能不提供回调或完成通知——如果5到10秒后仍未出现文件，说明数据并未传输成功。

### 45. 复杂着色器会导致渲染帧率低于录制帧率——输出文件中会出现大量重复帧

即便 `MovieFileOut` 的录制帧率为60fps，经过光线追踪的GLSL着色器可能仅能以8-15fps的速度生成画面。虽然录制功能依然可用（TD会每次写入最后渲染完成的帧），但生成的文件中会包含大量重复帧。在提取帧进行后期处理时，建议使用较低的帧率过滤选项，以避免出现冗余帧。
```bash
# Extract at 24fps from a 60fps recording of an 8fps shader:
ffmpeg -y -i /tmp/td_output.mov -t 25 -vf 'fps=24' /tmp/td_frames/frame_%06d.png
```
在开始长时间录制之前，请使用 `td_get_perf` 命令查看实际的渲染帧率。如果帧率低于 15，那么无论采用何种录制编码格式，最终输出的结果都将是幻灯片式播放。

### 46. 录制时长需手动设置——不会自动在音频结束时停止

MovieFileOut 会一直持续录制，直到设置 `par.record = False` 才会停止。如果音频在您手动停止之前就已结束，文件仍会因重复的帧而持续增大。因此，请务必在音频时长结束后立即停止录制。为确保精确控制，可在智能体端设置一个与音频时长相匹配的计时器，随后发送 `par.record = False` 的指令。作为最后保障，还可使用 ffmpeg 工具对多余的帧进行裁剪处理：
```bash
ffmpeg -i raw.mov -t 25 -c copy trimmed.mov
```

### 47. 顺序播放模式下，AudioFileIn的par.index值始终为0——并非可靠的进度指示器

当`audiofileinCHOP`处于`playmode=2`（顺序播放）状态时，即便音频正在播放且频谱数据仍在持续传输，`par.index.eval()`返回的值仍为0.0。因此，请勿在顺序播放模式下使用`par.index`来检测播放进度。

**如何确认音频确实在播放：**
- 通过`td_read_chop`读取频谱CHOP值——如果数值非零且在不同时间点（间隔1-2秒）有所变化，说明音频正在传输
- 直接读取音频CHOP数据：非零的波形样本可证明文件已加载并正在播放
- 虽然`par.play.eval()`返回True是必要条件，但并非充分条件——如果播放指令卡住，该值也可能为True，而实际上并无音频在播放

### 48. GLSL着色器过亮问题——需在着色器中对音频频谱值进行限制

原始频谱值经过Math CHOP增益处理后可能会产生极大的数值（5-20以上），从而导致着色器的光照效果过度增强，出现纯白或纯灰的视觉效果。因此，着色器必须对音频输入值进行限制：

```glsl
float bass = texture(sTD2DInputs[1], vec2(0.05, 0.25)).r;
bass = clamp(bass, 0.0, 3.0);   // prevent whiteout
mids = clamp(mids, 0.0, 3.0);
hi = clamp(hi, 0.0, 3.0);
```

在安静段落中，当增益设置为10时，输出亮度约为0.13（过暗），而增益设置为50时则约为9.4（完全过曝）。解决方案：保持增益为10，在AudioSpectrum中启用`highfreqboost=3.0`参数，并在着色器中进行亮度限制。

### 49. 1280x1280正方形分辨率下的非商业用途TD记录——必须进行后期裁剪

即便在GLSL TOP中设置了`resolutionw=1280, resolutionh=720`，非商业用途TD功能仍可能将输出分辨率设为1280x1280并保存到MovieFileOut中。因此务必使用ffprobe检查文件尺寸，并在提取过程中进行相应裁剪。

```bash
# Center-crop from 1280x1280 to 1280x720:
ffmpeg -y -i /tmp/td_output.mov -t 25 -r 24 -vf "crop=1280:720:0:280" /tmp/frames/frame_%06d.png
```

大小为1-2GB、分辨率为1280x1280的大型ProRes文件在解码时的速度约为3帧/秒，因此提取25秒的视频素材大约需要3分钟时间。

## 高级模式（问题51及以后）

### 51. 连接语法：应使用`outputConnectors`/`inputConnectors`，而非`outputs`/`inputs`

```python
# CORRECT
src.outputConnectors[0].connect(dst.inputConnectors[0])
# WRONG — raises IndexError or AttributeError
src.outputs[0].connect(dst.inputs[0])
```

如需提交反馈，必须同时提供TOP和BOTH信息。
```python
fb.par.top = target.path
target.outputConnectors[0].connect(fb.inputConnectors[0])
```

### 52. 在 TD 2025.32460 版本中，`moviefileoutTOP `par.input` 无法通过 Python 解析

尝试通过编程方式设置 `moviefileoutTOP.par.input` 是无效的。所有操作都会以“未指定足够的源文件”这一错误信息无声失败。

**临时解决方案——帧捕获 + ffmpeg：**
```python
out = op('/project1/out')
for i in range(300):
    delay = i * 5
    run(f"op('/project1/out').save('/tmp/frames/f_{i:04d}.png')", delayFrames=delay)
# Then: ffmpeg -y -framerate 30 -i /tmp/frames/f_%04d.png -c:v prores -pix_fmt yuv420p /tmp/output.mov
```

### 53. 批量帧捕获——使用 `me.fetch`/`me.store` 实现跨调用间的状态保持

```python
start = me.fetch('cap_frame', 0)
for i in range(60):
    frame = start + i
    op('/project1/out').save(f'/tmp/frames/frame_{str(frame).zfill(4)}.png')
me.store('cap_frame', start + 60)
```
调用5次即可生成300帧图像，每次调用都会从上一次停止的位置继续处理。  

### 54. TD 2025中GLSL TOP像素着色器的要求  

需完整处理所有输入数据，不得提前终止。

```glsl
// REQUIRED — declare output
layout(location = 0) out vec4 fragColor;

void main() {
    vec3 col = vec3(1.0, 0.0, 0.0);
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
```
**可用内置统一变量：** `uTDOutputInfo.res`（vec4类型）、`uTDTimeInfo.seconds`、`sTD2DInputs[N]`。  
**自动生成的DAT文件：** 包含示例代码的`name_pixel`、`name_vertex`、`name_compute`类型文本DAT文件。  

### 55. TOP.save()不会推进时间——导致循环中出现重复帧  
`.save()`会捕获当前已处理完成的帧，而不会推动TD的时间轴前进：
```python
# WRONG — all frames identical
for i in range(300):
    op('/project1/out').save(f'frames/f_{i:04d}.png')

# CORRECT — use run() with delayFrames
for i in range(300):
    delay = i * 5
    run(f"op('/project1/out').save('frames/f_{i:04d}.png')", delayFrames=delay)
```
**在 TD 中绝不可使用 `time.sleep()`**——该操作会阻塞主线程，从而导致界面冻结。

### 56. 反馈循环会掩盖输入变化——在捕获过程中强制切换

当反馈效果的透明度超过 0.7 时，缓冲区内容会占据主导地位。此时进行输入操作所产生的帧几乎完全一致。

**解决方案——在每次捕获时强制指定切换索引：**
```python
for i in range(300):
    idx = (i // 8) % num_inputs
    delay = i * 5
    run(f"op('/project1/vswitch').par.index={idx}; op('/project1/out').save('f_{i:04d}.png')", delayFrames=delay)
```

### 57. 大型的 td_execute_python 脚本执行失败——需拆分为多次调用

单个脚本中创建 10 个以上的操作符会导致时间相关问题。建议将其拆分为 2–4 次调用，每次调用处理 2–4 个操作符。在单次调用中，`create()` 会立即处理相关任务；而在多次调用之间，如果前一次调用尚未完成提交，`op('name')` 可能会返回 `None`。

### 58. 调用 project.load() 后的 MCP 实例重新连接

`project.load(path)` 会改变进程 ID。加载完成后，应调用 `td_list_instances()` 并使用新的 `target_instance`。对于 TOX 文件，则建议以子组件的形式导入（这样不会导致连接断开）。

### 59. TOX 反向工程工作流程

```python
comp = root.loadTox(r'/path/to/file.tox')
comp.name = '_study_comp'
for child in comp.children:
    print(f'{child.name} ({child.OPType})')
# Use td_get_operators_info, td_read_dat, check custom params
```

### 60. sliderCOMP 的命名规则——TD 会添加后缀  
TD 会自动将名称重命名为：`slider_brightness` → `slider_brightness1`。请务必在创建后检查其名称。  

### 61. create() 函数要求使用完整的操作符类型后缀

```python
# CORRECT
proj.create('audiofileinCHOP', 'audio_in')
proj.create('glslTOP', 'render')

# WRONG — raises "Unknown operator type"
proj.create('audiofilein', 'audio_in')
proj.create('glsl', 'render')
```

### 62. 重新设置COMP的父对象——请使用copyOPs而非connect()函数

通过`inputCOMPConnectors[0].connect()`来移动COMP是行不通的。应采用复制后删除的方法：
```python
copied = target.copyOPs([source])  # preserves internal wiring
source.destroy()
# Re-wire external connections manually after the move
```

### 63. 滑块接线问题——使用含 op() 表达式的 expressionCHOP 功能会导致 TD 程序崩溃

```python
# CRASHES TD — don't do this
echop = root.create(expressionCHOP, 'slider_ctrl')
echop.par.chan0expr = 'op("/project1/controls/slider_brightness1").par.value0'

# WORKING — parameterCHOP as bridge
pchop = root.create(parameterCHOP, 'slider_vals')
pchop.par.ops = '/project1/controls'
pchop.par.parameters = 'value0'
pchop.par.custom = True
pchop.par.builtin = False
```