---
title: Computer Use
sidebar_position: 16
---

# 计算机操作功能

Hermes Agent 能在 **macOS、Windows 和 Linux** 系统的**后台**操控你的桌面——包括点击、输入、滚动以及拖动操作。在此过程中，你的光标不会移动，键盘焦点也不会改变，虚拟桌面或工作区更不会自动切换。你与 Agent 共同在同一台设备上协同工作。

不同于大多数计算机操作集成方案，该功能可适配**任何具备相应工具能力的模型**——无论是 Claude、GPT、Gemini，还是运行在本地 OpenAI 兼容端点上的开源模型。无需担心 Anthropic 特有的架构规范问题。

## 工作原理

`computer_use` 工具集通过标准输入输出接口与开源的后台计算机操作驱动程序 [`cua-driver`](https://github.com/trycua/cua) 之间进行 MCP 协议通信。各平台在底层均采用相应的无障碍访问与输入处理机制：

| 平台 | 无障碍访问框架 | 输入处理方式 |
|---|---|---|
| macOS | AX（私有 SkyLight SPIs） | `SLPSPostEventRecordTo` —— 基于进程标识符处理事件，不会导致光标位置异常 |
| Windows | UIAutomation | `SendInput` + `PostMessage` —— 不会抢占焦点 |
| Linux | AT-SPI（X11 + Wayland） | XTest（X11）/虚拟键盘（Wayland） |

所有平台上的最终效果一致：Agent 能读取任何可见窗口的无障碍访问树信息，同时发送合成事件，而无需将窗口置顶、切换虚拟桌面或移动操作系统本身的光标。

关于底层协议机制——包括为何需要后台模式、无前台显示的约束条件以及点击事件处理流程等详细内容，请参阅 **[cua.ai/docs/explanation/the-no-foreground-contract](https://cua.ai/docs/explanation/the-no-foreground-contract)**。

## 启用方法

你可以选择最方便的方式，两种方式最终都会调用相同的底层安装程序：

**方式一：专用 CLI 命令（最为直接）。**

```
hermes computer-use install
```

该操作会下载并运行上游的cua-driver安装程序——在macOS/Linux系统上为`install.sh`，在Windows系统上为`install.ps1`。可使用`hermes computer-use status`命令来验证安装是否成功。

**选项2：以交互方式启用工具集。**

1. 运行`hermes tools`，选择`🖱️  Computer Use (macOS/Windows/Linux)`。
2. 系统将自动运行上游安装程序（与选项1相同）。

无论选择哪种安装路径，完成安装后都需要授予对应平台所需的权限：

| 平台 | 所需权限 |
|---|---|
| **macOS** | 进入“系统设置”→“隐私与安全性”→“辅助功能”和“屏幕录制”，允许终端（或Hermes应用）使用相关功能。`hermes computer-use doctor`命令可提示您缺少哪些权限。 |
| **Windows** | 安装时无需额外权限。如果通过SSH（而非RDP/控制台）进行远程操控，则需要设置自动启动模式——有关Session 0 ↔ Session 1+代理的配置方法，请参阅[cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)。 |
| **Linux** | 需要可访问的显示服务器：对于X11系统，需设置`DISPLAY`环境变量；对于Wayland系统，则需设置`XDG_SESSION_TYPE=wayland`。Wayland会话进行屏幕捕获时还需要XWayland桥接器。同时，AT-SPI功能必须处于开启状态（GNOME/KDE/Xfce系统默认已开启）。 |

之后即可启动已启用工具集的会话：

```
hermes -t computer_use chat
```

或者，在 `~/.hermes/config.yaml` 文件中，将 `computer_use` 添加到已启用的工具集中。

## `hermes computer-use doctor` —— 您的首选问题排查工具

`hermes computer-use doctor` 会运行 cua-driver 提供的结构化 `health_report` MCP 工具，并输出各项检查的结果矩阵。这是快速查明某个操作为何无法正常运行的最有效方法。

```
$ hermes computer-use doctor
⚠️  cua-driver 0.5.8 on darwin — degraded
  ✅ binary_version: cua-driver 0.5.8
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
- 当状态为 `degraded` 或 `failed` 时，退出码为 **1** —— 至少有一个检查失败；每次失败的提示会告知你需要修复什么问题。  
- 当无法访问 cua-driver 可执行文件本身时，退出码为 **2**。  

常用标志：  
- `--include CHECK` —— 仅运行列出的检查项（如需运行多个，可重复使用该选项）  
- `--skip CHECK` —— 跳过某个检查项（该选项优先于 `--include`）  
- `--json` —— 输出原始结构化数据，格式与 `tools/call health_report` MCP 响应一致  

检查矩阵会考虑平台差异：在 Windows 和 Linux 上，`bundle_identity` / `tcc_*` 类型的检查会被自动跳过，因为这些概念在这些平台上并不适用。`ax_capability` 检查会在 macOS 上检测 AX 接口，在 Windows 上检测 UIA 接口，在 Linux 上检测 AT-SPI 接口 —— 当无法连接到相应接口时，会给出相应的诊断提示。  

## Agent 光标与会话  

当 Agent 执行操作时，你会看到一个**带颜色的叠加光标**在屏幕上移动，标示出每次点击、输入或滚动的位置。真实的操作系统光标不会移动 —— 这个叠加光标只是用来提示“Agent 正在此处操作”。每次 Hermes 运行都会生成唯一的 cua-driver **会话 ID**（例如 `hermes-3a7b9c14d2e8`）；光标的标识与对应会话绑定，因此同时运行的多个实例或子 Agent 可以各自拥有独立的光标，互不干扰。  

你可以通过 `cua-driver` 的 CLI 标志或运行时的 `set_agent_cursor_style` MCP 工具来调整光标样式 —— 更完整的选项列表请参见 [cua.ai/docs/how-to-guides/driver/personalize-cursor](https://cua.ai/docs/how-to-guides/driver/personalize-cursor)，包括内置的“箭头”和“泪滴”形状、通过 `--cursor-icon` 参数自定义 SVG/PNG/ICO 图标、运行时渐变颜色以及光晕效果等。  

## 深入了解 —— cua-driver 技能包  

Hermes 故意将其技能文件（`skills/computer-use/SKILL.md`）聚焦于 Hermes 端的 `computer_use` 操作词汇表 —— 这是 Agent 加载操作指令的唯一权威来源。对于更深入的内容，比如针对不同平台的详细说明、录制功能逻辑、浏览器页面交互等，你可以让 Agent 使用 cua-driver 团队直接提供并维护的 cua-driver 技能包。

```
cua-driver skills install
```

该命令会将该包链接到你的智能体框架的技能目录中。执行完成后，智能体即可访问以下内容：

| 文件 | 主题 |
|---|---|
| `SKILL.md` | 跨平台核心机制（快照不变性、无前台契约、点击分发、AX树结构） |
| `MACOS.md` | macOS特定配置：无前台契约、AXMenuBar导航、SkyLight点击分发、Apple Events JS桥接 |
| `WINDOWS.md` | Windows特定配置：UIA树结构、UWP/`ApplicationFrameHost`托管机制、Session 0隔离机制、自动启动模式 |
| `LINUX.md` | Linux特定配置：AT-SPI树结构、X11/Wayland显示协议、终端模拟器检测 |
| `RECORDING.md` | 轨迹记录与视频录制相关规则 |
| `WEB_APPS.md` | 浏览器页面交互技巧 |
| `TESTS.md` | 基于轨迹回放的测试流程 |

这些文档是**针对各平台的深度解析，并非Hermes技能文件的重复内容**——当智能体反馈“在Windows系统中，我的点击落在了错误的元素上”时，它就会查阅`WINDOWS.md`中关于UIA/UWP的说明，了解原因及对应的解决方案。

命令`cua-driver skills status`可显示已安装的技能以及它们被链接到了哪些智能体框架中。目前自动检测功能已支持Claude Code、Codex、OpenCode、OpenClaw和Antigravity；**Hermes的自动检测功能计划作为后续在`trycua/cua`项目中实现**——在此之前，只需运行一次`cua-driver skills install`，然后将你的智能体框架指向生成的`~/.cua-driver/skills/cua-driver`目录（或将其链接到常规的技能目录中即可）。

## 简单示例

用户提示：“查找我来自Stripe的最新邮件，并总结他们希望我完成的任务。”

智能体的执行计划（在macOS/Windows/Linux上的结构相同——模型会自动替换为对应平台的常用快捷方式及应用名称）如下：

1. `computer_use(action="capture", mode="som", app="Mail")` ——截取邮件应用的屏幕截图，同时标注出所有侧边栏项目、工具栏按钮以及每条消息的序号。
2. `computer_use(action="click", element=14)` ——点击搜索框。
3. `computer_use(action="type", text="from:stripe")` ——输入搜索条件。
4. `computer_use(action="key", keys="return", capture_after=True)` ——提交搜索并再次截取屏幕截图。
5. 点击最顶端的搜索结果，阅读邮件内容并生成总结。

在整个过程中，光标会始终停留在用户原先的位置，且邮件应用不会被置为前台显示。

## 提供商兼容性

| 提供商 | 是否支持视觉识别？ | 是否可用？ | 备注 |
|---|---|---|---|
| Anthropic（Claude Sonnet/Opus 3+） | ✅ | ✅ | 整体表现最佳；支持SOM与原始坐标输入。 |
| OpenRouter（任意视觉识别模型） | ✅ | ✅ | 支持多部分工具消息。 |
| OpenAI（GPT-4+、GPT-5） | ✅ | ✅ | 功能与上述类似。 |
| Google（Gemini 2+） | ✅ | ✅ | 同时支持工具调用与视觉识别功能。 |
| Local vLLM / LM Studio / Ollama（视觉识别模型） | ✅ | ✅ | 需要模型支持多部分工具内容。 |
| 纯文本模型 | ❌ | ✅（功能受限） | 若需仅操作无障碍访问树结构，可使用`mode="ax"`模式。 |

屏幕截图会以OpenAI风格的`image_url`格式嵌入在工具结果中。对于Anthropic平台，适配器会将这些截图转换为原生的`tool_result`图像块。图像的MIME类型由cua-driver的`mimeType`字段明确指定（如`image/png`或`image/jpeg`），无需通过客户端进行魔法字节检测。

## 安全性

Hermes采用了多层防护机制：

- 破坏性操作（点击、输入、拖动、滚动、按键、聚焦应用）都需要获得授权——可通过CLI对话框交互式授权，也可通过消息平台的授权按钮完成。
- 在工具层面直接禁止某些关键组合操作：清空回收站、强制删除文件、锁定屏幕、登出账户、强制登出等。
- 禁止使用某些危险的输入模式：如`curl | bash`、`sudo rm -rf /`、分叉炸弹等。
- 智能体的系统提示会明确告知其：不得出现点击授权对话框，不得输入密码，也不得执行嵌入在屏幕截图中的指令。

如果你希望每项操作都经过确认，可在`~/.hermes/config.yaml`文件中设置`approvals.mode: manual`。

## 令牌效率优化

屏幕截图会消耗大量令牌。Hermes为此设计了四层优化策略：

- **截图缓存清理**——Anthropic适配器仅保留最近3张截图在上下文中；较旧的截图会被替换为`[screenshot removed to save context]`的占位符。
- **客户端压缩优化**——上下文压缩器能够识别多模态工具结果，并自动移除旧截图中的图像部分。
- **基于图像大小的令牌估算**——每张图片被计为约1500个令牌（按Anthropic的统一费率计算），而非其Base64编码后的字符长度。
- **服务器端上下文清理（仅限Anthropic）**——启用该功能后，适配器可通过`context_management`设置`clear_tool_uses_20250919`，让Anthropic的API在服务器端清除旧的工具结果。

在1568×900分辨率的屏幕上执行20次操作的会话，通常仅需要约3万令牌用于存储截图相关上下文，而非原本预估的60万令牌。

## 局限性

- **性能问题**：后台模式的速度慢于前台模式——在macOS上，通过无障碍访问通道发送事件需要约5–20毫秒；在Windows的UIA框架下约为3–10毫秒；在Linux的AT-SPI框架下则为5–15毫秒，远高于直接通过HID接口发送事件的速率。这种延迟对普通点击操作影响不大，但若尝试录制快速操作流程，则会较为明显。
- **不支持键盘输入密码**：`type`命令对命令行格式的输入内容有严格限制；如需输入密码，应使用系统的自动填充功能（macOS的Keychain、Windows的Credential Manager、GNOME的Keyring或KWallet）。
- **部分应用未提供无障碍访问树结构**：Windows上的现代UWP应用、Linux上版本低于28的Electron应用，以及一些具有自定义绘图功能的macOS应用（如Logic、Final Cut、某些游戏），其AX树结构可能较为简略甚至为空。此时可尝试使用像素坐标进行操作，或直接跳过该任务。
- **Windows：普通智能体无法控制高级权限窗口**：Windows的UIPI（用户界面权限隔离）机制设置了完整性级别限制：中等完整性级别的进程（即默认的Hermes智能体）无法获取高完整性级别（管理员权限）进程所拥有的窗口的UIA树结构，也无法向该类窗口发送鼠标输入。表现为`capture(mode='som')`会返回0个元素，而`click()`虽然显示操作成功但实际上并未执行任何操作，尽管截图仍然可以正常生成（因为GDI截图操作不在完整性检查范围内）。键盘事件可部分绕过UIPI限制，因此仍可使用Tab/Enter键在高级权限对话框中导航。这是操作系统层面的限制，并非cua-driver的缺陷——所有Windows自动化框架都存在此问题。若需控制高级权限窗口，需以高完整性级别运行Hermes智能体（从具有管理员权限的终端启动），否则只能操作普通权限窗口。
- **平台特定的部署注意事项**：
  - **macOS**使用专有的SkyLight SPI接口。苹果公司可在任何系统更新中更改这些接口，因此如果安装的cua-driver版本低于测试用版本，Hermes会发出警告。
  - **Windows**上的SSH会话在**Session 0**模式下运行，该模式没有交互式桌面。需在RDP/控制台会话内部启动Hermes，或设置cua-driver的自动启动计划任务——[windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)文档提供了相关配置方法。
  - **Linux**系统需要可访问的显示服务器。无桌面环境的服务器在运行`computer_use`命令进行截图或发送事件之前，需先启动Xvfb服务（如`Xvfb :99 -screen 0 1920x1080x24`）。纯Wayland会话则需要通过XWayland桥接来实现屏幕截图功能（cua-driver的Wayland输入注入机制可独立处理输入操作）。

对于无需桌面环境开销、且不涉及TCC/Session 0/X11配置的跨平台GUI自动化任务，`browser`工具集基于真正的无头Chromium浏览器，是处理纯网页任务的理想选择。

## 配置选项

如需修改驱动程序的二进制路径（用于测试、CI环境或本地构建），可进行相应配置：

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

当该功能处于开启状态时，`hermes computer-use doctor` 会显示 `telemetry: enabled`；而处于关闭状态（默认值）时，则会显示 `telemetry: disabled via CUA_DRIVER_RS_TELEMETRY_ENABLED`。

## 使用本地构建的 cua-driver 进行测试

如果您正在开发 cua-driver 本身，或希望测试尚未发布的修复版本，可以让 Hermes 指向您从源代码编译出的二进制文件，而非已发布的正式版本。Hermes 会通过 `shutil.which("cua-driver")` 来定位驱动程序，并且**不会强制要求符合 `HERMES_CUA_DRIVER_VERSION` 的规范**，因此本地构建的版本（显示为 `0.0.0-local-*`）可直接被接受。有以下两种实现方式：

### 方案 A — `install-local`（编译并添加到 PATH）

在您从 `trycua/cua` 分支克隆代码后，运行上游提供的本地安装程序。该程序会以正式发布模式编译 Rust 后端，并将 `cua-driver` 放置在与生产环境安装程序相同的目录结构中，同时会将它的二进制目录添加到您的 PATH 环境变量中：

```powershell
# Windows (PowerShell), from the cua repo root
./libs/cua-driver/scripts/install-local.ps1 -NoAutoStart
```

```bash
# macOS / Linux, from the cua repo root  (defaults to a debug build without --release)
./libs/cua-driver/scripts/install-local.sh --release
```

- Windows会将构建文件存放在`%USERPROFILE%\.cua-driver\packages\…`路径下，并通过符号链接将`%LOCALAPPDATA%\Programs\Cua\cua-driver\bin`（该路径会被添加到用户的PATH环境变量中）与该目录关联。而MacOS/Linux系统则会将`cua-driver`链接至`~/.local/bin`目录中（如需指定其他路径，可使用`--bin-dir <path>`选项进行覆盖）。
- `-NoAutoStart`选项用于跳过注册`cua-driver-serve`登录守护进程——在Hermes测试过程中无需使用该功能（详见相关说明）。

之后请打开一个新的终端窗口（这样PATH环境变量的更改才会生效），并进行确认操作。

```
cua-driver --version                 # local builds report 0.0.0-local-release
# Windows:      (Get-Command cua-driver).Source
# macOS/Linux:  which cua-driver
```

### 方案 B——直接将 Hermes 指向已生成的二进制文件（最快循环方式）

完全跳过安装步骤：执行 `cargo build`，然后将 `HERMES_CUA_DRIVER_CMD` 设置为生成的二进制文件路径。此方式非常适合快速进行编辑、构建和测试操作。

```bash
cargo build -p cua-driver            # add --release for a release build; run from libs/cua-driver/rust
```

```
# Windows (.env)
HERMES_CUA_DRIVER_CMD=C:\path\to\cua\libs\cua-driver\rust\target\debug\cua-driver.exe
# macOS / Linux (.env)
HERMES_CUA_DRIVER_CMD=/path/to/cua/libs/cua-driver/rust/target/debug/cua-driver
```

### 确认Hermes正在使用你的构建版本

- `hermes computer-use status` 会输出已解析的二进制文件路径及版本信息。
- `hermes computer-use doctor` 可用于确认二进制文件是否可访问，并对完整的MCP流程进行端到端测试。
- 在会话中，调用 `computer_use(action="capture")` 可对启动的 `cua-driver mcp` 子进程进行测试。

### 注意事项与潜在问题

- **Hermes会通过标准输入输出自行启动 `cua-driver mcp` 子进程**——它并不会连接到长期运行的 `cua-driver serve` 自动启动守护进程或其命名管道。因此，在测试时无需使用计划任务或LaunchAgent（使用 `-NoAutoStart` 即可）。只有对于某些需要在前台安全输入的应用程序（如WPF），自动启动守护进程和Windows UIAccess工作进程（`cua-driver-uia.exe`）才是必需的；而标准工具界面则是通过标准输入输出子进程来实现的。在Windows的SSH会话中，则必须使用自动启动模式——详情请参见“限制”部分。
- **Windows系统上的二进制文件被锁定**。正在运行的 `cua-driver-serve` 守护进程可能会占用 `cua-driver.exe`，从而阻止在重新构建时覆盖该文件。`install-local.ps1` 会自动将已被锁定的二进制文件重命名，移出当前路径；如果你选择手动执行 `cargo build`（方案B），则需先使用 `cua-driver autostart disable`（或 `schtasks /End /TN cua-driver-serve`）停止该守护进程。
- **重新构建循环**。修改 `cua-driver` 源代码后，若选择方案A，需重新运行 `install-local`（该命令会重新构建、重新加载状态，并切换 `current` 符号链接）；若选择方案B，则只需再次执行 `cargo build`——无论哪种方式都无需对Hermes进行任何修改。
- **本地构建会跳过版本检查**。当安装的 `cua-driver` 版本低于针对各操作系统测试确定的基准版本时，Hermes会发出警告，但 `0.0.0-local-*` 系列的开发构建版本则会被豁免——因此你的本地构建永远不会触发该警告。

## 故障排除

**一旦出现异常，首先执行 `hermes computer-use doctor`。**  
该工具提供的结构化检查矩阵能让你以及协助你调试的智能体准确了解问题所在。

但该工具无法检测到以下特定故障情况：

- **“computer_use backend unavailable: cua-driver is not installed”**——运行 `hermes computer-use install` 以获取 `cua-driver` 二进制文件，或运行 `hermes tools` 并启用“计算机使用”工具集。
- **点击操作似乎没有效果**——请进行捕获并验证。可能有一个你未注意到的模态窗口正在阻挡输入，可使用 `escape` 键或关闭按钮将其关闭。
- **元素索引已失效**——SOM索引仅在下一次捕获之前有效。在执行任何会改变应用状态的操作后，都需要重新捕获。封装层会通过特殊的 `element_token` 来检测索引是否失效——此时你会看到明确的错误提示，而非误触操作。
- **“type文本中存在被禁止的模式”**——你尝试输入的文本与危险命令模式列表匹配。请拆分命令或重新考虑输入内容。
- **Linux系统下捕获结果为空**——可能是未设置 `DISPLAY` 环境变量，或者你处于纯Wayland环境中且没有XWayland桥接。`hermes computer-use doctor` 会将该问题标记为 `ax_capability: fail`，并给出“设置DISPLAY（X11）……”的提示。
- **通过SSH连接Windows时捕获结果为空**——你当前处于会话0（服务会话）。可直接通过RDP或控制台进行操作，或者设置自动启动模式——详情请参见
  [cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)。

## 相关文档

- **Hermes端技能** —— `skills/computer-use/SKILL.md`，介绍了Hermes的 `computer_use` 操作相关术语，智能体会加载此文件中的内容。
- **cua-driver技能包** —— 若需了解针对不同平台的详细用法（如macOS的无前台模式要求、Windows的UIA与会话0模式、Linux的AT-SPI与X11/Wayland模式、录制功能、浏览器页面操作等），请运行 `cua-driver skills install`，并阅读 `MACOS.md` / `WINDOWS.md` / `LINUX.md` / `RECORDING.md` / `WEB_APPS.md` 这些文档。未来当 `cua-driver skills install` 能自动检测到Hermes时，安装过程将自动完成相关配置。
- **cua.ai/docs** —— `cua-driver`项目的官方文档：
  - [什么是计算机使用功能？](https://cua.ai/docs/explanation/what-is-computer-use) —— 概念介绍
  - [无前台模式协议](https://cua.ai/docs/explanation/the-no-foreground-contract) —— 说明为何需要后台模式
  - [安装指南](https://cua.ai/docs/how-to-guides/driver/install) —— 跨平台安装详细步骤
  - [自定义智能体光标](https://cua.ai/docs/how-to-guides/driver/personalize-cursor) —— 内置形状、自定义资源及运行时覆盖设置
  - [通过SSH控制Windows](https://cua.ai/docs/how-to-guides/driver/windows-ssh) —— 会话0到会话1+的自动启动模式
  - [保持 `cua-driver` 运行状态](https://cua.ai/docs/how-to-guides/driver/keep-running) —— 自动启动与守护进程生命周期管理
  - [连接你的智能体](https://cua.ai/docs/how-to-guides/driver/connect-your-agent) —— 将 `cua-driver` 注册到各类工具框架中（包括Hermes）
- [cua-driver源代码（trycua/cua）](https://github.com/trycua/cua)
- [浏览器自动化操作](./browser.md)，适用于无需控制原生应用、仅需执行跨平台网页任务的场景。
