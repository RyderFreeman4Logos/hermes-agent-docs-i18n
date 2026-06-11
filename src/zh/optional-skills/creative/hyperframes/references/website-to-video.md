# 网站转视频

将网页内容捕获并转化为专业级视频。适用于用户提供网址并希望生成视频的场景，如社交广告、产品展示、30秒宣传片等。

该流程共包含7个步骤，每个步骤都会生成一个中间成果，为后续步骤奠定基础。**请勿跳过任何步骤**——每一个中间成果都能有效避免后续出现故障。 

## 第1步：捕获与分析

```bash
npx hyperframes capture https://example.com -o example-video
```

该工具会生成 `example-video/capture/` 目录，其中包含以下内容：
- `capture/screenshots/` — 页面首屏内容及各板块截图（数量最多为 `--max-screenshots` 指定的值）
- `capture/assets/` — 徽标、主视觉图片以及背景视频（如有）
- `capture/extracted/tokens.json` — 颜色、字体及间距相关参数
- `capture/extracted/visible-text.txt` — 提取出的标题、段落及行动号召语句
- `capture/extracted/fonts.json` — 从计算样式中检测到的字体系列及组合
- `capture/asset-descriptions.md` — 自动生成的资产清单

后续所有步骤都将从 `capture/` 子目录中读取数据，例如 `capture/extracted/tokens.json`、`capture/assets/hero.png` 等。在引用这些文件时，切勿省略 `capture/` 前缀。

**筛选条件：** 生成站点概要——包括站点名称、Top 3颜色、主字体与显示字体、主视觉资产路径以及一句话概括的站点风格。该概要需保存在当前上下文中，无需再次进行内容抓取。

## 第2步：编写 DESIGN.md 文件

在项目根目录下创建一个简短的品牌参考文档。该文档包含6个部分，约90行内容。它仅作为参考手册，而非正式的创意方案。

```markdown
# DESIGN

## Brand
- Name: Example Co.
- One-line mission: "…"

## Colors
- Background: #0B0F14
- Primary: #00E0A4 (accent, CTA)
- Secondary: #7A8B9B (body text)
- Text: #FFFFFF

## Typography
- Display: "Inter Tight", 700, tight letter-spacing
- Body: "Inter", 400

## Motion
- Mood: precise, technical, confident
- Eases: `power3.out` for entrances, `expo.in` for exits

## Assets
- Logo: `capture/assets/logo.svg`
- Hero image: `capture/assets/hero.png`

## What NOT to Do
- No purple, no pastels, no serif body
- No playful/bubbly eases (`elastic`, `bounce`)
- No drop shadows on text
```

**触发条件：** 项目目录中存在 `DESIGN.md` 文件。

## 第 3 步：编写 SCRIPT.md

即旁白脚本，也是整个故事的骨架。**场景时长需依据旁白内容来确定，而非凭猜测。**

```markdown
# SCRIPT

## Scene 1 — Hook (0:00–0:04)
"What if your dashboards wrote themselves?"

## Scene 2 — Problem (0:04–0:11)
"Teams spend hours stitching together queries, charts, and callouts — every Monday."

## Scene 3 — Solution (0:11–0:22)
"Example Co. watches your data streams and proposes the dashboard you'd have built — in seconds."

## Scene 4 — CTA (0:22–0:28)
"Try it free at example.com."
```

运行命令 `npx hyperframes tts SCRIPT.md --voice af_nova --output narration.wav` 即可生成文本转语音音频。请注意记录其准确时长，该时长即为视频的持续时间。

**验证条件：** 文件 `SCRIPT.md` 和 `narration.wav` 必须存在，且两者的时长需符合要求（误差在 ±0.3秒以内）。

## 第4步：故事板设计

仅需要文本形式的场景规划：针对每个场景，描述核心画面——即在该场景最显眼的时刻屏幕上呈现的内容。

```markdown
# STORYBOARD

## Scene 1 (0:00–0:04) — Hook
Hero frame: giant "WHAT IF YOUR DASHBOARDS WROTE THEMSELVES?" in display font, centered, on near-black. Logo top-left at 40% opacity.
Entrance: each word staggers in, 0.08s apart.
Transition out: flash-through-white into Scene 2.
```

每个场景写成一段文字。切勿跳过此步骤——这是在编写 HTML 之前发现叙事漏洞的关键环节。

**前提条件：** 必须存在 `STORYBOARD.md` 文件。每个场景都应包含主角画面、出场动画以及过渡效果。

## 第 5 步：页面布局

逐个场景编写 `index.html` 文件：
- 每个场景为一个绝对定位的 `<div class="scene scene-N">` 元素，且需覆盖整个屏幕。
- 首先为主角画面编写纯 HTML+CSS 格式的代码（无需使用 GSAP）。
- 将叙事音频设置为 `data-start="0"`，并将其置于较高的图层索引位置。
- 在每个场景之间添加过渡效果组件（如 `flash-through-white`、`liquid-wipe` 等）。
- 接着添加使用 GSAP 实现的出场动画（如 `gsap.from()`），无需编写出场结束动画——过渡效果本身即可实现退出效果。
- 最后将 `window.__timelines["root"] = tl` 注册到全局变量中。

根据需要安装相应的过渡效果插件：

```bash
npx hyperframes add flash-through-white
```

## 第6步：渲染

```bash
npx hyperframes lint --strict          # must pass
npx hyperframes validate               # WCAG contrast audit
npx hyperframes render --quality draft --output draft.mp4
```

查看草稿。在 `REVIEW.md` 文件的列表中记录问题（场景、时间戳及问题描述）。修复问题后重新渲染。

确认无误后：

```bash
npx hyperframes render --quality high --output final.mp4
```

## 第7步：交付结果

- 向用户反馈文件路径、处理时长以及文件大小。
- 若用户需要竖屏格式，需使用9:16的构图比例重新渲染（设置`data-width="1080" data-height="1920"`），此时通常需要一个单独的`index_vertical.html`文件，以便调整字体大小并重新排列场景布局。

## 常见故障现象

- **忽略DESIGN.md文件** → 不同场景之间的颜色会出现差异，导致输出内容看起来像“AI制作的幻灯片”。
- **忽略STORYBOARD.md文件** → 各场景会相互重叠，或者核心画面会在过渡效果出现时发生碰撞。
- 在过渡效果触发前就出现退出动画 → 过渡发生时会出现空白帧。
- **旁白时长超过`data-duration`设置值** → 音频片段会在句子中间截断。需将构图中的`data-duration`值设置为与文本转语音输出时长相加0.5秒后的数值。
