# 装饰元素与视觉美化

装饰元素是一种特殊的mobject，用于标注、突出显示或框选其他mobject。它们能将技术上正确的动画转化为视觉效果出色的作品。

## SurroundingRectangle

在任意mobject周围绘制一个矩形框。是用于突出显示目标对象的常用工具：

```python
highlight = SurroundingRectangle(
    equation[2],            # the term to highlight
    color=YELLOW,
    buff=0.15,              # padding between content and border
    corner_radius=0.1,      # rounded corners
    stroke_width=2
)
self.play(Create(highlight))
self.wait(1)
self.play(FadeOut(highlight))
```

### 围绕方程的某一部分

```python
eq = MathTex(r"E", r"=", r"m", r"c^2")
box = SurroundingRectangle(eq[2:], color=YELLOW, buff=0.1)  # highlight "mc²"
label = Text("mass-energy", font_size=18, font="Menlo", color=YELLOW)
label.next_to(box, DOWN, buff=0.2)
self.play(Create(box), FadeIn(label))
```

## BackgroundRectangle

在复杂场景中提升文字可读性，为文本提供半透明背景：

```python
bg = BackgroundRectangle(equation, fill_opacity=0.7, buff=0.2, color=BLACK)
self.play(FadeIn(bg), Write(equation))

# Or using set_stroke for a "backdrop" effect on the text itself:
label.set_stroke(BLACK, width=5, background=True)
```

对于叠加在图表上的文字标签而言，使用 `set_stroke(background=True)` 的方式更为简洁。

## 大括号与 BraceLabel

用于标注图表或公式中各部分内容的花括号：

```python
brace = Brace(equation[2:4], DOWN, color=YELLOW)
brace_label = brace.get_text("these terms", font_size=20)
self.play(GrowFromCenter(brace), FadeIn(brace_label))

# Between two specific points
brace = BraceBetweenPoints(point_a, point_b, direction=UP)
```

### 支架放置位置

```python
# Below a group
Brace(group, DOWN)
# Above a group
Brace(group, UP)
# Left of a group
Brace(group, LEFT)
# Right of a group
Brace(group, RIGHT)
```

## 注释用箭头

### 指向 mobject 的实线箭头

```python
arrow = Arrow(
    start=label.get_bottom(),
    end=target.get_top(),
    color=YELLOW,
    stroke_width=2,
    buff=0.1,                    # gap between arrow tip and target
    max_tip_length_to_length_ratio=0.15  # small arrowhead
)
self.play(GrowArrow(arrow), FadeIn(label))
```

### 弧形箭头

```python
arrow = CurvedArrow(
    start_point=source.get_right(),
    end_point=target.get_left(),
    angle=PI/4,                  # curve angle
    color=PRIMARY
)
```

### 使用箭头进行标记

```python
# LabeledArrow: arrow with built-in text label
arr = LabeledArrow(
    Text("gradient", font_size=16, font="Menlo"),
    start=point_a, end=point_b, color=RED
)
```

## DashedLine与DashedVMobject

```python
# Dashed line (for asymptotes, construction lines, implied connections)
asymptote = DashedLine(
    axes.c2p(2, -3), axes.c2p(2, 3),
    color=YELLOW, dash_length=0.15
)

# Make any VMobject dashed
dashed_circle = DashedVMobject(Circle(radius=2, color=BLUE), num_dashes=30)
```

## 角度标记与直角标记

```python
line1 = Line(ORIGIN, RIGHT * 2)
line2 = Line(ORIGIN, UP * 2 + RIGHT)

# Angle arc between two lines
angle = Angle(line1, line2, radius=0.5, color=YELLOW)
angle_value = angle.get_value()  # radians

# Right angle marker (the small square)
right_angle = RightAngle(line1, Line(ORIGIN, UP * 2), length=0.3, color=WHITE)
```

## 跨项标记（划线）

用于将某内容标记为错误或已过时：

```python
cross = Cross(old_equation, color=RED, stroke_width=4)
self.play(Create(cross))
# Then show the correct version
```

## 下划线功能

```python
underline = Underline(important_text, color=ACCENT, stroke_width=3)
self.play(Create(underline))
```

## 颜色高亮工作流程

### 方法一：在创建时通过 t2c 实现

```python
text = Text("The gradient is negative here", t2c={"gradient": BLUE, "negative": RED})
```

### 方法二：在创建后通过 set_color_by_tex 设置颜色

```python
eq = MathTex(r"\nabla L = -\frac{\partial L}{\partial w}")
eq.set_color_by_tex(r"\nabla", BLUE)
eq.set_color_by_tex(r"\partial", RED)
```

### 方法 3：对子对象进行索引

```python
eq = MathTex(r"a", r"+", r"b", r"=", r"c")
eq[0].set_color(RED)    # "a"
eq[2].set_color(BLUE)   # "b"
eq[4].set_color(GREEN)  # "c"
```

## 组合标注功能

叠加多个标注以增强表达效果：

```python
# Highlight a term, add a brace, and an arrow — in sequence
box = SurroundingRectangle(eq[2], color=YELLOW, buff=0.1)
brace = Brace(eq[2], DOWN, color=YELLOW)
label = brace.get_text("learning rate", font_size=18)

self.play(Create(box))
self.wait(0.5)
self.play(FadeOut(box), GrowFromCenter(brace), FadeIn(label))
self.wait(1.5)
self.play(FadeOut(brace), FadeOut(label))
```

### 注解的生命周期

注解的呈现应遵循一定的节奏：
1. **出现**——吸引注意力（使用 Create、GrowFromCenter 功能）
2. **保持**——让观众能够阅读并理解内容（通过 self.wait 实现）
3. **消失**——为后续内容腾出展示空间（使用 FadeOut 功能）

切勿让注解无限期地显示在屏幕上——一旦其作用达成，它们就会变成视觉干扰。
