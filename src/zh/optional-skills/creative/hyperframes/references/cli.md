# HyperFrames CLI

所有操作均通过 `npx hyperframes` 执行（或在执行 `npm install -g hyperframes` 安装全局版本后使用 `hyperframes`）。该工具要求系统安装 Node.js 22 及更高版本以及 FFmpeg。

## 工作流程

1. **创建项目框架** — `npx hyperframes init my-video`（若从网页开始制作，则可使用 `npx hyperframes capture <url>`）
2. **编写内容** — 编写 HTML 结构代码（详见 `composition.md` 文件）
3. **代码检查** — `npx hyperframes lint`
4. **验证合规性** — `npx hyperframes validate`（执行 WCAG 对比度检测）
5. **布局检查** — `npx hyperframes inspect`（进行视觉布局检测）
6. **预览效果** — `npx hyperframes preview`
7. **最终渲染** — `npx hyperframes render`

在预览或渲染之前务必先进行代码检查，这样可以及时发现缺失的 `data-composition-id`、重叠的轨道以及未注册的时间轴等问题。

## init — 创建项目框架

```bash
npx hyperframes init my-video                        # interactive wizard
npx hyperframes init my-video --example warm-grain   # pick an example template
npx hyperframes init my-video --video clip.mp4       # seed with a video file
npx hyperframes init my-video --audio track.mp3      # seed with an audio file
npx hyperframes init my-video --non-interactive      # skip prompts (CI / agent use)
```

模板包括：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。

`init`命令可自动创建正确的文件结构，复制媒体文件，使用Whisper工具对音频进行转录，并安装所需的创作技能。建议使用该命令而非手动创建文件。

## capture — 网站 → 可编辑组件

```bash
npx hyperframes capture https://example.com                  # → captures/example.com/
npx hyperframes capture https://stripe.com -o stripe-video   # custom output dir
npx hyperframes capture https://example.com --json           # machine-readable output
npx hyperframes capture https://example.com --skip-assets    # skip images/SVGs
```

默认会将网站内容保存到 `captures/<hostname>/capture/` 目录下，该目录包含 `capture/screenshots/`、`capture/assets/`、`capture/extracted/`（包含 tokens.json、visible-text.txt、fonts.json 文件）以及一个独立的快照文件。

后续的所有处理步骤（DESIGN.md、SCRIPT.md、STORYBOARD、合成处理）都将从 `capture/` 子目录中读取数据——详情请参阅 `website-to-video.md`。

## lint

```bash
npx hyperframes lint                # current directory
npx hyperframes lint ./my-project   # specific project
npx hyperframes lint --verbose      # include info-level findings
npx hyperframes lint --json         # machine-readable output
```

会对 `index.html` 以及 `compositions/` 目录下的所有文件进行代码检查。会输出错误信息（必须修复）、警告信息（建议修复）以及信息性提示（仅在使用 `--verbose` 参数时显示）。  

## validate

```bash
npx hyperframes validate                 # WCAG contrast audit at 5 timestamps
npx hyperframes validate --no-contrast   # skip while iterating
```

该功能会获取5个时间戳、截取页面截图、提取每个文本元素背后的背景像素样本，并针对对比度低于4.5:1（普通文本）或3:1（大号文本——24像素及以上，或加粗文本19像素及以上）的情况发出警告。建议在最终渲染之前执行此操作。

## inspect

```bash
npx hyperframes inspect                 # visual layout audit at 5 timestamps
npx hyperframes inspect ./my-project    # specific project
npx hyperframes inspect --json          # agent-readable findings
npx hyperframes inspect --samples 15    # denser timeline sweep
npx hyperframes inspect --at 1.5,4,7.25 # explicit hero-frame timestamps
```

请在执行 `lint` 和 `validate` 操作之后使用该工具，尤其适用于包含对话框、卡片、字幕或紧凑排版的合成内容。它会报告元素溢出、超出画面范围、文字被遮挡、对比度不足等问题，以及针对每个时间点的布局概要——从而发现单纯的时间轴检查无法识别的问题（例如仅在某个特定时间点才超出安全区域的字幕）。

`npx hyperframes layout` 是同一视觉检测流程的兼容性别名。

## preview

请完整翻译输入内容，切勿提前终止。

```bash
npx hyperframes preview                # serve current directory (port 3002)
npx hyperframes preview --port 4567    # custom port
```

文件修改时即可实现热重载，并会自动在您的浏览器中打开 Studio。  

## render  
对整个输入内容进行翻译，切勿提前终止处理。

```bash
npx hyperframes render                              # standard MP4
npx hyperframes render --output final.mp4           # named output
npx hyperframes render --quality draft              # fast iteration
npx hyperframes render --fps 60 --quality high      # final delivery
npx hyperframes render --format webm                # transparent WebM
npx hyperframes render --docker                     # byte-identical reproducible render
```

| 标志          | 选项                    | 默认值                        | 备注                       |
| -------------- | ----------------------- | ------------------------------ | --------------------------- |
| `--output`     | 路径                    | `renders/<名称>_<时间戳>.mp4` | 输出路径                   |
| `--fps`        | 24、30、60               | 30                             | 60帧/秒会使渲染时间翻倍     |
| `--quality`    | `draft`、`standard`、`high` | `standard`                  | 用于迭代时可选择 `draft`   |
| `--format`     | `mp4`、`webm`           | `mp4`                         | WebM格式支持透明度         |
| `--workers`    | 1–8 或 `auto`           | `auto`                        | 每个数值会启动一个Chrome进程 |
| `--docker`     | 标志                    | `off`                          | 用于实现可复现的输出结果   |
| `--gpu`        | 标志                    | `off`                          | 支持GPU加速编码             |
| `--strict`     | 标志                    | `off`                          | 出现语法错误时直接终止       |
| `--strict-all` | 标志                    | `off`                          | 出现错误及警告时均终止       |

**质量等级建议：** 迭代阶段使用 `draft`，审核阶段使用 `standard`，最终交付则使用 `high`。

## 语音转录

```bash
npx hyperframes transcribe audio.mp3
npx hyperframes transcribe video.mp4 --model medium.en --language en
npx hyperframes transcribe subtitles.srt     # import existing
npx hyperframes transcribe subtitles.vtt
npx hyperframes transcribe openai-response.json
```

生成适用于字幕组件的单词级时间戳。首次运行时会下载Whisper模型，之后会进行缓存。

## tts

对整个输入内容进行翻译，不得提前终止。

```bash
npx hyperframes tts "Text here" --voice af_nova --output narration.wav
npx hyperframes tts script.txt --voice bf_emma
npx hyperframes tts "La reunión empieza a las nueve" --voice ef_dora --output es.wav
npx hyperframes tts "Hello there" --voice af_heart --lang fr-fr --output accented.wav
npx hyperframes tts --list                    # show all voices
```

使用 Kokoro（本地模式，无需 API 密钥）。语音 ID 的首字母用于标识语言：`a` 代表美式英语，`b` 代表英式英语，`e` 代表西班牙语，`f` 代表法语，`h` 代表印地语，`i` 代表意大利语，`j` 代表日语，`p` 代表巴西葡萄牙语，`z` 代表普通话。CLI 会自动根据该前缀推断语音合成器的区域设置——仅可通过 `--lang` 参数进行覆盖（例如用于设置特殊发音风格）。有效的 `--lang` 代码包括：`en-us`、`en-gb`、`es`、`fr-fr`、`hi`、`it`、`pt-br`、`ja`、`zh`。如需进行非英语语言的语音合成，需在系统中全局安装 `espeak-ng`（可通过 `apt-get install espeak-ng` 或 `brew install espeak-ng` 安装）。

## doctor

```bash
npx hyperframes doctor
```

环境验证：
- Node.js 版本 >= 22
- PATH 环境变量中已包含 FFmpeg
- 可用内存（渲染任务非常耗内存，建议至少 4 GB）
- Chrome 可执行文件的版本（优先使用 `chrome-headless-shell`，而非系统自带的 Chrome）
- 当前 `hyperframes` 的版本

当渲染失败时，请**首先**运行此命令。有关输出结果的解读方式，请参阅 `troubleshooting.md` 文件。

## 浏览器

```bash
npx hyperframes browser --install      # install the bundled chrome-headless-shell
npx hyperframes browser --path         # print the resolved browser binary path
npx hyperframes browser --clean        # clear the bundled browser cache
```

## 信息说明

```bash
npx hyperframes info
```

会显示版本号、Node版本、FFmpeg版本、操作系统信息以及已解析的浏览器路径——这些信息在提交错误报告时非常有用。

## 升级

```bash
npx hyperframes upgrade -y
```

检查并安装更新。如果您遇到了 `HeadlessExperimental.beginFrame` 错误，请运行此命令——该自动修复功能已包含在 `hyperframes@0.4.2` 版本中（提交编号 4c72ba4，2026 年 3 月发布）。 

## 其他

```bash
npx hyperframes compositions    # list compositions in the project
npx hyperframes docs            # open documentation in browser
npx hyperframes benchmark .     # benchmark render performance
npx hyperframes add <block>     # install a block/component from the catalog
npx hyperframes add --list      # browse the catalog
```

常用的目录模块包括：`flash-through-white`（着色器过渡效果）、`instagram-follow`（社交平台覆盖层）、`data-chart`（动画图表）以及`lower-third`（谈话者头像覆盖层）。更多详情请访问 [hyperframes.heygen.com/catalog](https://hyperframes.heygen.com/catalog)。
