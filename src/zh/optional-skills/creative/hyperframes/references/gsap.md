# HyperFrames 的 GSAP 功能

GSAP 是所有 HyperFrames 组件所使用的动画引擎。可在组件内部通过 CDN 加载该库：

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
```

## 核心动画方法

- **`gsap.to(targets, vars)`** — 从当前状态动画过渡到 `vars` 指定的状态。最为常用。
- **`gsap.from(targets, vars)`** — 从 `vars` 指定的状态动画过渡到当前状态（用于元素进入画面时的动画）。
- **`gsap.fromTo(targets, fromVars, toVars)`** — 明确指定起始状态和结束状态。
- **`gsap.set(targets, vars)`** — 立即应用动画效果（持续时间设为 0）。不要用于稍后才会进入画面的元素——应改在时间轴中使用 `tl.set(selector, vars, time)`。

属性名称始终请使用 **驼峰命名法**（如 `backgroundColor`、`rotationX`，而非 `background-color`）。

## 常用参数

- **`duration`** — 秒数（默认值为 0.5）。
- **`delay`** — 动画开始前的延迟时间（秒数）。
- **`ease`** — 缓动函数，默认值为 `"power1.out"`，其他可选值包括 `"power3.inOut"`、`"back.out(1.7)"`、`"elastic.out(1, 0.3)"`、`"none"`、`"expo.out"`、`"circ.inOut"`。
- **`stagger`** — 数值 `0.1`，或对象形式：`{ amount: 0.3, from: "center" }`、`{ each: 0.1, from: "random" }`。
- **`overwrite`** — 默认值为 `false`，可选值为 `true` 或 `"auto"`。
- **`repeat`** — 数值（在 HyperFrames 中不可设置为 `-1`）。**`yoyo`** — 结合 `repeat` 参数实现方向交替动画。
- **`onComplete`**、**`onStart`**、**`onUpdate`** — 回调函数。
- **`immediateRender`** — 对于 `from()`/`fromTo()` 方法，默认值为 `true`。若后续针对同一属性和元素进行动画，可将该值设为 `false`，以避免意外覆盖效果。

## 变形动画

建议优先使用 GSAP 提供的变形相关属性别名，而非直接的 CSS `transform` 属性：

| GSAP 属性               | 对应的 CSS 属性               |
| --------------------------- | ---------------------------- |
| `x`, `y`, `z`               | translateX/Y/Z (像素)        |
| `xPercent`, `yPercent`      | translateX/Y (%)           |
| `scale`, `scaleX`, `scaleY` | scale                      |
| `rotation`                  | rotate (度数)               |
| `rotationX`, `rotationY`    | 3D 旋转                     |
| `skewX`, `skewY`            | skew                       |
| `transformOrigin`           | transform-origin           |

- **`autoAlpha`** — 建议优先使用此属性而非 `opacity`。当其值为 0 时，同时会将元素的 `visibility` 属性设置为 `hidden`。
- **CSS 变量** — 例如 `"--hue": 180`。
- **方向性旋转** — 例如 `"360_cw"`、`"-170_short"`、`"90_ccw"`。
- **`clearProps`** — 参数值为 `"all"` 或用逗号分隔的多个值；动画完成后会移除元素的内联样式。
- **相对数值** — 例如 `"+=20"`、`"-=10"`、`"*=2"`。

## 基于函数的值

```js
gsap.to(".item", {
  x: (i, target, targets) => i * 50,
  stagger: 0.1,
});
```

## 缓动效果

内置缓动函数包括：`power1` 至 `power4`、`back`、`bounce`、`circ`、`elastic`、`expo`、`sine`。每种缓动函数均提供 `.in`、`.out`、`.inOut` 三种形式。

常用参考规则：
- 进入阶段：`power3.out`、`expo.out`、`back.out(1.4)`
- 离开阶段：`power2.in`、`expo.in`
- 被擦除区域：`none`（线性过渡）
- 在同一场景中的不同进入过渡部分应使用不同的缓动效果——至少需有3种不同的缓动函数。

## 默认设置

```js
gsap.defaults({ duration: 0.6, ease: "power2.out" });
```

## 时间轴（HyperFrames的主要使用模式）

```js
window.__timelines = window.__timelines || {};

const tl = gsap.timeline({ paused: true, defaults: { duration: 0.6, ease: "power2.out" } });

tl.from(".title",    { y: 50, opacity: 0 }, 0.3);
tl.from(".subtitle", { y: 30, opacity: 0 }, 0.5);
tl.from(".cta",      { scale: 0.8, opacity: 0, ease: "back.out(1.7)" }, 0.8);

window.__timelines["root"] = tl;
```

### 位置参数

`.from()` / `.to()` / `.add()` 方法的第三个参数：

- 绝对秒数：`0.5`、`2.1`。
- 相对于结束时间：`">+0.2"`（在之前时间点后0.2秒）、`"<"`（与之前时间点相同）、`"<+0.3"`（在之前时间点开始后0.3秒）。
- 命名标签：`tl.addLabel("act2", 5); tl.from(".x", { y: 30 }, "act2");`

### 嵌套

HyperFrames会自动对子组合时间轴进行嵌套。**请勿**手动调用 `tl.add(subTl)` —— 该框架会在子组合的 `data-start` 时间点将子时间轴连接到父时间轴中。

### 播放

播放控制由播放器负责。在构建阶段不要调用 `tl.play()`、`tl.pause()` 或 `tl.reverse()` 方法。必须使用 `{ paused: true }` 参数。 

## 错开播放

```js
// even distribution
tl.from(".card", { opacity: 0, y: 40, stagger: 0.1 });

// control total amount
tl.from(".card", { opacity: 0, stagger: { amount: 0.6, from: "center" } });

// deterministic "random" stagger (HyperFrames compositions must be deterministic)
tl.from(".dot", { opacity: 0, stagger: { each: 0.05, from: "random" } });
```

`stagger.from`：`"start"` | `"end"` | `"center"` | `"edges"` | `"random"` | 索引 | 网格格式下的 `[x, y]`。

## 性能优化

- 动画化变换属性（如 `x`、`y`、`scale`、`rotation`、`opacity`）——操作成本低，且可借助 GPU 加速。
- 避免动画化 `width`、`height`、`top`、`left`、`margin` 等属性——这会导致布局频繁重算。
- 避免对大型元素应用 box-shadow 或 filter 动画——此类操作成本较高。
- 几乎无需使用 `will-change` 属性，GSAP 会自动处理相关优化。

## gsap.matchMedia（在 HyperFrames 中极少需要）

由于合成内容的尺寸是固定的（通过 `data-width`/`data-height` 指定），因此无需考虑响应式断点。在制作 UI 预览时，仍可为 `prefers-reduced-motion` 设置使用 `matchMedia`，但在实际渲染的视频输出中则不会用到该功能。

## 应避免的做法

- 在任何地方使用 `repeat: -1`——这会破坏捕获引擎的正常运行。
- 在动画过渡值中使用 `Math.random()`、`Date.now()`、`performance.now()` 等函数——会导致结果不可预测。
- 在时间轴构建过程中使用 `async`、`setTimeout` 或 `Promise`——捕获引擎会以同步方式读取 `window.__timelines`。
- 直接动画化 `visibility` 或 `display` 属性——应改用 `autoAlpha`。
- 对在时间轴中后期才出现的剪辑元素使用 `gsap.set()`——因为页面加载时这些元素还不存在于 DOM 中。应在时间轴内部使用 `tl.set(sel, vars, time)` 方法。
