---
sidebar_position: 10
title: "Skins & Themes"
description: "Customize the Hermes CLI with built-in and user-defined skins"
---

# 外观皮肤与主题

皮肤用于控制Hermes CLI的**视觉呈现效果**，包括横幅颜色、加载动画的图案与文字、响应框标签、品牌标识文本以及工具操作的前缀。

对话风格与视觉风格是两个不同的概念：

- **个性设置**用于改变智能体的语气和用词方式。
- **皮肤设置**则用于改变CLI的整体外观。

## 更改皮肤

```bash
/skin                # show the current skin and list available skins
/skin ares           # switch to a built-in skin
/skin mytheme        # switch to a custom skin from ~/.hermes/skins/mytheme.yaml
```

或者可在 `~/.hermes/config.yaml` 中设置默认主题：

```yaml
display:
  skin: default
```

## 内置皮肤

| Skin | Description | Agent branding | Visual character |
|------|-------------|----------------|------------------|
| `default` | Classic Hermes — gold and kawaii | `Hermes Agent` | Warm gold borders, cornsilk text, kawaii faces in spinners. The familiar caduceus banner. Clean and inviting. |
| `ares` | War-god theme — crimson and bronze | `Ares Agent` | Deep crimson borders with bronze accents. Aggressive spinner verbs ("forging", "marching", "tempering steel"). Custom sword-and-shield ASCII art banner. |
| `mono` | Monochrome — clean grayscale | `Hermes Agent` | All grays — no color. Borders are `#555555`, text is `#c9d1d9`. Ideal for minimal terminal setups or screen recordings. |
| `slate` | Cool blue — developer-focused | `Hermes Agent` | Royal blue borders (`#4169e1`), soft blue text. Calm and professional. No custom spinner — uses default faces. |
| `daylight` | Light theme for bright terminals with dark text and cool blue accents | `Hermes Agent` | Designed for white or bright terminals. Dark slate text with blue borders, pale status surfaces, and a light completion menu that stays readable in light terminal profiles. |
| `warm-lightmode` | Warm brown/gold text for light terminal backgrounds | `Hermes Agent` | Warm parchment tones for light terminals. Dark brown text with saddle-brown accents, cream-colored status surfaces. An earthy alternative to the cooler daylight theme. |
| `poseidon` | Ocean-god theme — deep blue and seafoam | `Poseidon Agent` | Deep blue to seafoam gradient. Ocean-themed spinners ("charting currents", "sounding the depth"). Trident ASCII art banner. |
| `sisyphus` | Sisyphean theme — austere grayscale with persistence | `Sisyphus Agent` | Light grays with stark contrast. Boulder-themed spinners ("pushing uphill", "resetting the boulder", "enduring the loop"). Boulder-and-hill ASCII art banner. |
| `charizard` | Volcanic theme — burnt orange and ember | `Charizard Agent` | Warm burnt orange to ember gradient. Fire-themed spinners ("banking into the draft", "measuring burn"). Dragon-silhouette ASCII art banner. |

## 所有可配置键的完整列表

### 颜色 (`colors:`)

用于控制 CLI 中的所有颜色值。这些值均为十六进制颜色字符串。

| Key | Description | Default (`default` skin) |
|-----|-------------|--------------------------|
| `banner_border` | Panel border around the startup banner | `#CD7F32` (bronze) |
| `banner_title` | Title text color in the banner | `#FFD700` (gold) |
| `banner_accent` | Section headers in the banner (Available Tools, etc.) | `#FFBF00` (amber) |
| `banner_dim` | Muted text in the banner (separators, secondary labels) | `#B8860B` (dark goldenrod) |
| `banner_text` | Body text in the banner (tool names, skill names) | `#FFF8DC` (cornsilk) |
| `ui_accent` | General UI accent color (highlights, active elements) | `#FFBF00` |
| `ui_label` | UI labels and tags | `#DAA520` (goldenrod) |
| `ui_ok` | Success indicators (checkmarks, completion) | `#4caf50` (green) |
| `ui_error` | Error indicators (failures, blocked) | `#ef5350` (red) |
| `ui_warn` | Warning indicators (caution, approval prompts) | `#ffa726` (orange) |
| `prompt` | Interactive prompt text color | `#FFF8DC` |
| `input_rule` | Horizontal rule above the input area | `#CD7F32` |
| `response_border` | Border around the agent's response box (ANSI escape) | `#FFD700` |
| `session_label` | Session label color | `#DAA520` |
| `session_border` | Session ID dim border color | `#8B8682` |
| `status_bar_bg` | Background color for the TUI status / usage bar | `#1a1a2e` |
| `voice_status_bg` | Background color for the voice-mode status badge | `#1a1a2e` |
| `selection_bg` | Background color for the TUI mouse-selection highlighter. Falls back to `completion_menu_current_bg` when unset. | `#3a3a55` |
| `completion_menu_bg` | Background color for the completion menu list | `#1a1a2e` |
| `completion_menu_current_bg` | Background color for the active completion row | `#333355` |
| `completion_menu_meta_bg` | Background color for the completion meta column | `#1a1a2e` |
| `completion_menu_meta_current_bg` | Background color for the active completion meta column | `#333355` |

### 旋转动画组件 (`spinner:`)

用于控制在等待 API 响应时显示的动画旋转图标。

| 键值 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待 API 响应时循环显示的表情符号 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型进行推理时循环显示的表情符号 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 旋转动画消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | `[左, 右]` 对列表 | 旋转图标周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当这些参数未被设置（如使用 `default` 和 `mono` 模式时），将会使用 `display.py` 文件中预定义的默认值。

### 品牌标识 (`branding:`)

用于整个 CLI 界面中的文本字符串。

| 键值 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 显示在标题栏和状态栏中的代理名称 | `Hermes Agent` |
| `welcome` | CLI 启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 程序退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框标题上的标签 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示符前的符号（仅为基础符号，具体渲染效果会添加尾部空格） | `❯` |
| `help_header` | `/help` 命令输出时的标题文本 | `(^_^)? Available Commands` |

### 其他顶层键值

| 键名 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI 中工具输出行前添加的字符前缀 | `┊` |
| `tool_emojis` | 字典 | 各工具对应的旋转加载符和进度条表情符号自定义设置（格式：`{tool_name: emoji}`） | `{}` |
| `banner_logo` | 字符串 | 支持富标记格式的 ASCII 图形标识（可替换默认的 HERMES_AGENT 标识） | `""` |
| `banner_hero` | 字符串 | 支持富标记格式的主视觉图（可替换默认的双蛇杖图案） | `""` |

## 自定义主题

在 `~/.hermes/skins/` 目录下创建 YAML 文件即可。用户自定义的主题会从内置的 `default` 主题中继承缺失的配置，因此您只需指定需要修改的键名即可。

### 完整的自定义主题 YAML 模板

```yaml
# ~/.hermes/skins/mytheme.yaml
# Complete skin template — all keys shown. Delete any you don't need;
# missing values automatically inherit from the 'default' skin.

name: mytheme
description: My custom theme

colors:
  banner_border: "#CD7F32"
  banner_title: "#FFD700"
  banner_accent: "#FFBF00"
  banner_dim: "#B8860B"
  banner_text: "#FFF8DC"
  ui_accent: "#FFBF00"
  ui_label: "#4dd0e1"
  ui_ok: "#4caf50"
  ui_error: "#ef5350"
  ui_warn: "#ffa726"
  prompt: "#FFF8DC"
  input_rule: "#CD7F32"
  response_border: "#FFD700"
  session_label: "#DAA520"
  session_border: "#8B8682"
  status_bar_bg: "#1a1a2e"
  voice_status_bg: "#1a1a2e"
  selection_bg: "#333355"
  completion_menu_bg: "#1a1a2e"
  completion_menu_current_bg: "#333355"
  completion_menu_meta_bg: "#1a1a2e"
  completion_menu_meta_current_bg: "#333355"

spinner:
  waiting_faces:
    - "(⚔)"
    - "(⛨)"
    - "(▲)"
  thinking_faces:
    - "(⚔)"
    - "(⌁)"
    - "(<>)"
  thinking_verbs:
    - "processing"
    - "analyzing"
    - "computing"
    - "evaluating"
  wings:
    - ["⟪⚡", "⚡⟫"]
    - ["⟪●", "●⟫"]

branding:
  agent_name: "My Agent"
  welcome: "Welcome to My Agent! Type your message or /help for commands."
  goodbye: "See you later! ⚡"
  response_label: " ⚡ My Agent "
  prompt_symbol: "⚡"
  help_header: "(⚡) Available Commands"

tool_prefix: "┊"

# Per-tool emoji overrides (optional)
tool_emojis:
  terminal: "⚔"
  web_search: "🔮"
  read_file: "📄"

# Custom ASCII art banners (optional, Rich markup supported)
# banner_logo: |
#   [bold #FFD700] MY AGENT [/]
# banner_hero: |
#   [#FFD700]  Custom art here  [/]
```

### 最简自定义皮肤示例

由于所有内容均继承自 `default`，因此最简皮肤只需修改那些需要差异化的部分即可：

```yaml
name: cyberpunk
description: Neon terminal theme

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["jacking in", "decrypting", "uploading"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "

tool_prefix: "▏"
```

## Hermes Mod — 可视化皮肤编辑器

[Hermes Mod](https://github.com/cocktailpeanut/hermes-mod) 是一个由社区开发的网页界面，用于以可视化方式创建和管理皮肤。您无需手动编写 YAML 文件，而是可以通过点击式编辑器进行操作，并实时查看预览效果。

![Hermes Mod 皮肤编辑器](https://raw.githubusercontent.com/cocktailpeanut/hermes-mod/master/nous.png)

**功能特点：**

- 列出所有内置及自定义皮肤
- 打开任意皮肤后，即可进入可视化编辑器，可编辑所有 Hermes 皮肤相关参数（颜色、旋转图标、品牌标识、工具前缀、工具表情符号等）
- 根据文本提示生成 `banner_logo` 文字艺术效果
- 将上传的图片（PNG、JPG、GIF、WEBP 格式）转换为多种渲染风格的 `banner_hero` ASCII 艺术图（点阵、斜坡、方块、点状等）
- 直接保存到 `~/.hermes/skins/` 目录
- 通过修改 `~/.hermes/config.yaml` 文件来启用特定皮肤
- 显示生成的 YAML 配置文件及实时预览效果

### 安装方式

**方式一 — Pinokio（一键安装）：**

访问 [pinokio.computer](https://pinokio.computer) 即可找到该工具，点击一下即可完成安装。

**方式二 — npx（通过终端最快安装）：**

```bash
npx -y hermes-mod
```

**选项 3 — 手动方式：**

```bash
git clone https://github.com/cocktailpeanut/hermes-mod.git
cd hermes-mod/app
npm install
npm start
```

### 使用方法

1. 启动应用程序（通过 Pinokio 或终端）。
2. 打开 **Skin Studio**。
3. 选择内置皮肤或自定义皮肤进行编辑。
4. 根据文本生成标志，或上传图片作为主视觉图。同时选择渲染风格和宽度。
5. 编辑颜色、加载动画、品牌标识及其他相关字段。
6. 点击 **Save**，将生成的皮肤 YAML 文件保存至 `~/.hermes/skins/` 目录中。
7. 点击 **Activate**，将其设置为当前皮肤（这将更新 `config.yaml` 文件中的 `display.skin` 设置）。

Hermes Mod 会自动识别 `HERMES_HOME` 环境变量，因此也可与 [profiles](/user-guide/profiles) 功能配合使用。

## 操作注意事项

- 内置皮肤从 `hermes_cli/skin_engine.py` 文件中加载。
- 未知皮肤会自动回退为 `default` 皮肤。
- 使用 `/skin` 命令可立即更新当前会话的 CLI 主题。
- 若 `~/.hermes/skins/` 目录中存在与内置皮肤同名的自定义皮肤，后者将优先生效。
- 通过 `/skin` 命令更改的皮肤仅对当前会话有效。若要将某皮肤设为永久默认皮肤，请在 `config.yaml` 中进行配置。
- `banner_logo` 和 `banner_hero` 字段支持使用 Rich 控制台标记语法（例如 `[bold #FF0000]文本[/]`），以便生成带颜色的 ASCII 艺术字。
