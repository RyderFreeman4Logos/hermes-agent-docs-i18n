# 场景系统与创意构图

> **另请参阅：** architecture.md · composition.md · effects.md · shaders.md

## 场景设计理念

场景是用于叙事的核心单元，而非特效演示。每个场景都需要具备以下要素：
- **核心概念**——视觉上要呈现什么？不应只是“等离子体+光环”，而应是“从虚无中诞生”或“结晶过程”等更具描述性的概念；
- **发展脉络**——在场景呈现的整个过程中，内容如何发生变化？是逐渐构建、逐渐衰减、形态转变，还是逐步揭示？
- **功能定位**——该场景如何服务于整体视频叙事？是营造开场悬念、达到高潮氛围，还是推动剧情走向解决？

以下设计模式提供了各种构图技巧。相应的场景示例展示了这些技巧在不同复杂程度下的实际应用。协议部分则说明了所有场景必须遵循的技术规范。

优秀的场景设计始于明确的核心概念，随后再选择能够支撑该概念的特效与参数。设计模式部分会讲解如何有意识地组合不同层次的内容。示例部分则展示了各个复杂程度下的完整可用场景。协议部分则规定了所有场景都必须遵守的技术标准。

---

## 场景设计模式

这类高级设计模式用于构建富有意图、而非随机生成的场景。它们利用现有的基础元素（数值字段、混合模式、着色器、反馈机制），但以更具构图意识的思路对它们进行组织。

## 图层层级结构

每个场景都应包含层次分明、功能各异的视觉图层：

| 图层 | 网格密度 | 亮度 | 功能 |
|-------|----------|--------|------|
| **背景层** | xs或sm（密集） | 0.1–0.25 | 负责营造氛围与纹理，绝不能与主要内容形成竞争。 |
| **内容层** | md（均衡） | 0.4–0.8 | 承载场景的核心视觉理念，体现场景的整体概念。 |
| **强调层** | lg或sm（稀疏） | 0.5–1.0（覆盖范围较小） | 用于突出重点、添加视觉点缀，形成稀疏的亮点。 |

背景层负责营造整体氛围，内容层则是场景的核心表现内容，而强调层则在不过分抢镜的情况下为场景增添视觉趣味。

```python
def fx_example(r, f, t, S):
    local = t
    progress = min(local / 5.0, 1.0)

    g_bg = r.get_grid("sm")
    g_main = r.get_grid("md")
    g_accent = r.get_grid("lg")

    # --- Background: dim atmosphere ---
    bg_val = vf_smooth_noise(g_bg, f, t * 0.3, S, octaves=2, bri=0.15)
    # ... render bg to canvas

    # --- Content: the main visual idea ---
    content_val = vf_spiral(g_main, f, t, S, n_arms=n_arms, tightness=tightness)
    # ... render content on top of canvas

    # --- Accent: sparse highlights ---
    accent_val = vf_noise_static(g_accent, f, t, S, density=0.05)
    # ... render accent on top

    return canvas
```

## 方向性参数曲线

在场景的整个时长内，参数应朝着某个特定方向变化——而非像 `sin(t * N)` 那样无目的地来回振荡。

**错误示例：** `twist = 3.0 + 2.0 * math.sin(t * 0.6)` —— 会不断来回晃动，显得毫无目标感。

**正确示例：** `twist = 2.0 + progress * 5.0` —— 起始平缓，逐渐加剧。整个场景呈现出逐步推进的效果。

可使用 `progress = min(local / duration, 1.0)`（在场景中从 0 到 1 变化）来控制方向性变化：

| 模式 | 公式 | 效果感受 |
|------|------|----------|
| 线性渐变 | `progress * range` | 逐步稳步增强 |
| 减速结束 | `1 - (1 - progress) ** 2` | 快速开始，平缓结束 |
| 加速开始 | `progress ** 2` | 缓慢开始，逐渐加速 |
| 分步显现 | `np.clip((progress - 0.5) / 0.25, 0, 1)` | 前 50% 没有变化，之后逐渐显现 |
| 增强后平稳 | `min(1.0, progress * 1.5)` | 在 67% 时达到最大值，随后保持不变 |

对于*次要*参数（如饱和度闪烁、色调偏移），振荡效果是可行的。但作为场景*核心特征*的参数则应具有明确的方向性。

### 方向性曲线示例

| 场景概念 | 参数 | 曲线路径 |
|----------|------|----------|
| 出现 | 环形半径 | 0 → 最大值（减速结束） |
| 破裂 | Voronoi单元数量 | 8 → 38（线性变化） |
| 下降 | 隧道速度 | 2.0 → 10.0（线性变化） |
| 曼陀罗 | 形状复杂度 | 环形 → 多边形 → 星形 → 玫瑰花形（分步显现） |
| 渐强 | 图层数量 | 1 → 7（逐层出现） |
| 熵增 | 几何体可见度 | 1.0 → 0.0（逐渐消失） |

## 场景概念

每个场景都应围绕一个*视觉理念*来构建，而非仅以特效名称命名。

**错误示例：** “fx_plasma_cascade” —— 仅以特效名称命名，缺乏概念内涵。
**正确示例：** “fx_emergence” —— 一个光点逐渐扩展成一片区域。名称就能让人明白*发生了什么*。

优秀的场景概念应具备：
1. **视觉隐喻**（出现、下降、碰撞、熵增）
2. **方向性曲线**（元素从 A 变为 B，而非振荡）
3. **有针对性的图层设计**（每个图层都服务于该概念）
4. **与之匹配的反馈效果**（变换方向与隐喻相契合）

| 概念 | 隐喻 | 反馈变换方式 | 原因 |
|------|------|--------------|------|
| 出现 | 出生、扩张 | 缩放远离 | 过去的帧会向外部扩散 |
| 下降 | 下落、加速 | 缩放靠近 | 过去的帧会向中心快速移动 |
| 地狱之火 | 火焰上升 | 上方平移 | 过去的帧会随火焰一同上升 |
| 熵增 | 腐败、消散 | 无变换 | 效果干净利落，无残留——事物直接消失 |
| 渐强 | 积累 | 缩放 + 色调变化 | 所有元素不断叠加并发生变化 |

## 构图技巧

### 相反方向旋转的双系统

让同一特效的两个实例以相反方向旋转，可产生视觉干扰效果：

```python
# Primary spiral (clockwise)
s1_val = vf_spiral(g_main, f, t * 1.5, S, n_arms=n_arms_1, tightness=tightness_1)

# Counter-rotating spiral (counter-clockwise via negative time)
s2_val = vf_spiral(g_accent, f, -t * 1.2, S, n_arms=n_arms_2, tightness=tightness_2)

# Screen blend creates bright interference at crossing points
canvas = blend_canvas(canvas_with_s1, c2, "screen", 0.7)
```

可与螺旋、涡流及环状结构协同工作。反向旋转会形成不断变化的干涉图案。

### 波浪碰撞

从两侧汇聚而来的两个波前，在碰撞点相遇：

```python
collision_phase = abs(progress - 0.5) * 2  # 1→0→1 (0 at collision)

# Wave A approaches from left
offset_a = (1 - progress) * g.cols * 0.4
wave_a = np.sin((g.cc + offset_a) * 0.08 + t * 2) * 0.5 + 0.5

# Wave B approaches from right
offset_b = -(1 - progress) * g.cols * 0.4
wave_b = np.sin((g.cc + offset_b) * 0.08 - t * 2) * 0.5 + 0.5

# Interference peaks at collision
combined = wave_a * 0.5 + wave_b * 0.5 + np.abs(wave_a - wave_b) * (1 - collision_phase) * 0.5
```

### 逐步碎片化现象

随着时间推移，单元格数量不断增加的沃罗诺伊图——呈现视觉上的破碎效果：

```python
n_pts = int(8 + progress * 30)  # 8 cells → 38 cells
# Pre-generate enough points, slice to n_pts
px = base_x[:n_pts] + np.sin(t * 0.3 + np.arange(n_pts) * 0.7) * (3 + progress * 3)
```

随着进度推进，边缘光晕的宽度也会逐渐加宽，从而更突出裂缝效果。

### 熵值/消耗量

一种规则的几何图案正被自然演变过程所取代：

```python
# Geometry fades out
geo_val = clean_pattern * max(0.05, 1.0 - progress * 0.9)

# Organic process grows in
rd_val = vf_reaction_diffusion(g, f, t, S) * min(1.0, progress * 1.5)

# Render geometry first, organic on top — organic consumes geometry
```

### 分阶段层级加载（渐强效果）

各层会逐个加载，逐渐形成极高的密度：

```python
def layer_strength(enter_t, ramp=1.5):
    """0.0 until enter_t, ramps to 1.0 over ramp seconds."""
    return max(0.0, min(1.0, (local - enter_t) / ramp))

# Layer 1: always present
s1 = layer_strength(0.0)
# Layer 2: enters at 2s
s2 = layer_strength(2.0)
# Layer 3: enters at 4s
s3 = layer_strength(4.0)
# ... etc

# Each layer uses a different effect, grid, palette, and blend mode
# Screen blend between layers so they accumulate light
```

若需实现15秒的渐强效果，每2秒添加7个层次较为合适。可选用不同的混合模式：大多数情况下使用“屏幕”模式，需增强氛围时使用“叠加”模式，最终渲染阶段则使用“色阶偏移”模式。

## 场景排序

对于多场景混剪视频：
- **相邻场景的基调应有所差异**——避免将两个氛围平静的场景放在一起
- **随机排序而非按类型分组**——这样可以避免出现“效果演示”的感觉
- **以最精彩的场景作为结尾**——选择渐强效果或具有明确高潮点的场景
- **以充满活力的开场吸引注意力**——在视频前2秒内抓住观众视线

---

## 场景协议

场景是最高级别的创意单元。每个场景都是一个有时间限制的片段，拥有独立的特效功能、着色器链、反馈配置以及色调映射伽马值。

### 场景协议（v2）

### 函数签名

```python
def fx_scene_name(r, f, t, S) -> canvas:
    """
    Args:
        r: Renderer instance — access multiple grids via r.get_grid("sm")
        f: dict of audio/video features, all values normalized to [0, 1]
        t: time in seconds — local to scene (0.0 at scene start)
        S: dict for persistent state (particles, rain columns, etc.)

    Returns:
        canvas: numpy uint8 array, shape (VH, VW, 3) — full pixel frame
    """
```

**本地时间规范：** 无论场景在时间轴上的位置如何，场景函数接收的参数 `t` 始于场景第一帧的 0.0 值。渲染循环会在调用相关函数之前，先减去该场景的起始时间。

```python
# In render_clip:
t_local = fi / FPS - scene_start
canvas = fx_fn(r, feat, t_local, S)
```

这样一来，便无需修改代码即可重新排序场景。场景处理进度可按如下方式计算：

```python
progress = min(t / scene_duration, 1.0)  # 0→1 over the scene
```

它取代了旧版的v1协议——该协议返回的场景数据为`(字符, 颜色)`元组形式。而v2协议则让场景能够在内部完全掌控多网格渲染及像素级合成功能。

### 渲染器类

```python
class Renderer:
    def __init__(self):
        self.grids = {}   # lazy-initialized grid cache
        self.g = None      # "active" grid (for backward compat)
        self.S = {}        # persistent state dict

    def get_grid(self, key):
        """Get or create a GridLayer by size key."""
        if key not in self.grids:
            sizes = {"xs": 8, "sm": 10, "md": 16, "lg": 20, "xl": 24, "xxl": 40}
            self.grids[key] = GridLayer(FONT_PATH, sizes[key])
        return self.grids[key]

    def set_grid(self, key):
        """Set active grid (legacy). Prefer get_grid() for multi-grid scenes."""
        self.g = self.get_grid(key)
        return self.g
```

**与 v1 的主要区别**：在新版本中，场景会通过调用 `r.get_grid("sm")`、`r.get_grid("lg")` 等方法来访问多个网格。每个网格都会以延迟初始化的方式被创建并缓存起来。而对于仅包含单个网格的场景，`set_grid()` 方法依然可用。 

### 最简场景（单网格）

```python
def fx_simple_rings(r, f, t, S):
    """Single-grid scene: rings with distance-mapped hue."""
    canvas = _render_vf(r, "md",
        lambda g, f, t, S: vf_rings(g, f, t, S, n_base=8, spacing_base=3),
        hf_distance(0.3, 0.02), PAL_STARS, f, t, S, sat=0.85)
    return canvas
```

### 标准场景（双网格 + 混合）

```python
def fx_tunnel_ripple(r, f, t, S):
    """Two-grid scene: tunnel depth exclusion-blended with ripple."""
    canvas_a = _render_vf(r, "md",
        lambda g, f, t, S: vf_tunnel(g, f, t, S, speed=5.0, complexity=10) * 1.3,
        hf_distance(0.55, 0.02), PAL_GREEK, f, t, S, sat=0.7)

    canvas_b = _render_vf(r, "sm",
        lambda g, f, t, S: vf_ripple(g, f, t, S,
            sources=[(0.3,0.3), (0.7,0.7), (0.5,0.2)], freq=0.5, damping=0.012) * 1.4,
        hf_angle(0.1), PAL_STARS, f, t, S, sat=0.8)

    return blend_canvas(canvas_a, canvas_b, "exclusion", 0.8)
```

### 复杂场景（三网格结构 + 条件逻辑 + 自定义渲染）

```python
def fx_rings_explosion(r, f, t, S):
    """Three-grid scene with particles and conditional kaleidoscope."""
    # Layer 1: rings
    canvas_a = _render_vf(r, "sm",
        lambda g, f, t, S: vf_rings(g, f, t, S, n_base=10, spacing_base=2) * 1.4,
        lambda g, f, t, S: (g.angle / (2*np.pi) + t * 0.15) % 1.0,
        PAL_STARS, f, t, S, sat=0.9)

    # Layer 2: vortex on different grid
    canvas_b = _render_vf(r, "md",
        lambda g, f, t, S: vf_vortex(g, f, t, S, twist=6.0) * 1.2,
        hf_time_cycle(0.15), PAL_BLOCKS, f, t, S, sat=0.8)

    result = blend_canvas(canvas_b, canvas_a, "screen", 0.7)

    # Layer 3: particles (custom rendering, not _render_vf)
    g = r.get_grid("sm")
    if "px" not in S:
        S["px"], S["py"], S["vx"], S["vy"], S["life"], S["pch"] = (
            [], [], [], [], [], [])
    if f.get("beat", 0) > 0.5:
        chars = list("\u2605\u2736\u2733\u2738\u2726\u2728*+")
        for _ in range(int(80 + f.get("rms", 0.3) * 120)):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(1, 10) * (0.5 + f.get("sub_r", 0.3) * 2)
            S["px"].append(float(g.cols // 2))
            S["py"].append(float(g.rows // 2))
            S["vx"].append(math.cos(ang) * sp * 2.5)
            S["vy"].append(math.sin(ang) * sp)
            S["life"].append(1.0)
            S["pch"].append(random.choice(chars))

    # Update + draw particles
    ch_p = np.full((g.rows, g.cols), " ", dtype="U1")
    co_p = np.zeros((g.rows, g.cols, 3), dtype=np.uint8)
    i = 0
    while i < len(S["px"]):
        S["px"][i] += S["vx"][i]; S["py"][i] += S["vy"][i]
        S["vy"][i] += 0.03; S["life"][i] -= 0.02
        if S["life"][i] <= 0:
            for k in ("px","py","vx","vy","life","pch"): S[k].pop(i)
        else:
            pr, pc = int(S["py"][i]), int(S["px"][i])
            if 0 <= pr < g.rows and 0 <= pc < g.cols:
                ch_p[pr, pc] = S["pch"][i]
                co_p[pr, pc] = hsv2rgb_scalar(
                    0.08 + (1-S["life"][i])*0.15, 0.95, S["life"][i])
            i += 1

    canvas_p = g.render(ch_p, co_p)
    result = blend_canvas(result, canvas_p, "add", 0.8)

    # Conditional kaleidoscope on strong beats
    if f.get("bdecay", 0) > 0.4:
        result = sh_kaleidoscope(result.copy(), folds=6)

    return result
```

### 自定义角色渲染场景（矩阵雨效果）

当您需要超出 `_render_vf()` 能力范围的对单个像素的精细控制时：

```python
def fx_matrix_layered(r, f, t, S):
    """Matrix rain blended with tunnel — two grids, screen blend."""
    # Layer 1: Matrix rain (custom per-column rendering)
    g = r.get_grid("md")
    rows, cols = g.rows, g.cols
    pal = PAL_KATA

    if "ry" not in S or len(S["ry"]) != cols:
        S["ry"] = np.random.uniform(-rows, rows, cols).astype(np.float32)
        S["rsp"] = np.random.uniform(0.3, 2.0, cols).astype(np.float32)
        S["rln"] = np.random.randint(8, 35, cols)
        S["rch"] = np.random.randint(1, len(pal), (rows, cols))

    speed = 0.6 + f.get("bass", 0.3) * 3
    if f.get("beat", 0) > 0.5: speed *= 2.5
    S["ry"] += S["rsp"] * speed

    ch = np.full((rows, cols), " ", dtype="U1")
    co = np.zeros((rows, cols, 3), dtype=np.uint8)
    heads = S["ry"].astype(int)
    for c in range(cols):
        head = heads[c]
        for i in range(S["rln"][c]):
            row = head - i
            if 0 <= row < rows:
                fade = 1.0 - i / S["rln"][c]
                ch[row, c] = pal[S["rch"][row, c] % len(pal)]
                if i == 0:
                    v = int(min(255, fade * 300))
                    co[row, c] = (int(v*0.9), v, int(v*0.9))
                else:
                    v = int(fade * 240)
                    co[row, c] = (int(v*0.1), v, int(v*0.4))
    canvas_a = g.render(ch, co)

    # Layer 2: Tunnel on sm grid for depth texture
    canvas_b = _render_vf(r, "sm",
        lambda g, f, t, S: vf_tunnel(g, f, t, S, speed=5.0, complexity=10),
        hf_distance(0.3, 0.02), PAL_BLOCKS, f, t, S, sat=0.6)

    return blend_canvas(canvas_a, canvas_b, "screen", 0.5)
```

## 场景表

场景表用于定义时间线：指定每个场景在何时以何种配置被触发。

### 结构

```python
SCENES = [
    {
        "start": 0.0,           # start time in seconds
        "end": 3.96,            # end time in seconds
        "name": "starfield",    # identifier (used for clip filenames)
        "grid": "sm",           # default grid (for render_clip setup)
        "fx": fx_starfield,     # scene function reference (must be module-level)
        "gamma": 0.75,          # tonemap gamma override (default 0.75)
        "shaders": [            # shader chain (applied after tonemap + feedback)
            ("bloom", {"thr": 120}),
            ("vignette", {"s": 0.2}),
            ("grain", {"amt": 8}),
        ],
        "feedback": None,       # feedback buffer config (None = disabled)
        # "feedback": {"decay": 0.8, "blend": "screen", "opacity": 0.3,
        #              "transform": "zoom", "transform_amt": 0.02, "hue_shift": 0.02},
    },
    {
        "start": 3.96,
        "end": 6.58,
        "name": "matrix_layered",
        "grid": "md",
        "fx": fx_matrix_layered,
        "shaders": [
            ("crt", {"strength": 0.05}),
            ("scanlines", {"intensity": 0.12}),
            ("color_grade", {"tint": (0.7, 1.2, 0.7)}),
            ("bloom", {"thr": 100}),
        ],
        "feedback": {"decay": 0.5, "blend": "add", "opacity": 0.2},
    },
    # ... more scenes ...
]
```

### 基于节拍同步的场景剪辑

通过音频分析来确定剪辑点：

```python
# Get beat timestamps
beats = [fi / FPS for fi in range(N_FRAMES) if features["beat"][fi] > 0.5]

# Group beats into phrase boundaries (every 4-8 beats)
cuts = [0.0]
for i in range(0, len(beats), 4):  # cut every 4 beats
    cuts.append(beats[i])
cuts.append(DURATION)

# Or use the music's structure: silence gaps, energy changes
energy = features["rms"]
# Find timestamps where energy drops significantly -> natural break points
```

### `render_clip()` — 渲染循环

该函数可将一个场景渲染为视频片段文件：

```python
def render_clip(seg, features, clip_path):
    r = Renderer()
    r.set_grid(seg["grid"])
    S = r.S
    random.seed(hash(seg["id"]) + 42)  # deterministic per scene

    # Build shader chain from config
    chain = ShaderChain()
    for shader_name, kwargs in seg.get("shaders", []):
        chain.add(shader_name, **kwargs)

    # Setup feedback buffer
    fb = None
    fb_cfg = seg.get("feedback", None)
    if fb_cfg:
        fb = FeedbackBuffer()

    fx_fn = seg["fx"]

    # Open ffmpeg pipe
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "pipe:0",
           "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", clip_path]
    stderr_fh = open(clip_path.replace(".mp4", ".log"), "w")
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=stderr_fh)

    for fi in range(seg["frame_start"], seg["frame_end"]):
        t = fi / FPS
        feat = {k: float(features[k][fi]) for k in features}

        # 1. Scene renders canvas
        canvas = fx_fn(r, feat, t, S)

        # 2. Tonemap normalizes brightness
        canvas = tonemap(canvas, gamma=seg.get("gamma", 0.75))

        # 3. Feedback adds temporal recursion
        if fb and fb_cfg:
            canvas = fb.apply(canvas, **{k: fb_cfg[k] for k in fb_cfg})

        # 4. Shader chain adds post-processing
        canvas = chain.apply(canvas, f=feat, t=t)

        pipe.stdin.write(canvas.tobytes())

    pipe.stdin.close(); pipe.wait(); stderr_fh.close()
```

### 基于场景表构建分段

```python
segments = []
for i, scene in enumerate(SCENES):
    segments.append({
        "id": f"s{i:02d}_{scene['name']}",
        "name": scene["name"],
        "grid": scene["grid"],
        "fx": scene["fx"],
        "shaders": scene.get("shaders", []),
        "feedback": scene.get("feedback", None),
        "gamma": scene.get("gamma", 0.75),
        "frame_start": int(scene["start"] * FPS),
        "frame_end": int(scene["end"] * FPS),
    })
```

### 并行渲染

场景作为独立单元被分配至进程池中处理：

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
    futures = {
        pool.submit(render_clip, seg, features, clip_path): seg["id"]
        for seg, clip_path in zip(segments, clip_paths)
    }
    for fut in as_completed(futures):
        try:
            fut.result()
        except Exception as e:
            log(f"ERROR {futures[fut]}: {e}")
```

**序列化限制**：`ProcessPoolExecutor` 会通过 pickle 对参数进行序列化。模块级函数可以被序列化，而 lambda 表达式和闭包则不可。所有的 `fx_*` 场景函数都必须定义在模块级别，不得以闭包或类方法的形式存在。

### 测试帧模式

无需进行完整渲染，即可通过渲染特定时间戳下的单帧画面来验证视觉效果：

```python
if args.test_frame >= 0:
    fi = min(int(args.test_frame * FPS), N_FRAMES - 1)
    t = fi / FPS
    feat = {k: float(features[k][fi]) for k in features}
    scene = next(sc for sc in reversed(SCENES) if t >= sc["start"])
    r = Renderer()
    r.set_grid(scene["grid"])
    canvas = scene["fx"](r, feat, t, r.S)
    canvas = tonemap(canvas, gamma=scene.get("gamma", 0.75))
    chain = ShaderChain()
    for sn, kw in scene.get("shaders", []):
        chain.add(sn, **kw)
    canvas = chain.apply(canvas, f=feat, t=t)
    Image.fromarray(canvas).save(f"test_{args.test_frame:.1f}s.png")
    print(f"Mean brightness: {canvas.astype(float).mean():.1f}")
```

**CLI命令：** `python reel.py --test-frame 10.0`

---

## 场景设计检查清单

针对每个场景：

1. **选择2-3种网格尺寸**——不同的比例会导致视觉干扰
2. **为每层选择不同的数值字段**——避免在所有网格上使用相同的效果
3. **为每层选择不同的色调字段**——或至少使用不同的色调偏移量
4. **为每层选择不同的调色板**——将PAL_RUNE与PAL_BLOCKS混合的效果，会与PAL_RUNE与PAL_DENSE混合的效果有所不同
5. **选择与场景氛围相匹配的混合模式**：明亮效果选用“屏幕”模式，迷幻效果选用“差异”模式，柔和效果选用“排除”模式
6. **根据节奏添加条件效果**——如万花筒、镜像、故障效果等
7. **配置反馈效果**，以实现拖尾或递归视觉效果——若需干净切面，则可设置为无反馈
8. **如果使用破坏性着色器（如阳光化、海报化效果），请设置伽马值**
9. 在完整渲染之前，于场景中间节点使用`--test-frame`参数进行测试

---

## 场景示例

这些可直接复制粘贴的场景函数复杂度逐渐增加。每个都是一个功能完备的v2版本场景函数，能够生成像素画布。有关场景协议的信息，请参阅上方的“场景协议”部分；关于混合模式和色调映射的信息，则可在`composition.md`文件中查看。

---

### 最简单版本——单网格、单一效果

### 呼吸等离子体效果

仅包含一个网格、一个数值字段和一个色调字段，这是最简单的场景形式。

```python
def fx_breathing_plasma(r, f, t, S):
    """Plasma field with time-cycling hue. Audio modulates brightness."""
    canvas = _render_vf(r, "md",
        lambda g, f, t, S: vf_plasma(g, f, t, S) * 1.3,
        hf_time_cycle(0.08), PAL_DENSE, f, t, S, sat=0.8)
    return canvas
```

### 反应-扩散珊瑚模型

基于单网格与仿真技术的场模型，会随着时间推移自然演化。

```python
def fx_coral(r, f, t, S):
    """Gray-Scott reaction-diffusion — coral branching pattern.
    Slow-evolving, organic. Best for ambient/chill sections."""
    canvas = _render_vf(r, "sm",
        lambda g, f, t, S: vf_reaction_diffusion(g, f, t, S,
            feed=0.037, kill=0.060, steps_per_frame=6, init_mode="center"),
        hf_distance(0.55, 0.015), PAL_DOTS, f, t, S, sat=0.7)
    return canvas
```

### SDF几何体

源自SDF的几何形状。简洁、精准且具有出色的视觉效果。

```python
def fx_sdf_rings(r, f, t, S):
    """Concentric SDF rings with smooth pulsing."""
    def val_fn(g, f, t, S):
        d1 = sdf_ring(g, radius=0.15 + f.get("bass", 0.3) * 0.05, thickness=0.015)
        d2 = sdf_ring(g, radius=0.25 + f.get("mid", 0.3) * 0.05, thickness=0.012)
        d3 = sdf_ring(g, radius=0.35 + f.get("hi", 0.3) * 0.04, thickness=0.010)
        combined = sdf_smooth_union(sdf_smooth_union(d1, d2, 0.05), d3, 0.05)
        return sdf_glow(combined, falloff=0.08) * (0.5 + f.get("rms", 0.3) * 0.8)
    canvas = _render_vf(r, "md", val_fn, hf_angle(0.0), PAL_STARS, f, t, S, sat=0.85)
    return canvas
```

### 标准模式 —— 双网格叠加混合

### 穿透噪声

采用两种不同密度的网格，并通过屏幕混合技术呈现。细微的噪声纹理会透过较为粗糙的隧道字符显现出来。

```python
def fx_tunnel_noise(r, f, t, S):
    """Tunnel depth on md grid + fBM noise on sm grid, screen blended."""
    canvas_a = _render_vf(r, "md",
        lambda g, f, t, S: vf_tunnel(g, f, t, S, speed=4.0, complexity=8) * 1.2,
        hf_distance(0.5, 0.02), PAL_BLOCKS, f, t, S, sat=0.7)

    canvas_b = _render_vf(r, "sm",
        lambda g, f, t, S: vf_fbm(g, f, t, S, octaves=4, freq=0.05, speed=0.15) * 1.3,
        hf_time_cycle(0.06), PAL_RUNE, f, t, S, sat=0.6)

    return blend_canvas(canvas_a, canvas_b, "screen", 0.7)
```

### 沃罗诺伊单元 + 螺旋叠加效果

在沃罗诺伊单元的边界上叠加了螺旋臂图案。

```python
def fx_voronoi_spiral(r, f, t, S):
    """Voronoi edge detection on md + logarithmic spiral on lg."""
    canvas_a = _render_vf(r, "md",
        lambda g, f, t, S: vf_voronoi(g, f, t, S,
            n_cells=15, mode="edge", edge_width=2.0, speed=0.4),
        hf_angle(0.2), PAL_CIRCUIT, f, t, S, sat=0.75)

    canvas_b = _render_vf(r, "lg",
        lambda g, f, t, S: vf_spiral(g, f, t, S, n_arms=4, tightness=3.0) * 1.2,
        hf_distance(0.1, 0.03), PAL_BLOCKS, f, t, S, sat=0.9)

    return blend_canvas(canvas_a, canvas_b, "exclusion", 0.6)
```

### 域扭曲型 fBM

由两层相同的 fBM 组成，其中一层经过域扭曲处理，随后通过差异混合技术，从而营造出迷幻的有机质感。

```python
def fx_organic_warp(r, f, t, S):
    """Clean fBM vs domain-warped fBM, difference blended."""
    canvas_a = _render_vf(r, "sm",
        lambda g, f, t, S: vf_fbm(g, f, t, S, octaves=5, freq=0.04, speed=0.1),
        hf_plasma(0.2), PAL_DENSE, f, t, S, sat=0.6)

    canvas_b = _render_vf(r, "md",
        lambda g, f, t, S: vf_domain_warp(g, f, t, S,
            warp_strength=20.0, freq=0.05, speed=0.15),
        hf_time_cycle(0.05), PAL_BRAILLE, f, t, S, sat=0.7)

    return blend_canvas(canvas_a, canvas_b, "difference", 0.7)
```

### 复杂模式 — 三格布局 + 条件触发 + 反馈效果

### 迷幻大教堂

采用三格构图，结合节奏触发的万花筒效果与反馈式缩放通道，是视觉效果最为复杂的图案。

```python
def fx_cathedral(r, f, t, S):
    """Three-layer cathedral: interference + rings + noise, kaleidoscope on beat,
    feedback zoom tunnel."""
    # Layer 1: interference pattern on sm grid
    canvas_a = _render_vf(r, "sm",
        lambda g, f, t, S: vf_interference(g, f, t, S, n_waves=7) * 1.3,
        hf_angle(0.0), PAL_MATH, f, t, S, sat=0.8)

    # Layer 2: pulsing rings on md grid
    canvas_b = _render_vf(r, "md",
        lambda g, f, t, S: vf_rings(g, f, t, S, n_base=10, spacing_base=3) * 1.4,
        hf_distance(0.3, 0.02), PAL_STARS, f, t, S, sat=0.9)

    # Layer 3: temporal noise on lg grid (slow morph)
    canvas_c = _render_vf(r, "lg",
        lambda g, f, t, S: vf_temporal_noise(g, f, t, S,
            freq=0.04, t_freq=0.2, octaves=3),
        hf_time_cycle(0.12), PAL_BLOCKS, f, t, S, sat=0.7)

    # Blend: A screen B, then difference with C
    result = blend_canvas(canvas_a, canvas_b, "screen", 0.8)
    result = blend_canvas(result, canvas_c, "difference", 0.5)

    # Beat-triggered kaleidoscope
    if f.get("bdecay", 0) > 0.3:
        folds = 6 if f.get("sub_r", 0.3) > 0.4 else 8
        result = sh_kaleidoscope(result.copy(), folds=folds)

    return result

# Scene table entry with feedback:
# {"start": 30.0, "end": 50.0, "name": "cathedral", "fx": fx_cathedral,
#  "gamma": 0.65, "shaders": [("bloom", {"thr": 110}), ("chromatic", {"amt": 4}),
#                              ("vignette", {"s": 0.2}), ("grain", {"amt": 8})],
#  "feedback": {"decay": 0.75, "blend": "screen", "opacity": 0.35,
#               "transform": "zoom", "transform_amt": 0.012, "hue_shift": 0.015}}
```

### 带吸引子叠加的遮蔽型反应扩散模型

通过动态变化的虹膜遮罩来呈现反应扩散效果，其下方则隐藏着由奇异吸引子构成的密度场。

```python
def fx_masked_life(r, f, t, S):
    """Attractor base + reaction-diffusion visible through iris mask + particles."""
    g_sm = r.get_grid("sm")
    g_md = r.get_grid("md")

    # Layer 1: strange attractor density field (background)
    canvas_bg = _render_vf(r, "sm",
        lambda g, f, t, S: vf_strange_attractor(g, f, t, S,
            attractor="clifford", n_points=30000),
        hf_time_cycle(0.04), PAL_DOTS, f, t, S, sat=0.5)

    # Layer 2: reaction-diffusion (foreground, will be masked)
    canvas_rd = _render_vf(r, "md",
        lambda g, f, t, S: vf_reaction_diffusion(g, f, t, S,
            feed=0.046, kill=0.063, steps_per_frame=4, init_mode="ring"),
        hf_angle(0.15), PAL_HALFFILL, f, t, S, sat=0.85)

    # Animated iris mask — opens over first 5 seconds of scene
    scene_start = S.get("_scene_start", t)
    if "_scene_start" not in S:
        S["_scene_start"] = t
    mask = mask_iris(g_md, t, scene_start, scene_start + 5.0,
                     max_radius=0.6)
    canvas_rd = apply_mask_canvas(canvas_rd, mask, bg_canvas=canvas_bg)

    # Layer 3: flow-field particles following the R-D gradient
    rd_field = vf_reaction_diffusion(g_sm, f, t, S,
        feed=0.046, kill=0.063, steps_per_frame=0)  # read without stepping
    ch_p, co_p = update_flow_particles(S, g_sm, f, rd_field,
        n=300, speed=0.8, char_set=list("·•◦∘°"))
    canvas_p = g_sm.render(ch_p, co_p)

    result = blend_canvas(canvas_rd, canvas_p, "add", 0.7)
    return result
```

### 使用缓动关键帧实现场序列的平滑过渡

该功能展示了时间连贯性：通过为参数设置关键帧，实现各种效果之间的流畅过渡。

```python
def fx_morphing_journey(r, f, t, S):
    """Morphs through 4 value fields over 20 seconds with eased transitions.
    Parameters (twist, arm count) also keyframed."""
    # Keyframed twist parameter
    twist = keyframe(t, [(0, 1.0), (5, 5.0), (10, 2.0), (15, 8.0), (20, 1.0)],
                     ease_fn=ease_in_out_cubic, loop=True)

    # Sequence of value fields with 2s crossfade
    fields = [
        lambda g, f, t, S: vf_plasma(g, f, t, S),
        lambda g, f, t, S: vf_vortex(g, f, t, S, twist=twist),
        lambda g, f, t, S: vf_fbm(g, f, t, S, octaves=5, freq=0.04),
        lambda g, f, t, S: vf_domain_warp(g, f, t, S, warp_strength=15),
    ]
    durations = [5.0, 5.0, 5.0, 5.0]

    val_fn = lambda g, f, t, S: vf_sequence(g, f, t, S, fields, durations,
                                             crossfade=2.0)

    # Render with slowly rotating hue
    canvas = _render_vf(r, "md", val_fn, hf_time_cycle(0.06),
                        PAL_DENSE, f, t, S, sat=0.8)

    # Second layer: tiled version of same sequence at smaller grid
    tiled_fn = lambda g, f, t, S: vf_sequence(
        make_tgrid(g, *uv_tile(g, 3, 3, mirror=True)),
        f, t, S, fields, durations, crossfade=2.0)
    canvas_b = _render_vf(r, "sm", tiled_fn, hf_angle(0.1),
                          PAL_RUNE, f, t, S, sat=0.6)

    return blend_canvas(canvas, canvas_b, "screen", 0.5)
```

### 专用功能 —— 独特的状态模式

### 带“幽灵轨迹”的生命游戏

具有模拟渐隐轨迹的元胞自动机，Beat功能可随机生成新单元格。

```python
def fx_life(r, f, t, S):
    """Conway's Game of Life with fading ghost trails.
    Beat events inject random live cells for disruption."""
    canvas = _render_vf(r, "sm",
        lambda g, f, t, S: vf_game_of_life(g, f, t, S,
            rule="life", steps_per_frame=1, fade=0.92, density=0.25),
        hf_fixed(0.33), PAL_BLOCKS, f, t, S, sat=0.8)

    # Overlay: coral automaton on lg grid for chunky texture
    canvas_b = _render_vf(r, "lg",
        lambda g, f, t, S: vf_game_of_life(g, f, t, S,
            rule="coral", steps_per_frame=1, fade=0.85, density=0.15, seed=99),
        hf_time_cycle(0.1), PAL_HATCH, f, t, S, sat=0.6)

    return blend_canvas(canvas, canvas_b, "screen", 0.5)
```

### 在沃罗诺伊图上形成的鸟群飞动效果

在单元格背景上呈现出的自组织群体运动现象。

```python
def fx_boid_swarm(r, f, t, S):
    """Flocking boids over animated voronoi cells."""
    # Background: voronoi cells
    canvas_bg = _render_vf(r, "md",
        lambda g, f, t, S: vf_voronoi(g, f, t, S,
            n_cells=20, mode="distance", speed=0.2),
        hf_distance(0.4, 0.02), PAL_CIRCUIT, f, t, S, sat=0.5)

    # Foreground: boids
    g = r.get_grid("md")
    ch_b, co_b = update_boids(S, g, f, n_boids=150, perception=6.0,
                              max_speed=1.5, char_set=list("▸▹►▻→⟶"))
    canvas_boids = g.render(ch_b, co_b)

    # Trails for the boids
    # (boid positions are stored in S["boid_x"], S["boid_y"])
    S["px"] = list(S.get("boid_x", []))
    S["py"] = list(S.get("boid_y", []))
    ch_t, co_t = draw_particle_trails(S, g, max_trail=6, fade=0.6)
    canvas_trails = g.render(ch_t, co_t)

    result = blend_canvas(canvas_bg, canvas_trails, "add", 0.3)
    result = blend_canvas(result, canvas_boids, "add", 0.9)
    return result
```

### 通过SDF文字模板呈现的火焰效果

火焰效果仅通过文字的轮廓展现出来。

```python
def fx_fire_text(r, f, t, S):
    """Fire columns visible through text stencil. Text acts as window."""
    g = r.get_grid("lg")

    # Full-screen fire (will be masked)
    canvas_fire = _render_vf(r, "sm",
        lambda g, f, t, S: np.clip(
            vf_fbm(g, f, t, S, octaves=4, freq=0.08, speed=0.8) *
            (1.0 - g.rr / g.rows) *  # fade toward top
            (0.6 + f.get("bass", 0.3) * 0.8), 0, 1),
        hf_fixed(0.05), PAL_BLOCKS, f, t, S, sat=0.9)  # fire hue

    # Background: dark domain warp
    canvas_bg = _render_vf(r, "md",
        lambda g, f, t, S: vf_domain_warp(g, f, t, S,
            warp_strength=8, freq=0.03, speed=0.05) * 0.3,
        hf_fixed(0.6), PAL_DENSE, f, t, S, sat=0.4)

    # Text stencil mask
    mask = mask_text(g, "FIRE", row_frac=0.45)
    # Expand vertically for multi-row coverage
    for offset in range(-2, 3):
        shifted = mask_text(g, "FIRE", row_frac=0.45 + offset / g.rows)
        mask = mask_union(mask, shifted)

    canvas_masked = apply_mask_canvas(canvas_fire, mask, bg_canvas=canvas_bg)
    return canvas_masked
```

### 肖像模式：垂直雨滴效果 + 引文展示

专为 9:16 比例优化。利用垂直空间呈现长长的雨滴轨迹以及层叠式的文字内容。

```python
def fx_portrait_rain_quote(r, f, t, S):
    """Portrait-optimized: matrix rain (long vertical trails) with stacked quote.
    Designed for 1080x1920 (9:16)."""
    g = r.get_grid("md")  # ~112x100 in portrait

    # Matrix rain — long trails benefit from portrait's extra rows
    ch, co, S = eff_matrix_rain(g, f, t, S,
        hue=0.33, bri=0.6, pal=PAL_KATA, speed_base=0.4, speed_beat=2.5)
    canvas_rain = g.render(ch, co)

    # Tunnel depth underneath for texture
    canvas_tunnel = _render_vf(r, "sm",
        lambda g, f, t, S: vf_tunnel(g, f, t, S, speed=3.0, complexity=6) * 0.8,
        hf_fixed(0.33), PAL_BLOCKS, f, t, S, sat=0.5)

    result = blend_canvas(canvas_tunnel, canvas_rain, "screen", 0.8)

    # Quote text — portrait layout: short lines, many of them
    g_text = r.get_grid("lg")  # ~90x80 in portrait
    quote_lines = layout_text_portrait(
        "The code is the art and the art is the code",
        max_chars_per_line=20)
    # Center vertically
    block_start = (g_text.rows - len(quote_lines)) // 2
    ch_t = np.full((g_text.rows, g_text.cols), " ", dtype="U1")
    co_t = np.zeros((g_text.rows, g_text.cols, 3), dtype=np.uint8)
    total_chars = sum(len(l) for l in quote_lines)
    progress = min(1.0, (t - S.get("_scene_start", t)) / 3.0)
    if "_scene_start" not in S: S["_scene_start"] = t
    render_typewriter(ch_t, co_t, quote_lines, block_start, g_text.cols,
                      progress, total_chars, (200, 255, 220), t)
    canvas_text = g_text.render(ch_t, co_t)

    result = blend_canvas(result, canvas_text, "add", 0.9)
    return result
```

### 场景表模板

将多个场景串联成一段完整的视频：

```python
SCENES = [
    {"start": 0.0,  "end": 5.0,  "name": "coral",
     "fx": fx_coral, "grid": "sm", "gamma": 0.70,
     "shaders": [("bloom", {"thr": 110}), ("vignette", {"s": 0.2})],
     "feedback": {"decay": 0.8, "blend": "screen", "opacity": 0.3,
                  "transform": "zoom", "transform_amt": 0.01}},

    {"start": 5.0,  "end": 15.0, "name": "tunnel_noise",
     "fx": fx_tunnel_noise, "grid": "md", "gamma": 0.75,
     "shaders": [("chromatic", {"amt": 3}), ("bloom", {"thr": 120}),
                 ("scanlines", {"intensity": 0.06}), ("grain", {"amt": 8})],
     "feedback": None},

    {"start": 15.0, "end": 35.0, "name": "cathedral",
     "fx": fx_cathedral, "grid": "sm", "gamma": 0.65,
     "shaders": [("bloom", {"thr": 100}), ("chromatic", {"amt": 5}),
                 ("color_wobble", {"amt": 0.2}), ("vignette", {"s": 0.18})],
     "feedback": {"decay": 0.75, "blend": "screen", "opacity": 0.35,
                  "transform": "zoom", "transform_amt": 0.012, "hue_shift": 0.015}},

    {"start": 35.0, "end": 50.0, "name": "morphing",
     "fx": fx_morphing_journey, "grid": "md", "gamma": 0.70,
     "shaders": [("bloom", {"thr": 110}), ("grain", {"amt": 6})],
     "feedback": {"decay": 0.7, "blend": "screen", "opacity": 0.25,
                  "transform": "rotate_cw", "transform_amt": 0.003}},
]
```
