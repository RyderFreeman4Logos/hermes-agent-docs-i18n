# 故障排除

## LaTeX 错误

**缺少原始字符串**（最常见错误）：
```python
# WRONG: MathTex("\\frac{1}{2}")  -- \\f is form-feed
# RIGHT: MathTex(r"\frac{1}{2}")
```

**括号不匹配**：`MathTex(r"\frac{1}{2")` —— 缺少右括号。

**未安装 LaTeX**：运行 `which pdflatex` —— 请安装 texlive-full 或 mactex。

**缺少所需包**：需在文档开头添加相应的代码：
```python
tex_template = TexTemplate()
tex_template.add_to_preamble(r"\usepackage{mathrsfs}")
MathTex(r"\mathscr{L}", tex_template=tex_template)
```

## VGroup 类型错误

**错误信息：** `TypeError: Only values of type VMobject can be added as submobjects of VGroup`

**原因：** `Text()` 对象属于 `Mobject` 类型，而非 `VMobject` 类型。在 Manim CE v0.20 及更高版本中，将 `Text` 对象与形状一起放入 `VGroup` 中会导致错误。

```python
# WRONG: Text is not a VMobject
group = VGroup(circle, Text("Label"))

# RIGHT: use Group for mixed types
group = Group(circle, Text("Label"))

# RIGHT: VGroup is fine for shapes-only
shapes = VGroup(circle, square, arrow)

# RIGHT: MathTex IS a VMobject — VGroup works
equations = VGroup(MathTex(r"a"), MathTex(r"b"))
```

**规则：** 如果组中包含任何 `Text()` 对象，则应使用 `Group`；若所有元素均为形状或 `MathTex` 对象，使用 `VGroup` 即可。

**将所有元素设为渐隐效果：** 应始终使用 `Group(*self.mobjects)`，而非 `VGroup(*self.mobjects)`。
```python
self.play(FadeOut(Group(*self.mobjects)))  # safe for mixed types
```

## 不支持群组对象的 save_state() / restore() 方法

**错误信息：** `NotImplementedError: 请在子类中重写该功能。`

**原因：** 在 Manim CE v0.20+ 版本中，尚未实现 `Group.save_state()` 和 `Group.restore()` 方法。仅有 `VGroup` 类以及各个独立的 `Mobject` 子类支持数据的保存与恢复功能。

```python
# WRONG: Group doesn't support save_state
group = Group(circle, Text("label"))
group.save_state()  # NotImplementedError!

# RIGHT: use FadeIn with shift/scale instead of save_state/restore
self.play(FadeIn(group, shift=UP * 0.3, scale=0.8))

# RIGHT: or save/restore on individual VMobjects
circle.save_state()
self.play(circle.animate.shift(RIGHT))
self.play(Restore(circle))
```

## “letter_spacing”并非有效参数

**错误信息：** `TypeError: Mobject.__init__() got an unexpected keyword argument 'letter_spacing'`

**原因：** `Text()`函数不支持`letter_spacing`参数。Manim使用Pango进行文本渲染，因此并未在`Text()`对象中提供字距调整功能。

```python
# WRONG
Text("HERMES", letter_spacing=6)

# RIGHT: use MarkupText with Pango attributes for spacing control
MarkupText('<span letter_spacing="6000">HERMES</span>', font_size=18)
# Note: Pango letter_spacing is in 1/1024 of a point
```

## 动画错误

**动画不可见**——未添加 mobject：
```python
# WRONG: circle = Circle(); self.play(circle.animate.set_color(RED))
# RIGHT: self.play(Create(circle)); self.play(circle.animate.set_color(RED))
```

**消除混淆**——执行 Transform(A, B) 后，A 会显示在屏幕上，而 B 则不会。若需要保留 B，则请使用 ReplacementTransform。

**重复动画**——在单次播放中多次出现同一个 mobject：
```python
# WRONG: self.play(c.animate.shift(RIGHT), c.animate.set_color(RED))
# RIGHT: self.play(c.animate.shift(RIGHT).set_color(RED))
```

**更新器与动画效果的冲突问题**：
```python
mob.suspend_updating()
self.play(mob.animate.shift(RIGHT))
mob.resume_updating()
```

## 渲染问题

**输出模糊**：使用了 -ql（480p）模式。如需最终版本，请改用 -qm/-qh。

**渲染速度过慢**：开发阶段可使用 -ql 模式，并降低表面分辨率，同时缩短 self.wait() 的时间间隔。

**输出内容过时**：运行命令 `manim -ql --disable_caching script.py Scene` 可解决此问题。

**ffmpeg 合并失败**：所有视频片段必须具有相同的分辨率、帧率及编码格式。

## 常见错误

**文字出现在边缘**：对对象使用 `.to_edge()` 方法时，需设置 `buff >= 0.5`。

**文字重叠**：应使用 `ReplacementTransform(old, new)` 方法，而非直接在上方使用 `Write(new)`。

**元素过于密集**：屏幕上同时显示的元素数量不宜超过5-6个。建议将内容拆分为多个场景，或通过透明度叠加来处理。

**缺乏缓冲时间**：对象出现后至少需设置 `self.wait(1.5)` 的等待时间，关键场景则需设置为 `self.wait(2.0)`。

**缺少背景颜色**：每个场景都应设置 `self.camera.background_color = BG`。

## 调试策略

1. 渲染静态图像：运行命令 `manim -ql -s script.py Scene`，即可快速检查布局。
2. 定位问题场景：仅渲染出出现问题的那个场景。
3. 将 `self.play()` 替换为 `self.add()`，以便立即查看最终状态。
4. 打印对象位置：使用命令 `print(mob.get_center())` 查看坐标。
5. 清除缓存：删除 `media/` 目录中的文件。
