---
sidebar_position: 11
title: "Pets (Petdex Mascots)"
description: "Adopt an animated mascot that reacts to agent activity across the CLI, TUI, and desktop app"
---

# 宠物插件

Hermes 能在 **CLI**、**TUI** 以及 **桌面应用** 中展示一个动态的**宠物**——即一个小型的吉祥物精灵，它会根据智能体当前的状态（空闲、正在使用工具、思考、任务完成或失败）做出相应反应。这些宠物来自公开的 [petdex](https://github.com/crafter-station/petdex) 图库。

宠物仅具有装饰性，**不会影响提示词缓存、令牌数量或智能体的行为**——该精灵纯粹用于视觉展示。此功能默认处于关闭状态，直到您安装并选择某个宠物后才会启用。

## 工作原理

- 宠物会被安装到您个人配置文件中的 `pets/` 目录下（路径为 `<HERMES_HOME>/pets/<slug>/`），因此每个 [配置文件](../profiles.md) 都会拥有自己独立的宠物集合。
- 选择某个宠物后，系统会将 `display.pet.slug` 和 `display.pet.enabled` 的值写入 `config.yaml` 文件中——相关数据不会以密钥或环境变量的形式存储。
- 各种界面都会监控自身已追踪的智能体活动，并将其映射为六种动画状态之一。由于映射规则统一，所有界面的表现都一致：

  | 智能体状态 | 宠物状态 |
  | --- | --- |
  | 工具使用或轮次刚刚失败 | `failed` |
  | 计划完成（所有任务均处理完毕） | `jump`（庆祝状态） |
  | 轮次顺利结束 | `wave` |
  | 正在执行工具 | `run` |
  | 模型正在思考或读取内容 | `review` |
  | 正在处理中（状态未明确） | `run` |
  | 等待用户操作（需进一步澄清或确认） | `waiting`（在旧版8行界面中会回退为 `idle` 状态） |
  | 没有发生任何活动 | `idle` |

## 渲染方式

在终端（CLI/TUI）环境中，只要终端支持图形协议（如 **kitty**、**Ghostty**、**WezTerm**、**iTerm2** 或 **sixel**），Hermes 就会以最高清晰度渲染该精灵图像；否则它会自动切换为真彩色 Unicode **半块**渲染模式。而对于管道或重定向操作（即没有 TTY 的情况），系统设计上会禁用终端渲染功能。

桌面应用程序则会在画布上将该宠物以浮动精灵的形式展示，用户可通过 **设置 → 外观** 来切换其显示模式。

## 快速入门（CLI）

```bash
# Browse the gallery (filter by substring)
hermes pets list
hermes pets list cat

# Install a pet and make it active in one step
hermes pets install boba --select

# Preview / animate it in your terminal (Ctrl+C to stop)
hermes pets show

# Check your setup
hermes pets doctor
```

## `hermes pets` 命令

| 功能 | 命令 |
| --- | --- |
| 浏览插件库 | `hermes pets list [查询条件] [--limit N]` |
| 列出已安装的插件 | `hermes pets list --installed` |
| 安装插件 | `hermes pets install <slug> [--select] [--force]` |
| 设置当前使用的插件 | `hermes pets select [slug]`（省略 slug 可自动选择） |
| 调整所有插件的显示大小 | `hermes pets scale <比例值>`（例如 `0.5`，范围限制在 0.1–3.0 之间） |
| 预览/播放动画 | `hermes pets show [slug] [--state <状态>] [--cycle] [--once] [--mode <模式>] [--scale <比例值>]` |
| 禁用插件 | `hermes pets off` |
| 移除已安装的插件 | `hermes pets remove <slug>` |
| 检查配置状态 | `hermes pets doctor` |

`hermes pets show` 的可选参数：

- `--state` — 播放特定状态（`idle`、`wave`、`run`、`failed`、`review`、`jump`）。
- `--cycle` — 循环播放所有状态。
- `--once` — 仅播放一次，而非循环播放。
- `--mode` — 覆盖渲染协议（`kitty`、`iterm`、`sixel`、`unicode`、`auto`）。
- `--scale` — 覆盖屏幕显示比例（`0` 表示使用配置值）。

## `/pet` 路径命令

在 CLI 和 TUI 环境中，无需离开当前会话即可管理插件：

- `/pet` — 切换插件的开启/关闭状态（若没有当前激活的插件，则自动启用第一个已安装的插件）。
- `/pet list` — 浏览插件库。
- `/pet scale <比例值>` — 调整所有插件的显示大小（例如 `/pet scale 0.5`）。
- `/pet <slug>` — 使用指定的插件。
- `/pet off` — 禁用插件。

在 TUI 中，`/pet list` 会弹出交互式选择界面；而在桌面应用中，则会打开 Cmd+K 插件调色板。

## 生成宠物（`/hatch`）

除了从图库中安装现成的宠物外，Hermes 还能通过文本描述**生成全新的宠物**——这得益于其专有的 AI 精灵图生成流程。

- **命令行/TUI**：使用 `/hatch <description>`（别名 `/generate-pet`），或输入 `hermes pets` 查看生成流程。
- **桌面应用**：采用类似宝可梦图鉴的**生成界面**——包含动画蛋效果、孵化特效以及草图选择器。

生成过程分为两步，且会受到成本限制：

1. **基础草图生成**：首先会生成少量低成本、仅基于提示词的“宠物外观设想”版本。你可以从中选择一个，或进行修改并重新尝试以获得新结果。
2. **孵化完成**：所选的基础草图将作为参考图像，为 Hermes 的每种状态（空闲、思考、使用工具等）生成一列对应的动画帧。这些帧会被确定性地切割成单个画面，并打包进标准的宠物图鉴/Codex 图集格式（8×9 网格，共 192×208 个单元格）。最终得到的就是可直接保存的有效精灵图集，甚至可以用于 `petdex submit` 功能。

### 图像后端

生成过程会使用当前激活的[图像生成提供方](/user-guide/features/image-generation)，但该功能需要**参考图像作为基准**，以确保每列动画的字符与基础模型保持一致。支持参考图像功能的后端包括：**Nous Portal**、**OpenRouter**、**OpenAI**（`gpt-image-2`）以及 **Krea**。OpenRouter 和 Nous 默认会启用以质量优先的模型链。

- 解决方案优先级为 Nous Portal → OpenAI → OpenRouter。
- 若未配置具备参考功能的后端，生成过程会显示一条可操作的错误提示，指引用户前往 `hermes tools` → Image Generation。（安装或使用现有的图库宠物则无需图像后端。）
- 可通过 `HERMES_PET_IMAGE_PROVIDER` 环境变量来覆盖后端（例如：`HERMES_PET_IMAGE_PROVIDER=openrouter`）。

## 桌面应用

在桌面应用中，您可以通过两种方式管理宠物：

- **Cmd+K → “Pets…”** — 无需离开键盘即可浏览、搜索、领养宠物并切换显示状态（操作方式与主题选择器相同）。
- **设置 → 外观** — 除了相同的图库外，还提供一个**大小滑块**，允许您在拖动时实时调整浮动吉祥物的尺寸。

这两种方式均可直接在原位对浮动吉祥物进行领养、切换或调整尺寸——尺寸变化会立即生效；新宠物被领养后也会瞬间亮起。

### 自由移动功能

“设置 → 外观”中有一个**自由移动**开关：开启后，当智能体处于空闲状态时，宠物会自行在窗口内移动——行走、暂停或在不同位置间跳跃。此功能仅在宠物位于窗口内且处于活跃状态、同时智能体处于静止状态时才会运行；一旦智能体开始执行其他操作（如工作、庆祝），该功能会立即停止。该开关默认处于关闭状态，且会在重启后保持设置。

### 使用 Alt+滚轮调整尺寸

按住 **Alt** 键并滚动鼠标滚轮，将光标悬停在宠物模型上即可实时调整其大小——无论是在应用窗口中还是弹出的覆盖层上均可操作。覆盖层会向光标位置缩放，且调整后的比例会被保存下来，因此即使重启应用，该比例依然保持不变，并与应用内的宠物模型同步。

### 情感反馈

对智能体说些赞美的话，比如“很棒的机器人”、“谢谢”、“爱你”、“<3”或发送心形表情符号，宠物就会做出相应反应：在桌面端会浮现浮动的心形，在CLI/TUI模式下则会闪烁心形。系统通过本地预置的无令牌词典来分析每条用户消息（无需调用模型），仅对针对智能体的赞美与感激之情作出响应，而不会对一般的积极情感做出反应。所有界面——CLI宠物、TUI模式、桌面浮动宠物以及弹出覆盖层——都会基于相同的信号作出反应。

### 弹出覆盖层

按住 **Shift** 键并点击浮动宠物，即可将其弹出为独立的透明窗口，始终显示在屏幕最上层。即便将Hermes最小化（类似Codex模式），该窗口依然可见，让您一目了然地了解智能体当前正在做什么。

弹出后的手势操作：

| 手势 | 操作 |
| --- | --- |
| **拖动** | 将宠物移动到屏幕上的任意位置，甚至应用外部。其位置及出现/隐藏状态在重启后依然保持不变。 |
| **单击** | 打开迷你编辑器，向最近的会话发送提示语——无需打开完整应用。 |
| **双击** | 切换应用窗口：若窗口处于最前端则最小化，若已隐藏则恢复显示。 |
| **按住 Shift 键后点击** | 将宠物重新唤回到窗口中。 |
| **邮件图标** | 仅当您离开时某轮对话结束才会出现；点击可在最近的对话线程中唤起应用（并标记为已读）。 |

仅有弹出的宠物会显示**对话气泡**（如“正在处理…”、“正在思考…”、“轮到您了”等）——在窗口内的情况下，应用本身即为界面载体，因此宠物不会发出声音。

该悬浮层只是应用内宠物的镜像版本——它不拥有独立的网关连接，也不会出现在任务栏或应用切换器中。

## 配置

所有相关设置均位于 `config.yaml` 文件的 `display.pet` 部分：

```yaml
display:
  pet:
    enabled: false        # master on/off (true once you select a pet)
    slug: ""              # active pet; empty = first installed
    render_mode: auto      # auto | kitty | iterm | sixel | unicode | off
    scale: 0.33           # master size knob (relative to native 192x208 frames)
    unicode_cols: 0       # hard override for terminal width (0 = derive from scale)
```

- **`scale`** 是唯一的整体缩放控制参数。该数值会同步缩小所有界面元素：桌面画布会根据其值调整像素大小，而 CLI/TUI 则以此为依据确定终端列宽。半块字符的回退机制会设定一个最低可读性标准——它无法像真正的像素级渲染或 GUI 渲染那样大幅缩小，否则内容会变得模糊不清，因此相同的 `scale` 值在像素级渲染下显示清晰，但在半块字符模式下则会被限制在最低标准。

- **`render_mode: auto`** 会自动检测当前使用的终端图形协议（如 kitty/iTerm2/sixel），若无法识别则回退至 Unicode 半块字符模式。如需强制指定某种协议，可显式设置该参数；若设置为 `off`，则可在保持桌面宠物显示的同时禁用终端渲染功能。

- **`unicode_cols`** 用于独立于 `scale` 固定终端列宽；若将其值设为 `0`，则列宽将由 `scale` 自动决定。

## 故障排除

运行 `hermes pets doctor` 命令，该命令会输出以下信息：

- 宠物目录及其包含的宠物列表，
- `display.pet.enabled`、`display.pet.slug` 以及当前激活的宠物信息，
- 配置的 `render_mode`、检测到的终端图形协议以及 TTY 的实际渲染模式，
- 是否能够导入用于精灵图解码的 Pillow 库。

一旦宠物已安装、被选中、处于启用状态且 Pillow 可用，该命令会输出 `✓ ready`。

常见注意事项：

- 宠物只有在**既已安装又已被选中**（即 `enabled: true`）的情况下才会显示。
- 在管道或重定向操作中（不存在 TTY 环境），按设计要求终端渲染功能会被禁用。
- petdex npm CLI 会将程序安装到 `~/.codex/pets` 目录；而 Hermes 则使用自身基于用户配置的 `<HERMES_HOME>/pets/` 目录——请通过 `hermes pets` 命令进行安装。

## 参见

- [`hermes-agent` 技能](../skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent.md)允许智能体根据您的需求为您安装或更换宠物（详情请参阅其`references/petdex.md`文件）。
