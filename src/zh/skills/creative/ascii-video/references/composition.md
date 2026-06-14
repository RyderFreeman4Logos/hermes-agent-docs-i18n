# 组合模式与亮度参考

组合系统是实现视觉复杂度的核心，它在三个层面发挥作用：像素级混合模式、多网格组合以及自适应亮度管理。本文档将涵盖以上三者，同时还会介绍用于空间控制的遮罩/模板系统。

> **另请参阅：** architecture.md · effects.md · scenes.md · shaders.md · troubleshooting.md

## 像素级混合模式

### `blend_canvas()` 函数

所有混合操作都在完整的像素画布上执行（格式为 `uint8 H,W,3`）。为保证精度，系统会将其内部转换为浮点数 [0,1] 进行混合运算，根据透明度进行线性插值，最后再转换回原始格式。

```python
def blend_canvas(base, top, mode="normal", opacity=1.0):
    af = base.astype(np.float32) / 255.0
    bf = top.astype(np.float32) / 255.0
    fn = BLEND_MODES.get(mode, BLEND_MODES["normal"])
    result = fn(af, bf)
    if opacity < 1.0:
        result = af * (1 - opacity) + result * opacity
    return np.clip(result * 255, 0, 255).astype(np.uint8)
```

### 20种混合模式

```python
BLEND_MODES = {
    # Basic arithmetic
    "normal":       lambda a, b: b,
    "add":          lambda a, b: np.clip(a + b, 0, 1),
    "subtract":     lambda a, b: np.clip(a - b, 0, 1),
    "multiply":     lambda a, b: a * b,
    "screen":       lambda a, b: 1 - (1 - a) * (1 - b),

    # Contrast
    "overlay":      lambda a, b: np.where(a < 0.5, 2*a*b, 1 - 2*(1-a)*(1-b)),
    "softlight":    lambda a, b: (1 - 2*b)*a*a + 2*b*a,
    "hardlight":    lambda a, b: np.where(b < 0.5, 2*a*b, 1 - 2*(1-a)*(1-b)),

    # Difference
    "difference":   lambda a, b: np.abs(a - b),
    "exclusion":    lambda a, b: a + b - 2*a*b,

    # Dodge / burn
    "colordodge":   lambda a, b: np.clip(a / (1 - b + 1e-6), 0, 1),
    "colorburn":    lambda a, b: np.clip(1 - (1 - a) / (b + 1e-6), 0, 1),

    # Light
    "linearlight":  lambda a, b: np.clip(a + 2*b - 1, 0, 1),
    "vividlight":   lambda a, b: np.where(b < 0.5,
                        np.clip(1 - (1-a)/(2*b + 1e-6), 0, 1),
                        np.clip(a / (2*(1-b) + 1e-6), 0, 1)),
    "pin_light":    lambda a, b: np.where(b < 0.5,
                        np.minimum(a, 2*b), np.maximum(a, 2*b - 1)),
    "hard_mix":     lambda a, b: np.where(a + b >= 1.0, 1.0, 0.0),

    # Compare
    "lighten":      lambda a, b: np.maximum(a, b),
    "darken":       lambda a, b: np.minimum(a, b),

    # Grain
    "grain_extract": lambda a, b: np.clip(a - b + 0.5, 0, 1),
    "grain_merge":  lambda a, b: np.clip(a + b - 0.5, 0, 1),
}
```

### 混合模式选择指南

**使图像变亮的模式**（适用于暗色调的输入内容）：
- `screen` — 始终能提升亮度。两个50%灰度的图层混合后为75%。是最安全且常用的混合模式。
- `add` — 简单的叠加效果，亮度达到白色时停止增加。非常适合用于制作闪光、发光效果及粒子叠加层。
- `colordodge` — 在重叠区域产生极强的亮化效果，但也可能导致图像过曝。建议使用较低的透明度（0.3-0.5）。
- `linearlight` — 强力提升亮度，效果与`add`类似，但具有偏移特性。

**使图像变暗的模式**（不建议用于暗色调的输入内容）：
- `multiply` — 会使所有内容都变暗。仅建议在两个图层本身已经较亮时使用。
- `overlay` — 当底层亮度低于0.5时会变暗，高于0.5时会变亮。对于暗色调的输入内容，其效果会极为显著：例如`2 * 0.12 * 0.12 = 0.03`。处理暗色材质时建议改用`screen`模式。
- `colorburn` — 在重叠区域产生极强的暗化效果。

**用于创造对比度的模式**：
- `softlight` — 轻微的对比度，适合用于柔和的纹理叠加。
- `hardlight` — 强烈的对比度，效果类似`overlay`，但以顶层图层为基准。
- `vividlight` — 对比度极高，建议谨慎使用。

**用于生成色彩效果的模式**：
- `difference` — 会产生类似XOR运算的图案。两个完全相同的图层混合后为黑色；若图层有偏移，则会形成独特的色彩效果，非常适合打造迷幻风格。
- `exclusion` — 是`difference`的柔和版本，可生成互补色图案。
- `hard_mix` — 在图层交叉处将图像简化为纯黑、纯白或高饱和度的颜色。

**用于纹理混合的模式**：
- `grain_extract` / `grain_merge` — 从一个图层中提取纹理，并应用到另一个图层上。

### 多图层链式处理

```python
# Pattern: render layers -> blend sequentially
canvas_a = _render_vf(r, "md", vf_plasma, hf_angle(0.0), PAL_DENSE, f, t, S)
canvas_b = _render_vf(r, "sm", vf_vortex, hf_time_cycle(0.1), PAL_RUNE, f, t, S)
canvas_c = _render_vf(r, "lg", vf_rings, hf_distance(), PAL_BLOCKS, f, t, S)

result = blend_canvas(canvas_a, canvas_b, "screen", 0.8)
result = blend_canvas(result, canvas_c, "difference", 0.6)
```

顺序很重要：`screen(A, B)` 是可交换的，但 `difference(screen(A,B), C)` 与 `difference(A, screen(B,C))` 的结果并不相同。

### 线性光混合模式

标准的 `blend_canvas()` 函数在 sRGB 空间中运行——即使用原始字节值。对于大多数应用而言这已经足够，但由于 sRGB 在感知上是非线性的：在 sRGB 空间中进行混合会使中间色调变暗，并轻微改变色相。若需实现符合物理特性的混合效果（即模拟光线实际混合的方式），则应先将其转换为线性光空间。

该功能使用了 `architecture.md` 中关于 OKLAB 颜色系统的 `srgb_to_linear()` / `linear_to_srgb()` 函数。

```python
def blend_canvas_linear(base, top, mode="normal", opacity=1.0):
    """Blend in linear light space for physically accurate results.
    
    Identical API to blend_canvas(), but converts sRGB → linear before
    blending and linear → sRGB after. More expensive (~2x) due to the
    gamma conversions, but produces correct results for additive blending,
    screen, and any mode where brightness matters.
    """
    af = srgb_to_linear(base.astype(np.float32) / 255.0)
    bf = srgb_to_linear(top.astype(np.float32) / 255.0)
    fn = BLEND_MODES.get(mode, BLEND_MODES["normal"])
    result = fn(af, bf)
    if opacity < 1.0:
        result = af * (1 - opacity) + result * opacity
    result = linear_to_srgb(np.clip(result, 0, 1))
    return np.clip(result * 255, 0, 255).astype(np.uint8)
```

**何时使用 `blend_canvas_linear()` 而非 `blend_canvas()`：**

| 使用场景 | 推荐函数 | 原因 |
|----------|---------|------|
| 混合两个高亮度的图层 | `linear` | sRGB 显示模式会使高光部分过度变亮 |
| 实现发光/泛光效果 | `linear` | 加性光遵循线性物理规律 |
| 混合透明度较低的文字叠加层 | `srgb` | 从感知角度而言，此模式能让文字混合效果更自然 |
| 用于阴影处理或加深颜色 | `srgb` | 对于加深操作而言，两种模式的效果差异极小 |
| 需要精确控制颜色的工作（如匹配参考色） | `linear` | 可避免 sRGB 在中间色调区域导致的色相偏移 |
| 对性能要求极高的内部循环处理 | `srgb` | 处理速度约为前者的两倍，足以满足大多数 ASCII 艺术作品的需求 |

**批量处理版本**适用于合成多个图层（一次性转换、混合多张图层后再转换回原格式）：

```python
def blend_many_linear(layers, modes, opacities):
    """Blend a stack of layers in linear light space.
    
    Args:
        layers: list of uint8 (H,W,3) canvases
        modes: list of blend mode strings (len = len(layers) - 1)
        opacities: list of floats (len = len(layers) - 1)
    Returns:
        uint8 (H,W,3) canvas
    """
    # Convert all to linear at once
    linear = [srgb_to_linear(l.astype(np.float32) / 255.0) for l in layers]
    result = linear[0]
    for i in range(1, len(linear)):
        fn = BLEND_MODES.get(modes[i-1], BLEND_MODES["normal"])
        blended = fn(result, linear[i])
        op = opacities[i-1]
        if op < 1.0:
            blended = result * (1 - op) + blended * op
        result = np.clip(blended, 0, 1)
    result = linear_to_srgb(result)
    return np.clip(result * 255, 0, 255).astype(np.uint8)
```

## 多网格组合技术

这是核心的视觉技术。通过以不同的网格密度（字符大小）来渲染同一个概念场景，可以产生自然的纹理干涉效果——因为不同比例的字符会在不同的空间频率上相互重叠。

### 其原理

- `sm` 网格（10pt字体）：320×83个字符。细节丰富，纹理密集。
- `md` 网格（16pt）：192×56个字符。中等密度。
- `lg` 网格（20pt）：160×45个字符。字符较为粗大。

当在 `sm` 网格上渲染等离子体场，在 `lg` 网格上渲染涡流，再将两者进行屏幕混合时，精细的等离子体纹理会从粗大的涡流字符间隙中显现出来。这样的效果比单独使用任一层都要具有更高的视觉复杂性。

### `_render_vf()` 辅助函数

这是核心功能函数。它接收值场、色调场、调色板以及网格参数，进而将内容渲染到完整的像素画布上：

```python
def _render_vf(r, grid_key, val_fn, hue_fn, pal, f, t, S, sat=0.8, threshold=0.03):
    """Render a value field + hue field to a pixel canvas via a named grid.

    Args:
        r: Renderer instance (has .get_grid())
        grid_key: "xs", "sm", "md", "lg", "xl", "xxl"
        val_fn: (g, f, t, S) -> float32 [0,1] array (rows, cols)
        hue_fn: callable (g, f, t, S) -> float32 hue array, OR float scalar
        pal: character palette string
        f: feature dict
        t: time in seconds
        S: persistent state dict
        sat: HSV saturation (0-1)
        threshold: minimum value to render (below = space)

    Returns:
        uint8 array (VH, VW, 3) — full pixel canvas
    """
    g = r.get_grid(grid_key)
    val = np.clip(val_fn(g, f, t, S), 0, 1)
    mask = val > threshold
    ch = val2char(val, mask, pal)

    # Hue: either a callable or a fixed float
    if callable(hue_fn):
        h = hue_fn(g, f, t, S) % 1.0
    else:
        h = np.full((g.rows, g.cols), float(hue_fn), dtype=np.float32)

    # CRITICAL: broadcast to full shape and copy (see Troubleshooting)
    h = np.broadcast_to(h, (g.rows, g.cols)).copy()

    R, G, B = hsv2rgb(h, np.full_like(val, sat), val)
    co = mkc(R, G, B, g.rows, g.cols)
    return g.render(ch, co)
```

### 网格组合策略

| 组合方式 | 效果 | 适用场景 |
|----------|------|----------|
| `sm` + `lg` | 细节部分与大块区域之间形成最大对比度 | 强烈视觉冲击、图形化风格 |
| `sm` + `md` | 轻微的纹理层次感，尺度相近 | 自然流畅的视觉效果 |
| `md` + `lg` + `xs` | 三重尺度叠加，复杂度最高 | 迷幻风格、密集视觉效果 |
| `sm` + `sm`（不同效果） | 尺度相同，仅产生图案干涉效果 | 莫尔纹、干涉图案 |

### 完整的多网格场景示例

```python
def fx_psychedelic(r, f, t, S):
    """Three-layer multi-grid scene with beat-reactive kaleidoscope."""
    # Layer A: plasma on medium grid with rainbow hue
    canvas_a = _render_vf(r, "md",
        lambda g, f, t, S: vf_plasma(g, f, t, S) * 1.3,
        hf_angle(0.0), PAL_DENSE, f, t, S, sat=0.8)

    # Layer B: vortex on small grid with cycling hue
    canvas_b = _render_vf(r, "sm",
        lambda g, f, t, S: vf_vortex(g, f, t, S, twist=5.0) * 1.2,
        hf_time_cycle(0.1), PAL_RUNE, f, t, S, sat=0.7)

    # Layer C: rings on large grid with distance hue
    canvas_c = _render_vf(r, "lg",
        lambda g, f, t, S: vf_rings(g, f, t, S, n_base=8, spacing_base=3) * 1.4,
        hf_distance(0.3, 0.02), PAL_BLOCKS, f, t, S, sat=0.9)

    # Blend: A screened with B, then difference with C
    result = blend_canvas(canvas_a, canvas_b, "screen", 0.8)
    result = blend_canvas(result, canvas_c, "difference", 0.6)

    # Beat-triggered kaleidoscope
    if f.get("bdecay", 0) > 0.3:
        result = sh_kaleidoscope(result.copy(), folds=6)

    return result
```

## 自适应色调映射

### 亮度问题

ASCII字符本质上是黑色背景上的小亮点。任何画面中的大多数像素都属于背景色（黑色）。这意味着：
- 画面的平均亮度天生较低（通常在255分制的5到30分之间）
- 不同效果组合会导致极其不同的亮度水平
- 例如，螺旋结构场景的平均亮度可能为50，而火焰场景则为9
- 线性倍增操作（如`canvas * 2.0`）要么让暗场景保持黑暗，要么使亮场景过曝

### `tonemap()`函数

它用针对每帧的自适应归一化处理及伽马校正，替代了传统的线性亮度倍增方式：

```python
def tonemap(canvas, target_mean=90, gamma=0.75, black_point=2, white_point=253):
    """Adaptive tone-mapping: normalizes + gamma-corrects so no frame is
    fully dark or washed out.

    1. Compute 1st and 99.5th percentile on 4x subsample (16x fewer values,
       negligible accuracy loss, major speedup at 1080p+)
    2. Stretch that range to [0, 1]
    3. Apply gamma curve (< 1 lifts shadows, > 1 darkens)
    4. Rescale to [black_point, white_point]
    """
    f = canvas.astype(np.float32)
    sub = f[::4, ::4]  # 4x subsample: ~390K values vs ~6.2M at 1080p
    lo = np.percentile(sub, 1)
    hi = np.percentile(sub, 99.5)
    if hi - lo < 10:
        hi = max(hi, lo + 10)  # near-uniform frame fallback
    f = np.clip((f - lo) / (hi - lo), 0.0, 1.0)
    np.power(f, gamma, out=f)          # in-place: avoids allocation
    np.multiply(f, (white_point - black_point), out=f)
    np.add(f, black_point, out=f)
    return np.clip(f, 0, 255).astype(np.uint8)
```

### 为何选择伽马而非线性方式

线性倍率 `* 2.0`：
```
input 10  -> output 20   (still dark)
input 100 -> output 200  (ok)
input 200 -> output 255  (clipped, lost detail)
```

标准化处理后的 Gamma 值为 0.75：
```
input 0.04 -> output 0.08 (lifted from invisible to visible)
input 0.39 -> output 0.50 (moderate lift)
input 0.78 -> output 0.84 (gentle lift, no clipping)
```

当 Gamma 值小于 1 时，会压缩高光区域并扩展阴影部分。这正是我们所需要的：在不使亮部过曝的情况下，让暗色的 ASCII 内容变得可见。

### 流处理顺序

`render_clip()` 函数中的流处理顺序为：

```
scene_fn(r, f, t, S)  ->  canvas
         |
    tonemap(canvas, gamma=scene_gamma)
         |
    FeedbackBuffer.apply(canvas, ...)
         |
    ShaderChain.apply(canvas, f=f, t=t)
         |
    ffmpeg pipe
```

色调映射在反馈处理和着色器之前执行。这意味着：
- 反馈处理作用于标准化数据（无论场景亮度如何都能保持一致的行为）
- 如阳光化、贴图化、对比度等着色器则作用于范围正确的数据
- 此时链中的亮度着色器已不再需要（色调映射可完成该功能）

### 每个场景的伽马值调整

默认伽马值为0.75。对于需要使用破坏性后期处理的场景，由于处理是在色调映射之后进行的，因此需要更强的亮度提升效果：

| 场景类型 | 推荐伽马值 | 原因 |
|----------|------------|------|
| 标准效果 | 0.75 | 默认值，适用于大多数场景 |
| 阳光化后期处理 | 0.50-0.60 | 阳光化效果会反转亮像素，从而降低整体亮度 |
| 贴图化后期处理 | 0.50-0.55 | 贴图化处理会进行量化，常常导致中间色调变为黑色 |
| 强烈差异混合 | 0.60-0.70 | 差异模式会产生大量接近零的像素 |
| 本身已很亮的场景 | 0.85-1.0 | 不要过度提升天然明亮的场景亮度 |

可通过场景表格进行配置：

```python
SCENES = [
    {"start": 9.17, "end": 11.25, "name": "fire", "gamma": 0.55,
     "fx": fx_fire, "shaders": [("solarize", {"threshold": 200}), ...]},
    {"start": 25.96, "end": 27.29, "name": "diamond", "gamma": 0.5,
     "fx": fx_diamond, "shaders": [("bloom", {"thr": 90}), ...]},
]
```

### 亮度验证

渲染完成后，对帧的亮度进行抽查：

```python
# In test-frame mode
canvas = scene["fx"](r, feat, t, r.S)
canvas = tonemap(canvas, gamma=scene.get("gamma", 0.75))
chain = ShaderChain()
for sn, kw in scene.get("shaders", []):
    chain.add(sn, **kw)
canvas = chain.apply(canvas, f=feat, t=t)
print(f"Mean brightness: {canvas.astype(float).mean():.1f}, max: {canvas.max()}")
```

经过色调映射与着色器处理后的目标范围：
- 安静/环境场景：平均值 30-60
- 活跃场景：平均值 40-100
- 高潮/剧烈场景：平均值 60-150
- 若平均值 < 20：说明伽马值过高，或某个着色器正在削弱亮度
- 若平均值 > 180：说明伽马值过低，或叠加效果过强

---

## FeedbackBuffer 空间变换

反馈缓冲区用于存储上一帧图像，并通过渐变方式将其与当前帧融合。在融合之前对缓冲区应用空间变换，便能在反馈轨迹中营造出运动的效果。

### 实现方式

```python
class FeedbackBuffer:
    def __init__(self):
        self.buf = None

    def apply(self, canvas, decay=0.85, blend="screen", opacity=0.5,
              transform=None, transform_amt=0.02, hue_shift=0.0):
        if self.buf is None:
            self.buf = canvas.astype(np.float32) / 255.0
            return canvas

        # Decay old buffer
        self.buf *= decay

        # Spatial transform
        if transform:
            self.buf = self._transform(self.buf, transform, transform_amt)

        # Hue shift the feedback for rainbow trails
        if hue_shift > 0:
            self.buf = self._hue_shift(self.buf, hue_shift)

        # Blend feedback into current frame
        result = blend_canvas(canvas,
                              np.clip(self.buf * 255, 0, 255).astype(np.uint8),
                              blend, opacity)

        # Update buffer with current frame
        self.buf = result.astype(np.float32) / 255.0
        return result

    def _transform(self, buf, transform, amt):
        h, w = buf.shape[:2]
        if transform == "zoom":
            # Zoom in: sample from slightly inside (creates expanding tunnel)
            m = int(h * amt); n = int(w * amt)
            if m > 0 and n > 0:
                cropped = buf[m:-m or None, n:-n or None]
                # Resize back to full (nearest-neighbor for speed)
                buf = np.array(Image.fromarray(
                    np.clip(cropped * 255, 0, 255).astype(np.uint8)
                ).resize((w, h), Image.NEAREST)).astype(np.float32) / 255.0
        elif transform == "shrink":
            # Zoom out: pad edges, shrink center
            m = int(h * amt); n = int(w * amt)
            small = np.array(Image.fromarray(
                np.clip(buf * 255, 0, 255).astype(np.uint8)
            ).resize((w - 2*n, h - 2*m), Image.NEAREST))
            new = np.zeros((h, w, 3), dtype=np.uint8)
            new[m:m+small.shape[0], n:n+small.shape[1]] = small
            buf = new.astype(np.float32) / 255.0
        elif transform == "rotate_cw":
            # Small clockwise rotation via affine
            angle = amt * 10  # amt=0.005 -> 0.05 degrees per frame
            cy, cx = h / 2, w / 2
            Y = np.arange(h, dtype=np.float32)[:, None]
            X = np.arange(w, dtype=np.float32)[None, :]
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            sx = (X - cx) * cos_a + (Y - cy) * sin_a + cx
            sy = -(X - cx) * sin_a + (Y - cy) * cos_a + cy
            sx = np.clip(sx.astype(int), 0, w - 1)
            sy = np.clip(sy.astype(int), 0, h - 1)
            buf = buf[sy, sx]
        elif transform == "rotate_ccw":
            angle = -amt * 10
            cy, cx = h / 2, w / 2
            Y = np.arange(h, dtype=np.float32)[:, None]
            X = np.arange(w, dtype=np.float32)[None, :]
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            sx = (X - cx) * cos_a + (Y - cy) * sin_a + cx
            sy = -(X - cx) * sin_a + (Y - cy) * cos_a + cy
            sx = np.clip(sx.astype(int), 0, w - 1)
            sy = np.clip(sy.astype(int), 0, h - 1)
            buf = buf[sy, sx]
        elif transform == "shift_up":
            pixels = max(1, int(h * amt))
            buf = np.roll(buf, -pixels, axis=0)
            buf[-pixels:] = 0  # black fill at bottom
        elif transform == "shift_down":
            pixels = max(1, int(h * amt))
            buf = np.roll(buf, pixels, axis=0)
            buf[:pixels] = 0
        elif transform == "mirror_h":
            buf = buf[:, ::-1]
        return buf

    def _hue_shift(self, buf, amount):
        """Rotate hues of the feedback buffer. Operates on float32 [0,1]."""
        rgb = np.clip(buf * 255, 0, 255).astype(np.uint8)
        hsv = np.zeros_like(buf)
        # Simple approximate RGB->HSV->shift->RGB
        r, g, b = buf[:,:,0], buf[:,:,1], buf[:,:,2]
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        delta = mx - mn + 1e-10
        # Hue
        h = np.where(mx == r, ((g - b) / delta) % 6,
            np.where(mx == g, (b - r) / delta + 2, (r - g) / delta + 4))
        h = (h / 6 + amount) % 1.0
        # Reconstruct with shifted hue (simplified)
        s = delta / (mx + 1e-10)
        v = mx
        c = v * s; x = c * (1 - np.abs((h * 6) % 2 - 1)); m = v - c
        ro = np.zeros_like(h); go = np.zeros_like(h); bo = np.zeros_like(h)
        for lo, hi, rv, gv, bv in [(0,1,c,x,0),(1,2,x,c,0),(2,3,0,c,x),
                                     (3,4,0,x,c),(4,5,x,0,c),(5,6,c,0,x)]:
            mask = ((h*6) >= lo) & ((h*6) < hi)
            ro[mask] = rv[mask] if not isinstance(rv, (int,float)) else rv
            go[mask] = gv[mask] if not isinstance(gv, (int,float)) else gv
            bo[mask] = bv[mask] if not isinstance(bv, (int,float)) else bv
        return np.stack([ro+m, go+m, bo+m], axis=2)
```

### 反馈预设

| 预设 | 配置参数 | 视觉效果 |
|------|----------|-----------|
| 无限缩放通道 | `decay=0.8, blend="screen", transform="zoom", transform_amt=0.015` | 不断扩大的环形图案 |
| 彩虹轨迹 | `decay=0.7, blend="screen", transform="zoom", transform_amt=0.01, hue_shift=0.02` | 迷幻色彩轨迹 |
| 幽灵回声 | `decay=0.9, blend="add", opacity=0.15, transform="shift_up", transform_amt=0.01` | 微弱的向上模糊效果 |
| 万花筒式递归 | `decay=0.75, blend="screen", transform="rotate_cw", transform_amt=0.005, hue_shift=0.01` | 旋转的曼荼罗式反馈效果 |
| 颜色演变 | `decay=0.8, blend="difference", opacity=0.4, hue_shift=0.03` | 帧与帧之间的颜色异或效果 |
| 上升的热浪 | `decay=0.5, blend="add", opacity=0.2, transform="shift_up", transform_amt=0.02` | 炎热空气产生的光晕 |

---

## 遮罩/模板系统

遮罩为范围在 [0, 1] 之间的 float32 数组，格式为 `(行数, 列数)` 或 `(垂直高度, 水平宽度)`。它们用于控制效果的出现区域：1.0 表示完全可见，0.0 表示完全隐藏。可通过遮罩来构建主体与背景的关系、突出焦点以及实现有形状的渐显效果。

### 形状遮罩

```python
def mask_circle(g, cx_frac=0.5, cy_frac=0.5, radius=0.3, feather=0.05):
    """Circular mask centered at (cx_frac, cy_frac) in normalized coords.
    feather: width of soft edge (0 = hard cutoff)."""
    asp = g.cw / g.ch if hasattr(g, 'cw') else 1.0
    dx = (g.cc / g.cols - cx_frac)
    dy = (g.rr / g.rows - cy_frac) * asp
    d = np.sqrt(dx**2 + dy**2)
    if feather > 0:
        return np.clip(1.0 - (d - radius) / feather, 0, 1)
    return (d <= radius).astype(np.float32)

def mask_rect(g, x0=0.2, y0=0.2, x1=0.8, y1=0.8, feather=0.03):
    """Rectangular mask. Coordinates in [0,1] normalized."""
    dx = np.maximum(x0 - g.cc / g.cols, g.cc / g.cols - x1)
    dy = np.maximum(y0 - g.rr / g.rows, g.rr / g.rows - y1)
    d = np.maximum(dx, dy)
    if feather > 0:
        return np.clip(1.0 - d / feather, 0, 1)
    return (d <= 0).astype(np.float32)

def mask_ring(g, cx_frac=0.5, cy_frac=0.5, inner_r=0.15, outer_r=0.35,
              feather=0.03):
    """Ring / annulus mask."""
    inner = mask_circle(g, cx_frac, cy_frac, inner_r, feather)
    outer = mask_circle(g, cx_frac, cy_frac, outer_r, feather)
    return outer - inner

def mask_gradient_h(g, start=0.0, end=1.0):
    """Left-to-right gradient mask."""
    return np.clip((g.cc / g.cols - start) / (end - start + 1e-10), 0, 1).astype(np.float32)

def mask_gradient_v(g, start=0.0, end=1.0):
    """Top-to-bottom gradient mask."""
    return np.clip((g.rr / g.rows - start) / (end - start + 1e-10), 0, 1).astype(np.float32)

def mask_gradient_radial(g, cx_frac=0.5, cy_frac=0.5, inner=0.0, outer=0.5):
    """Radial gradient mask — bright at center, dark at edges."""
    d = np.sqrt((g.cc / g.cols - cx_frac)**2 + (g.rr / g.rows - cy_frac)**2)
    return np.clip(1.0 - (d - inner) / (outer - inner + 1e-10), 0, 1)
```

### 将值字段用作掩码

可将任何 `vf_*` 函数的输出作为空间掩码使用：

```python
def mask_from_vf(vf_result, threshold=0.5, feather=0.1):
    """Convert a value field to a mask by thresholding.
    feather: smooth edge width around threshold."""
    if feather > 0:
        return np.clip((vf_result - threshold + feather) / (2 * feather), 0, 1)
    return (vf_result > threshold).astype(np.float32)

def mask_select(mask, vf_a, vf_b):
    """Spatial conditional: show vf_a where mask is 1, vf_b where mask is 0.
    mask: float32 [0,1] array. Intermediate values blend."""
    return vf_a * mask + vf_b * (1 - mask)
```

### 文本模板

将文本渲染为遮罩效果。各类特效仅通过字母轮廓呈现出来：

```python
def mask_text(grid, text, row_frac=0.5, font=None, font_size=None):
    """Render text string as a float32 mask [0,1] at grid resolution.
    Characters = 1.0, background = 0.0.

    row_frac: vertical position as fraction of grid height.
    font: PIL ImageFont (defaults to grid's font if None).
    font_size: override font size for the mask text (for larger stencil text).
    """
    from PIL import Image, ImageDraw, ImageFont

    f = font or grid.font
    if font_size and font != grid.font:
        f = ImageFont.truetype(font.path, font_size)

    # Render text to image at pixel resolution, then downsample to grid
    img = Image.new("L", (grid.cols * grid.cw, grid.ch), 0)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    x = (grid.cols * grid.cw - tw) // 2
    draw.text((x, 0), text, fill=255, font=f)
    row_mask = np.array(img, dtype=np.float32) / 255.0

    # Place in full grid mask
    mask = np.zeros((grid.rows, grid.cols), dtype=np.float32)
    target_row = int(grid.rows * row_frac)
    # Downsample rendered text to grid cells
    for c in range(grid.cols):
        px = c * grid.cw
        if px + grid.cw <= row_mask.shape[1]:
            cell = row_mask[:, px:px + grid.cw]
            if cell.mean() > 0.1:
                mask[target_row, c] = cell.mean()
    return mask

def mask_text_block(grid, lines, start_row_frac=0.3, font=None):
    """Multi-line text stencil. Returns full grid mask."""
    mask = np.zeros((grid.rows, grid.cols), dtype=np.float32)
    for i, line in enumerate(lines):
        row_frac = start_row_frac + i / grid.rows
        line_mask = mask_text(grid, line, row_frac, font)
        mask = np.maximum(mask, line_mask)
    return mask
```

### 动态遮罩

可随时间变化以实现画面渐显、淡出及变形效果的遮罩：

```python
def mask_iris(g, t, t_start, t_end, cx_frac=0.5, cy_frac=0.5,
              max_radius=0.7, ease_fn=None):
    """Iris open/close: circle that grows from 0 to max_radius.
    ease_fn: easing function (default: ease_in_out_cubic from effects.md)."""
    if ease_fn is None:
        ease_fn = lambda x: x * x * (3 - 2 * x)  # smoothstep fallback
    progress = np.clip((t - t_start) / (t_end - t_start), 0, 1)
    radius = ease_fn(progress) * max_radius
    return mask_circle(g, cx_frac, cy_frac, radius, feather=0.03)

def mask_wipe_h(g, t, t_start, t_end, direction="right"):
    """Horizontal wipe reveal."""
    progress = np.clip((t - t_start) / (t_end - t_start), 0, 1)
    if direction == "left":
        progress = 1 - progress
    return mask_gradient_h(g, start=progress - 0.05, end=progress + 0.05)

def mask_wipe_v(g, t, t_start, t_end, direction="down"):
    """Vertical wipe reveal."""
    progress = np.clip((t - t_start) / (t_end - t_start), 0, 1)
    if direction == "up":
        progress = 1 - progress
    return mask_gradient_v(g, start=progress - 0.05, end=progress + 0.05)

def mask_dissolve(g, t, t_start, t_end, seed=42):
    """Random pixel dissolve — noise threshold sweeps from 0 to 1."""
    progress = np.clip((t - t_start) / (t_end - t_start), 0, 1)
    rng = np.random.RandomState(seed)
    noise = rng.random((g.rows, g.cols)).astype(np.float32)
    return (noise < progress).astype(np.float32)
```

### 掩码布尔运算

```python
def mask_union(a, b):
    """OR — visible where either mask is active."""
    return np.maximum(a, b)

def mask_intersect(a, b):
    """AND — visible only where both masks are active."""
    return np.minimum(a, b)

def mask_subtract(a, b):
    """A minus B — visible where A is active but B is not."""
    return np.clip(a - b, 0, 1)

def mask_invert(m):
    """NOT — flip mask."""
    return 1.0 - m
```

### 为画布应用遮罩

```python
def apply_mask_canvas(canvas, mask, bg_canvas=None):
    """Apply a grid-resolution mask to a pixel canvas.
    Expands mask from (rows, cols) to (VH, VW) via nearest-neighbor.

    canvas: uint8 (VH, VW, 3)
    mask: float32 (rows, cols) [0,1]
    bg_canvas: what shows through where mask=0. None = black.
    """
    # Expand mask to pixel resolution
    mask_px = np.repeat(np.repeat(mask, canvas.shape[0] // mask.shape[0] + 1, axis=0),
                        canvas.shape[1] // mask.shape[1] + 1, axis=1)
    mask_px = mask_px[:canvas.shape[0], :canvas.shape[1]]

    if bg_canvas is not None:
        return np.clip(canvas * mask_px[:, :, None] +
                       bg_canvas * (1 - mask_px[:, :, None]), 0, 255).astype(np.uint8)
    return np.clip(canvas * mask_px[:, :, None], 0, 255).astype(np.uint8)

def apply_mask_vf(vf_a, vf_b, mask):
    """Apply mask at value-field level — blend two value fields spatially.
    All arrays are (rows, cols) float32."""
    return vf_a * mask + vf_b * (1 - mask)
```

## PixelBlendStack

用于多层合成操作的高级封装工具：

```python
class PixelBlendStack:
    def __init__(self):
        self.layers = []

    def add(self, canvas, mode="normal", opacity=1.0):
        self.layers.append((canvas, mode, opacity))
        return self

    def composite(self):
        if not self.layers:
            return np.zeros((VH, VW, 3), dtype=np.uint8)
        result = self.layers[0][0]
        for canvas, mode, opacity in self.layers[1:]:
            result = blend_canvas(result, canvas, mode, opacity)
        return result
```

## 文本背景层（可读性遮罩）

当在复杂的多网格 ASCII 背景上显示文字时，这些文字往往会与背景融为一体而变得难以辨认。**务必在文本区域后方设置深色背景层。**

实现方法为：首先计算所有文字字符的边界框，接着创建一个带有边距的高斯模糊深色遮罩来覆盖该区域；在将文字渲染到上方之前，先通过公式 `(1 - 遮罩值 * 深度系数)` 对背景颜色进行叠加处理。

```python
from scipy.ndimage import gaussian_filter

def apply_text_backdrop(canvas, glyphs, padding=80, darkness=0.75):
    """Darken the background behind text for readability.
    
    Call AFTER rendering background, BEFORE rendering text.
    
    Args:
        canvas: (VH, VW, 3) uint8 background
        glyphs: list of {"x": float, "y": float, ...} glyph positions
        padding: pixel padding around text bounding box
        darkness: 0.0 = no darkening, 1.0 = fully black
    Returns:
        darkened canvas (uint8)
    """
    if not glyphs:
        return canvas
    xs = [g['x'] for g in glyphs]
    ys = [g['y'] for g in glyphs]
    x0 = max(0, int(min(xs)) - padding)
    y0 = max(0, int(min(ys)) - padding)
    x1 = min(VW, int(max(xs)) + padding + 50)   # extra for char width
    y1 = min(VH, int(max(ys)) + padding + 60)   # extra for char height
    
    # Soft dark mask with gaussian blur for feathered edges
    mask = np.zeros((VH, VW), dtype=np.float32)
    mask[y0:y1, x0:x1] = 1.0
    mask = gaussian_filter(mask, sigma=padding * 0.6)
    
    factor = 1.0 - mask * darkness
    return (canvas.astype(np.float32) * factor[:, :, np.newaxis]).astype(np.uint8)
```

### 在渲染流程中的使用方式

将其插入到背景渲染与文本渲染之间：

```python
# 1. Render background (multi-grid ASCII effects)
bg = render_background(cfg, t)

# 2. Darken behind text region
bg = apply_text_backdrop(bg, frame_glyphs, padding=80, darkness=0.75)

# 3. Render text on top (now readable against dark backdrop)
bg = text_renderer.render(bg, frame_glyphs, color=(255, 255, 255))
```

对于文本始终需要居中的场景，可将其与**反向渐晕效果**（详见 shaders.md）结合使用——反向渐晕效果能够持续形成中心暗区，而背景组件则负责处理每一帧中文字的位置。

## 外部布局计算模式

在那些文字占比很高、且文字需要围绕障碍物（形状、图标或其他文字）动态重新排版的视频中，建议使用外部布局引擎来预先计算文字位置，并通过 JSON 格式将这些数据传递给 Python 渲染器。

### 架构

```
Layout Engine (browser/Node.js)  →  layouts.json  →  Python ASCII Renderer
         ↑                                                    ↑
   Computes per-frame                               Reads glyph positions,
   glyph (x,y) positions                            renders as ASCII chars
   with obstacle-aware reflow                        with full effect pipeline
```

### JSON数据交换格式

```json
{
  "meta": {
    "canvas_width": 1080, "canvas_height": 1080,
    "fps": 24, "total_frames": 1248,
    "fonts": {
      "body": {"charW": 12.04, "charH": 24, "fontSize": 20},
      "hero": {"charW": 24.08, "charH": 48, "fontSize": 40}
    }
  },
  "scenes": [
    {
      "id": "scene_name",
      "start_frame": 0, "end_frame": 96,
      "frames": {
        "0": {
          "glyphs": [
            {"char": "H", "x": 287.1, "y": 400.0, "alpha": 1.0},
            {"char": "e", "x": 311.2, "y": 400.0, "alpha": 1.0}
          ],
          "obstacles": [
            {"type": "circle", "cx": 540, "cy": 540, "r": 80},
            {"type": "rect", "x": 300, "y": 500, "w": 120, "h": 80}
          ]
        }
      }
    }
  ]
}
```

### 适用场景

- 需要根据移动物体动态调整布局的文本
- 每个字符独立的动画效果（出现、散开、物理模拟等）
- 需要精确测量尺寸的动态排版
- Python 的 Pillow 库无法满足需求的任何场景

### 不适用场景

- 静态居中显示的文本（可直接使用 PIL 的 `draw.text()` 函数）
- 仅具有淡入淡出效果且无空间动画的文本
- 简单的打字机效果（可通过 Python 中的字符计数器实现）

### 运行布局引擎

可使用 Playwright 在无头浏览器中启动该布局引擎：

```javascript
// extract.mjs
import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto(`file://${oraclePath}`);
await page.waitForFunction(() => window.__ORACLE_DONE__ === true, null, { timeout: 60000 });
const result = await page.evaluate(() => window.__ORACLE_RESULT__);
writeFileSync('layouts.json', JSON.stringify(result));
await browser.close();
```

### 使用 Python 进行调用

```python
# In the renderer, map pixel positions to the canvas:
for glyph in frame_data['glyphs']:
    char, px, py = glyph['char'], glyph['x'], glyph['y']
    alpha = glyph.get('alpha', 1.0)
    # Render using PIL draw.text() at exact pixel position
    draw.text((px, py), char, fill=(int(255*alpha),)*3, font=font)
```

JSON 中标识的障碍物也可以发光的 ASCII 图形（圆形、矩形）的形式呈现，从而直观展示重排区域。
