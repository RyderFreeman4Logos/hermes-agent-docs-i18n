# 更新器与值追踪器

## 更新器解决的问题

普通动画是离散的：`self.play()` 仅能让对象从状态 A 转变为状态 B。但若需要保持连续的关系——比如让标签始终悬浮在移动的点上方，或让线条始终连接两个点——该怎么办？

如果没有更新器，就必须在每次调用 `self.play()` 前手动重新定位所有依赖对象。若有五个动画都在移动一个点，那么标签就需要进行五次手动重定位操作。一旦遗漏其中一次，标签就会固定在错误的位置。

更新器允许你只需声明一次关系。Manim 会以每帧（根据画质不同为15-60帧/秒）的频率调用该更新器函数，从而确保无论发生什么情况，这种关系都能得以维持。

## ValueTracker：无形的控制杆

ValueTracker 是一种不可见的 Mobject，用于存储一个浮点数值。它永远不会显示在屏幕上，存在的意义在于让你能够为其设置动画，同时让其他对象根据其数值做出响应。

可以将其想象成一个滑块：将滑块从0拖动到5，所有与之关联的对象都会实时作出反应。

```python
tracker = ValueTracker(0)        # invisible, stores 0.0
tracker.get_value()              # read: 0.0
tracker.set_value(5)             # write: jump to 5.0 instantly
tracker.animate.set_value(5)     # animate: smoothly interpolate to 5.0
```

### 三步操作模式

所有 ValueTracker 的使用均遵循以下步骤：

1. **创建追踪器**（即那个不可见的滑块）
2. **创建可通过更新器读取该追踪器值的可见对象**
3. **为追踪器添加动画效果**——所有关联对象将自动随之更新

```python
# Step 1: Create tracker
x_tracker = ValueTracker(1)

# Step 2: Create dependent objects
dot = always_redraw(lambda: Dot(axes.c2p(x_tracker.get_value(), 0), color=YELLOW))
v_line = always_redraw(lambda: axes.get_vertical_line(
    axes.c2p(x_tracker.get_value(), func(x_tracker.get_value())), color=BLUE
))
label = always_redraw(lambda: DecimalNumber(x_tracker.get_value(), font_size=24)
    .next_to(dot, UP))

self.add(dot, v_line, label)

# Step 3: Animate the tracker — everything follows
self.play(x_tracker.animate.set_value(5), run_time=3)
```

## 更新器类型

### Lambda更新器（最常用）

会在每一帧中调用一个函数，并将该mobject本身作为参数传递：

```python
# Label always stays above the dot
label.add_updater(lambda m: m.next_to(dot, UP, buff=0.2))

# Line always connects two points
line.add_updater(lambda m: m.put_start_and_end_on(
    point_a.get_center(), point_b.get_center()
))
```

### 基于时间的更新器（含 dt 参数）

第二个参数 `dt` 表示自上一帧以来的时间间隔（在 60fps 下约为 0.017 秒）：

```python
# Continuous rotation
square.add_updater(lambda m, dt: m.rotate(0.5 * dt))

# Continuous rightward drift
dot.add_updater(lambda m, dt: m.shift(RIGHT * 0.3 * dt))

# Oscillation
dot.add_updater(lambda m, dt: m.move_to(
    axes.c2p(m.get_center()[0], np.sin(self.time))
))
```

对于物理模拟、连续运动以及与时间相关的效果，建议使用 `dt` 更新器。

### always_redraw：每帧完全重绘

该模式会在每一帧从头开始创建一个新的 mobject。虽然其性能开销高于 `add_updater`，但能够处理 mobject 结构发生变化的情况（而不仅仅是位置或颜色的变化）：

```python
# Brace that follows a resizing square
brace = always_redraw(Brace, square, UP)

# Area under curve that updates as function changes
area = always_redraw(lambda: axes.get_area(
    graph, x_range=[0, x_tracker.get_value()], color=BLUE, opacity=0.3
))

# Label that reconstructs its text
counter = always_redraw(lambda: Text(
    f"n = {int(x_tracker.get_value())}", font_size=24, font="Menlo"
).to_corner(UR))
```

**何时使用哪种方式：**
- `add_updater` — 用于调整位置、颜色和透明度（成本较低，推荐使用）
- `always_redraw` — 用于形状或结构本身发生改变时（成本较高，应谨慎使用）

## DecimalNumber：实时显示数值

```python
# Counter that tracks a ValueTracker
tracker = ValueTracker(0)
number = DecimalNumber(0, font_size=48, num_decimal_places=1, color=PRIMARY)
number.add_updater(lambda m: m.set_value(tracker.get_value()))
number.add_updater(lambda m: m.next_to(dot, RIGHT, buff=0.3))

self.add(number)
self.play(tracker.animate.set_value(100), run_time=3)
```

### 变量：带标签的版本

```python
var = Variable(0, Text("x", font_size=24, font="Menlo"), num_decimal_places=2)
self.add(var)
self.play(var.tracker.animate.set_value(PI), run_time=2)
# Displays: x = 3.14
```

## 移除更新工具

```python
# Remove all updaters
mobject.clear_updaters()

# Suspend temporarily (during an animation that would fight the updater)
mobject.suspend_updating()
self.play(mobject.animate.shift(RIGHT))
mobject.resume_updating()

# Remove specific updater (if you stored a reference)
def my_updater(m):
    m.next_to(dot, UP)
label.add_updater(my_updater)
# ... later ...
label.remove_updater(my_updater)
```

## 基于动画的更新器

### UpdateFromFunc / UpdateFromAlphaFunc

这些属于动画类型（通过 `self.play` 传递），而非持久型更新器：

```python
# Call a function on each frame of the animation
self.play(UpdateFromFunc(mobject, lambda m: m.next_to(moving_target, UP)), run_time=3)

# With alpha (0 to 1) — useful for custom interpolation
self.play(UpdateFromAlphaFunc(circle, lambda m, a: m.set_fill(opacity=a)), run_time=2)
```

### turn_animation_into_updater

将一次性动画转换为连续更新器：

```python
from manim import turn_animation_into_updater

# This would normally play once — now it loops forever
turn_animation_into_updater(Rotating(gear, rate=PI/4))
self.add(gear)
self.wait(5)  # gear rotates for 5 seconds
```

## 实用模式

### 模式 1：使用点号追踪函数调用路径

```python
tracker = ValueTracker(0)
graph = axes.plot(np.sin, x_range=[0, 2*PI], color=PRIMARY)
dot = always_redraw(lambda: Dot(
    axes.c2p(tracker.get_value(), np.sin(tracker.get_value())),
    color=YELLOW
))
tangent = always_redraw(lambda: axes.get_secant_slope_group(
    x=tracker.get_value(), graph=graph, dx=0.01,
    secant_line_color=HIGHLIGHT, secant_line_length=3
))

self.add(graph, dot, tangent)
self.play(tracker.animate.set_value(2*PI), run_time=6, rate_func=linear)
```

### 模式2：曲线下方实时区域

```python
tracker = ValueTracker(0.5)
area = always_redraw(lambda: axes.get_area(
    graph, x_range=[0, tracker.get_value()],
    color=PRIMARY, opacity=0.3
))
area_label = always_redraw(lambda: DecimalNumber(
    # Numerical integration
    sum(func(x) * 0.01 for x in np.arange(0, tracker.get_value(), 0.01)),
    font_size=24
).next_to(axes, RIGHT))

self.add(area, area_label)
self.play(tracker.animate.set_value(4), run_time=5)
```

### 模式 3：关联图谱

```python
# Nodes that can be moved, with edges that auto-follow
node_a = Dot(LEFT * 2, color=PRIMARY)
node_b = Dot(RIGHT * 2, color=SECONDARY)
edge = Line().add_updater(lambda m: m.put_start_and_end_on(
    node_a.get_center(), node_b.get_center()
))
label = Text("edge", font_size=18, font="Menlo").add_updater(
    lambda m: m.move_to(edge.get_center() + UP * 0.3)
)

self.add(node_a, node_b, edge, label)
self.play(node_a.animate.shift(UP * 2), run_time=2)
self.play(node_b.animate.shift(DOWN + RIGHT), run_time=2)
# Edge and label follow automatically
```

### 模式4：参数探索

```python
# Explore how a parameter changes a curve
a_tracker = ValueTracker(1)
curve = always_redraw(lambda: axes.plot(
    lambda x: a_tracker.get_value() * np.sin(x),
    x_range=[0, 2*PI], color=PRIMARY
))
param_label = always_redraw(lambda: Text(
    f"a = {a_tracker.get_value():.1f}", font_size=24, font="Menlo"
).to_corner(UR))

self.add(curve, param_label)
self.play(a_tracker.animate.set_value(3), run_time=3)
self.play(a_tracker.animate.set_value(0.5), run_time=2)
self.play(a_tracker.animate.set_value(1), run_time=1)
```

## 常见错误

1. **更新器干扰动画效果**：如果某个 mobject 拥有用于设置其位置的更新器，而您又试图在其他地方对其进行动画处理，那么在每一帧中更新器都会占据主导地位。此时应先暂停更新操作。

2. **简单移动时滥用 always_redraw**：如果仅需调整对象位置，应使用 `add_updater` 函数。而 `always_redraw` 会在每一帧都重新构建整个 mobject——这不仅效率低下，对于仅进行位置追踪而言也毫无必要。

3. **忘记将对象添加到场景中**：更新器仅能在场景中的 mobject 上运行。虽然 `always_redraw` 会创建该 mobject，但您仍需通过 `self.add()` 方法将其加入场景。

4. **更新器创建新对象却未进行清理**：如果您的更新器在每一帧都创建 Text 对象，这些对象会不断累积。此时应使用能自动处理清理工作的 `always_redraw`，或直接修改对象的属性。
