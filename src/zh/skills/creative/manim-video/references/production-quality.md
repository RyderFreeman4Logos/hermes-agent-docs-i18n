# 生产质量检查清单

用于确保动画输出达到发布标准的各项规范与检查项。

## 编码前的检查清单

在编写任何 Manim 代码之前：

- [ ] 已撰写叙事脚本，并标注出视觉节奏节点
- [ ] 已列出场景清单，明确每个场景的功能、时长及布局
- [ ] 已定义颜色调色板，并为每种颜色指定含义（如 `PRIMARY` 表示核心主题等）
- [ ] 已将字体常量设置为 `MONO = "Menlo"`
- [ ] 已确定目标分辨率与宽高比

## 文本质量

### 防止内容重叠

```python
# RULE: buff >= 0.5 for edge text
label.to_edge(DOWN, buff=0.5)     # GOOD
label.to_edge(DOWN, buff=0.3)     # BAD — may clip

# RULE: FadeOut previous before adding new at same position
self.play(ReplacementTransform(note1, note2))  # GOOD
self.play(Write(note2))                          # BAD — overlaps note1

# RULE: Reduce font size for dense scenes
# When > 4 text elements visible, use font_size=20 not 28
```

### 宽度限制机制

过长的文本字符串会导致界面框溢出：

```python
# RULE: Set max width for any text that might be long
text = Text("This is a potentially long description", font_size=22, font=MONO)
if text.width > config.frame_width - 1.0:
    text.set_width(config.frame_width - 1.0)
```

### 字体一致性

```python
# RULE: Define MONO once, use everywhere
MONO = "Menlo"

# WRONG: mixing fonts
Text("Title", font="Helvetica")
Text("Label", font="Arial")
Text("Code", font="Courier")

# RIGHT: one font
Text("Title", font=MONO, weight=BOLD, font_size=48)
Text("Label", font=MONO, font_size=20)
Text("Code", font=MONO, font_size=18)
```

## 空间布局

### 坐标预算

可见区域的宽度约为14.2，高度约为8.0（默认比例为16:9）。并且需要预留一定的边距：

```
Usable area: x ∈ [-6.5, 6.5], y ∈ [-3.5, 3.5]
Top title zone: y ∈ [2.5, 3.5]
Bottom note zone: y ∈ [-3.5, -2.5]
Main content: y ∈ [-2.5, 2.5], x ∈ [-6.0, 6.0]
```

### 填充画面框架

空荡荡的场景会显得未完成。如果主要内容较少，可添加背景元素：
- 内容背后的暗色调网格/坐标轴
- 顶部的标题/副标题
- 底部的来源标注
- 低透明度的装饰性几何图形

### 同时显示的最大元素数量

**硬性限制：最多6个处于可见状态的元素。** 超过此数量后，观众将无法同时关注所有内容。若需要更多元素：
- 将旧元素调至0.3的透明度
- 移除已完成其功能的元素
- 将内容拆分为两个场景

## 动画质量

### 多样性检查

需确保连续的两个场景不会使用完全相同的元素：
- 动画类型（如果场景3全部使用“写入”动画，场景4则应使用“淡入”或“创建”动画）
- 颜色风格（交替使用调色板中的不同颜色）
- 布局方式（居中、左右排列、网格布局——交替使用）
- 节奏快慢（如果场景2节奏缓慢且从容，场景3则可以更快）

### 节奏曲线

优质的视频会遵循一定的节奏曲线：

```
Slow ──→ Medium ──→ FAST (climax) ──→ Slow (conclusion)

Scene 1: Slow (introduction, setup)
Scene 2: Medium (building understanding)
Scene 3: Medium-Fast (core content, lots of animation)
Scene 4: FAST (montage of applications/results)
Scene 5: Slow (conclusion, key takeaway)
```

### 过渡效果质量

场景切换时：
- **平滑退出**：使用 `self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)` 实现
- **短暂停顿**：在淡出后、下一个场景的第一个动画开始前，调用 `self.wait(0.3)`
- **杜绝生硬切换**：始终通过动画实现过渡效果

## 颜色质量

### 深色背景下的色调变化

在白色背景下显得鲜艳的色彩，在深色背景（如 #0D1117、#1C1C1C）上则会显得暗淡无光。请对您的配色方案进行测试：

```python
# Colors that work well on dark backgrounds:
# Bright and saturated: #58C4DD, #83C167, #FFFF00, #FF6B6B
# Colors that DON'T work: #666666 (invisible), #2244AA (too dark)

# RULE: Structural elements (axes, grids) at opacity 0.15
# Context elements at 0.3-0.4
# Primary elements at 1.0
```

### 颜色含义的一致性

一旦为某种颜色指定了特定含义，该颜色在整段视频中都将保持这一含义：

```python
# If PRIMARY (#58C4DD) means "the model" in Scene 1,
# it means "the model" in every scene.
# Never reuse PRIMARY for a different concept later.
```

## 数据可视化质量标准

### 图表的基本要求

- 每个坐标轴都必须标注轴标签
- Y轴的数值范围需从0开始（或设有明确的刻度分隔标识）
- 条形图/折线图的色彩需与图例一致
- 重要数据点上必须标注数值（至少包括最大值和对比值）

### 动态计数器

在显示数值变化时：
```python
# GOOD: DecimalNumber with smooth animation
counter = DecimalNumber(0, font_size=48, num_decimal_places=0, font="Menlo")
self.play(counter.animate.set_value(1000), run_time=3, rate_func=rush_from)

# BAD: Text that jumps between values
```

## 预渲染检查清单

在运行 `manim -qh` 之前，请确认：

- [ ] 所有场景使用 `-ql` 参数渲染时均无错误
- [ ] 对于文字较多的场景，使用 `-qm` 参数预览静态图片（检查字距调整情况）
- [ ] 每个场景均已设置背景颜色（`self.camera.background_color = BG`）
- [ ] 所有重要的动画都使用了 `add_subcaption()` 或 `subcaption=` 参数
- [ ] 无字体大小小于 font_size=18 的文字
- [ ] 未使用比例字体，所有文字均采用等宽字体
- [ ] 所有 `.to_edge()` 调用中的缓冲值 buff 均大于或等于 0.5
- [ ] 每个场景结尾都会执行完整淡出效果（FadeOut all）
- [ ] 每次内容展示后都添加了 `self.wait()` 延时
- [ ] 仅使用颜色常量，场景代码中无硬编码的十六进制颜色值
- [ ] 所有场景均使用相同的质量参数（不可同时混用 `-ql` 和 `-qh`）

## 后渲染检查清单

在拼接完成最终视频后，请检查：

- [ ] 以正常速度播放完整视频——是否有任何部分显得过于仓促？
- [ ] 是否存在两个元素同时动画变化从而导致视觉混乱的情况？
- [ ] 每个文字标签都有足够的时间供观众阅读
- [ ] 场景之间的切换是否流畅（无黑帧，无突兀的切换效果）？
- [ ] 若使用了旁白，其音频是否与画面同步？
- [ ] 视频给人的初始印象是否良好？前5秒足以决定观众是否会继续观看下去
