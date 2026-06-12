# 组合内容创作

包括 HTML 结构、数据属性、时间线规范以及不可违背的规则。

## 根结构

独立的 `index.html` 文件即为核心组合内容。**不使用 `<template>` 标签**，需将 `data-composition-id` div 直接放置在 `<body>` 中。

```html
<!doctype html>
<html>
  <body>
    <div
      id="stage"
      data-composition-id="root"
      data-start="0"
      data-duration="10"
      data-width="1920"
      data-height="1080"
    >
      <!-- clips go here -->
      <video id="clip-1" data-start="0" data-duration="5" data-track-index="0" src="intro.mp4" muted playsinline></video>
      <img id="logo" data-start="2" data-duration="3" data-track-index="1" src="logo.png" />
      <audio id="music" data-start="0" data-duration="10" data-track-index="2" data-volume="0.5" src="music.wav"></audio>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      tl.from("#logo", { opacity: 0, y: 40, duration: 0.6 }, 2);
      window.__timelines["root"] = tl;
    </script>
  </body>
</html>
```

通过 `data-composition-src` 加载的子组合**必须**使用 `<template>` 标签：

```html
<template id="my-comp-template">
  <div data-composition-id="my-comp" data-width="1920" data-height="1080">
    <!-- content + scoped <style> + <script> with window.__timelines["my-comp"] -->
  </div>
</template>
```

从根层级加载：<div id="el-1" data-composition-id="my-comp" data-composition-src="compositions/my-comp.html" data-start="0" data-duration="10" data-track-index="1"></div>

## 数据属性

### 所有片段

| 属性                | 是否必填 | 取值说明                                 |
|---------------------|----------|------------------------------------------|
| `id`                | 是       | 唯一标识符                               |
| `data-start`         | 是       | 秒数，或片段 ID 引用（如 `"el-1"`、`"intro + 2"`） |
| `data-duration`     | 图片/div/组合片段必填 | 秒数。视频/音频则默认使用媒体本身的时长   |
| `data-track-index`   | 是       | 整数。同一轨道上的片段不能重叠             |
| `data-media-start`  | 否       | 源文件的裁剪偏移量（秒数）                 |
| `data-volume`       | 否       | 0–1（默认值为 1）                         |

`data-track-index` 仅用于控制时间轴布局，**不**影响视觉层次。如需控制层级，请使用 CSS 的 `z-index` 属性。

### 组合片段

| 属性                    | 是否必填 | 取值说明                                 |
| -------------------------- | -------- | ------------------------------------------ |
| `data-composition-id`    | 是       | 唯一的组合片段 ID                         |
| `data-start`              | 是       | 开始时间（根级组合片段为 `"0"`）           |
| `data-duration`            | 是       | 其优先级高于 GSAP 时间轴的时长设置         |
| `data-width` / `data-height` | 是       | 像素尺寸（1920x1080 或 1080x1920）        |
| `data-composition-src`    | 否       | 外部 HTML 文件的路径                     |

## 时间轴规范

- 所有时间轴初始状态均为 `{ paused: true }`——播放控制由播放器负责。
- 需为每个时间轴进行注册：`window.__timelines["<composition-id>"] = tl`。
- 时长取自 `data-duration`，而非 GSAP 时间轴的时长值。
- 框架会自动嵌套子时间轴——无需手动添加。
- 绝对不要仅为设置时长而创建空动画过渡。

## 不可违反的规则

1. **确定性原则。** 禁止使用 `Math.random()`、`Date.now()` 或任何基于时间的逻辑。如需伪随机效果，可使用带种子的伪随机数生成器（如 mulberry32）。
2. **仅对视觉属性使用 GSAP。** 仅可动画化 `opacity`、`x`、`y`、`scale`、`rotation`、`color`、`backgroundColor`、`borderRadius` 及各种变换属性。严禁动画化 `visibility`、`display`，也不得调用 `video.play()`/`audio.play()`。
3. **不同时间轴之间不得存在属性冲突。** 禁止同时从多个时间轴对同一元素进行相同的属性动画。
4. **禁止使用 `repeat: -1`。** 无限循环的动画过渡会破坏捕获引擎的功能。应通过计算得出 `repeat: Math.ceil(duration / cycleDuration) - 1`。
5. **时间轴必须同步构建。** 禁止在 `async`/`await`、`setTimeout` 或 Promise 代码块中创建时间轴。捕获引擎会在页面加载后同步读取 `window.__timelines`。字体由编译器自动嵌入，无需等待加载完成。
6. **根级组合片段不得使用 `<template>` 包装层。** 仅子组合片段可使用 `<template>`。
7. **视频始终需设置为 `muted playsinline` 状态。** 音频必须为独立的 `<audio>` 元素——即便源文件相同也是如此。
8. **内容容器应使用内边距，而非绝对定位。** 示例样式：`.scene-content { width: 100%; height: 100%; padding: Npx; display: flex; flex-direction: column; gap: Npx; box-sizing: border-box }`。使用绝对定位的内容容器会导致内容溢出。仅将 `position: absolute` 用于装饰性元素。

## 场景切换

多场景组合片段必须严格遵守以下规则：

1. **场景之间必须使用过渡效果。** 禁止直接跳转。
2. **每个场景元素都必须有进入动画。** 所有元素均需通过 `gsap.from()` 实现从外部向内的动画效果，任何元素都不得一开始就完全显示。
3. **禁止使用离开动画**（最终场景除外）。也就是说，禁止使用将 `opacity` 动画设置为 0 或将 `y` 值移出屏幕的 `gsap.to()` 动画。场景切换本身即视为离开动画。在切换开始时，即将消失的场景内容必须完全可见。
4. **仅最终场景允许**将元素淡出。这是唯一允许使用 `gsap.to(..., { opacity: 0 })` 的场景。

## 字体与资源

- **字体：** 在 CSS 中指定所需的 `font-family`——编译器会自动嵌入支持的字体。不支持的字体会导致编译器警告。
- 对于外部媒体文件，需添加 `crossorigin="anonymous"` 属性。
- 如需动态调整文本大小，可使用 `window.__hyperframes.fitTextFontSize(text, { maxWidth, fontFamily, fontWeight })` 函数。
- 所有项目文件均应与 `index.html` 一同存储在项目根目录下。子组合片段可通过 `../` 路径引用资源。
- 对于已渲染的视频内容，标题字体大小需大于 60px，正文大于 20px，数据标签大于 16px。数字列应设置 `font-variant-numeric: tabular-nums`。避免在深色背景上使用全屏线性渐变（会导致 H.264 编码出现条纹效果——建议使用径向渐变或实色搭配局部发光效果）。

## 动画规范

- 第一个动画的起始时间应偏移 0.1–0.3 秒，而非正好在 `t=0` 时开始。
- 不同进入动画的缓动函数应有所差异——每个场景至少需使用 3 种不同的缓动效果。
- 同一场景内不得重复使用相同的进入动画模式。

## 绝对禁止的行为

1. 忘记对时间轴进行 `window.__timelines` 注册。
2. 用视频代替音频——必须使用静音视频并搭配独立的 `<audio>` 元素。
3. 将视频嵌套在带时间戳的 div 中——应使用无时间戳的容器。
4. 使用 `data-layer` 属性（应使用 `data-track-index`），或使用 `data-end` 属性（应使用 `data-duration`）。
5. 直接动画化视频元素的尺寸——应改为动画化其包装层 div。
6. 对媒体元素调用 `play`/`pause`/`seek` 方法——播放控制由框架统一管理。
7. 创建没有 `data-composition-id` 的顶级容器。
8. 在任何时间轴或动画过渡上使用 `repeat: -1`。
9. 异步构建时间轴。
10. 对后续场景中的元素使用 `gsap.set()` 方法——因为这些元素在页面加载时还不存在于 DOM 中。应在时间轴中、且在该片段 `data-start` 时间点之后，使用 `tl.set(selector, vars, timePosition)` 方法进行设置。
11. 在文本内容中使用 `<br>` 标签——这会导致文本自然换行时出现不必要的额外换行。应改用 `max-width` 属性控制宽度。例外情况：那些刻意将每个单词单独占一行的短显示标题（例如 “THE\nIMMORTAL\nGAME”）。
