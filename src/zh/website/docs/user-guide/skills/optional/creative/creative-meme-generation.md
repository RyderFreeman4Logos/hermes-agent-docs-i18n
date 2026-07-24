---
title: "Meme Generation — Create meme PNGs from templates with Pillow text overlay"
sidebar_label: "Meme Generation"
description: "Create meme PNGs from templates with Pillow text overlay"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 模因生成

使用 Pillow 在模板上添加文字，生成模因 PNG 图像。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/meme-generation` 安装 |
| 路径 | `optional-skills/creative/meme-generation` |
| 版本 | `2.0.0` |
| 创建者 | adanaleycio |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `creative`、`memes`、`humor`、`images` |
| 相关技能 | [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art)、`generative-widgets` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体将以此作为操作指令。
:::

# 模因生成

根据指定主题生成真实的模因图像。系统会自动选择模板、编写标题，并输出带有文字叠加效果的完整 .png 文件。

## 适用场景

- 用户要求你创建或生成模因
- 用户希望针对特定主题、情境或烦恼制作模因
- 用户说出“把……做成模因”之类的话语

## 可用模板

该脚本支持通过名称或 ID 调用 **约 100 种流行的 imgflip 模板**，此外还包含 10 种经过精心挑选、文字位置已优化调整的模板。

### 精选模板（自定义文字位置）

| ID | 名称 | 字段位置 | 最佳适用场景 |
|----|------|----------|--------------|
| `this-is-fine` | 一切正常 | 顶部、底部 | 表现镇定、否认现实 |
| `drake` | Drake Hotline Bling | 拒绝、同意 | 表达拒绝或偏好 |
| `distracted-boyfriend` | 分心的男友 | 分心物、当前对象、本人 | 描述诱惑或注意力转移 |
| `two-buttons` | 两个按钮 | 左侧、右侧、本人 | 面对两难选择 |
| `expanding-brain` | 扩展的大脑 | 4个层级 | 表现逐渐加剧的讽刺感 |
| `change-my-mind` | 改变我的想法 | 文本输入框 | 表达激进观点 |
| `woman-yelling-at-cat` | 女人对着猫大喊 | 女人、猫 | 描绘争吵场景 |
| `one-does-not-simply` | 事情没那么简单 | 顶部、底部 | 表示事物看似容易实则困难 |
| `grus-plan` | 格鲁的计划 | 步骤1-3、最终醒悟 | 描述计划失败的过程 |
| `batman-slapping-robin` | 蝙蝠侠打罗宾 | 罗宾、蝙蝠侠 | 表示制止错误想法 |

### 动态模板（来自 imgflip API）

任何未列入精选列表的模板，都可以通过名称或 imgflip ID 调用。这类模板会自动设置智能的默认文字位置（双字段模板为顶部/底部，三字段及以上为均匀分布）。可通过以下方式搜索：
```bash
python "$SKILL_DIR/scripts/generate_meme.py" --search "disaster"
```

## 操作步骤

### 模式1：经典模板（默认）

1. 阅读用户输入的主题，识别其中的核心情感或情境（如混乱、两难、偏好、反讽等）。
2. 选择最匹配的模板。可通过“适用场景”一列进行筛选，或使用 `--search` 参数进行搜索。
3. 为每个字段编写简短的标题说明（每字段字数建议在8-12字之间，越简短越好）。
4. 找到对应技能的脚本目录：
   ```
   SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
   ```
5. 运行生成器：
   ```bash
   python "$SKILL_DIR/scripts/generate_meme.py" <template_id> /tmp/meme.png "caption 1" "caption 2" ...
   ```
6. 使用 `MEDIA:/tmp/meme.png` 返回图像。

### 模式2：自定义AI图像（当支持 `image_generate` 功能时）

当传统模板不适用，或用户希望获得原创内容时，可使用此模式。

1. 先编写文字说明。
2. 使用 `image_generate` 创建与表情包概念相匹配的场景。在图像提示词中不要包含任何文字——文字将由脚本添加，只需描述视觉场景即可。
3. 从 `image_generate` 的结果URL中获取生成的图像路径，如需可将图像下载到本地。
4. 运行脚本并加上 `--image` 参数来添加文字，可选择以下模式之一：
   - **叠加**（文字直接显示在图像上，白色背景并带有黑色轮廓）：
     ```bash
     python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png /tmp/meme.png "top text" "bottom text"
     ```
- **条形栏**（上下为黑色条带，配以白色文字——视觉更简洁，且始终清晰可读）：
     ```bash
     python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png --bars /tmp/meme.png "top text" "bottom text"
     ```
当图像内容过于复杂或细节繁多，导致文字难以清晰显示时，请使用 `--bars` 参数。
5. **通过视觉功能进行验证**（若支持 `vision_analyze` 功能）：检查结果是否正常。
   ```
   vision_analyze(image_url="/tmp/meme.png", question="Is the text legible and well-positioned? Does the meme work visually?")
   ```
如果视觉模型检测到问题（如文字难以辨认、位置不当等），请尝试其他模式（在叠加显示和条形图显示之间切换），或重新生成该场景。
6. 使用 `MEDIA:/tmp/meme.png` 返回图像。

## 示例

**“凌晨2点进行生产环境调试”：**
```bash
python generate_meme.py this-is-fine /tmp/meme.png "SERVERS ARE ON FIRE" "This is fine"
```

**“在入睡与再看一集之间做选择”：**
```bash
python generate_meme.py drake /tmp/meme.png "Getting 8 hours of sleep" "One more episode at 3 AM"
```

**“周一早上的各个阶段”：**
```bash
python generate_meme.py expanding-brain /tmp/meme.png "Setting an alarm" "Setting 5 alarms" "Sleeping through all alarms" "Working from bed"
```

## 模板列表

如需查看所有可用模板：
```bash
python generate_meme.py --list
```

## 常见问题

- 文字说明请保持简短。包含过长文字的模因效果会很糟糕。
- 文本参数的数量需与模板中的字段数量相匹配。
- 应根据笑话的结构来选择模板，而不仅仅是依据主题。
- 禁止生成充满仇恨、辱骂性或针对个人的内容。
- 脚本会在首次下载后将模板图片缓存到 `scripts/.cache/` 目录中。

## 验证标准

只有满足以下条件，输出才视为正确：
- 输出路径下已生成 .png 格式的文件；
- 模板上的文字清晰可见（白色背景搭配黑色轮廓）；
- 笑话表达恰当——文字说明符合模板预期的结构；
- 文件可通过 MEDIA: path 方式进行传输。
