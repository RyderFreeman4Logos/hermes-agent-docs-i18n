---
sidebar_position: 8
title: "Use Voice Mode with Hermes"
description: "A practical guide to setting up and using Hermes voice mode across CLI, Telegram, Discord, and Discord voice channels"
---

# 在 Hermes 中使用语音模式

本指南是[语音模式功能参考文档](/user-guide/features/voice-mode)的实用补充。

如果说功能页面介绍了语音模式的功能特性，那么本指南则详细讲解如何将其高效运用。

:::提示
[Nous Portal](/integrations/nous-portal)通过单一 OAuth 统一整合了大型语言模型与文本转语音功能——因此使用语音模式时无需额外凭证，可实现端到端操作。
:::

## 语音模式的适用场景

在以下情况下，语音模式尤为实用：
- 您希望实现无需手动的 CLI 工作流程
- 您希望在 Telegram 或 Discord 中获得语音回复
- 您希望让 Hermes 进入 Discord 音频频道以便进行实时对话
- 您希望在行走时快速记录想法、调试问题或进行交流，而无需动手输入

## 选择适合您的语音模式配置

Hermes 提供了三种不同类型的语音体验。

| 模式 | 最佳适用场景 | 平台 |
|---|---|---|
| 交互式麦克风循环 | 编码或研究时实现个人级免提操作 | CLI |
| 聊天中的语音回复 | 在常规消息交流的同时获得语音回应 | Telegram、Discord |
| 实时音频频道机器人 | 在音频频道中进行群体或个人实时对话 | Discord 音频频道 |

推荐的配置步骤如下：
1. 先确保文本输入功能正常工作
2. 接着开启语音回复功能
3. 如需完整体验，最后再尝试在 Discord 音频频道中使用

## 第一步：先确认常规 Hermes 功能正常运行

在尝试使用语音模式之前，请先验证以下内容：
- Hermes 已成功启动
- 您的提供商配置正确
- Agent 能够正常响应文本指令

```bash
hermes
```

询问简单的问题即可：

```text
What tools do you have available?
```

如果该功能尚未稳定，建议先修复文本模式问题。

## 第 2 步：安装所需的附加组件

### CLI 麦克风与播放功能

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[voice]"
```

### 消息平台

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[messaging]"
```

### 高级版 ElevenLabs 文本转语音服务

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[tts-premium]"
```

### 本地 NeuTTS（可选）

```bash
python -m pip install -U neutts[all]
```

### 全部内容

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"
```

## 第 3 步：安装系统依赖项

### macOS

```bash
brew install portaudio ffmpeg opus
brew install espeak-ng
```

### Ubuntu / Debian 系统

```bash
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng
```

为何这些组件如此重要：
- `portaudio` → 用于 CLI 语音模式的麦克风输入/输出功能
- `ffmpeg` → 用于文本转语音及消息传输的音频转换功能
- `opus` → 对 Discord 语音编码格式的支持
- `espeak-ng` → NeuTTS 的音素合成后端

## 第4步：选择文本转语音与语音合成服务提供商

Hermes 支持本地及云端的语音处理方案。

### 最简单/成本最低的配置方式

使用本地文本转语音服务以及免费的 Edge TTS：
- 文本转语音提供商：`local`
- 语音合成提供商：`edge`

这通常是最佳的开端选择。

### 配置文件示例

将其添加到 `~/.hermes/.env` 文件中：

```bash
# Cloud STT options (local needs no key)
GROQ_API_KEY=***
VOICE_TOOLS_OPENAI_KEY=***

# Premium TTS (optional)
ELEVENLABS_API_KEY=***
```

### 提供商推荐

#### 语音转文本

- `local` → 最佳默认选择，兼具隐私保护和零成本优势
- `groq` → 速度极快的云端转录服务
- `openai` → 性能良好的付费备选方案

#### 文本转语音

- `edge` → 免费且对大多数用户而言已足够实用
- `neutts` → 免费的本地/设备端文本转语音功能
- `elevenlabs` → 最高的语音质量
- `openai` → 性能不错的折中选择
- `mistral` → 支持多语言，采用原生 Opus 编码

### 若使用 `hermes setup` 工具

如果在设置向导中选择了 NeuTTS，Hermes 会首先检查系统中是否已安装 `neutts`。若未安装，向导会告知您该工具需要 Python 包 `neutts` 以及系统包 `espeak-ng`，并主动为您提供安装服务——它会通过您的平台包管理器安装 `espeak-ng`，之后再继续执行后续操作：

```bash
python -m pip install -U neutts[all]
```

如果跳过该安装步骤或安装失败，向导将会自动回退至 Edge TTS。  

## 第 5 步：推荐配置

```yaml
voice:
  record_key: "ctrl+b"
  submit_mode: "direct"  # TUI: direct | draft
  max_recording_seconds: 120
  auto_tts: false
  beep_enabled: true
  silence_threshold: 200
  silence_duration: 3.0

stt:
  provider: "local"
  local:
    model: "base"

tts:
  provider: "edge"
  edge:
    voice: "en-US-AriaNeural"
```

对于大多数人而言，这是一个相当稳妥的默认设置。

在 TUI 中，`voice.submit_mode` 用于控制转录完成后的操作：

- `direct`（默认值）会立即提交转录结果。
- `draft` 会将转录内容暂存于编辑器中，这样您便可以在按下回车键之前对其进行修改或取消操作。

如需使用可编辑的语音草稿，请设置：

```yaml
voice:
  submit_mode: "draft"
```

如果您希望使用本地语音合成功能，可将 `tts` 块更改为：

```yaml
tts:
  provider: "neutts"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

## 使用场景 1：CLI 语音模式

## 启用该模式

启动 Hermes：

```bash
hermes
```

在 CLI 内部：

```text
/voice on
```

### 录音流程

默认快捷键：
- `Ctrl+B`

操作步骤：
1. 按下 `Ctrl+B`
2. 开始说话
3. 等待系统检测到安静环境后自动停止录音
4. Hermes 会进行文字转录并给出回复
5. 若启用了文本转语音功能，系统会将回复以语音形式输出
6. 可通过该循环实现持续使用

### 实用命令

```text
/voice
/voice on
/voice off
/voice tts
/voice status
```

### 优秀的 CLI 工作流程

#### 即时调试

只需说出：

```text
I keep getting a docker permission error. Help me debug it.
```

随后即可继续使用免提模式：
- “再读一遍上次的错误信息”
- “用更简单的语言解释根本原因”
- “现在直接告诉我确切的解决方案”

#### 研究/头脑风暴

非常适合用于：
- 边走动边思考
- 口头表达尚未成型的想法
- 要求Hermes实时帮你梳理思路

#### 无障碍操作/减少输入的场景

当输入较为不便时，语音模式是保持完整参与Hermes交互的最快捷方式之一。

## 调整CLI行为

### 静音阈值

如果Hermes的启动/停止过于频繁，可调整此参数：

```yaml
voice:
  silence_threshold: 250
```

阈值越高，灵敏度越低。

### 沉默时长

如果您在句子之间经常暂停，可提高该值：

```yaml
voice:
  silence_duration: 4.0
```

### 记录键

如果 `Ctrl+B` 与您的终端或 tmux 使用习惯冲突：

```yaml
voice:
  record_key: "ctrl+space"
```

## 使用场景 2：在 Telegram 或 Discord 中发送语音回复

该模式比完整的语音频道更为简单。

Hermes 依然是一个普通的聊天机器人，但能够以语音形式回复消息。

### 启动网关

```bash
hermes gateway
```

### 开启语音回复功能

在 Telegram 或 Discord 内部：

```text
/voice on
```

或

```text
/voice tts
```

### 模式

| 模式 | 含义 |
|---|---|
| `off` | 仅文本回复 |
| `voice_only` | 仅当用户发送语音时才进行语音回复 |
| `all` | 每次回复均以语音形式给出 |

### 如何选择合适的模式

- 若希望仅对语音消息返回语音回复，请使用 `/voice on`；
- 若希望始终获得完整的语音助手服务，请使用 `/voice tts`。

### 优秀的消息交互流程

#### 手机上的 Telegram 助手

适用场景：
- 当您远离电脑时；
- 您希望发送语音便条并快速获得语音回复时；
- 您希望让 Hermes 充当便携式的研究或运维助手时。

#### 支持语音输出的 Discord 私信

当您需要私密互动且不希望出现服务器频道相关提示时，此模式非常实用。

## 使用场景 3：Discord 语音频道

这是最高级的模式。Hermes 会加入 Discord 语音频道，监听用户的语音并将其转录为文本，随后执行常规的智能体处理流程，最后以语音形式将回复发送回频道。

## Discord 所需权限

除了常规的文本机器人设置外，还需确保机器人拥有以下权限：
- Connect
- Speak
- 最佳选择：Use Voice Activity

同时还需在开发者门户中启用以下特权意图：
- Presence Intent
- Server Members Intent
- Message Content Intent

## 加入与离开频道

在已加入机器人的 Discord 文本频道中：

```text
/voice join
/voice leave
/voice status
```

### 加入语音通话后会发生什么

- 用户在语音通话中发言
- Hermes 识别语音边界
- 文本转录内容会被发布到对应的文本频道
- Hermes 以文本和音频形式进行回应
- 该文本频道即为发送 `/voice join` 命令的频道

### Discord 语音通话的使用最佳实践

- 严格限制 `DISCORD_ALLOWED_USERS` 的范围
- 初期建议使用专用的机器人/测试频道
- 在尝试语音通话模式之前，先确认普通文本聊天语音模式下的语音转文字和文字转语音功能正常

## 语音质量优化建议

### 最佳质量配置

- 语音转文字：本地使用的 `large-v3` 模型或 Groq 的 `whisper-large-v3` 模型
- 文字转语音：ElevenLabs

### 最佳速度/便捷性配置

- 语音转文字：本地使用的 `base` 模型或 Groq 模型
- 文字转语音：Edge 服务

### 免费方案的最佳配置

- 语音转文字：本地处理
- 文字转语音：Edge 服务

## 常见故障及解决方案

### “未找到音频设备”

请安装 `portaudio`。

### “机器人已加入但听不到声音”

请检查以下事项：
- 您的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 列表中
- 您未被静音
- 特权意图已启用
- 机器人拥有连接/发言权限

### “可以转录文字但无法生成语音”

请检查以下事项：
- 文字转语音服务提供商的配置
- ElevenLabs 或 OpenAI 的 API 密钥及使用配额
- 是否安装了用于 Edge 转换路径的 `ffmpeg` 工具

### “Whisper 生成的音频质量很差”

可尝试以下方法：
- 选择更安静的环境
- 提高 `silence_threshold` 值
- 更换语音转文字服务提供商或模型
- 发言内容更简短、更清晰

### “在私信中可以正常使用，但在服务器频道中不行”

这通常与提及规则有关。默认情况下，除非另有配置，机器人在 Discord 服务器文本频道中需要通过 `@mention` 才能被识别。

## 首周建议配置方案

如果您希望最快实现成功：

1. 先让Hermes正常运行。  
2. 运行 `hermes setup tts` 命令以启用语音功能。  
3. 通过本地文本转语音技术与Edge TTS结合，使用CLI的语音模式。  
4. 随后在Telegram或Discord中开启 `/voice on` 功能。  
5. 只有完成以上步骤后，才能尝试使用Discord的视频通话模式。  

这样的逐步操作能有效缩小调试范围。  

## 推荐阅读内容  

- [语音模式功能参考](/user-guide/features/voice-mode)  
- [消息网关](/user-guide/messaging)  
- [Discord配置指南](/user-guide/messaging/discord)  
- [Telegram配置指南](/user-guide/messaging/telegram)  
- [配置设置](/user-guide/configuration)
