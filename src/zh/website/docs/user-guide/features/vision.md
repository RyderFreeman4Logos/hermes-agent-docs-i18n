---
title: Vision & Image Paste
description: Paste images from your clipboard into the Hermes CLI for multimodal vision analysis.
sidebar_label: Vision & Image Paste
sidebar_position: 7
---

# 视觉功能与图片粘贴

Hermes Agent 支持**多模态视觉处理**——您可以直接将剪贴板中的图片粘贴到 CLI 中，然后让智能体对其进行分析、描述或进行其他操作。图片会以 base64 编码的形式作为内容块发送给模型，因此任何具备视觉处理能力的模型都能对其进行处理。

:::提示
Portal 用户可在同一目录中获取具备视觉处理功能的模型（如 Claude、GPT-5、Gemini），无需额外凭证。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 工作原理

1. 将图片复制到剪贴板（截图、浏览器中的图片等）
2. 使用以下任意一种方法将图片附加进去
3. 输入问题后按回车键
4. 图片会以 `[📎 图片 #1]` 的标签形式显示在输入框上方
5. 提交后，图片会作为视觉内容块发送给模型

您可以在提交前附加多张图片——每张图片都会有独立的标签。按 `Ctrl+C` 可清除所有已附加的图片。

图片会以带有时间戳的 PNG 文件形式保存在 `~/.hermes/images/` 目录中。

## 粘贴方法

图片的附加方式取决于您的终端环境。并非所有方法在所有环境中都可用，具体说明如下：

### `/paste` 命令

**最可靠、明确的图片附加方式。**

```
/paste
```

输入 `/paste` 并按回车键。Hermes 会检查剪贴板中的图像并将其附加。当终端对 `Cmd+V`/`Ctrl+V` 指令进行了重写，或者您仅复制了图像而无需检查任何带括号的粘贴文本内容时，这是最安全的选择。

### Ctrl+V / Cmd+V

如今，Hermes 将粘贴操作视为分层处理流程：
- 首先粘贴普通文本；
- 若终端未能正确传输文本，则回退到使用原生剪贴板内容或 OSC52 格式的文本；
- 当剪贴板内容或粘贴数据为图像或图像路径时，再附加该图像。

这意味着 macOS 截图生成的临时路径以及 `file://...` 格式的图像 URI 可以立即被附加，而不会以原始文本形式留在编辑器中。

:::warning
如果您的剪贴板**仅包含图像（无文本）**，终端仍然无法直接传输二进制图像数据。此时请使用 `/paste` 作为明确的图像附加回退选项。
:::

### 适用于 VS Code / Cursor / Windsurf 的 `/terminal-setup` 命令

如果您在 macOS 上的本地 VS Code 系列集成终端中运行 TUI，Hermes 可以自动安装推荐的 `workbench.action.terminal.sendSequence` 绑定，从而提升多行文本处理能力以及撤销/重做功能的稳定性：

```text
/terminal-setup
```

当 IDE 拦截了 `Cmd+Enter`、`Cmd+Z` 或 `Shift+Cmd+Z` 等快捷键时，此功能尤为实用。请仅在本地机器上运行该命令，切勿在 SSH 会话中执行。

## 平台兼容性

| 环境 | `/paste` | Cmd/Ctrl+V | `/terminal-setup` | 备注 |
|---|---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | 无需 | 最佳体验——支持原生剪贴板及截图路径恢复 |
| **Apple Terminal** | ✅ | ✅ | 无需 | 若 `Cmd+←/→/⌫` 的功能被重写，可改用 `Ctrl+A` / `Ctrl+E` / `Ctrl+U` 作为替代 |
| **Linux X11 桌面环境** | ✅ | ✅ | 无需 | 需要安装 `xclip`（可通过 `apt install xclip` 安装） |
| **Linux Wayland 桌面环境** | ✅ | ✅ | 无需 | 需要安装 `wl-paste`（可通过 `apt install wl-clipboard` 安装） |
| **WSL2（Windows Terminal）** | ✅ | ✅ | 无需 | 使用 `powershell.exe`，无需额外安装 |
| **VS Code / Cursor / Windsurf（本地运行）** | ✅ | ✅ | ✅ | 更能确保 `Cmd+Enter`、撤销/重做等快捷键功能的一致性，推荐使用 |
| **VS Code / Cursor / Windsurf（SSH 运行）** | ❌² | ❌² | ❌³ | 请在本地机器上运行 `/terminal-setup` 命令 |
| **任意 SSH 终端** | ❌² | ❌² | 无需 | 无法访问远程剪贴板 |

² 详情请参见下文的[SSH与远程会话](#ssh--remote-sessions)部分
³ 该命令用于设置本地 IDE 的快捷键绑定，不应在远程主机上执行

## 各平台特定设置

### macOS

**无需额外设置。** Hermes 会利用 macOS 自带的 `osascript` 功能来读取剪贴板内容。如需提升性能，可选择性安装 `pngpaste`：

```bash
brew install pngpaste
```

### Linux (X11)

安装 `xclip`：

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Linux（Wayland版）

现代Linux桌面系统（如Ubuntu 22.04及以上版本、Fedora 34及以上版本）通常默认使用Wayland显示协议。请先安装`wl-clipboard`工具：

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::提示 如何查看当前是否处于 Wayland 环境中
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = no display server
```
:::

### WSL2

**无需额外设置。** Hermes 会通过 `/proc/version` 自动检测 WSL2 环境，并利用 .NET 的 `System.Windows.Forms.Clipboard` 接口，通过 `powershell.exe` 访问 Windows 剪贴板。这一功能已内置在 WSL2 的 Windows 互操作机制中，因此 `powershell.exe` 默认即可使用。

剪贴板数据会以 Base64 编码的 PNG 格式通过标准输出进行传输，因此无需进行文件路径转换或创建临时文件。

:::info WSLg 注意事项
如果您使用的是支持 GUI 的 WSL2（WSLg），Hermes 会首先尝试通过 PowerShell 访问剪贴板，若失败则会转而使用 `wl-paste` 工具。WSLg 的剪贴板桥接功能仅支持 BMP 格式的图像——Hermes 会自动使用 Pillow（如已安装）或 ImageMagick 的 `convert` 命令将 BMP 图像转换为 PNG 格式。
:::

#### 验证对 WSL2 剪贴板的访问能力

```bash
# 1. Check WSL detection
grep -i microsoft /proc/version

# 2. Check PowerShell is accessible
which powershell.exe

# 3. Copy an image, then check
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::ContainsImage()"
# Should print "True"
```

## SSH与远程会话

**通过SSH无法完全实现剪贴板图片粘贴功能。** 当您通过SSH连接到远程机器时，Hermes CLI会在该远程主机上运行。各类剪贴板工具（如`xclip`、`wl-paste`、`powershell.exe`、`osascript`）会读取其所在机器的剪贴板内容——也就是远程服务器，而非您的本地机器。因此，远程端无法访问您本地的图片剪贴板。

虽然有时可以通过终端粘贴或OSC52协议传输文本，但图片剪贴板访问功能以及本地截图的临时存储路径仍与运行Hermes的机器绑定。

### SSH环境下的解决方案

1. **上传图片文件**——先将图片保存在本地，再通过`scp`、VSCode的文件资源管理器（拖放功能）或任何文件传输方式将其上传到远程服务器，之后通过路径来引用该图片。（未来版本计划推出`/attach <filepath>`命令。）

2. **使用URL地址**——如果图片可在线访问，只需在消息中粘贴对应的URL即可。Agent可以直接使用`vision_analyze`功能来解析任何图片URL。

3. **X11转发**——使用`ssh -X`命令建立连接以实现X11协议转发。这样，远程机器上的`xclip`工具就能访问您本地的X11剪贴板。此方法要求本地需运行X服务器（macOS上为XQuartz，Linux X11桌面系统则内置该服务），且处理大尺寸图片时效率较低。

4. **使用消息平台**——通过Telegram、Discord、Slack或WhatsApp等平台将图片发送给Hermes。这些平台本身就支持图片上传功能，不受剪贴板或终端限制的影响。

## 为何终端无法粘贴图片

这是一个常见的疑问，以下是技术层面的解释：

终端属于**基于文本的**界面。当您按下Ctrl+V（或Cmd+V）时，终端模拟器会执行以下操作：

1. 读取剪贴板中的**文本内容**
2. 将其用[括号式粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列包裹起来
3. 通过终端的文本流将其发送给对应应用程序

如果剪贴板中仅包含图片而不存在文本，终端就没有任何内容可发送。目前还没有针对二进制图片数据的标准终端转义序列，因此终端会直接不做任何处理。

正因如此，Hermes采用了独立的剪贴板检测机制——它不会通过终端粘贴事件接收图片数据，而是直接通过子进程调用操作系统级的工具（如`osascript`、`powershell.exe`、`xclip`、`wl-paste`）来独立读取剪贴板内容。

## 支持的模型

任何具备视觉处理能力的模型都支持图片粘贴功能。图片会以OpenAI视觉内容格式中的base64编码数据URL形式被发送。

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

大多数现代模型都支持这种格式，其中包括 GPT-4 Vision、具备视觉功能的 Claude、Gemini，以及通过 OpenRouter 提供的各类开源多模态模型。

## 图像路由（具备视觉功能的模型与仅支持文本的模型）

当用户从 CLI 剪贴板、网关（Telegram/Discord 中的图片）或其他任何途径上传图片时，Hermes 会根据当前模型是否具备视觉处理能力来决定图像的处理方式：

| 模型类型 | 图像的处理方式 |
|---|---|
| **具备视觉功能**（如 GPT-4V、具备视觉功能的 Claude、Gemini、Qwen-VL、MiMo-VL 等） | 以**真实像素**的形式传输，使用对应提供商的原始图像格式，不包含任何文本描述层。 |
| **仅支持文本**（如 DeepSeek V3、较小的开源模型、旧版的纯文本聊天端点） | 会通过 `vision_analyze` 辅助工具进行处理——该辅助视觉模型会对图像进行描述，然后将文本描述插入对话中。 |

用户无需手动配置此设置，Hermes 会自动从提供商的元数据中查询当前模型的能力，并选择合适的处理路径。实际效果是：用户可以在会话进行过程中在具备视觉功能的模型与仅支持文本的模型之间切换，而图像处理功能仍能正常工作，无需改变原有的工作流程。对于仅支持文本的模型，它们也能获得关于图像的连贯上下文，而不会收到无法处理的乱码多模态数据。

负责文本描述生成的辅助模型可在 `auxiliary.vision` 中进行配置——详情请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。

### `vision_analyze` 也具有相同的双重处理机制

`vision_analyze` 工具本身也遵循相同的路由规则。当当前主模型具备视觉功能，且其对应的提供商支持在工具结果中嵌入图像内容时（目前包括 Anthropic、OpenAI、Azure-OpenAI 以及 Gemini 3.x 系列），`vision_analyze` 会直接跳过辅助描述模块，以多模态工具结果的形式返回原始图像像素。这样，主模型在下一轮处理时就能直接看到图像——无需调用辅助模块，也不会丢失文本描述信息，更不会有额外的延迟。

而对于仅支持文本的主模型（或那些工具结果中不包含图像的提供商），`vision_analyze` 会回退到传统处理方式：它会让已配置的辅助视觉模型对图像进行描述，并以纯文本形式返回描述内容。无论哪种情况，调用该工具的接口格式都保持不变——具体采用哪种处理路径由运行时的当前模型决定。
