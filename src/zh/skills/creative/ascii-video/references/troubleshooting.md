# 故障排查参考

> **另请参阅：** composition.md · architecture.md · shaders.md · scenes.md · optimization.md

## 快速诊断

| 症状 | 可能原因 | 解决方案 |
|---------|-----------|----------|
| 全屏黑色输出 | 亮度映射的伽马值过高或未渲染任何效果 | 将伽马值降至 0.5，并检查 scene_fn 是否返回非零尺寸的画布 |
| 颜色过淡/过亮 | 使用了线性亮度倍增器而非亮度映射 | 将 `canvas * N` 替换为 `tonemap(canvas, gamma=0.75)` |
| ffmpeg 在渲染过程中卡住 | stderr=subprocess.PIPE 导致的死锁 | 将 stderr 重定向到文件中 |
| “只读”数组错误 | 未使用 `.copy()` 即直接进行广播传输 | 在 broadcast_to 之后添加 `.copy()` |
| PicklingError 错误 | SCENES 表中包含 Lambda 函数或闭包 | 所有 fx_* 函数都应在模块级别定义 |
| 输出中出现随机黑洞 | 字体缺少 Unicode 图形 | 在初始化时验证颜色调色板 |
| 视频与音频不同步 | 帧定时累积问题 | 使用整数帧计数器，每帧重新计算时间值 |
| 输出为单色平铺效果 | 色相字段的形状不匹配 | 在执行 hsv2rgb 操作前，确保 h、s、v 数组的行数和列数一致 |
| 背景复杂时文字无法辨认 | 文字与背景对比度不足 | 使用 `apply_text_backdrop()`（来自 composition.md）以及 `reverse_vignette` 着色器（来自 shaders.md） |
| 文字显示混乱/反相 | 对包含可读文字的场景应用了万花筒或镜像着色器 | **切勿对需要可读文字的场景应用万花筒、mirror_h/v/quad/diag 等着色器**——这类效果会破坏文字的可读性。此类着色器仅适用于背景层或无文字的场景 |

ASCII 视频开发过程中常见的错误、陷阱以及特定平台相关的问题。

## NumPy 广播机制

### `broadcast_to().copy()` 的隐患

色相字段生成器通常会返回广播视图形式的数组——其形状为 `(1, cols)` 或 `(rows, 1)`，NumPy 会将其广播为 `(rows, cols)`。这类视图是**只读的**。如果后续代码试图直接修改它们（例如 `h %= 1.0`），NumPy 将会抛出错误：

```
ValueError: output array is read-only
```

**修复方案**：在调用 `broadcast_to()` 后务必使用 `.copy()` 方法。

```python
h = np.broadcast_to(h, (g.rows, g.cols)).copy()
```

在 `_render_vf()` 函数中，这一点尤为重要，因为色调数组会经过 `hsv2rgb()` 处理。

### `+=` 与 `+` 的陷阱

当操作数的形状不完全匹配时，使用就地运算符进行广播也会失败：

```python
# FAILS if result is (rows,1) and operand is (rows, cols)
val += np.sin(g.cc * 0.02 + t * 0.3) * 0.5

# WORKS — creates a new array
val = val + np.sin(g.cc * 0.02 + t * 0.3) * 0.5
```

`vf_plasma()`函数存在此缺陷。在混合不同形状的数组时，应使用`+`而非`+=`。

### `hsv2rgb()`中的形状不匹配问题

`hsv2rgb(h, s, v)`要求三个输入数组的形状完全一致。如果`h`的形状为`(1, cols)`，而`s`的形状为`(rows, cols)`，则该函数会崩溃或产生错误结果。

**解决方案**：在调用该函数之前，确保所有输入数据都经过广播处理并转换为`(rows, cols)`形状。

---

## 混合模式常见陷阱

### Overlay模式会使深色图像过暗

当`a < 0.5`时，`overlay(a, b) = 2*a*b`。两个值为0.12的输入，计算结果为`2 * 0.12 * 0.12 = 0.03`，此结果比任意一个输入值都更暗。

**影响**：由于ASCII艺术图像通常都是深色的，使用Overlay模式会导致输出接近纯黑。

**解决方案**：对于深色源图像，应使用Screen模式。Screen模式始终能提升亮度，其计算公式为`1 - (1-a)*(1-b)`。

### Colordodge模式存在除零错误

`colordodge(a, b) = a / (1 - b)`。当`b = 1.0`（即纯白色像素）时，该公式会出现除零错误。

**解决方案**：加入极小值修正项：`a / (1 - b + 1e-6)`。`BLEND_MODES`中的实现也应包含这一处理。

### Colorburn模式存在除零错误

`colorburn(a, b) = 1 - (1-a) / b`。当`b = 0`（即纯黑色像素）时，该公式也会出现除零错误。

**解决方案**：加入极小值修正项：`1 - (1-a) / (b + 1e-6)`。

### Multiply模式始终使图像变暗

`multiply(a, b) = a * b`。由于两个操作数的取值范围都在[0,1]之间，因此计算结果始终小于或等于`min(a,b)`。切勿将Multiply模式用于反馈效果——否则画面会在几帧内变为纯黑。

**解决方案**：对于反馈效果，应使用Screen模式，或使用透明度较低的Add模式。

---

## 多进程处理

### pickle序列化的限制

`ProcessPoolExecutor`通过pickle机制对函数参数进行序列化，这限制了可传递给工作进程的参数类型：

| 可被序列化 | 无法被序列化 |
|-----------|---------------|
| 模块级函数（`def fx_foo():`） | Lambda表达式（`lambda x: x + 1`） |
| 字典、列表、numpy数组 | 回调函数（在函数内部定义的函数） |
| 具有`__reduce__`方法的类实例 | 实例方法 |
| 字符串、数字 | 文件句柄、套接字 |

**影响**：SCENES表中引用的所有场景函数都必须以模块级函数的形式定义，即使用`def`关键字。如果使用Lambda表达式或回调函数，则会导致问题。

```
_pickle.PicklingError: Can't pickle <function <lambda> at 0x...>
```

**解决方案**：将所有场景函数定义在模块的顶层。在 `_render_vf()` 函数中作为 `val_fn/hue_fn` 使用的 Lambda 表达式是可行的，因为它们会在工作进程内部执行——不会被序列化并跨进程传递。

### macOS 的 `spawn` 模式与 Linux 的 `fork` 模式

在 macOS 上，`multiprocessing` 模块默认使用 `spawn` 模式（完全序列化）。而在 Linux 上则默认使用 `fork` 模式（写时复制）。这意味着：

- **macOS**：每个工作进程都会对特征数组进行独立序列化处理（30秒的视频大约需要57KB内存，且随视频时长增加而增长）。每个工作进程都需要重新导入整个模块。
- **Linux**：特征数组通过写时复制机制实现共享，各工作进程可继承父进程的内存。

**影响**：在 macOS 上，模块级的代码（如 `detect_hardware()`）会在每个工作进程中执行。如果这些代码存在副作用（例如调用子进程），则相应操作会重复执行 N+1 次。

### 工作进程间的状态隔离

每个工作进程都会创建属于自己的：
- `Renderer` 实例（带有全新的网格缓存）
- `FeedbackBuffer`（反馈信息不会跨场景传递）
- 随机种子（通过 `random.seed(hash(seg_id) + 42)` 生成）

这意味着：
- 粒子状态不会在不同场景之间保留（符合预期）
- 场景切换时反馈轨迹会重置（符合预期）
- `np.random` 的状态并不会由 `random.seed()` 控制——二者使用独立的随机数生成器

**实现确定性噪声的解决方案**：显式使用 `np.random.RandomState(seed)`：

```python
rng = np.random.RandomState(hash(seg_id) + 42)
noise = rng.random((rows, cols))
```

## 亮度问题

### 应用色调映射后场景仍过暗

如果应用色调映射后场景依然偏暗，请检查以下原因：

1. **伽马值过高**：对于需要经过破坏性后期处理的场景，应降低伽马值（0.5-0.6）。
2. **着色器导致亮度损失**：着色器链中的阳光化、贴图化或对比度调整功能可能会抵消色调映射的效果。建议将这类具有破坏性的着色器置于处理流程的更早阶段，或提高伽马值以进行补偿。
3. **乘法混合模式带来的负面影响**：乘法混合模式会导致每一帧画面都变暗，请改用屏幕混合模式或加法混合模式。
4. **场景中使用了叠加混合模式**：如果场景函数使用了带有深色图层的 `blend_canvas(..., "overlay", ...)` 参数，应将其更改为屏幕混合模式。

### 诊断方法：测试帧亮度检测

```bash
python reel.py --test-frame 10.0
# Output: Mean brightness: 44.3, max: 255
```

如果均值小于20，说明该场景需要处理。常见解决方案包括：
- 降低SCENES设置中的伽马值
- 将内部混合模式从“叠加/正片叠底”更改为“屏幕/相加”
- 提高数值字段的乘数（例如：`vf_plasma(...) * 1.5`）
- 检查着色器链中是否存在过强的阳光效果或阈值设置

### v1亮度模式（已废弃）

旧版本的模式采用线性乘数机制：

```python
# OLD — don't use
canvas = np.clip(canvas.astype(np.float32) * 2.0, 0, 255).astype(np.uint8)
```

此操作失败的原因如下：
- 暗场景（平均值 8）：`8 * 2.0 = 16` —— 仍然偏暗
- 亮场景（平均值 130）：`130 * 2.0 = 255` —— 值被截断，细节丢失

建议改用 `tonemap()` 函数。详情请参阅 `composition.md` 中的“自适应色调映射”部分。

---

## ffmpeg 相关问题

### 管道死锁

这是生产环境中最常见的问题。如果您使用了 `stderr=subprocess.PIPE`：

```python
# DEADLOCK — stderr buffer fills at 64KB, blocks ffmpeg, blocks your writes
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
```

**修复方案**：始终将标准错误流重定向到文件中：

```python
stderr_fh = open(err_path, "w")
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL, stderr=stderr_fh)
```

### 帧数不匹配问题

如果写入管道的帧数与 ffmpeg 根据 `-r` 参数及时长所预期的数值不一致，输出内容可能会出现以下问题：
- 末尾缺少帧
- 时长不正确
- 音视频不同步

**解决方案**：手动计算帧数，公式为 `n_frames = int(duration * FPS)`。在未确认总帧数匹配之前，切勿直接使用 `range(int(start*FPS), int(end*FPS))` 这类方法。

```
[concat @ ...] Unsafe file name
```

**修复方案**：始终使用 `-safe 0` 参数。
```python
["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_path, ...]
```

## 字体相关问题

### 单元格高度（macOS Pillow）

在某些版本的 macOS Pillow 中，`textbbox()` 和 `getbbox()` 函数返回的高度值不正确。建议使用 `getmetrics()` 函数：

```python
ascent, descent = font.getmetrics()
cell_height = ascent + descent  # correct
# NOT: font.getbbox("M")[3]  # wrong on some versions
```

### 缺失的 Unicode 字形

并非所有字体都能显示所有的 Unicode 字符。如果某字符不在该字体中，其字形将会显示为空白或“豆腐块”，在输出结果中呈现为黑色空洞。

**解决方案**：在初始化时进行验证：

```python
all_chars = set()
for pal in [PAL_DEFAULT, PAL_DENSE, PAL_RUNE, ...]:
    all_chars.update(pal)

valid_chars = set()
for c in all_chars:
    if c == " ":
        valid_chars.add(c)
        continue
    img = Image.new("L", (20, 20), 0)
    ImageDraw.Draw(img).text((0, 0), c, fill=255, font=font)
    if np.array(img).max() > 0:
        valid_chars.add(c)
    else:
        log(f"WARNING: '{c}' (U+{ord(c):04X}) missing from font")
```

### 平台字体路径

| 平台 | 常见路径 |
|------|----------|
| macOS | `/System/Library/Fonts/Menlo.ttc`, `/System/Library/Fonts/Monaco.ttf` |
| Linux | `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf` |
| Windows | `C:\Windows\Fonts\consola.ttf`（Consolas字体） |

建议始终检测多个路径，并在无法找到对应字体时优雅地降级处理。详情请参阅 `architecture.md` 中的“字体选择”部分。

---

## 性能优化

### 性能低下的着色器

某些着色器使用了 Python 循环，在 1080p 分辨率下运行速度极慢：

| 着色器 | 问题 | 解决方案 |
|------|------|----------|
| `wave_distort` | 每行都存在 Python 循环 | 改用向量化的高级索引方式 |
| `halftone` | 存在三层嵌套循环 | 通过分块处理实现向量化 |
| `matrix rain` | 每列每条轨迹都有循环 | 累积索引数组后批量赋值 |

### 渲染时间调整

如果渲染耗时远超预期：
1. 检查网格数量——每增加一个网格，初始化阶段大约会增加 100-150 毫秒/帧
2. 检查粒子数量——将其控制在与质量要求相匹配的范围内
3. 检查着色器数量——每个着色器大约会增加 2-25 毫秒的渲染时间
4. 检查效果代码中是否存在意外的 Python 循环（应仅使用 numpy 库）

---

## 常见错误

### 使用 `r.S` 与直接使用 `S` 参数

v2 场景协议会将 `S`（即状态字典）作为独立参数传递。但实际上 `S` 就是 `r.S`——二者指的是同一个对象。两种用法均可正常工作：

```python
def fx_scene(r, f, t, S):
    S["counter"] = S.get("counter", 0) + 1   # via parameter (preferred)
    r.S["counter"] = r.S.get("counter", 0) + 1  # via renderer (also works)
```

为提高可读性，建议使用 `S` 参数。通过明确指定该参数，可以清晰地表明该函数具有持久状态。

### 忘记处理空特征值的问题

当音频处于静音状态时，其音频特征值默认为 0.0。此时应使用带有合理默认值的 `.get()` 方法：

```python
energy = f.get("bass", 0.3)  # default to 0.3, not 0
```

若将该值设置为默认的 0，则在静音期间效果将显示为空白。

### 创建新文件而非编辑现有状态

粒子系统中的一个常见缺陷：每帧都创建新的数组，而非更新持久化状态。

```python
# WRONG — particles reset every frame
S["px"] = []
for _ in range(100):
    S["px"].append(random.random())

# RIGHT — only initialize once, update each frame
if "px" not in S:
    S["px"] = []
# ... emit new particles based on beats
# ... update existing particles
```

### 避免截断数值字段

数值字段的值应处于 [0, 1] 范围内。若超出此范围，`val2char()` 函数将会引发索引错误：

```python
# WRONG — vf_plasma() * 1.5 can exceed 1.0
val = vf_plasma(g, f, t, S) * 1.5

# RIGHT — clip after scaling
val = np.clip(vf_plasma(g, f, t, S) * 1.5, 0, 1)
```

 `_render_vf()` 辅助函数会自动进行裁剪处理，但如果您正在构建自定义场景，则需要手动执行裁剪操作。

## 亮度优化最佳实践

- 对于密集的动画背景——切勿使用纯黑色，而应确保填满整个网格
- 暗角效果的最小值应设置为 0.15（而非 0.12）
- 荧光效果阈值设定为 130（而非 170），这样更多像素能够参与发光效果
- 对于深色 ASCII 图层，应使用 `screen` 混合模式（而非 `overlay`）——因为 `overlay` 模式会使得深色区域的数值变为：`2 * 0.12 * 0.12 = 0.03`
- FeedbackBuffer 的衰减最小值应为 0.5——若低于此值，反馈效果会消失得过快而无法观察
- 值字段的下限应设置为 `vf * 0.8 + 0.05`，这样才能确保没有单元格的数值真正为零
- 不同场景可自定义伽马值：默认值为 0.75，日晒效果为 0.55，贴图效果为 0.50，明亮场景则为 0.85
- 尽早进行帧测试：在开始完整渲染之前，先在关键时间点渲染单帧图像进行验证

**完整渲染前的快速检查清单：**
1. 渲染 3 帧测试图像（起始帧、中间帧和结束帧）
2. 检查经过色调映射处理后的 `canvas.mean()` 值是否大于 8
3. 确保没有场景呈现为纯黑色
4. 验证各部分之间的差异性（每个场景的背景、调色板及颜色均应不同）
5. 确认着色器链中已包含荧光效果处理（阈值设为 130）
6. 确认暗角强度不超过 0.25
