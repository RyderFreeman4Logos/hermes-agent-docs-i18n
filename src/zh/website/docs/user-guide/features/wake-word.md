---
sidebar_position: 11
title: "Wake Word"
description: "Hands-free 'Hey Hermes' wake word — start a voice session by speaking, the 'Hey Siri' way"
---

# 唤醒词（“Hey Hermes”）

该唤醒词能让 Hermes 在 CLI、TUI 以及桌面应用中充当免提助手：只需开启此项设置，Hermes 就会在后台持续监听特定的语音触发语。一旦说出该语句，Hermes 便会启动新会话，打开麦克风，通过常规的 [语音处理流程](/user-guide/features/voice-mode) 接收您的指令并予以回应，其工作方式与 “Hey Siri” 或 “Alexa” 完全相同。您可以使用 `surface` 命令来指定由哪个组件负责监听。

语音检测**完全在设备端完成**。处于常开状态的监听器仅负责监测唤醒词；在您实际向助手发出指令之前，不会有任何音频离开您的设备。

## 工作原理

1. 当设置 `wake_word.enabled: true`（或执行 `/wake on` 命令后），一个轻量级的语音触发词检测器会在您指定的输入设备上开始监听；如果未设置 `wake_word.input_device`，则默认使用系统麦克风。
2. 一旦检测到唤醒词，该检测器会立即暂停自身运行（从而释放麦克风），启动新会话，并借助语音模式的静音检测功能记录下一次语音输入。
3. 您的语音会被转录并发送给助手。在助手回复后，监听器会自动恢复工作状态，继续等待下一个唤醒词。

该功能**默认处于关闭状态**——在您将其开启之前，不会有任何组件进行监听。

在桌面应用程序中，只需**说出“stop”**（或“never mind”、“goodbye”、“cancel”、“that's all”）即可结束免提语音对话——该口头指令会直接终止对话，而不会被发送给智能体。系统仅会匹配完整的停止指令，因此像“停止docker容器”这样的实际请求仍会正常处理。

## 远程桌面（客户端采集）

当桌面应用程序连接到**远程**Hermes后端时（例如无界面的Docker主机或位于其他房间的机器），该后端通常**没有麦克风**。此时，服务器端的PortAudio会因“无法打开唤醒词麦克风”而失败。

针对这种情况，Hermes支持**客户端采集**功能：

1. 桌面应用会通过`capture: client`参数启动唤醒功能（当后端没有本地输入设备时，GUI会自动启用此功能；也可手动在下方进行设置）。
2. `openWakeWord`功能仍在**后端**运行（使用相同的引擎和模型）。
3. 桌面应用会打开**本地的Mac/PC麦克风**，将其采样率转换为16 kHz单声道int16格式，然后通过`wake.feed` RPC接口传输短帧数据。
4. 一旦检测到唤醒词，后端会像往常一样发送`wake.detected`信号；桌面应用则会使用客户端麦克风启动常规的语音处理流程。

```yaml
wake_word:
  enabled: true
  capture: auto    # auto | local | client
  # auto   — local PortAudio unless the desktop arms with client_capture
  # local  — always open the backend mic (CLI/TUI default)
  # client — always expect wake.feed PCM from the desktop (remote-friendly)
```

桌面 GUI 在调用 `wake.start` 时始终会设置 `client_capture: true`，因此那些在客户端模式下不支持麦克风输入的远程后端会自动启用该功能。而 CLI 和 TUI 则仅在您明确指定 `capture: client` 时才会进行本地捕获。

隐私说明：通过客户端捕获功能，唤醒所需的 PCM 数据会通过经过身份验证的桌面 ↔ 后端 WebSocket 通道传输（与会话中的其他数据使用同一通道）。检测系统仍不会将音频发送给第三方唤醒 API；相关处理均在后端进程的本地完成。

## 检测引擎

| 引擎 | 费用 | API 密钥 | 备注 |
|------|------|---------|-------|
| **openWakeWord**（默认） | 免费 | 无 | 使用本地 ONNX 模型。随 Hermes 提供预置的 **“hey hermes”** 模型（默认），同时支持 `hey_jarvis`、`alexa`、`hey_mycroft` 等指令以及自定义模型 |
| **sherpa** | 免费 | 无 | **开放词汇表**——无需任何训练即可识别任何输入的短语。首次使用时会自动下载小型英语模型（约 13 MB） |
| **Porcupine** | 免费版/付费版 | `PORCUPINE_ACCESS_KEY` | Picovoice 引擎；内置关键词功能，同时支持自定义 `.ppn` 文件 |

默认唤醒指令为 **“hey hermes”**——Hermes 已预置该指令的模型，因此无需训练即可立即使用。（首次使用时，openWakeWord 会下载其共享的特征提取模型，仅需进行一次少量数据下载。）

这两种引擎都会在您首次启用唤醒功能时才进行延迟安装（通过 `--include-desktop` 参数预装桌面版本的软件可提前完成安装，从而让设备立即可用）。如需提前安装：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[wake]"
```

## 快速入门

```bash
# In an interactive `hermes` session:
/wake on        # start listening (installs the engine on first use)
/wake status    # show phrase, provider, and state
/wake off       # stop listening
```

在桌面应用程序中，点击编辑器中的耳机图标即可。该切换开关本身即为设置选项：通过 `/wake` 命令或桌面上的耳机按钮开启/关闭唤醒词功能，同时也会将 `wake_word.enabled` 的值写入 `~/.hermes/config.yaml` 文件中，从而确保您的选择在多次会话之间依然有效。您也可以手动进行切换操作。

```yaml
wake_word:
  enabled: true
```

## 配置设置

```yaml
wake_word:
  enabled: false
  surface: auto               # eligible surface: "auto" | "cli" | "tui" | "gui"
  input_device: null           # PortAudio input index or device-name substring; null = process default
  capture: auto               # auto | local | client — where PCM is captured (see Remote desktop)
  provider: openwakeword      # "openwakeword" (free, local) | "sherpa" (free, any phrase) | "porcupine"
  phrase: "hey hermes"        # cosmetic label only — detection is keyed by the model/keyword below
  sensitivity: 0.6            # 0.0-1.0 — higher = stricter (fewer false triggers), consistent across all engines
  confirmation_frames: 3      # openWakeWord only — consecutive over-threshold frames required to fire
  start_new_session: true     # start a fresh session on wake vs. continue the current one
  openwakeword:
    model: hey_hermes         # bundled default; OR a built-in name OR a path to a custom .onnx/.tflite
    inference_framework: ""   # "" (auto) | "onnx" | "tflite"
  porcupine:
    keyword: jarvis           # built-in keyword OR path to a custom .ppn
```

`sensitivity`、`phrase` 以及 `start_new_session` 这三个参数对两种检测引擎均适用。而 `openwakeword` 和 `porcupine` 这两个选项则用于选择具体的检测模型。

`input_device` 参数会直接传递给唤醒监听器的 PortAudio（即 `sounddevice`）流。使用时既可以指定数字形式的设备索引，也可以使用唯一确定的设备名称子串。此设置仅会影响唤醒词的识别功能；桌面级即按即说功能仍会使用桌面应用程序自身的麦克风路径。

### 减少环境语音带来的误触发现象

openWakeWord 是逐个对长度约为 80 毫秒的音频帧进行评分的，因此背景对话中偶尔出现的杂音音素就有可能使某一个帧的评分超过阈值，从而意外触发唤醒词识别。可通过两个参数来控制这一问题：

- **`confirmation_frames`**（默认值为 `3`，仅适用于 openWakeWord 模式）——在触发唤醒功能之前，需要连续多少个超过阈值的数据帧。真正的“hey hermes”指令会在多个数据帧中保持较高的得分，而环境中的偶然信号仅会在单个数据帧中出现峰值。如果在嘈杂环境中仍会出现误触，可将其值提高（例如设置为 `4`–`5`），但这样会带来几十毫秒的额外延迟。将此值设为 `1` 可恢复到最初“第一帧即触发”的行为。
- **`sensitivity`**（默认值为 `0.6`）——检测阈值，取值范围为 `0.0`–`1.0`。数值越高，检测标准越严格（误触越少）。这一规则在**所有**引擎中都是一致的：对于 openWakeWord 模式，它是每个数据帧的原始得分阈值；对于 sherpa 模式，它会转换为关键词阈值；而对于 Porcupine 模式，其内部逻辑会进行反向处理，因此“数值越高，标准越严格”的原则同样适用。默认值 `0.6` 高于 openWakeWord 模式较为宽松的 `0.5` 基准值，后者允许类似“hey hor”这样的接近匹配被识别；如果仍存在误触，可将其值提高至接近 `0.8`；若无法识别真正的“hey hermes”指令，则应降低该值。

sherpa 和 Porcupine 引擎会内部解析整个指令语句，因此不存在单帧峰值问题，也会忽略 `confirmation_frames` 参数（但仍会遵循 `sensitivity` 阈值）。

`inference_framework`用于选择openWakeWord后端。若保持为空（即默认值），则由Hermes根据不同平台自动选择：在Apple Silicon架构设备上使用tflite后端，其他所有平台则使用onnx后端。由于openWakeWord的onnx后端在macOS ARM64架构上的识别准确率几乎为零（参见[openWakeWord#336](https://github.com/dscripka/openWakeWord/issues/336)），因此将监听器设置为`onnx`后端时，虽然设备看似处于监听状态，但实际上永远不会触发响应。而tflite后端在macOS上需要`ai-edge-litert`组件，Hermes会自动在其他唤醒词相关依赖项一同安装该组件。

### 听觉界面（CLI、TUI、GUI）

该唤醒词功能可在Hermes的三种听觉界面中正常使用，`surface`参数用于指定由哪个界面负责管理监听器，并在触发时启动新会话：

| `surface` | 行为 |
|-----------|------|
| `auto`（默认值） | 所有本地听觉界面均可参与；第一个进入运行状态的界面将拥有监听器控制权。 |
| `cli` | 仅适用于传统的`hermes` CLI命令行界面。 |
| `tui` | 仅适用于`hermes --tui`命令启动的文本用户界面。 |
| `gui` | 仅适用于桌面应用程序。 |

由于检测功能在设备端运行且仅支持单麦克风输入，因此即使Hermes的多个听觉界面在独立进程中运行，也同时只能有一个界面处于监听状态。监听器控制权具有粘性：第一个符合条件的界面将一直持有控制权，直到该界面停止运行、断开连接或进程退出为止。Hermes不会自动无缝切换到另一个处于可用状态的界面。如需强制指定监听器的所属界面而非让最先请求的界面获得控制权，请设置`surface`参数。TUI和桌面GUI共享相同的Python后端（`tui_gateway`），该后端在服务器端运行检测功能，同时在执行命令录音时将麦克风控制权交由语音捕获模块处理。

## 使用其他唤醒语

“Hey Hermes”可直接使用——默认采用的便是内置的openWakeWord模型（`model: hey_hermes`）。若想使用其他唤醒语，最简便的方法就是采用开放词汇引擎：

### 方案A — sherpa（支持任意短语，无需训练）

直接输入您希望使用的唤醒语即可；系统会在运行时对其进行分词处理——无论是“hey coder”、“computer”、“wake up neo”，还是其他任何语句均可。

```yaml
wake_word:
  enabled: true
  provider: sherpa
  phrase: "hey coder"        # detection key — just type your phrase
```

小型英文版 KWS 模型（约 13 MB）会在首次使用时下载一次。每个配置文件都可以设置自己的唤醒语——您为每个运行的配置文件指定不同的“hey <配置文件名>”语句。

### 唤醒特定配置文件（桌面端）

借助 sherpa 引擎，一个监听器即可唤醒任意配置文件。所有在配置中设置了 `wake_word.enabled: true` 的配置文件都会自动被注册；若未设置该参数，则其唤醒语默认为 `hey <配置文件名>`。说出对应配置文件的唤醒语后，桌面应用会立即切换到该配置文件，开启新的会话，并启动免提语音功能：

- “hey hermes” → 默认配置文件
- “hey coder” → “coder” 配置文件
- “hey trader” → “trader” 配置文件

若希望监听器仅响应自身的唤醒语，可在其配置文件中将 `wake_word.profile_routing: false` 设为 true。CLI 和 TUI 是单配置文件进程：对于属于其他配置文件的唤醒语，系统会直接输出切换命令（`hermes -p <配置文件名>`），而不会进行路由处理。

名称的匹配是通过其英文子词发音来实现的：由两个不同且包含2个以上音节的单词构成的唤醒语效果最佳。如果名称过短、包含复杂的非英文发音特征，或是有两个发音相似的配置文件，可能会导致匹配精度下降——必要时可调整各配置文件的 `sensitivity` 参数。

### 方案 B — openWakeWord（免费，经过训练的模型）

您可以选择内置模型（如 `hey_jarvis`、`alexa`、`hey_mycroft` 等），或者为获得更高的稳定性自行训练自定义模型（在免费 GPU 或 Colab 环境下大约需要75–90分钟），将生成的 `.onnx` 文件放置到指定位置后即可直接调用。

```yaml
wake_word:
  enabled: true
  provider: openwakeword
  phrase: "computer"
  openwakeword:
    model: ~/.hermes/wakewords/computer.onnx   # or a built-in name like hey_jarvis
```

培训参考资料：

- [openWakeWord](https://github.com/dscripka/openWakeWord)
- [2026年训练用Colab文档](https://github.com/alfiedennen/openwakeword-colab-2026)

:::提示 选择具有辨识度的短语
与日常用语不冲突的唤醒词通用性最佳。由一个不常见单词构成的双音节词（如“hermes”）比“hello”或“stop”这类常用词更佳。
:::

### 方案C — Porcupine（自定义秒级唤醒词）

在[Picovoice控制台](https://console.picovoice.ai/)中创建“Hey Hermes”这一唤醒词，下载对应的`.ppn`文件，然后：

```yaml
wake_word:
  enabled: true
  provider: porcupine
  phrase: "hey hermes"
  porcupine:
    keyword: ~/.hermes/wakewords/hey_hermes.ppn
```

在 `~/.hermes/.env` 文件中设置您的访问密钥：

```bash
PORCUPINE_ACCESS_KEY=your-key-here
```

## 需求条件

- 一个可正常工作的麦克风，以及 `sounddevice` + `numpy` 音频处理库（该要求与语音模式相同）。
- 用于将语音指令转录为文本的 STT 服务提供商——本地的 `faster-whisper` 可直接使用；完整的提供商列表请参见 [语音模式](/user-guide/features/voice-mode)。
- 用于将回复内容转换为语音的 TTS 服务提供商（默认的 `edge-tts` 无需额外配置即可使用）。由于唤醒流程为完全免持设计，因此只有在 STT 和 TTS 均准备就绪后才会启动唤醒功能——可通过 `hermes tools`（语音部分）进行相关设置。
- 唤醒引擎所需的依赖项（会自动安装，也可通过 `hermes-agent[wake]` 安装）。

若监听器无法启动，`/wake status` 命令会明确显示缺失了哪些组件。

### 在 macOS 系统上“处于监听状态”但始终无法唤醒

macOS 是按**进程**来授予麦克风访问权限的。桌面应用中的 STT 功能已证明*渲染层*拥有麦克风访问权，但唤醒监听器是在 Python *后端*中运行的，因此也需要单独的授权。若未获得授权，CoreAudio 会向后端提供一条“看似正常”但实际上仅输出静音的音频流，从而导致系统显示正在监听，却无法触发唤醒指令。Hermes 能检测到这种情况（`/wake status` 会显示“麦克风仅输出静音”；桌面端的提示信息也会给出相同提示）。解决方法：进入系统设置 → 隐私与安全性 → 麦克风，为 Hermes 后端开启权限（它可能显示为终端、`python` 或 Hermes），之后再关闭并重新打开唤醒词功能。

### 在 Windows 系统上“处于监听状态”但仅收到静音信号

桌面式即按即说功能与唤醒词识别功能会使用不同的麦克风路径。即按即说功能通过桌面应用程序的浏览器接口来捕获音频，而唤醒词监听器则会在 Python 后端打开一个 PortAudio 流。这样一来，当其中一个功能正在运行时，另一个功能所使用的 Windows 麦克风输入可能会处于静音状态或无法正常使用。

`/wake status` 命令可用于查看当前所选的输入设备以及 Windows 的音频主机 API。如果该命令检测到当前为静音状态，需将 `wake_word.input_device` 设置为正在工作的 PortAudio 输入设备的数字索引或唯一名称，之后即可切换唤醒词识别功能。

```bash
hermes config set wake_word.input_device "Microphone Array"
```

若要恢复到流程的默认设置，可使用 `null`：

```bash
hermes config set wake_word.input_device null
```

## 注意事项与限制

- **仅支持本地麦克风。** 该唤醒词识别功能可在 CLI、TUI 以及桌面 GUI 环境中运行——即任何具备本地麦克风的场景下均可使用。但在不具备麦克风的消息平台（如 Telegram、Discord 等）中则无法使用。
- **一次仅可使用一个麦克风。** 在录制指令时，检测模块会释放麦克风控制权；待当前操作结束后才会重新获取控制权，从而避免与语音采集功能发生冲突。
- **隐私保护。** 唤醒词识别为本地处理方式。若出现误触发情况，请提高 `sensitivity` 设置值；若无法准确识别您的指令，则可降低该值。
