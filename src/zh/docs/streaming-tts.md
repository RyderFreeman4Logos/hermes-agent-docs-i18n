# 流式文本转语音功能

Hermes 能够在语音合成结果从服务提供商处实时传输时即可进行流式播放，而无需等待完整音频生成后再开始播放。该功能被语音模式（CLI/TUI 实时对话）、控制台的语音流 WebSocket，以及通过 `StreamingTTSConsumer` 网关实现的任何支持流式音频的平台适配器所采用。这样，语音回复会在生成第一个语句后就开始播放，而无需等待整个文本完成生成与合成。

## 架构设计

流式处理流程包含四个部分：

1. **生成端**——大语言模型在生成响应时会逐步输出文本增量信息  
2. **句子分块器**——`tools.tts_streaming.SentenceChunker` 负责汇总这些增量信息，剔除 `<think>` 块（即便该块分布在多个增量中），并将完整的句子输出  
3. **文本转语音服务提供商**——已注册的 `StreamingTTSProvider` 会将每个句子转换为原始 PCM 数据块（采用该提供商指定的采样率，为 int16 单声道格式）  
4. **音频输出端**——用于本地播放的 `sounddevice.OutputStream`（如 `tools.tts_tool_speaker.stream_tts_to_speaker`），或是网关平台适配器中的 `write_streaming_tts` 方法（位于 `gateway/streaming_tts_consumer.py` 文件中）

那些没有提供分块接口的服务提供商，仍可通过经过验证的同步式 `text_to_speech_tool` 方式实现按句子逐句播放，因此默认的边缘模式同样具备对话功能。所有待播放的文本都会经过 `tools.tts_text_normalize.prepare_spoken_text` 函数处理（统一使用同一处理函数，适配所有路径）。

## 如何选择服务提供商

默认情况下，只要您已配置的提供方（即 `tts.provider`）具备分块式 API，调度器就会使用该提供方进行流式传输——它绝不会为了实现流式播放而擅自将您的声音切换到其他提供方。

如需更改此设置，请在 `config.yaml` 文件中设置 `tts.streaming.provider` 参数：
- 指定提供方名称（如 `elevenlabs`、`gemini`、`openai`、`xai`），即可强制使用该提供方的流式服务；
- 设置为 `auto` 时，系统会按优先级顺序 `elevenlabs → gemini → openai → xai` 依次尝试，一旦找到能成功验证凭据的提供方即立即使用——这相当于主动选择“可用性最佳的分块式语音服务”。

```yaml
tts:
  provider: gemini
  streaming:
    provider: gemini      # or "auto"
  gemini:
    model: gemini-2.5-flash-preview-tts
    voice: Kore
```

## 功能矩阵

| 提供商       | 传输协议                         | 分块 PCM | 凭证信息               |
|--------------|----------------------------------|-----------|------------------------|
| elevenlabs   | 分块 HTTP (`pcm_24000`)           | 是        | `ELEVENLABS_API_KEY` / `tts.elevenlabs` |
| openai       | 分块 HTTP (`with_streaming_response`, `pcm`) | 是        | `tts.openai.api_key` → 环境变量 → 托管网关 |
| gemini       | SSE (`streamGenerateContent?alt=sse`) | 是        | `GEMINI_API_KEY` / `GOOGLE_API_KEY` |
| xai          | WebSocket (`wss://api.x.ai/v1/tts`)   | 是        | xAI OAuth 或 `XAI_API_KEY` |
| edge、piper、kitten、neutts、mistral、minimax、deepinfra 等 | — | 否（支持按句同步回退） | 与常规方式相同 |

所有凭证查询均通过 `resolve_provider_secret()` 完成
（配置 > 环境变量/.env > 凭证池）——绝不会直接读取环境变量。流式传输的数据量每句最多为 16 MiB，这一限制与同步型提供商的上行数据大小限制一致。

## 添加新的流式传输提供商

1. 在 `tools/tts_streaming.py` 中继承 `StreamingTTSProvider` 类
2. 设置 `sample_rate`（若非单声道 int16 格式，则还需设置 `channels` / `sample_width`）
3. 实现 `available()` 方法（仅用于检测，不得实际安装任何组件）以及 `stream(self, text) -> Iterator[bytes]` 方法，用于返回原始 PCM 分块数据
4. 使用 `@register("yourname")` 进行装饰
5. 在 `tests/tools/test_tts_streaming.py` 中编写测试用例
ABC 负责执行协议约束，而注册表则确保服务提供者能够被发现；调度器（`stream_tts_to_speaker`）以及网关消费者会免费处理句子缓冲区、停止事件以及音频输出功能。

## 网关流式传输（平台适配器）

`gateway/streaming_tts_consumer.py` 用于将智能体的状态变化同步到适配器的流式音频处理流程中。各适配器可通过在 `BasePlatformAdapter` 类上重写以下方法来实现该功能：
- `supports_streaming_tts(chat_id, audio_format) -> bool`
- `begin_streaming_tts / write_streaming_tts / finish_streaming_tts / abort_streaming_tts`

这些方法的默认行为均为“不支持”或“无操作”，因此不会影响现有的适配器。当某次对话的流式音频播放完成后，该次对话对应的整段自动文本转语音回复将被抑制，从而避免重复播放；如果在任何音频内容可听之前流式传输失败，网关则会回退到传统的整段语音回复方式。
