# 视觉设计原则

## 12项核心原则

1. **先几何形态，后代数公式** —— 先展示形状，再呈现方程式。
2. **透明度分层** —— PRIMARY层透明度为1.0，CONTEXT层为0.4，GRID层为0.15。通过亮度差异引导视觉焦点。
3. **每个场景一个新概念** —— 每个场景仅引入一个概念。
4. **空间一致性** —— 同一概念在整个画面中始终占据相同区域。
5. **颜色即含义** —— 为概念而非mobject分配颜色。若速度用蓝色表示，则始终保持为蓝色。
6. **渐进式展示** —— 先呈现最简版本，再逐步增加复杂性。
7. **变换而非替换** —— 使用Transform/ReplacementTransform来展示元素间的关联。
8. **留出呼吸空间** —— 展示新内容后至少等待1.5秒。
9. **视觉权重平衡** —— 避免将所有元素集中在画面一侧。
10. **统一的运动表现方式** —— 选择少量动画类型并反复使用。
11. **深色背景搭配浅色内容** —— 使用#1C1C1C至#2D2B55的背景可最大化对比度。
12. **刻意留白** —— 至少保留15%的画幅空白区域。

## 布局模板

### FULL_CENTER
一个主要元素居中显示，标题在上方，说明在下方。
适用场景：单个方程式、单个图表、标题卡片。

### LEFT_RIGHT
两个元素并排位于x=-3.5和x=3.5位置。
适用场景：公式与图形结合展示、前后对比、对照分析。

### TOP_BOTTOM
主要元素位于y=1.5位置，辅助内容位于y=-1.5位置。
适用场景：概念与示例搭配、定理与实例结合。

### GRID
通过`arrange_in_grid()`函数排列多个元素。
适用场景：对比矩阵、多步骤流程展示。

### PROGRESSIVE
元素依次逐个出现，沿垂直方向排列且对齐边为左侧。
适用场景：算法演示、证明过程、分步操作展示。

### ANNOTATED_DIAGRAM
中心为图表，周围通过箭头连接浮动标签。
适用场景：架构图、带注释的图形。

## 颜色方案

### 经典3B1B方案
```python
BG="#1C1C1C"; PRIMARY=BLUE; SECONDARY=GREEN; ACCENT=YELLOW; HIGHLIGHT=RED
```

### 智慧学术助手
```python
BG="#2D2B55"; PRIMARY="#FF6B6B"; SECONDARY="#FFD93D"; ACCENT="#6BCB77"
```

### Neon Tech 技术文档
```python
BG="#0A0A0A"; PRIMARY="#00F5FF"; SECONDARY="#FF00FF"; ACCENT="#39FF14"
```

## 字体选择

**建议为所有文本使用等宽字体。** Manim的Pango文本渲染引擎在所有尺寸和分辨率下，使用比例字体（如Helvetica、Inter、SF Pro、Arial）时都会出现字距调整异常的问题。字符之间会出现重叠，且间距也不均匀。这是Pango本身的固有限制，并非Manim的漏洞。

等宽字体的每个字符宽度是固定的——从设计上就不存在字距调整的问题。

### 推荐字体

| 使用场景 | 推荐字体 | 备用字体 |
|----------|----------|----------|
| **所有文本（默认）** | `"Menlo"` | `"Courier New"`, `"DejaVu Sans Mono"` |
| 代码、标签 | `"JetBrains Mono"`, `"SF Mono"` | `"Menlo"` |
| 数学公式 | 使用`MathTex`（通过LaTeX而非Pango进行渲染） | — |

```python
MONO = "Menlo"  # define once at top of file

title = Text("Fourier Series", font_size=48, color=PRIMARY, weight=BOLD, font=MONO)
label = Text("n=1: (4/pi) sin(x)", font_size=20, color=BLUE, font=MONO)
note = Text("Convergence at discontinuities", font_size=18, color=DIM, font=MONO)

# Math — always use MathTex, not Text
equation = MathTex(r"\nabla L = \frac{\partial L}{\partial w}")
```

### 何时可使用等宽字体

对于较大的标题文字（字体大小 ≥ 48），且文本长度较短（1-3个单词）的情况，使用等宽字体不会出现明显的字距问题。而对于其他类型的文本——如标签、描述、多词文本或较小尺寸的文字——则应使用等宽字体。

### 字体可用性

- **macOS**：Menlo（预装）、SF Mono  
- **Linux**：DejaVu Sans Mono（预装）、Liberation Mono  
- **跨平台**：JetBrains Mono（可从 jetbrains.com 安装）

`"Menlo"` 是最安全的默认选择——它在 macOS 上已预装，而 Linux 系统则会回退到 DejaVu Sans Mono。

### 更精细的文本控制

`Text()` 函数不支持 `letter_spacing` 或字距调整参数。如需更精细的控制，可使用带有 Pango 属性的 `MarkupText`。

```python
# Letter spacing (Pango units: 1/1024 of a point)
MarkupText('<span letter_spacing="6000">HERMES</span>', font_size=18, font="Menlo")

# Bold specific words
MarkupText('This is <b>important</b>', font_size=24, font="Menlo")

# Color specific words
MarkupText('Red <span foreground="#FF6B6B">warning</span>', font_size=24, font="Menlo")
```

### 最小字体大小

无论在何种分辨率下，`font_size=18`都是确保文字可读性的最低值。若小于18，文本在`-ql`模式下会显得模糊不清，即便在`-qh`模式下也几乎难以辨认。

## 视觉层次结构检查清单

针对每一帧画面：
1. 最应吸引注意的元素是什么？（最亮/最大的内容）
2. 背景信息是什么？（亮度调至0.3-0.4）
3. 结构性元素是什么？（亮度调至0.15）
4. 空白空间是否充足？（占比需大于15%）
5. 所有文字在手机屏幕尺寸下是否均可清晰阅读？
