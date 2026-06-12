---
title: Computer Use
sidebar_position: 16
---

# 计算机操作（macOS）

Hermes Agent 可以在**后台**控制您的 Mac 桌面——执行点击、输入、滚动、拖动等操作。您的光标不会移动，键盘焦点也不会改变，macOS 也不会自动切换桌面空间。您与 Agent 共同在同一台设备上工作。

与大多数计算机操作集成不同，该功能适用于**任何具备相应能力的模型**——无论是 Claude、GPT、Gemini，还是本地 vLLM 端点上的开源模型。无需担心 Anthropic 特有的架构规范。

## 工作原理

`computer_use` 工具集通过标准输入输出接口与 [`cua-driver`](https://github.com/trycua/cua) 进行 MCP 通信，后者是一个 macOS 驱动程序。它利用 SkyLight 的私有 SPI 接口（如 `SLEventPostToPid`、`SLPSPostEventRecordTo`）以及 `_AXObserverAddNotificationAndCheckRemote` 辅助功能 SPI 来实现以下功能：

- 直接向目标进程发送合成事件——无需模拟 HID 事件，也不会扭曲光标位置。
- 在不弹出窗口的情况下切换 AppKit 的活动状态——无需切换桌面空间。
- 当窗口被遮挡时，仍能保持 Chromium/Electron 应用的辅助功能树活跃。

这正是 OpenAI 的 Codex “后台计算机操作”功能所采用的方案，而 cua-driver 则是其开源版本。

## 启用方法

选择最方便的方式即可——两种方式都会使用相同的上游安装程序：

**选项 1：专用 CLI 命令（最为直接）。**

```
hermes computer-use install
```

此命令会下载并运行上游的 cua-driver 安装程序：
`curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh`。
可使用 `hermes computer-use status` 命令来验证安装是否成功。

**选项 2：以交互方式启用该工具集。**

1. 运行 `hermes tools`，选择 `🖱️ Computer Use (macOS)` → `cua-driver (background)`。
2. 系统将自动运行上游的安装程序（与选项 1 的流程相同）。

无论您选择哪种安装方式，在完成安装后都需要执行以下操作：

3. 根据系统提示授予 macOS 权限：
   - 进入 **系统设置 → 隐私与安全性 → 辅助功能**，允许终端（或 Hermes 应用）使用相关功能。
   - 进入 **系统设置 → 隐私与安全性 → 屏幕录制**，同样允许该应用执行屏幕录制操作。
4. 启用工具集后开始使用会话：
   ```
   hermes -t computer_use chat
   ```
或者，在 `~/.hermes/config.yaml` 中将 `computer_use` 添加到已启用的工具集中。

## 保持 cua-driver 最新版本

cua-driver 项目会定期发布修复补丁（例如，v0.1.6 版修复了 UTM 工作流中 Safari 窗口聚焦的错误）。Hermes 会在两个地方刷新二进制文件，以避免您使用过时的版本：

- **`hermes update`** — 当您更新 Hermes 本身时，如果 `cua-driver` 已经在 PATH 中，上游安装程序会在更新过程结束时重新运行。对于非 macOS 用户以及未安装 cua-driver 的用户，此操作不会执行任何操作。
- **`hermes computer-use install --upgrade`** — 手动强制刷新。无论是否已安装 cua-driver，都会重新运行上游安装程序。当您希望立即获得最新修复而不必等待下一次代理更新时，可使用此命令。

`hermes computer-use status` 命令会显示二进制文件路径旁的已安装版本信息。

## 快速示例

用户指令：“查找我来自 Stripe 的最新邮件，并总结他们希望我做什么。”

代理的执行计划：

1. `computer_use(action="capture", mode="som", app="Mail")` — 截取 Mail 的屏幕截图，确保所有侧边栏项目、工具栏按钮以及消息行都带有编号。
2. `computer_use(action="click", element=14)` — 点击搜索框（即截图中的第 14 个元素）。
3. `computer_use(action="type", text="from:stripe")`
4. `computer_use(action="key", keys="return", capture_after=True)` — 提交查询并获取新的屏幕截图。
5. 点击最顶端的搜索结果，阅读邮件内容并进行总结。

在整个过程中，光标会保持在原来的位置，且 Mail 窗口不会被置顶。

## 提供商兼容性

| 提供商 | 支持视觉功能？ | 能正常工作？ | 备注 |
|---|---|---|---|
| Anthropic（Claude Sonnet/Opus 3+） | ✅ | ✅ | 整体表现最佳；支持 SOM 模式和原始坐标。 |
| OpenRouter（任意视觉模型） | ✅ | ✅ | 支持多部分工具消息。 |
| OpenAI（GPT-4+、GPT-5） | ✅ | ✅ | 功能与上述相同。 |
| Local vLLM / LM Studio（视觉模型） | ✅ | ✅ | 需要模型支持多部分工具内容。 |
| 仅文本模型 | ❌ | ✅（功能受限） | 若需仅操作无障碍信息树，可使用 `mode="ax"` 模式。 |

屏幕截图会以 OpenAI 风格的 `image_url` 格式嵌入在工具结果中。对于 Anthropic，适配器会将它们转换为原生的 `tool_result` 图像块。

## 安全性

Hermes 采用了多层防护机制：

- 破坏性操作（点击、输入、拖动、滚动、按键、聚焦应用）都需要获得授权——可通过 CLI 对话框交互式授权，也可通过消息平台上的授权按钮进行授权。
- 在工具层面会硬性阻止某些关键组合操作：清空回收站、强制删除、锁屏、登出、强制登出等。
- 也会硬性阻止某些输入模式：如 `curl | bash`、`sudo rm -rf /`、分叉炸弹等。
- 代理的系统提示会明确告知其不得进行点击授权操作、不得输入密码，也不得遵循嵌入在屏幕截图中的指令。

如果您希望每项操作都经过确认，可在 `~/.hermes/config.yaml` 中将 `approvals.mode` 设置为 `manual`。

## 令牌效率

屏幕截图会消耗大量资源。Hermes 采用了四层优化措施：

- **屏幕截图筛选** — Anthropic 适配器仅保留最近 3 张屏幕截图在上下文环境中；较旧的截图则会变为 `[screenshot removed to save context]` 的占位符。
- **客户端压缩优化** — 上下文压缩器能识别多模态工具结果，并从旧截图中移除图像部分。
- **基于图像的令牌估算** — 每张图片会被计为约 1500 个令牌（按 Anthropic 的统一费率计算），而非其 Base64 编码后的字符长度。
- **服务器端上下文编辑（仅限 Anthropic）** — 当此功能启用时，适配器会通过 `context_management` 启用 `clear_tool_uses_20250919` 功能，从而使 Anthropic 的 API 在服务器端清除旧的工具结果。

在 1568×900 分辨率的屏幕上执行 20 次操作的会话，通常仅需约 30K 个令牌用于存储屏幕截图上下文，而非原来的约 600K 个令牌。

## 局限性

- **仅支持 macOS。** cua-driver 依赖 Apple 的私有 SPI 接口，这些接口在 Linux 或 Windows 系统上并不存在。如需跨平台进行 GUI 自动化操作，建议使用 `browser` 工具集。
- **私有 SPI 的风险。** Apple 可能在任何操作系统更新中更改 SkyLight 的符号系统。如果您希望在不同版本的 macOS 上获得一致的结果，可通过 `HERMES_CUA_DRIVER_VERSION` 环境变量锁定驱动程序版本。
- **性能问题。** 后台模式的速度慢于前台模式——通过 SkyLight 转发的事件处理时间约为 5-20 毫秒，而直接通过 HID 接口发送指令的速度则更快。对于普通点击操作，这种差异并不明显；但若尝试录制高速操作流程，则能明显感受到性能差距。
- **不支持键盘输入密码。** `type` 操作对命令行脚本类型的输入有严格限制；如需输入密码，建议使用系统的自动填充功能。

## 配置

（在测试/持续集成环境中）可覆盖驱动程序的二进制文件路径：

```
HERMES_CUA_DRIVER_CMD=/opt/homebrew/bin/cua-driver
HERMES_CUA_DRIVER_VERSION=0.5.0    # optional pin
```

完全更换后端（用于测试）：

```
HERMES_COMPUTER_USE_BACKEND=noop   # records calls, no side effects
```

## 故障排除

**错误信息：`computer_use backend unavailable: cua-driver is not installed`** — 请运行 `hermes computer-use install` 命令以获取 cua-driver 二进制文件，或者运行 `hermes tools` 并启用“计算机使用”工具集。

**点击操作似乎无效** — 请进行截图并验证。可能有某个您未注意到的弹窗正在拦截输入操作，请使用 `escape` 键或关闭按钮将其关闭。

**元素索引已过期** — SOM 索引仅在下一次“截图”操作之前有效。在执行任何会改变页面状态的操作后，请重新截图。

**错误信息：“type text”中存在被屏蔽的模式** — 您尝试输入的文本与危险命令模式列表相匹配。请拆分该命令或重新考虑输入内容。

## 相关参考

- [通用技能：`macos-computer-use`](https://github.com/NousResearch/hermes-agent/blob/main/skills/apple/macos-computer-use/SKILL.md)
- [cua-driver 源代码（trycua/cua）](https://github.com/trycua/cua)
- 如需执行跨平台的网页操作，可参考[浏览器自动化](./browser.md)相关文档。
