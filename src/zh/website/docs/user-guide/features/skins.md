---
sidebar_position: 10
title: "Skins & Themes"
description: "Customize the Hermes CLI with built-in and user-defined skins"
---

# 外观皮肤与主题

外观皮肤用于控制Hermes CLI的**视觉呈现效果**，包括横幅颜色、加载动画的图案与文字、响应框标签、品牌标识文本以及工具操作的前缀。

对话风格与视觉风格是两个不同的概念：

- **个性设置**用于改变智能体的语气和用词方式。
- **外观皮肤**则用于改变CLI的整体外观。

## 更改外观皮肤

```bash
/skin                # show the current skin and list available skins
/skin ares           # switch to a built-in skin
/skin mytheme        # switch to a custom skin from ~/.hermes/skins/mytheme.yaml
```

或者可以在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置主题皮肤

| 主题 | 描述 | Agent品牌标识 | 视觉风格 |
|------|-------------|----------------|----------|
| `default` | 经典Hermes风格——金色与可爱元素 | `Hermes Agent` | 采用暖金色边框、米色文字，加载动画中带有可爱表情符号，还有熟悉的双蛇杖标志。整体设计简洁且富有亲和力。 |
| `ares` | 战神主题——深红与青铜色 | `Ares Agent` | 深红色边框搭配青铜色点缀，加载动画中的动词具有攻击性风格（如“锻造”、“进军”、“淬炼钢铁”），并配有自定义的剑盾风格ASCII艺术标志。 |
| `mono` | 单色风格——纯灰度 | `Hermes Agent` | 全部为灰色调，无彩色元素。边框颜色为`#555555`，文字颜色为`#c9d1d9`，非常适合极简终端环境或屏幕录制场景。 |
| `slate` | 冷蓝风格——面向开发者 | `Hermes Agent` | 采用深蓝色边框（`#4169e1`）和浅蓝色文字，风格冷静专业。不使用自定义加载动画，而是采用默认表情符号。 |
| `daylight` | 亮色主题——适合明亮终端，搭配深色文字与冷蓝点缀 | `Hermes Agent` | 专为白色或明亮色调的终端设计，具有深石板色文字、蓝色边框、浅色状态栏，以及能在亮色终端背景下保持可读性的浅色补全菜单。 |
| `warm-lightmode` | 适用于亮色终端背景的暖棕/金色文字 | `Hermes Agent` | 为亮色终端提供温暖的羊皮纸色调，文字为深棕色并带有马鞍棕色点缀，状态栏为奶油色，是比冷色调的daylight主题更为自然的替代方案。 |
| `poseidon` | 海神主题——深蓝与海绿色 | `Poseidon Agent` | 采用从深蓝到海绿的渐变色彩，加载动画与海洋主题相关（如“绘制洋流图”、“探测水深”），并配有三叉戟风格的ASCII艺术标志。 |
| `sisyphus` | 西西弗斯主题——简洁灰度风格，强调坚韧精神 | `Sisyphus Agent` | 以浅灰色为主色调，对比度鲜明。加载动画与巨石主题相关（如“向上推石”、“重置巨石”、“坚持循环”），并配有巨石与山丘风格的ASCII艺术标志。 |
| `charizard` | 火山主题——焦橙色与余烬色 | `Charizard Agent` | 采用从暖焦橙色到余烬色的渐变色彩，加载动画与火焰主题相关（如“注入能量”、“测量燃烧程度”），并配有龙形轮廓的ASCII艺术标志。 |

## 所有可配置键的完整列表

### 颜色 (`colors:`)

用于控制CLI中的所有颜色值，数值为十六进制颜色字符串。

| 键 | 描述 | 默认值（`default`主题） |
|-----|-------------|--------------------------|
| `banner_border` | 启动标志周围的边框颜色 | `#CD7F32`（青铜色） |
| `banner_title` | 标志中的标题文字颜色 | `#FFD700`（金色） |
| `banner_accent` | 标志中的章节标题颜色（如“可用工具”等） | `#FFBF00`（琥珀色） |
| `banner_dim` | 标志中的浅色文字颜色（分隔符、次要标签） | `#B8860B`（深金黄色） |
| `banner_text` | 标志中的正文文字颜色（工具名称、技能名称等） | `#FFF8DC`（米色） |
| `ui_accent` | 整体UI的强调色（高亮元素、活动状态元素） | `#FFBF00` |
| `ui_label` | UI标签与标记 | `#4dd0e1`（青色） |
| `ui_ok` | 成功指示器颜色（对号、完成状态等） | `#4caf50`（绿色） |
| `ui_error` | 错误指示器颜色（失败、阻塞状态等） | `#ef5350`（红色） |
| `ui_warn` | 警告指示器颜色（提醒、确认提示等） | `#ffa726`（橙色） |
| `prompt` | 交互式提示符文字颜色 | `#FFF8DC` |
| `input_rule` | 输入区域上方的横线颜色 | `#CD7F32` |
| `response_border` | Agent响应框周围的边框颜色（ANSI转义代码） | `#FFD700` |
| `session_label` | 会话标签颜色 | `#DAA520` |
| `session_border` | 会话ID的浅色边框颜色 | `#8B8682` |
| `status_bar_bg` | TUI状态/使用率栏的背景颜色 | `#1a1a2e` |
| `voice_status_bg` | 语音模式状态徽章的背景颜色 | `#1a1a2e` |
| `selection_bg` | TUI鼠标选中区域的背景颜色；若未设置，则回退为`completion_menu_current_bg`的值。 | `#333355` |
| `completion_menu_bg` | 补全菜单列表的背景颜色 | `#1a1a2e` |
| `completion_menu_current_bg` | 当前激活的补全行的背景颜色 | `#333355` |
| `completion_menu_meta_bg` | 补全菜单元数据列的背景颜色 | `#1a1a2e` |
| `completion_menu_meta_current_bg` | 当前激活的补全元数据列的背景颜色 | `#333355` |

### 加载动画 (`spinner:`)

用于控制等待API响应时显示的动画加载符号。

| 键 | 类型 | 描述 | 示例 |
|-----|------|-------------|---------|
| `waiting_faces` | 字符串列表 | 等待API响应时循环显示的表情符号 | `["(⚔)", "(⛨)", "(▲)"]` |
| `thinking_faces` | 字符串列表 | 模型推理过程中循环显示的表情符号 | `["(⚔)", "(⌁)", "(<>)"]` |
| `thinking_verbs` | 字符串列表 | 加载动画消息中显示的动词 | `["forging", "plotting", "hammering plans"]` |
| `wings` | `[左, 右]对列表` | 加载符号周围的装饰性括号 | `[["⟪⚔", "⚔⟫"], ["⟪▲", "▲⟫"]]` |

当`spinner`相关键的值为空时（如`default`和`mono`主题），将使用`display.py`文件中预定义的默认值。

### 品牌标识 (`branding:`)

用于CLI界面各处的文本字符串。

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `agent_name` | 显示在标志标题及状态栏中的名称 | `Hermes Agent` |
| `welcome` | CLI启动时显示的欢迎消息 | `Welcome to Hermes Agent! Type your message or /help for commands.` |
| `goodbye` | 程序退出时显示的消息 | `Goodbye! ⚕` |
| `response_label` | 响应框标题上的标签文字 | ` ⚕ Hermes ` |
| `prompt_symbol` | 用户输入提示符前的符号（仅为基础符号，具体渲染器可能会在后面添加空格） | `❯` |
| `help_header` | `/help`命令输出结果的标题文字 | `(^_^)? Available Commands` |

### 其他顶层键

| 键 | 类型 | 描述 | 默认值 |
|-----|------|-------------|---------|
| `tool_prefix` | 字符串 | CLI中工具输出行前的前缀字符 | `┊` |
| `tool_emojis` | 字典 | 每个工具对应的加载动画及进度条的emoji替换值（格式：`{工具名称: emoji}`） | `{}` |
| `banner_logo` | 字符串 | 支持富标记格式的ASCII艺术标志，可替代默认的HERMES_AGENT标志 | `""` |
| `banner_hero` | 字符串 | 支持富标记格式的主角形象图，可替代默认的双蛇杖图案 | `""` |

## 自定义主题皮肤

可在`~/.hermes/skins/`目录下创建YAML文件。用户自定义的主题会自动继承内置`default`主题中缺失的配置值，因此只需指定需要修改的键即可。

### 完整的自定义主题皮肤YAML模板

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

由于所有内容都继承自 `default`，因此最简皮肤只需修改那些需要差异化的部分即可：

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
- 打开任意皮肤后，即可进入可视化编辑器，可调整所有 Hermes 皮肤相关参数（颜色、旋转组件、品牌标识、工具前缀、工具表情符号等）
- 根据文本提示生成 `banner_logo` 文字艺术效果
- 将上传的图片（PNG、JPG、GIF、WEBP 格式）转换为多种渲染风格的 `banner_hero` ASCII 艺术图（点阵、斜坡、方块、点状等）
- 直接保存到 `~/.hermes/skins/` 目录
- 通过修改 `~/.hermes/config.yaml` 文件来启用特定皮肤
- 显示生成的 YAML 文件内容及实时预览效果

### 安装方式

**方案 1 — Pinokio（一键安装）：**

访问 [pinokio.computer](https://pinokio.computer) 即可找到该工具，点击一下即可完成安装。

**方案 2 — npx（终端中最快捷的方式）：**

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
4. 根据文本生成徽标，或上传图片作为主视觉图。同时选择渲染风格和宽度。
5. 编辑颜色、加载动画、品牌标识及其他相关字段。
6. 点击 **Save**，将皮肤配置的 YAML 文件保存至 `~/.hermes/skins/` 目录中。
7. 点击 **Activate**，将其设置为当前皮肤（此操作会更新 `config.yaml` 文件中的 `display.skin` 设置）。

Hermes Mod 会优先使用 `HERMES_HOME` 环境变量指定的路径，因此也可与 [profiles](/user-guide/profiles) 功能协同使用。

## 操作注意事项

- 内置皮肤从 `hermes_cli/skin_engine.py` 文件中加载。
- 未知皮肤会自动回退为 `default` 皮肤。
- 使用 `/skin` 命令可立即为当前会话更新活跃的 CLI 主题。
- 位于 `~/.hermes/skins/` 目录中的用户自定义皮肤，其优先级高于同名的内置皮肤。
- 通过 `/skin` 命令更改的皮肤设置仅适用于当前会话。若要将某皮肤设为永久默认值，则需在 `config.yaml` 中进行配置。
- `banner_logo` 和 `banner_hero` 字段支持使用富文本标记语法（例如 `[bold #FF0000]text[/]`），以便生成带颜色的 ASCII 艺术字。
