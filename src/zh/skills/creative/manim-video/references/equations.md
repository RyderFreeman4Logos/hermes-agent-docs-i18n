# 方程式与 LaTeX 参考手册

## 基础 LaTeX 用法

```python
eq = MathTex(r"E = mc^2")
eq = MathTex(r"f(x) &= x^2 + 2x + 1 \\ &= (x + 1)^2")  # multi-line aligned
```

**始终请使用原始字符串（`r""`）。**

## 逐步推导过程

```python
step1 = MathTex(r"a^2 + b^2 = c^2")
step2 = MathTex(r"a^2 = c^2 - b^2")
self.play(Write(step1), run_time=1.5)
self.wait(1.5)
self.play(TransformMatchingTex(step1, step2), run_time=1.5)
```

## 选择性上色

```python
eq = MathTex(r"a^2", r"+", r"b^2", r"=", r"c^2")
eq[0].set_color(RED)
eq[4].set_color(GREEN)
```

## 逐步构建

```python
parts = MathTex(r"f(x)", r"=", r"\sum_{n=0}^{\infty}", r"\frac{f^{(n)}(a)}{n!}", r"(x-a)^n")
self.play(Write(parts[0:2]))
self.wait(0.5)
self.play(Write(parts[2]))
self.wait(0.5)
self.play(Write(parts[3:]))
```

## 高亮显示功能

```python
highlight = SurroundingRectangle(eq[2], color=YELLOW, buff=0.1)
self.play(Create(highlight))
self.play(Indicate(eq[4], color=YELLOW))
```

## 注解说明

```python
brace = Brace(eq, DOWN, color=YELLOW)
label = brace.get_text("Fundamental Theorem", font_size=24)
self.play(GrowFromCenter(brace), Write(label))
```

## 常用 LaTeX 代码

```python
MathTex(r"\frac{a}{b}")                  # fraction
MathTex(r"\alpha, \beta, \gamma")         # Greek
MathTex(r"\sum_{i=1}^{n} x_i")           # summation
MathTex(r"\int_{0}^{\infty} e^{-x} dx")  # integral
MathTex(r"\vec{v}")                       # vector
MathTex(r"\lim_{x \to \infty} f(x)")    # limit
```

## 矩阵

`MathTex` 支持通过 `amsmath`（默认已加载）来使用标准的 LaTeX 矩阵环境：

```python
# Bracketed matrix
MathTex(r"\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}")

# Parenthesized matrix
MathTex(r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}")

# Determinant (vertical bars)
MathTex(r"\begin{vmatrix} a & b \\ c & d \end{vmatrix}")

# Plain (no delimiters)
MathTex(r"\begin{matrix} x_1 \\ x_2 \\ x_3 \end{matrix}")
```

对于矩阵类型，若需逐元素设置动画或单独更改特定单元格的颜色，建议使用 `IntegerMatrix`、`DecimalMatrix` 或 `MobjectMatrix` 这类 mobject——详情请参阅 `mobjects.md`。

## 分段函数与条件函数

```python
MathTex(r"""
    f(x) = \begin{cases}
        x^2    & \text{if } x \geq 0 \\
        -x^2   & \text{if } x < 0
    \end{cases}
""")
```

## 对齐环境

对于需要内容对齐的多行推导式，可在 `MathTex` 中使用 `aligned` 标签：

```python
MathTex(r"""
    \begin{aligned}
        \nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\
        \nabla \cdot \mathbf{B} &= 0 \\
        \nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
        \nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}
    \end{aligned}
""")
```

注意：`MathTex` 默认会将内容包裹在 `align*` 中。如有需要，可通过 `tex_environment` 进行自定义设置。
```python
MathTex(r"...", tex_environment="gather*")
```

## 推导模式

```python
class DerivationScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        s1 = MathTex(r"ax^2 + bx + c = 0")
        self.play(Write(s1))
        self.wait(1.5)
        s2 = MathTex(r"x^2 + \frac{b}{a}x + \frac{c}{a} = 0")
        s2.next_to(s1, DOWN, buff=0.8)
        self.play(s1.animate.set_opacity(0.4), TransformMatchingTex(s1.copy(), s2))
```

## 复杂方程中的子串隔离功能

对于那些难以手动拆分、结构较为复杂的方程，可使用 `substrings_to_isolate` 函数来指定 Manim 应将哪些子串视为独立元素进行处理：

```python
# Without isolation — the whole expression is one blob
lagrangian = MathTex(
    r"\mathcal{L} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}"
)

# With isolation — each named substring is a separate submobject
lagrangian = MathTex(
    r"\mathcal{L} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}",
    substrings_to_isolate=[r"\psi", r"D_\mu", r"\gamma^\mu", r"F_{\mu\nu}"]
)
# Now you can color individual terms
lagrangian.set_color_by_tex(r"\psi", BLUE)
lagrangian.set_color_by_tex(r"F_{\mu\nu}", YELLOW)
```

对于包含复杂公式的“转换匹配文本”功能而言，这是不可或缺的——若无法对公式进行隔离处理，密集的表达式将无法实现正确匹配。

## 多行复杂公式

对于由多行相关内容构成的公式，需将每一行作为独立的参数传入：

```python
maxwell = MathTex(
    r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}",
    r"\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}"
).arrange(DOWN)

# Each line is a separate submobject — animate independently
self.play(Write(maxwell[0]))
self.wait(1)
self.play(Write(maxwell[1]))
```

## 使用 key_map 对 TransformMatchingTex 进行转换

在转换过程中，可建立源方程与目标方程之间特定子字符串的映射关系：

```python
eq1 = MathTex(r"A^2 + B^2 = C^2")
eq2 = MathTex(r"A^2 = C^2 - B^2")

self.play(TransformMatchingTex(
    eq1, eq2,
    key_map={"+": "-"},   # map "+" in source to "-" in target
    path_arc=PI / 2,      # arc the pieces into position
))
```

## set_color_by_tex — 根据子字符串设置颜色

```python
eq = MathTex(r"E = mc^2")
eq.set_color_by_tex("E", BLUE)
eq.set_color_by_tex("m", RED)
eq.set_color_by_tex("c", GREEN)
```

## 使用 matched_keys 对 TransformMatchingTex 进行转换

当匹配的子串存在歧义时，可明确指定应对应哪个子串：

```python
kw = dict(font_size=72, t2c={"A": BLUE, "B": TEAL, "C": GREEN})
lines = [
    MathTex(r"A^2 + B^2 = C^2", **kw),
    MathTex(r"A^2 = C^2 - B^2", **kw),
    MathTex(r"A^2 = (C + B)(C - B)", **kw),
    MathTex(r"A = \sqrt{(C + B)(C - B)}", **kw),
]

self.play(TransformMatchingTex(
    lines[0].copy(), lines[1],
    matched_keys=["A^2", "B^2", "C^2"],  # explicitly match these
    key_map={"+": "-"},                    # map + to -
    path_arc=PI / 2,                       # arc pieces into position
))
```

若未设置 `matched_keys`，该动画功能将会匹配最长的公共子串，这在处理复杂方程式时可能会导致意外结果（例如将不同项之间的“^2 = C^2”视为匹配）。
