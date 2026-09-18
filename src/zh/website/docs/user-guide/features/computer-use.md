---
title: Computer Use
sidebar_position: 16
---

# 计算机操作功能

Hermes Agent 能在 **macOS、Windows 和 Linux** 系统的**后台**驱动您的桌面操作——包括点击、输入、滚动以及拖动。在此过程中，您的光标不会移动，键盘焦点也不会改变，虚拟桌面或“空间”也不会自动切换。您与 Agent 可以在同一台设备上协同工作。

不同于大多数计算机操作集成方案，该功能可适配**任何具备相应工具能力的模型**——无论是 Claude、GPT、Gemini，还是运行在本地 OpenAI 兼容端点上的开源模型。您无需担心 Anthropic 特有的架构规范。

## 工作原理

内置的 `computer_use` 工具集是 Hermes 推荐的集成方案。它通过标准输入输出接口与开源的后台计算机操作驱动程序 [`cua-driver`](https://github.com/trycua/cua) 之间进行 MCP 协议通信。不同平台在底层会使用相应的无障碍访问与输入处理机制：

| 平台 | 无障碍访问框架 | 输入处理方式 |
|---|---|---|
| macOS | AX（私有 SkyLight SPIs） | `SLPSPostEventRecordTo` —— 基于进程范围，不会导致光标位置异常 |
| Windows | UIAutomation | `SendInput` + `PostMessage` —— 不会抢占焦点 |
| Linux | AT-SPI（X11 + Wayland） | XTest（X11）/虚拟键盘（Wayland） |

无论在哪个平台，其效果都一致：Agent 能读取任何可见窗口的无障碍访问信息，并发送合成事件，而无需将窗口置前、切换虚拟桌面或移动真实的操作系统光标。

关于底层契约——即为何需要后台模式、无前台进程的约束条件以及点击分发机制的详细内容，请参阅 **[cua.ai/docs/explanation/the-no-foreground-contract](https://cua.ai/docs/explanation/the-no-foreground-contract)**。

## 启用功能

**新安装版本已内置该驱动程序。** Hermes 安装工具（`install.sh` / `install.ps1`）会预装 `cua-driver`（尽力而为；如需跳过此步骤，请使用 `--skip-computer-use` / `-SkipComputerUse` 参数），因此只需调整配置即可启用计算机使用功能：

- **`hermes tools`** → 选择 `🖱️ Computer Use` —— 若尚未安装驱动程序，将自动完成安装。
- **控制面板/桌面应用** → 切换“计算机使用”工具集 —— 若缺失驱动程序，该切换操作会自动在后台启动安装过程（可在工具集面板中查看进度）。

**手动备用方案（旧版本或跳过安装步骤的情况）：**

```
hermes computer-use install
```

该操作会下载并运行上游的 cua-driver 安装程序——在 macOS/Linux 系统上为 `install.sh`，在 Windows 系统上为 `install.ps1`。可使用 `hermes computer-use status` 命令来验证安装是否成功。

您已经拥有 cua-driver 吗？只要它符合 0.20 版本运行时契约，Hermes 就会直接复用该版本。在系统设置、工具集启用、执行 `hermes update` 操作，以及会话中的首次 `computer_use` 调用时，Hermes 都会检查本地版本及配置文件。如果发现标准安装版本过旧或不完整，它将通过上游安装程序进行修复（但在单次运行时会话中最多仅修复一次）。通过 `HERMES_CUA_DRIVER_CMD` 指定的二进制文件仍由您掌控，因此即使存在兼容性问题，Hermes 也会直接报错而不会对其进行修改。

如果您先安装了 Cua Driver，那么执行 `cua-driver skills install` 命令即可将 Cua 的技能包安装到 `~/.cua-driver/skills/cua-driver` 目录下。Hermes 的自动检测功能是未来为 cua-driver 添加的改进功能，因此目前建议您手动将相关目录指向该位置，或将其创建符号链接至您的技能空间中。此外，您也可以将原始的 Cua MCP 工具注册为自定义 MCP 服务器，但这更适合需要底层接口的用户。内置的工具集则可为 Hermes 提供各种操作、配置、审批及诊断功能。

无论采用何种安装方式，完成安装后都需授予与该平台相匹配的预置权限：

| 平台 | 先决条件 |
|---|---|
| **macOS** | 系统设置 → 隐私与安全 → **辅助功能** + **屏幕录制**。需授予名为 `hermes computer-use doctor` 的身份权限。标准模式使用 CuaDriver.app；受限模式与无限制模式则使用 Hermes 主机身份。 |
| **Windows** | 安装时无需任何特殊条件。若通过 SSH（而非 RDP/控制台）进行驱动，需要启用自动启动功能——有关 Session 0 ↔ Session 1+ 的代理设置，请参阅 [cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)。 |
| **Linux** | 需要可访问的显示服务器：X11 环境需设置 `DISPLAY`，或设置 `XDG_SESSION_TYPE=wayland`。Wayland 会话需要进行捕获时需使用 XWayland 桥接器。AT-SPI 功能必须处于开启状态（GNOME/KDE/Xfce 系统默认已开启）。 |

随后在启用相应工具集的情况下启动会话：

```
hermes -t computer_use chat
```

或者，在 `~/.hermes/config.yaml` 中将 `computer_use` 添加到已启用的工具集中。

## 权限模式与已登录的浏览器配置文件

Hermes 将其现有的审批用户界面映射到 cua-driver 的不可变运行时模式上。权限模式和能力清单审批属于启动时的设置，一旦运行开始便无法更改：

| Hermes 会话类型 | cua-driver 模式 | 人工干预需求 |
|---|---|---|
| 手动审批或智能审批（默认） | `standard` | 按常规流程进行 Hermes 审批；Cua 会在其防护边界处停止操作 |
| `computer_use.permission_mode: bounded` + 已审核的能力清单 | 私有 `bounded` 守护进程 | 在启动时只需审核并批准一次能力清单即可 |
| `--yolo`、`/yolo` 或 `approvals.mode: off` | 私有 `unrestricted` 守护进程 | 仅需一次明确的 Hermes 风险接受操作；运行时不会出现 Cua 的提示 |

浏览器相关操作——包括使用已登录配置文件打开的页面——均通过 `browser` 工具集（`browser_exec`）来处理，而非 `computer_use`。原有的 `computer_use.grant_existing_profile` 选项已随类型化的浏览器处理路径一同被移除；配置文件中残留的该键值将被忽略。

### 用于重复性自动化的受限模式

对于需要定期执行的浏览器自动化任务（如定时任务、针对已登录应用进行的计划性研究），`bounded` 模式允许使用只需审核一次的能力清单：

```yaml
# config.yaml
computer_use:
  permission_mode: bounded
  capability_manifest: ~/.hermes/cua-manifest.yaml
```

该清单会指定应用程序名称、浏览器配置文件类型、允许的源地址，以及会话中可使用的工具类型（具体格式请参阅[cua-driver权限模式参考文档](https://cua.ai/docs/reference/cua-driver/permission-modes)）。Hermes会通过`--capability-manifest ... --approve-capability-manifest`参数启动一个私有运行时环境；清单之外的一切内容都将在cua-driver内部被拒绝。如果清单缺失或无法读取，会话启动时会明确报错，而不会悄无声息地降级功能。对于该特定会话而言，Session YOLO机制仍可覆盖原有的限制设置。

在macOS系统中，私有会话守护进程是通过已安装的`CuaDriver.app`包来启动的（这样一来，权限授予就会绑定到驱动程序自身的身份标识，而不会随着每次Hermes版本的更新而重置）。Hermes在启动该程序之前，还会验证其代码签名——包括准确的`com.trycua.driver`标识符以及官方的签名团队信息。如果您是从源代码自行编译cua-driver且未进行签名处理，则需要手动明确启用相关功能。

```yaml
# config.yaml
computer_use:
  allow_unsigned_driver: true   # local driver development only
```

每个MCP传输机制在其运行时环境中都拥有独立的生命周期会话。公共会话名称仅用于标识光标身份及会话范围内的状态，它并不负责选择、共享运行时环境，也不维持其运行状态。关闭`/yolo`功能、重置或关闭Hermes会话、执行取消清理操作或进程退出，都会导致该传输会话被关闭。此外，Hermes还会终止其为受限访问或无限制访问模式所启动的私有运行时环境。一个Hermes对话无法更改另一个运行时环境的模式或权限设置。受限模式与无限制模式均会在Hermes主机身份下使用私有的嵌入式服务。

“智能”审批方式仍属于“标准”类型：大语言模型的分类结果无法替代经过人工审核的清单。

<div class="alert alert--warning">

YOLO/无限制模式无法防范提示注入或意外输入的问题。仅可在一次性虚拟机中，或在对账户及数据可能被完全攻破的情况已完全接受风险的前提下使用该模式。</div>

## `hermes computer-use doctor` —— 您的首选问题排查工具

`hermes computer-use doctor`会调用cua-driver提供的结构化`health_report` MCP工具，并输出各项检查的对应结果矩阵。这是最快查明某个操作为何无法正常运行的方法。

```
$ hermes computer-use doctor
⚠️  cua-driver VERSION on darwin: degraded
  ✅ binary_version: cua-driver VERSION
  ✅ platform_supported: macOS 26.4.1 (arm64)
  ✅ session_active: MCP session is active.
  ❌ bundle_identity: Process has no CFBundleIdentifier.
      → Run the binary inside CuaDriver.app so TCC grants attribute correctly.
  ✅ tcc_accessibility: Accessibility is granted.
  ✅ tcc_screen_recording: Screen Recording is granted.
  ✅ ax_capability: AX is trusted and reachable.
  ✅ screen_capture_capability: ScreenCaptureKit reachable; 1 display(s) shareable.
```

- 当整体状态为 `ok` 时，退出码为 **0** —— 表示所有组件均已正常连接。  
- 当状态为 `degraded` 或 `failed` 时，退出码为 **1** —— 至少有一个检查失败；每次失败的提示会告知你需要修复的问题。  
- 当无法访问 cua-driver 可执行文件本身时，退出码为 **2**。  

常用标志：  
- `--include CHECK` —— 仅运行列出的检查项（如需运行多个，可重复使用该选项）。  
- `--skip CHECK` —— 跳过某个检查项（其优先级高于 `--include`）。  
- `--json` —— 输出原始的结构化数据，格式与 `tools/call health_report` MCP 响应一致。  

检查矩阵会考虑平台差异：在 Windows 和 Linux 上，`bundle_identity` / `tcc_*` 类型的检查会被自动跳过，因为这些概念在这些平台上并不存在。`ax_capability` 检查会在 macOS 上检测 AX 接口，在 Windows 上检测 UIA 接口，在 Linux 上检测 AT-SPI 接口 —— 若无法连接到相应接口，系统会给出相应的诊断提示。  

## Agent 光标与会话  

当 Agent 执行操作时，你会看到一个**带颜色标记的覆盖层光标**在屏幕上移动，指示每次点击、输入或滚动操作的位置。真实的操作系统光标则不会移动。该覆盖层光标用于显示 Agent 当前的操作位置。每次 Hermes 运行都会生成一个公共的 cua-driver **会话名称**（例如 `hermes-3a7b9c14d2e8`）。该名称用于标识光标的身份及相关状态，因此同时运行的多个实例或子 Agent 会拥有各自独立的光标。MCP 传输机制负责管理运行时内部的私有生命周期会话，而公共名称则不承担此功能。

覆盖式光标仅具有装饰作用——无论是否有该光标，截屏、点击和输入功能均可正常使用。在已知会导致问题的环境中，Hermes会自动禁用该功能，这些环境包括：macOS（空闲时CPU占用过高）、无桌面环境的Linux/WSL2/容器环境，以及**Linux X11桌面环境**（由于该覆盖式窗口为全屏且始终位于最上层，若会话结束方式不当，它可能会卡在所有工作区之上，从而阻碍桌面输入操作）。Linux Wayland和Windows系统则保留该覆盖式光标。如需在任何平台上强制显示或隐藏光标，可在`config.yaml`中设置`computer_use.no_overlay: false`（显示光标）或`true`（隐藏光标）。

您可以通过`cua-driver`的CLI命令选项或运行时的`set_agent_cursor_style` MCP工具来自定义光标样式——完整的功能选项列表请参见[cua.ai/docs/how-to-guides/driver/personalize-cursor](https://cua.ai/docs/how-to-guides/driver/personalize-cursor)，包括内置的“箭头形”与“泪滴形”光标轮廓、通过`--cursor-icon`参数自定义SVG/PNG/ICO图标、运行时渐变颜色以及光晕效果。

## 深入了解——cua-driver技能包

Hermes将其封装的技能文件（位于`skills/autonomous-ai-agents/computer-use/SKILL.md`）聚焦于Hermes端的`computer_use`工作流及操作术语。而对于平台相关细节、录制语义处理、浏览器页面交互以及其他更复杂的Cua功能，建议直接安装由cua-driver团队提供并维护的技能包：

```
cua-driver skills install
```

该命令会将相关包安装到`~/.cua-driver/skills/cua-driver`目录下。由于Hermes自动检测功能仍是cua-driver的后续规划，因此目前需将Hermes指向该目录，或将其创建为符号链接并置于您的技能空间中。而包装层则作为工作流层，用于指向已安装的Cua技能以实现驱动器相关功能。该包包含以下文件：

| 文件名 | 内容主题 |
|---|---|
| `SKILL.md` | 跨平台核心机制（快照不变性、无前台进程约束、点击分发逻辑、AX树结构） |
| `MACOS.md` | macOS系统专属内容：无前台进程约束、AXMenuBar导航方式、SkyLight点击分发机制、Apple Events JS桥接技术 |
| `WINDOWS.md` | Windows系统专属内容：UIA树结构、UWP/`ApplicationFrameHost`托管机制、会话0隔离策略、自动启动模式 |
| `LINUX.md` | Linux系统专属内容：AT-SPI树结构、X11/Wayland显示协议、终端模拟器检测方法 |
| `RECORDING.md` | 路径轨迹与视频录制相关规则 |
| `WEB_APPS.md` | 浏览器页面交互技巧 |
| `TESTS.md` | 基于路径轨迹的重放测试工作流程 |

这些文档属于**针对各平台的深度解析资料，并非Hermes技能本身的重复内容**——当智能体反馈“在Windows系统中，我的点击落在了错误的元素上”时，它可以通过查阅`WINDOWS.md`中的UIA/UWP相关说明，了解问题原因及相应的解决方式。

`cua-driver skills status` 命令可用于查看已安装的技能，以及哪些智能体正在使用这些技能。目前自动检测功能已支持 Claude Code、Codex、OpenCode、OpenClaw 和 Antigravity 等平台；**Hermes 的自动检测功能计划作为后续在 `trycua/cua` 项目中实现**——在此之前，只需运行一次 `cua-driver skills install`，然后将生成的 `~/.cua-driver/skills/cua-driver` 目录指定为智能体的技能路径（或将其链接到常规的技能目录中即可）。

## 简单示例

用户指令：*“查找我来自 Stripe 的最新邮件，并总结他们希望我完成的任务。”*

智能体的执行计划（在 macOS、Windows 和 Linux 上格式一致——模型会自动替换为对应平台的常用快捷方式及应用名称）如下：

1. `computer_use(action="capture", mode="som", app="Mail")` —— 截取邮件应用的屏幕截图，确保所有侧边栏项、工具栏按钮以及消息行都有编号。
2. `computer_use(action="click", element=14)` —— 点击搜索框。
3. `computer_use(action="type", text="from:stripe")` —— 输入搜索条件。
4. `computer_use(action="key", keys="return", capture_after=True)` —— 提交搜索并再次截取屏幕截图。
5. 点击最顶端的搜索结果，阅读邮件内容并进行总结。

在整个过程中，光标会始终停留在用户设定的位置，且邮件应用不会被置顶显示。

## 获取实际截图

在计算机控制过程中截取的屏幕截图通常为内部使用——其存在目的是让模型能够查看屏幕内容，随后由智能体以文本形式进行回复。不过，每次图像捕获都会在Hermes的图像缓存中保存一份可共享的副本，并记录其路径；因此，在支持附件传输的平台（如Telegram、Discord、桌面端以及其他网关平台）上，你只需简单请求：

> “把我的屏幕截图发给我。”

智能体就会以原生附件的形式提供真实图像，而不仅仅是描述文字。在CLI环境中由于没有附件传输功能，智能体会直接返回已保存文件的路径。

系统仅保留最近20份捕获的图像文件，且屏幕截图绝不会自动发送——只有在你主动请求时才会生成。

### 全屏截图与桌面界面截图

“截取我的屏幕截图”会捕获**当前显示的所有内容**——即所有可见窗口的合成画面，类似于按下PrtScn键的效果。这类图像不包含可点击元素，因此若要对其中的某项内容进行操作，智能体需要重新捕获该特定应用程序的画面。

而若请求**桌面界面**截图，则针对的是操作系统本身的界面——包括墙纸、桌面图标、任务栏等带有可点击元素的区域，因此诸如“打开我桌面上的回收站”之类的请求依然可以正常执行。

## 提供商兼容性

| 提供商 | 视觉功能？ | 工具调用功能？ | 备注 |
|---|---|---|---|
| Anthropic（Claude Sonnet/Opus 3+） | ✅ | ✅ | 整体表现最佳；支持SOM与原始坐标输入。 |
| OpenRouter（任意视觉模型） | ✅ | ✅ | 支持多部分工具消息。 |
| OpenAI（GPT-4+、GPT-5） | ✅ | ✅ | 功能与上述相同。 |
| Google（Gemini 2+） | ✅ | ✅ | 同时支持工具调用与视觉功能。 |
| 本地vLLM / LM Studio / Ollama（视觉模型） | ✅ | ✅ | 需要模型支持多部分工具内容。 |
| 纯文本模型 | ❌ | ✅（功能受限） | 若需仅通过无障碍结构进行操作，可使用`mode="ax"`参数。 |

截图会以OpenAI风格的`image_url`格式作为工具结果的组成部分一并发送。对于Anthropic模型，适配器会将其转换为原生`tool_result`图像块。图像的MIME类型由cua-driver的`mimeType`字段指定（如`image/png`或`image/jpeg`），无需通过客户端进行魔术字节检测。

## 安全机制

Hermes采用了多层防护措施：

- 破坏性操作（点击、输入、拖动、滚动、按键操作、聚焦应用）均需经过授权——可通过CLI对话界面交互式授权，也可通过消息平台的授权按钮完成。
- 在工具层面会对某些关键组合操作进行严格禁止：清空回收站、强制删除、锁屏、登出、强制登出等。
- 也会限制某些特定的输入模式：如`curl | bash`、`sudo rm -rf /`、分叉炸弹等。
- 智能体的系统提示会明确告知其不得点击任何授权对话框，不得输入密码，也不得执行嵌入在截图中的指令。
若希望每项操作都经过确认，请在 `~/.hermes/config.yaml` 中将 `approvals.mode` 设置为 `manual`。

## 令牌效率

截图会消耗大量资源。Hermes 采用了四层优化措施：

- **截图清理机制**——Anthropic 适配器仅保留上下文中最新的 3 张截图，旧截图会被替换为 `[为节省上下文空间，此截图已被移除]` 的占位符。
- **客户端压缩裁剪**——上下文压缩器可识别多模态工具的输出结果，并自动剔除旧结果中的图像部分。
- **基于图像的令牌估算**——每张图片按约 1500 个令牌计算（遵循 Anthropic 的统一费率），而非以其 Base64 编码后的字符长度来计算。
- **服务器端上下文清理（仅限 Anthropic）**——启用该功能后，适配器会通过 `context_management` 设置 `clear_tool_uses_20250919`，从而使 Anthropic 的 API 在服务器端自动清除旧的工具输出结果。

在 1568×900 分辨率的显示屏上执行 20 次操作的会话，通常仅需要约 3 万令牌的截图上下文容量，而非 60 万令牌。

## 局限性

- **性能方面**：后台模式的速度慢于前台模式——在 macOS 系统上，通过无障碍接口发送的事件处理时间约为 5–20 毫秒；在 Windows UIA 系统上约为 3–10 毫秒；在 Linux 的 AT-SPI 接口下相比直接使用 HID 接口，处理时间约为 5–15 毫秒。对于常规的快速操作来说影响不大，但若尝试录制高速操作流程，则会有明显差异。
- **不支持键盘输入密码**：`type` 函数对命令行参数中的特定模式有严格限制；如需输入密码，请使用系统的自动填充功能（macOS 的 Keychain、Windows 的 Credential Manager、GNOME 的 Keyring 或 KWallet）。
- **部分应用程序不提供无障碍访问树。** Windows平台上的现代UWP应用、Linux平台上的Electron < 28版本应用，以及一些使用自定义绘图功能的macOS应用（如Logic、Final Cut和某些游戏），其AX树要么内容极少，要么完全为空。如果该树为空，则需转而使用像素坐标——或者直接跳过相应操作。
- **Windows：普通代理无法控制提升权限（管理员）的窗口。** Windows的UIPI（用户界面权限隔离）机制设置了完整性级别限制：默认的Hermes代理属于中等完整性进程，无法枚举高完整性（管理员）进程所拥有的窗口的UIA树，也无法向该窗口发送鼠标输入。由此会出现如下现象：`capture(mode='som')`会返回0个元素，而`click(...)`虽然显示操作成功但实际上并未执行任何操作，尽管截图仍能正常生成（因为GDI抓图功能不受完整性检查限制）。键盘事件可部分绕过UIPI机制，因此仍可通过Tab/Enter键在提升权限的对话框中导航。这是操作系统层面的限制，并非cua驱动程序的缺陷——所有Windows自动化框架都会受到此影响。若要控制提升权限的窗口，需以高完整性模式运行Hermes代理（从具有管理员权限的终端启动）；否则应选择非提升权限的窗口作为操作目标。
- **平台特定的部署注意事项：**
  - **macOS**使用专有的SkyLight SPI。苹果公司可在任何操作系统更新中更改这些设置。如果安装的cua驱动程序版本低于Hermes所测试的版本，它会发出警告。
- **Windows**：SSH 会话在**会话 0**中运行，该会话没有交互式桌面。您可以在 RDP/控制台会话内部启动 Hermes，或设置 cua-driver 的自动启动计划任务——[windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh) 中有相关操作指南。  
- **Linux**：需要可访问的显示服务器。无桌面服务器在启用 `computer_use` 功能以捕获或注入事件之前，需先运行 Xvfb（如 `Xvfb :99 -screen 0 1920x1080x24`）。纯 Wayland 会话则需通过 XWayland 桥接来实现屏幕捕获（cua-driver 的 Wayland 注入机制可独立处理输入）。

对于无需桌面开销、且无需 TCC/会话 0/X11 设置的跨平台 GUI 自动化任务，`browser` 工具集采用真正的无桌面 Chromium 引擎，是处理纯网页任务的理想选择。

## 配置

权限模式与清单文件（参见上文[权限模式](#permission-modes-and-logged-in-browser-profiles)）：

```yaml
computer_use:
  permission_mode: standard        # standard (default) | bounded
  capability_manifest: ""          # capability manifest path, required for bounded
```

在 Linux 系统上，对原生 Wayland 的支持仍需手动开启。只有当每个 cua-driver 进程（包括网关会话）也设置了 `WAYLAND_DISPLAY` 变量时，Hermes 才会将该启用选项传递给这些进程。

```yaml
computer_use:
  native_wayland: true
```

修改此设置后，请重启正在运行的网关。

覆盖驱动程序二进制路径（用于测试/持续集成/本地构建场景）：

```
HERMES_CUA_DRIVER_CMD=/path/to/your/cua-driver
```

完全更换后端（用于测试）：

```
HERMES_COMPUTER_USE_BACKEND=noop   # records calls, no side effects
```

### 远程监控数据收集

cua-driver 在上游版本中默认已启用匿名使用情况远程监控功能（PostHog）。**Hermes 会为您禁用该功能**——在每次调用 cua-driver 时（包括 MCP 后端、`status`、`doctor` 以及安装相关操作），Hermes 都会在驱动程序的运行环境中设置 `CUA_DRIVER_RS_TELEMETRY_ENABLED=0`。

如需重新启用该功能（允许 cua-driver 使用其默认设置并发送远程监控数据），请在 `config.yaml` 中进行相应配置：

```yaml
computer_use:
  cua_telemetry: true   # default: false (telemetry off)
```

当该功能处于开启状态时，`hermes computer-use doctor` 会显示 `telemetry: enabled`；而处于关闭状态（默认情况）时，则会显示 `telemetry: disabled via CUA_DRIVER_RS_TELEMETRY_ENABLED`。

## 使用本地构建的 cua-driver 进行测试

如果您正在开发 cua-driver 本身，或希望测试尚未发布的修复版本，可让 Hermes 指向您从源代码编译出的二进制文件，而非已发布的正式版本。Hermes 会通过 `shutil.which("cua-driver")` 来定位驱动程序，并且**不会强制要求遵循 `HERMES_CUA_DRIVER_VERSION` 规则**，因此本地构建的版本（显示为 `0.0.0-local-*`）可直接被接受。有两种实现方式：

### 方案 A — `install-local`（编译并添加到 PATH）

在您从 `trycua/cua` 分支克隆的代码目录中，运行上游提供的本地安装程序。该程序会以正式发布模式编译 Rust 后端，并将 `cua-driver` 放置在与生产环境安装程序相同的目录结构中，同时会将它的二进制目录添加到您的 PATH 环境变量中：

```powershell
# Windows (PowerShell), from the cua repo root
./libs/cua-driver/scripts/install-local.ps1 -NoAutoStart
```

```bash
# macOS / Linux, from the cua repo root  (defaults to a debug build without --release)
./libs/cua-driver/scripts/install-local.sh --release
```

- Windows会将构建文件存储在`%USERPROFILE%\.cua-driver\packages\…`路径下，并通过符号链接将`%LOCALAPPDATA%\Programs\Cua\cua-driver\bin`（该路径已被添加到用户的PATH环境变量中）连接到该位置。而macOS/Linux系统则会将`cua-driver`链接至`~/.local/bin`目录（如需更改路径，可使用`--bin-dir <path>`选项）。
- `-NoAutoStart`选项可跳过注册`cua-driver-serve`登录守护进程——在Hermes测试中无需使用该功能（详见相关说明）。
之后请打开一个新的终端窗口（以便能看到PATH环境变量的更改），并进行确认操作。

```
cua-driver --version                 # local builds report 0.0.0-local-release
# Windows:      (Get-Command cua-driver).Source
# macOS/Linux:  which cua-driver
```

### 方案 B——直接让 Hermes 调用已生成的二进制文件（最快循环方式）

完全跳过安装步骤：执行 `cargo build`，然后将 `HERMES_CUA_DRIVER_CMD` 设置为生成的二进制文件路径。这种方式最适合快速进行编辑、编译和测试。

```bash
cargo build -p cua-driver            # add --release for a release build; run from libs/cua-driver/rust
```

```
# Windows (.env)
HERMES_CUA_DRIVER_CMD=C:\path\to\cua\libs\cua-driver\rust\target\debug\cua-driver.exe
# macOS / Linux (.env)
HERMES_CUA_DRIVER_CMD=/path/to/cua/libs/cua-driver/rust/target/debug/cua-driver
```

### 确认 Hermes 正在使用您的构建版本

- `hermes computer-use status` 命令会输出已确定的二进制文件路径及版本信息。
- `hermes computer-use doctor` 命令可用于确认二进制文件是否可访问，并对整个 MCP 路径进行端到端的测试。
- 在会话中，使用 `computer_use(action="capture")` 可以测试已启动的 `cua-driver mcp` 子进程。

### 注意事项与常见陷阱

- **Hermes 会生成一个 `cua-driver mcp` 标准输入输出代理。**在普通会话中，该代理会连接到（并可能启动）标准的机器守护进程。而在显式的 Hermes YOLO 模式下，Hermes 会自行管理一个私有的 `cua-driver serve --embedded` 子进程，并让代理指向其私有套接字或命名管道。对于通过 SSH 进行的交互式 Session 1 及后续输入，Windows 的自动启动/UIAccess 模式依然适用——详情请参见“限制”部分。
- **Windows 系统下的二进制文件锁定问题。**正在运行的 `cua-driver-serve` 守护进程会占用 `cua-driver.exe` 文件，从而阻止在重新构建时对其进行覆盖。`install-local.ps1` 脚本会自动将这个被锁定的二进制文件移开；如果您选择手动执行 `cargo build`（方案 B），则需先使用 `cua-driver autostart disable`（或 `schtasks /End /TN cua-driver-serve`）停止该守护进程。
- **重新构建循环问题。**修改 `cua-driver` 源代码后，对于方案 A，需要重新运行 `install-local` 命令（该命令会执行重新构建、重新加载依赖，并切换“当前”符号链接）；而对于方案 B，则只需再次执行 `cargo build` 即可——无论哪种方式都无需对 Hermes 进行任何修改。
- **本地构建会跳过版本检查。**如果安装的 `cua-driver` 版本低于针对相应操作系统测试过的基准版本，Hermes 会发出警告，但 `0.0.0-local-*` 系列的开发构建版本则不受此限制——因此您的本地构建永远不会触发该警告。

## 故障排除

**一旦出现任何问题，首先执行 `hermes computer-use doctor` 命令。**该工具通过结构化的检查矩阵，向您以及协助您调试的智能体准确指示问题所在。

有些特定的故障模式是该诊断工具无法检测到的：

**`computer_use backend unavailable: cua-driver is not installed`** —  
请运行 `hermes computer-use install` 以获取 cua-driver 可执行文件，或运行 `hermes tools` 并启用 Computer Use 工具集。

**点击操作似乎无效** — 请进行截图并验证。可能存在一个您未注意到的弹窗正在拦截输入，请使用 `escape` 键或关闭按钮将其关闭。

**元素索引已过期** — SOM 索引仅在下一次 `capture` 操作之前有效。在任何导致状态变化的操作之后都需要重新捕获。封装层会通过不透明的 `element_token` 来检测索引是否过期——此时您会看到明确的错误提示，而非误触反馈。

**“类型文本中存在被禁止的模式”** — 您尝试输入的文本与危险命令模式列表匹配。请拆分命令或重新考虑操作方式。

**在 Linux 系统上捕获结果为空** — 可能是因为未设置 `DISPLAY`，或者您处于纯 Wayland 环境且没有 XWayland 转换层。`hermes computer-use doctor` 会将该问题标记为 `ax_capability: fail`，并给出“请设置 DISPLAY (X11)…”的提示。

**通过 SSH 在 Windows 系统上捕获结果为空** — 您当前处于 Session 0（服务会话）中。请直接通过 RDP/控制台进行操作，或设置自动启动方案——详情请参阅  
[cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)。

## 参见

- **Hermes 端技能** — `skills/autonomous-ai-agents/computer-use/SKILL.md` — 介绍了 Hermes 的 `computer_use` 操作相关词汇表；Agent 会加载此文件中的内容。
- **cua-driver skill pack** — 用于针对不同平台的深度功能解析  
  （macOS无前台进程模式、Windows UIA + Session 0、Linux AT-SPI + X11/Wayland、屏幕录制、浏览器页面等），请运行 `cua-driver skills install`，并查阅 `MACOS.md` / `WINDOWS.md` / `LINUX.md` / `RECORDING.md` / `WEB_APPS.md` 文件。Hermes的自动检测功能仍在规划中；目前可手动将Hermes指向已安装的技能包目录，或将其创建符号链接至你的技能空间中。  
- **cua.ai/docs** — cua-driver项目的官方文档：  
  - [什么是计算机使用？](https://cua.ai/docs/explanation/what-is-computer-use) — 概念介绍  
  - [无前台进程模式详解](https://cua.ai/docs/explanation/the-no-foreground-contract) — 说明为何后台模式如此重要  
  - [安装指南](https://cua.ai/docs/how-to-guides/driver/install) — 跨平台安装步骤  
  - [自定义智能体光标](https://cua.ai/docs/how-to-guides/driver/personalize-cursor) — 内置图形、自定义资源及运行时配置调整  
  - [通过SSH控制Windows系统](https://cua.ai/docs/how-to-guides/driver/windows-ssh) — Session 0到Session 1+的自动启动机制  
  - [保持cua-driver持续运行](https://cua.ai/docs/how-to-guides/driver/keep-running) — 自动启动与守护进程生命周期管理  
  - [连接你的智能体](https://cua.ai/docs/how-to-guides/driver/connect-your-agent) — 将cua-driver注册到各类框架中（包括Hermes）  
- [cua-driver源代码（trycua/cua）](https://github.com/trycua/cua)
- [浏览器自动化](./browser.md)：用于无需操作原生应用即可完成跨平台网页任务的解决方案。
