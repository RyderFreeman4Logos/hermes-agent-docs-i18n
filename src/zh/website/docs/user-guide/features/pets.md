---
sidebar_position: 11
title: "Pets (Petdex Mascots)"
description: "Adopt an animated mascot that reacts to agent activity across the CLI, TUI, and desktop app"
---

# 宠物插件

Hermes 能在 **CLI**、**TUI** 以及 **桌面应用** 中展示一个动画形式的**宠物**——这是一个小型吉祥物精灵，会根据智能体的当前状态（空闲、使用工具、思考、完成任务或失败）做出相应反应。这些宠物取自公开的 [petdex](https://github.com/crafter-station/petdex) 图库。

宠物仅具有装饰性，**不会影响提示词缓存、令牌数量或智能体的行为**——该精灵纯粹用于视觉展示。此功能默认处于关闭状态，需手动安装并选择宠物后才会启用。

## 工作原理

- 宠物会被安装到用户个人资料目录下的 `pets/` 文件夹中（路径为 `<HERMES_HOME>/pets/<slug>/`），因此每个[个人资料](../profiles.md)都会拥有独立的宠物集合。
- 选择某个宠物后，系统会将 `display.pet.slug` 和 `display.pet.enabled` 的值写入 `config.yaml` 文件中，这些信息不会以机密或环境变量的形式存储。
- 所有的界面都会监控自身已记录的智能体活动，并将其映射为六种动画状态之一。由于映射规则统一，所有界面的表现方式都一致：

  | 智能体状态 | 宠物状态 |
  | --- | --- |
  | 使用工具或轮次刚刚失败 | `failed` |
  | 计划已完成（所有任务均处理完毕） | `jump`（庆祝状态） |
  | 轮次顺利结束 | `wave` |
  | 正在执行工具 | `run` |
  | 模型正在思考或读取内容 | `review` |
  | 处于处理中（状态未明确） | `run` |
  | 等待用户操作（需用户进一步说明或确认） | `waiting`（在旧版8行界面中会回退为 `idle` 状态） |
  | 没有发生任何活动 | `idle` |

## 渲染方式

在终端（CLI/TUI）环境中，如果终端支持图形协议（如 **kitty**、**Ghostty**、**WezTerm**、**iTerm2** 或 **sixel**），Hermes 会以高保真度渲染该精灵。否则，系统会自动回退为纯色 Unicode **半块字符**渲染方式。在管道或重定向操作中（即没有 TTY 的情况下），出于设计考虑，终端渲染功能会被禁用。

桌面应用则将宠物作为浮动精灵显示在画布上，用户可通过 **设置 → 外观** 来切换其显示状态。

## CLI 快速入门

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
| 浏览宠物库 | `hermes pets list [查询条件] [--limit N]` |
| 列出已安装的宠物 | `hermes pets list --installed` |
| 安装宠物 | `hermes pets install <slug> [--select] [--force]` |
| 设置当前激活的宠物 | `hermes pets select [slug]`（省略 slug 可自动选择） |
| 调整所有位置上的宠物大小 | `hermes pets scale <比例值>`（例如 `0.5`，范围为 0.1–3.0） |
| 预览/播放动画 | `hermes pets show [slug] [--state <状态>] [--cycle] [--once] [--mode <模式>] [--scale <比例>]` |
| 禁用宠物功能 | `hermes pets off` |
| 移除已安装的宠物 | `hermes pets remove <slug>` |
| 检查配置问题 | `hermes pets doctor` |

`hermes pets show` 的选项包括：

- `--state` — 播放特定状态（`idle`、`wave`、`run`、`failed`、`review`、`jump`）。
- `--cycle` — 循环播放所有状态。
- `--once` — 仅播放一次，而非循环播放。
- `--mode` — 覆盖渲染协议（`kitty`、`iterm`、`sixel`、`unicode`、`auto`）。
- `--scale` — 覆盖屏幕显示比例（`0` 表示使用配置值）。

## `/pet` 斜杠命令

在 CLI 和 TUI 环境中，无需离开当前会话即可管理宠物功能：

- `/pet` — 切换宠物功能的开启/关闭状态（若无激活的宠物，则自动启用第一个已安装的宠物）。
- `/pet list` — 浏览宠物库。
- `/pet scale <比例值>` — 调整所有位置上的宠物大小（例如 `/pet scale 0.5`）。
- `/pet <slug>` — 选用特定的宠物。
- `/pet off` — 禁用宠物功能。

在 TUI 中，`/pet list` 会弹出交互式选择界面；而在桌面应用中，则会打开 Cmd+K 宠物调色板。

## 桌面应用

在桌面应用中，可通过两种方式管理宠物：

- **Cmd+K → “Pets…”** — 无需离开键盘即可浏览、搜索、选用及切换宠物功能（与主题选择器类似）。
- **设置 → 外观** — 显示相同的宠物库，此外还配有**大小滑块**，可实时调整浮动吉祥物的尺寸。

这两种方式都能直接在原位调整浮动吉祥物的大小——尺寸变化会立即生效；选用新宠物后，它也会瞬间亮起。

### 弹出式覆盖层

按住 **Shift 键并点击** 浮动宠物，即可将其弹出到独立的透明全屏窗口中。即使将 Hermes 最小化（类似 Codex 模式），该窗口依然保持可见，让您一目了然地了解智能体当前正在执行什么操作。

宠物弹出后支持的交互手势：

| 手势 | 功能 |
| --- | --- |
| **拖动** | 将宠物移动到屏幕上的任意位置，甚至可以移出应用范围。其位置及显示状态在重启后依然保留。 |
| **单击** | 打开迷你指令输入框，无需打开完整应用即可向当前会话发送提示语。 |
| **双击** | 切换应用窗口状态：若窗口处于最前面则最小化，若已隐藏则恢复显示。 |
| **按住 Shift 键再点击** | 将宠物重新拉回窗口内。 |
| **邮件图标** | 仅在您离开时某轮对话已完成时出现；点击该图标可在最新对话线程中唤起应用并标记该消息为已读。 |

只有弹出式的宠物才会显示**对话气泡**（如“正在处理…”、“正在思考…”、“轮到您了”等）——在窗口内的情况下，应用界面本身即为显示载体，因此宠物不会在那里显示任何信息。

该覆盖层实际上是应用内宠物的纯化版本——它不建立独立的网关连接，也不会出现在任务栏或应用切换器中。

## 配置设置

所有相关设置均保存在 `config.yaml` 文件的 `display.pet` 部分中：

```yaml
display:
  pet:
    enabled: false        # master on/off (true once you select a pet)
    slug: ""              # active pet; empty = first installed
    render_mode: auto      # auto | kitty | iterm | sixel | unicode | off
    scale: 0.33           # master size knob (relative to native 192x208 frames)
    unicode_cols: 0       # hard override for terminal width (0 = derive from scale)
```

- **`scale`** 是唯一的整体缩放控制参数。该数值会同时影响所有界面元素的尺寸：桌面画布会根据它来调整像素大小，而 CLI/TUI 则以此为依据确定终端列的宽度。半块字符的回退机制会设定一个最低可读性标准——由于无法像真正的像素级渲染或 GUI 渲染那样大幅缩小尺寸，否则内容就会变得模糊不清，因此相同的 `scale` 值在像素级渲染下显示清晰，但在半块字符模式下则会被限制在最低标准。

- **`render_mode: auto`** 会自动检测当前使用的终端图形协议，如 kitty、iTerm2 或 sixel，并回退到 Unicode 半块字符模式。如需强制指定某种协议，可显式设置该参数；若设置为 `off`，则可在保持桌面宠物显示的同时禁用终端渲染功能。

- **`unicode_cols`** 用于独立于 `scale` 参数来固定终端列的宽度；若将其设置为 `0`，则列宽将由 `scale` 自动决定。

## 故障排除

运行 `hermes pets doctor` 命令，即可查看以下信息：

- 宠物目录及已安装的宠物列表；
- `display.pet.enabled`、`display.pet.slug` 以及当前激活的宠物信息；
- 配置的 `render_mode`、检测到的终端图形协议以及 TTY 的实际渲染模式；
- 是否能够成功导入用于精灵图解码的 Pillow 库。

一旦宠物被安装、选中、启用且 Pillow 可用，该命令会输出 `✓ ready`。

常见注意事项：

- 宠物只有在**既已安装又处于选中状态**（即 `enabled: true`）时才会显示。
- 在管道或重定向操作中（不存在 TTY），按设计要求终端渲染功能会被禁用。
- petdex npm CLI 会将安装包保存在 `~/.codex/pets` 目录下；而 Hermes 则使用其自身的基于用户配置的 `<HERMES_HOME>/pets/` 目录——请通过 `hermes pets` 命令进行安装。

## 参考资料

- [`petdex` 技能](../skills/bundled/productivity/productivity-petdex.md)允许智能体根据用户需求自动安装和切换宠物。
