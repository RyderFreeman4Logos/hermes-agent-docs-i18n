# 优化参考指南

> **另请参阅：** architecture.md · composition.md · scenes.md · shaders.md · inputs.md · troubleshooting.md

## 硬件检测

在脚本启动时检测用户的硬件配置，并自动调整渲染参数。切勿直接硬编码工作线程数量或分辨率。

### CPU与内存检测

```python
import multiprocessing
import platform
import shutil
import os

def detect_hardware():
    """Detect hardware capabilities and return render config."""
    cpu_count = multiprocessing.cpu_count()
    
    # Leave 1-2 cores free for OS + ffmpeg encoding
    if cpu_count >= 16:
        workers = cpu_count - 2
    elif cpu_count >= 8:
        workers = cpu_count - 1
    elif cpu_count >= 4:
        workers = cpu_count - 1
    else:
        workers = max(1, cpu_count)
    
    # Memory detection (platform-specific)
    try:
        if platform.system() == "Darwin":
            import subprocess
            mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
        elif platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        mem_bytes = int(line.split()[1]) * 1024
                        break
        else:
            mem_bytes = 8 * 1024**3  # assume 8GB on unknown
    except Exception:
        mem_bytes = 8 * 1024**3

    mem_gb = mem_bytes / (1024**3)
    
    # Each worker uses ~50-150MB depending on grid sizes
    # Cap workers if memory is tight
    mem_per_worker_mb = 150
    max_workers_by_mem = int(mem_gb * 1024 * 0.6 / mem_per_worker_mb)  # use 60% of RAM
    workers = min(workers, max_workers_by_mem)
    
    # ffmpeg availability and codec support
    has_ffmpeg = shutil.which("ffmpeg") is not None
    
    return {
        "cpu_count": cpu_count,
        "workers": workers,
        "mem_gb": mem_gb,
        "platform": platform.system(),
        "arch": platform.machine(),
        "has_ffmpeg": has_ffmpeg,
    }
```

### 自适应质量配置文件

根据硬件性能动态调整分辨率、帧率、CRF值以及网格密度：

```python
def quality_profile(hw, target_duration_s, user_preference="auto"):
    """
    Returns render settings adapted to hardware.
    user_preference: "auto", "draft", "preview", "production", "max"
    """
    if user_preference == "draft":
        return {"vw": 960, "vh": 540, "fps": 12, "crf": 28, "workers": min(4, hw["workers"]),
                "grid_scale": 0.5, "shaders": "minimal", "particles_max": 200}
    
    if user_preference == "preview":
        return {"vw": 1280, "vh": 720, "fps": 15, "crf": 25, "workers": hw["workers"],
                "grid_scale": 0.75, "shaders": "standard", "particles_max": 500}
    
    if user_preference == "max":
        return {"vw": 3840, "vh": 2160, "fps": 30, "crf": 15, "workers": hw["workers"],
                "grid_scale": 2.0, "shaders": "full", "particles_max": 3000}
    
    # "production" or "auto"
    # Auto-detect: estimate render time, downgrade if it would take too long
    n_frames = int(target_duration_s * 24)
    est_seconds_per_frame = 0.18  # ~180ms at 1080p
    est_total_s = n_frames * est_seconds_per_frame / max(1, hw["workers"])
    
    if hw["mem_gb"] < 4 or hw["cpu_count"] <= 2:
        # Low-end: 720p, 15fps
        return {"vw": 1280, "vh": 720, "fps": 15, "crf": 23, "workers": hw["workers"],
                "grid_scale": 0.75, "shaders": "standard", "particles_max": 500}
    
    if est_total_s > 3600:  # would take over an hour
        # Downgrade to 720p to speed up
        return {"vw": 1280, "vh": 720, "fps": 24, "crf": 20, "workers": hw["workers"],
                "grid_scale": 0.75, "shaders": "standard", "particles_max": 800}
    
    # Standard production: 1080p 24fps
    return {"vw": 1920, "vh": 1080, "fps": 24, "crf": 20, "workers": hw["workers"],
            "grid_scale": 1.0, "shaders": "full", "particles_max": 1200}


def apply_quality_profile(profile):
    """Set globals from quality profile."""
    global VW, VH, FPS, N_WORKERS
    VW = profile["vw"]
    VH = profile["vh"]
    FPS = profile["fps"]
    N_WORKERS = profile["workers"]
    # Grid sizes scale with resolution
    # CRF passed to ffmpeg encoder
    # Shader set determines which post-processing is active
```

### CLI集成

```python
parser = argparse.ArgumentParser()
parser.add_argument("--quality", choices=["draft", "preview", "production", "max", "auto"],
                    default="auto", help="Render quality preset")
parser.add_argument("--aspect", choices=["landscape", "portrait", "square"],
                    default="landscape", help="Aspect ratio preset")
parser.add_argument("--workers", type=int, default=0, help="Override worker count (0=auto)")
parser.add_argument("--resolution", type=str, default="", help="Override resolution e.g. 1280x720")
args = parser.parse_args()

hw = detect_hardware()
if args.workers > 0:
    hw["workers"] = args.workers
profile = quality_profile(hw, target_duration, args.quality)

# Apply aspect ratio preset (before manual resolution override)
ASPECT_PRESETS = {
    "landscape": (1920, 1080),
    "portrait":  (1080, 1920),
    "square":    (1080, 1080),
}
if args.aspect != "landscape" and not args.resolution:
    profile["vw"], profile["vh"] = ASPECT_PRESETS[args.aspect]

if args.resolution:
    w, h = args.resolution.split("x")
    profile["vw"], profile["vh"] = int(w), int(h)
apply_quality_profile(profile)

log(f"Hardware: {hw['cpu_count']} cores, {hw['mem_gb']:.1f}GB RAM, {hw['platform']}")
log(f"Render:   {profile['vw']}x{profile['vh']} @{profile['fps']}fps, "
    f"CRF {profile['crf']}, {profile['workers']} workers")
```

### 竖屏模式注意事项

竖屏分辨率（1080x1920）的像素数与横屏1080p相同，因此性能表现相当。但构图方式存在差异：

| 考量因素 | 横屏 | 竖屏 |
|---------|-----------|----------|
| `lg`尺寸下的网格列数 | 160 | 90 |
| `lg`尺寸下的网格行数 | 45 | 80 |
| 文本行最大字符数 | 居中显示约50个字符 | 居中显示约25-30个字符 |
| 垂直雨滴效果 | 移动距离较短 | 移动距离较长，更具视觉冲击力 |
| 水平光谱效果 | 覆盖整个宽度 | 需要旋转或压缩才能完整显示 |
| 径向效果 | 形成自然圆形 | 形成高椭圆状（可通过纵横比校正功能解决） |
| 粒子爆炸效果 | 扩散范围较广 | 扩散方向更垂直 |
| 文本堆叠数量 | 3-4行较为合适 | 8-10行较为合适 |
| 引用文本布局 | 2-3行宽文本 | 5-6行短文本 |

**针对竖屏优化的构图方案：**
- 垂直雨滴/矩阵效果会得到自然强化——粒子移动距离更长
- 火焰柱能占据更多屏幕空间向上延伸
- 上升的余烬/粒子有更长的垂直移动路径
- 文本可以更密集地堆叠更多行数
- 若应用纵横比校正功能，径向效果也能正常呈现（GridLayer可自动处理此功能）
- 光谱条可旋转90度（从底部开始显示垂直条）

**竖屏文本布局建议：**
```python
def layout_text_portrait(text, max_chars_per_line=25, grid=None):
    """Break text into short lines for portrait display."""
    words = text.split()
    lines = []; current = ""
    for w in words:
        if len(current) + len(w) + 1 > max_chars_per_line:
            lines.append(current.strip())
            current = w + " "
        else:
            current += w + " "
    if current.strip():
        lines.append(current.strip())
    return lines
```

## 性能预算

目标值：每帧100-200毫秒（单线程模式下为5-10帧/秒，8个工作进程并行时为40-80帧/秒）。

| 组件 | 耗时 | 备注 |
|-----------|------|------|
| 特征提取 | 1-5毫秒 | 在渲染前为所有帧预先计算 |
| 效果函数处理 | 2-15毫秒 | 使用向量化numpy运算，避免Python循环 |
| 字符渲染 | 80-150毫秒 | **性能瓶颈**——依赖逐单元的Python循环 |
| 着色器管线 | 5-25毫秒 | 取决于当前启用的着色器数量 |
| ffmpeg编码 | 约5毫秒 | 通过管道缓冲实现耗时均摊 |

## 图像预光栅化

在初始化时对所有字符进行一次光栅化处理，而非每帧都重新处理：

```python
# At init time -- done once
for c in all_characters:
    img = Image.new("L", (cell_w, cell_h), 0)
    ImageDraw.Draw(img).text((0, 0), c, fill=255, font=font)
    bitmaps[c] = np.array(img, dtype=np.float32) / 255.0  # float32 for fast multiply

# At render time -- fast lookup
bitmap = bitmaps[char]
canvas[y:y+ch, x:x+cw] = np.maximum(canvas[y:y+ch, x:x+cw],
                                      (bitmap[:,:,None] * color).astype(np.uint8))
```

将所有调色板中的字符以及叠加的文本全部收集到初始集合中，对于缺失的字符则采用延迟加载机制。

## 预渲染背景纹理

适用于那些字符无需每帧变化的背景场景，可作为 `_render_vf()` 的替代方案。在初始化阶段一次性预烘焙出静态的 ASCII 纹理，随后在每一帧通过单元格颜色场对其进行叠加处理。这种方式仅需一次矩阵乘法运算，而非数千次位图绘制操作。

适用场景：背景层使用固定的字符调色板，且仅颜色或亮度会随帧变化。不适用于字符选择需依据动态变化值字段来确定的层。

### 初始化步骤：烘焙纹理

```python
# In GridLayer.__init__:
self._bg_row_idx = np.clip(
    (np.arange(VH) - self.oy) // self.ch, 0, self.rows - 1
)
self._bg_col_idx = np.clip(
    (np.arange(VW) - self.ox) // self.cw, 0, self.cols - 1
)
self._bg_textures = {}

def make_bg_texture(self, palette):
    """Pre-render a static ASCII texture (grayscale float32) once."""
    if palette not in self._bg_textures:
        texture = np.zeros((VH, VW), dtype=np.float32)
        rng = random.Random(12345)
        ch_list = [c for c in palette if c != " " and c in self.bm]
        if not ch_list:
            ch_list = list(self.bm.keys())[:5]
        for row in range(self.rows):
            y = self.oy + row * self.ch
            if y + self.ch > VH:
                break
            for col in range(self.cols):
                x = self.ox + col * self.cw
                if x + self.cw > VW:
                    break
                bm = self.bm[rng.choice(ch_list)]
                texture[y:y+self.ch, x:x+self.cw] = bm
        self._bg_textures[palette] = texture
    return self._bg_textures[palette]
```

### 渲染功能：色场效果与缓存纹理

```python
def render_bg(self, color_field, palette=PAL_CIRCUIT):
    """Fast background: pre-rendered ASCII texture * per-cell color field.
    color_field: (rows, cols, 3) uint8. Returns (VH, VW, 3) uint8."""
    texture = self.make_bg_texture(palette)
    # Expand cell colors to pixel coords via pre-computed index maps
    color_px = color_field[
        self._bg_row_idx[:, None], self._bg_col_idx[None, :]
    ].astype(np.float32)
    return (texture[:, :, None] * color_px).astype(np.uint8)
```

### 在场景中的使用方式

```python
# Build per-cell color from effect fields (cheap — rows*cols, not VH*VW)
hue = ((t * 0.05 + val * 0.2) % 1.0).astype(np.float32)
R, G, B = hsv2rgb(hue, np.full_like(val, 0.5), val)
color_field = mkc(R, G, B, g.rows, g.cols)  # (rows, cols, 3) uint8

# Render background — single matrix multiply, no per-cell loop
canvas_bg = g.render_bg(color_field, PAL_DENSE)
```

纹理初始化循环仅执行一次，并会为每个调色板缓存结果。每帧的处理成本仅为一次高级索引查找以及一次广播乘法运算——相较于`render()`函数中用于处理密集背景的逐像素位图拷贝循环，其速度快了多个数量级。

## 坐标数组缓存

应在初始化阶段预先计算所有基于网格的坐标数组，而非在每帧中重复计算：

```python
# These are O(rows*cols) and used in every effect
self.rr = np.arange(rows)[:, None]    # row indices
self.cc = np.arange(cols)[None, :]    # col indices
self.dist = np.sqrt(dx**2 + dy**2)   # distance from center
self.angle = np.arctan2(dy, dx)       # angle from center
self.dist_n = ...                      # normalized distance
```

## 向量化效果模式

### 避免在效果处理中使用逐单元格的 Python 循环

渲染循环（位图合成）本质上属于逐单元格操作，这是不可避免的。但效果函数必须完全基于向量化 numpy 实现——绝不能使用 Python 语言对行或列进行遍历。

错误的（O(rows*cols) 时间复杂度的 Python 循环）：
```python
for r in range(rows):
    for c in range(cols):
        val[r, c] = math.sin(c * 0.1 + t) * math.cos(r * 0.1 - t)
```

良好（已向量化）：
```python
val = np.sin(g.cc * 0.1 + t) * np.cos(g.rr * 0.1 - t)
```

### 向量化矩阵雨效果

那种逐列、逐轨迹像素的简单循环，是仅次于渲染循环的第二大性能瓶颈。建议使用 NumPy 的高级索引功能来解决这一问题：

```python
# Instead of nested Python loops over columns and trail pixels:
# Build row index arrays for all active trail pixels at once
all_rows = []
all_cols = []
all_fades = []
for c in range(cols):
    head = int(S["ry"][c])
    trail_len = S["rln"][c]
    for i in range(trail_len):
        row = head - i
        if 0 <= row < rows:
            all_rows.append(row)
            all_cols.append(c)
            all_fades.append(1.0 - i / trail_len)

# Vectorized assignment
ar = np.array(all_rows)
ac = np.array(all_cols)
af = np.array(all_fades, dtype=np.float32)
# Assign chars and colors in bulk using fancy indexing
ch[ar, ac] = ...  # vectorized char assignment
co[ar, ac, 1] = (af * bri * 255).astype(np.uint8)  # green channel
```

### 向量化火焰列

采用相同模式——批量累积索引数组并统一赋值：

```python
fire_val = np.zeros((rows, cols), dtype=np.float32)
for fi in range(n_cols):
    fx_c = int((fi * cols / n_cols + np.sin(t * 2 + fi * 0.7) * 3) % cols)
    height = int(energy * rows * 0.7)
    dy = np.arange(min(height, rows))
    fr = rows - 1 - dy
    frac = dy / max(height, 1)
    # Width spread: base columns wider at bottom
    for dx in range(-1, 2):  # 3-wide columns
        c = fx_c + dx
        if 0 <= c < cols:
            fire_val[fr, c] = np.maximum(fire_val[fr, c],
                                          (1 - frac * 0.6) * (0.5 + rms * 0.5))
# Now map fire_val to chars and colors in one vectorized pass
```

## 面向大量文本场景的PIL字符串渲染方案

在渲染众多长文本字符串（如滚动行情显示器、打字机效果、连续文字流）时，该方案可作为逐像素位图拷贝方法的替代选择。它利用PIL内置的`ImageDraw.text()`函数，通过一次C语言级调用即可完成整个字符串的渲染，而无需像传统方法那样为每个字符都执行一次Python循环中的位图拷贝操作。

典型优势：对于包含56行文本的场景，该方案仅需调用56次`text()`函数，而非约1万次单独的位图拷贝操作。

适用场景：需要渲染多行可读文本字符串的场景。不适用于字符分布稀疏或空间上分散的单个字符（此类场景应使用常规的`render()`函数）。

```python
from PIL import Image, ImageDraw

def render_text_layer(grid, rows_data, font):
    """Render dense text rows via PIL instead of per-cell bitmap blitting.

    Args:
        grid: GridLayer instance (for oy, ch, ox, font metrics)
        rows_data: list of (row_index, text_string, rgb_tuple) — one per row
        font: PIL ImageFont instance (grid.font)

    Returns:
        uint8 array (VH, VW, 3) — canvas with rendered text
    """
    img = Image.new("RGB", (VW, VH), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for row_idx, text, color in rows_data:
        y = grid.oy + row_idx * grid.ch
        if y + grid.ch > VH:
            break
        draw.text((grid.ox, y), text, fill=color, font=font)
    return np.array(img)
```

### 在行情监控场景中的使用方式

```python
# Build ticker data (text + color per row)
rows_data = []
for row in range(n_tickers):
    text = build_ticker_text(row, t)       # scrolling substring
    color = hsv2rgb_scalar(hue, 0.85, bri) # (R, G, B) tuple
    rows_data.append((row, text, color))

# One PIL pass instead of thousands of bitmap blits
canvas_tickers = render_text_layer(g_md, rows_data, g_md.font)

# Blend with other layers normally
result = blend_canvas(canvas_bg, canvas_tickers, "screen", 0.9)
```

这纯粹是一种渲染优化手段——视觉效果保持不变，但绘制调用次数有所减少。对于那些需要根据数值字段逐个定位字符的稀疏字符字段，仍需使用网格的 `render()` 方法。

## Bloom优化方案

**请勿使用 `scipy.ndimage.uniform_filter`**——其运行速度为每帧424毫秒。

建议采用4倍下采样结合手动框模糊处理的方式——此时每帧仅需84毫秒（速度提升5倍）：

```python
sm = canvas[::4, ::4].astype(np.float32)  # 4x downsample
br = np.where(sm > threshold, sm, 0)
for _ in range(3):                          # 3-pass manual box blur
    p = np.pad(br, ((1,1),(1,1),(0,0)), mode='edge')
    br = (p[:-2,:-2] + p[:-2,1:-1] + p[:-2,2:] +
          p[1:-1,:-2] + p[1:-1,1:-1] + p[1:-1,2:] +
          p[2:,:-2] + p[2:,1:-1] + p[2:,2:]) / 9.0
bl = np.repeat(np.repeat(br, 4, axis=0), 4, axis=1)[:H, :W]
```

## 背景图像缓存

距离场会受分辨率和强度的影响，且不会随每一帧而改变：

```python
_vig_cache = {}
def sh_vignette(canvas, strength):
    key = (canvas.shape[0], canvas.shape[1], round(strength, 2))
    if key not in _vig_cache:
        Y = np.linspace(-1, 1, H)[:, None]
        X = np.linspace(-1, 1, W)[None, :]
        _vig_cache[key] = np.clip(1.0 - np.sqrt(X**2+Y**2) * strength, 0.15, 1).astype(np.float32)
    return np.clip(canvas * _vig_cache[key][:,:,None], 0, 255).astype(np.uint8)
```

CRT桶形畸变的处理方式也是如此（即通过重新映射缓存坐标来实现）。 

## 影片颗粒优化

以半分辨率生成噪声，再对其进行拼接处理：

```python
noise = np.random.randint(-amt, amt+1, (H//2, W//2, 1), dtype=np.int16)
noise = np.repeat(np.repeat(noise, 2, axis=0), 2, axis=1)[:H, :W]
```

两种块状颗粒效果类似电影胶片颗粒，其生成成本仅为随机生成的1/4。

## 并行渲染

### 工作进程架构

```python
hw = detect_hardware()
N_WORKERS = hw["workers"]

# Batch splitting (for non-clip architectures)
batch_size = (n_frames + N_WORKERS - 1) // N_WORKERS
batches = [(i, i*batch_size, min((i+1)*batch_size, n_frames), features, seg_path) ...]

with multiprocessing.Pool(N_WORKERS) as pool:
    segments = pool.starmap(render_batch, batches)
```

### 单片段并行处理（适用于分段视频）

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
    futures = {pool.submit(render_clip, seg, features, path): seg["id"]
               for seg, path in clip_args}
    for fut in as_completed(futures):
        clip_id = futures[fut]
        try:
            fut.result()
            log(f"  {clip_id} done")
        except Exception as e:
            log(f"  {clip_id} FAILED: {e}")
```

### 工作进程隔离

每个工作进程：
- 创建属于自己的 `Renderer` 实例（包含完整的网格与位图初始化）
- 启动独立的 ffmpeg 子进程
- 拥有独立的随机种子（`random.seed(batch_id * 10000)`）
- 将输出写入各自的片段文件及标准错误日志中

### ffmpeg 管道安全性

**重要提示**：在运行时间较长的 ffmpeg 进程中，绝不可使用 `stderr=subprocess.PIPE`。因为标准错误缓冲区在约 64KB 时会被填满，从而导致程序死锁：

```python
# WRONG -- will deadlock
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

# RIGHT -- stderr to file
stderr_fh = open(err_path, "w")
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=stderr_fh)
# ... write all frames ...
pipe.stdin.close()
pipe.wait()
stderr_fh.close()
```

### 连接合并

```python
with open(concat_file, "w") as cf:
    for seg in segments:
        cf.write(f"file '{seg}'\n")

cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file]
if audio_path:
    cmd += ["-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest"]
else:
    cmd += ["-c:v", "copy"]
cmd.append(output_path)
subprocess.run(cmd, capture_output=True, check=True)
```

## 粒子系统性能

根据质量设置限制粒子数量：

| 系统类型 | 低质量 | 标准质量 | 高质量 |
|--------|-------|----------|------|
| 爆炸效果 | 300 | 1000 | 2500 |
| 火焰颗粒 | 500 | 1500 | 3000 |
| 星空效果 | 300 | 800 | 1500 |
| 溶解效果 | 200 | 600 | 1200 |

通过截断列表来过滤粒子：
```python
MAX_PARTICLES = profile.get("particles_max", 1200)
if len(S["px"]) > MAX_PARTICLES:
    for k in ("px", "py", "vx", "vy", "life", "char"):
        S[k] = S[k][-MAX_PARTICLES:]  # keep newest
```

## 内存管理

- 特征数组：为所有帧预先计算，并通过复制语义在多个工作进程间共享（写时复制机制）
- 画布：每个工作进程仅分配一次，之后可重复使用（通过 `np.zeros()` 实现）
- 字符数组：为每个帧单独分配（内存占用较低——为行数×列数的 U1 类型字符串）
- 彩色图缓存：每个网格大小约需 500KB 内存，每个工作进程仅初始化一次

单个工作进程的总内存占用约为 50-150MB；若拥有 8 个工作进程，则总内存占用约为 400-800MB。

对于内存容量较小的系统（< 4GB），建议减少工作进程数量并使用更小的网格尺寸。

## 亮度验证

渲染完成后，可在选定时间点对亮度进行抽样检测：

```python
for t in [2, 30, 60, 120, 180]:
    cmd = ["ffmpeg", "-ss", str(t), "-i", output_path,
           "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    r = subprocess.run(cmd, capture_output=True)
    arr = np.frombuffer(r.stdout, dtype=np.uint8)
    print(f"t={t}s  mean={arr.mean():.1f}  max={arr.max()}")
```

**目标参数：** 静态区域的均值需大于5，动态区域的均值需大于15。若这些数值持续偏低，则应提高效果处理中的亮度下限值和/或全局增强倍率。

## 渲染时间预估

渲染时间随硬件性能而变化。基准条件为1080p、24fps分辨率，每个工作线程每帧的渲染时间约为180毫秒。

| 时长 | 帧数 | 4个工作线程 | 8个工作线程 | 16个工作线程 |
|------|------|------------|------------|------------|
| 30秒 | 720帧 | 约3分钟 | 约2分钟 | 约1分钟 |
| 2分钟 | 2,880帧 | 约13分钟 | 约7分钟 | 约4分钟 |
| 3.5分钟 | 5,040帧 | 约23分钟 | 约12分钟 | 约6分钟 |
| 5分钟 | 7,200帧 | 约33分钟 | 约17分钟 | 约9分钟 |
| 10分钟 | 14,400帧 | 约65分钟 | 约33分钟 | 约17分钟 |

在720p分辨率下，上述时间需乘以约0.5；在4K分辨率下，则需乘以约4。较为复杂的特效（如大量粒子、密集的网格结构以及额外的着色器渲染步骤）会使渲染时间增加约20-50%。

---

## 临时文件清理

渲染过程中会生成各种中间文件，这些文件会在多次渲染后不断累积。应在最终合并/混音处理完成后进行清理。

### 需要清理的文件类型

| 文件类型 | 生成来源 | 存放位置 |
|----------|----------|----------|
| WAV音频提取文件 | `ffmpeg -i input.mp3 ... tmp.wav` | `tempfile.mktemp()`生成的临时目录或项目目录 |
| 分段片段文件 | `render_clip()`函数输出 | `segments/seg_00.mp4`等路径 |
| 合并列表文件 | ffmpeg合并解码器输入文件 | `segments/concat.txt` |
| ffmpeg错误日志 | 为调试目的而导出的日志文件 | 项目目录下的`*.log`文件 |
| 特征缓存文件 | 被序列化的NumPy数组 | `*.pkl`或`*.npz`文件 |

### 清理函数

```python
import glob
import tempfile
import shutil

def cleanup_render_artifacts(segments_dir="segments", keep_final=True):
    """Remove intermediate files after successful render.
    
    Call this AFTER verifying the final output exists and plays correctly.
    
    Args:
        segments_dir: directory containing segment clips and concat list
        keep_final: if True, only delete intermediates (not the final output)
    """
    removed = []
    
    # 1. Segment clips
    if os.path.isdir(segments_dir):
        shutil.rmtree(segments_dir)
        removed.append(f"directory: {segments_dir}")
    
    # 2. Temporary WAV files
    for wav in glob.glob("*.wav"):
        if wav.startswith("tmp") or wav.startswith("extracted_"):
            os.remove(wav)
            removed.append(wav)
    
    # 3. ffmpeg stderr logs
    for log in glob.glob("ffmpeg_*.log"):
        os.remove(log)
        removed.append(log)
    
    # 4. Feature cache (optional — useful to keep for re-renders)
    # for cache in glob.glob("features_*.npz"):
    #     os.remove(cache)
    #     removed.append(cache)
    
    print(f"Cleaned {len(removed)} artifacts: {removed}")
    return removed
```

### 与 Render Pipeline 的集成

在主渲染脚本执行完毕、最终输出经过验证之后，调用清理函数：

```python
# At end of main()
if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
    cleanup_render_artifacts(segments_dir="segments")
    print(f"Done. Output: {output_path}")
else:
    print("WARNING: final output missing or empty — skipping cleanup")
```

### 临时文件使用最佳实践

- 对于各个处理模块的目录，建议使用 `tempfile.mkdtemp()` 创建——这样可以避免污染项目目录
- WAV音频文件的提取文件应通过 `tempfile.mktemp(suffix=".wav")` 生成，这样它们会存储在操作系统的临时目录中
- 在进行调试时，可设置环境变量 `KEEP_INTERMEDIATES=1` 以跳过文件清理步骤
- 特征缓存文件（如 `.npz` 格式）的存储成本较低，但重新计算的成本很高——因此默认情况下应保留这些缓存文件
