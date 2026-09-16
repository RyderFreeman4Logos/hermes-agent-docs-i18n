# 内置唤醒词模型

`hey_hermes.onnx` / `hey_hermes.tflite` —— 用于设备端的“Hey Hermes”唤醒词模型。该模型是唤醒词功能的默认检测器（详见 `website/docs/user-guide/features/wake-word.md`）；使用“hey hermes”发起指令无需进行任何训练或设置。

- **引擎：** [openWakeWord](https://github.com/dscripka/openWakeWord)（Apache-2.0许可证）。
- **来源：** 该模型是通过openWakeWord训练流程（基于合成TTS生成的语音）训练而成的，因此会生成`.onnx`和`.tflite`两种格式的文件。根据openWakeWord许可证，允许对该模型进行再分发。
- **标识名称：** 该模型注册的名称为`hey_hermes`，与文件名一致。
- **运行时说明：** openWakeWord的共享特征提取模型（梅尔频谱图+嵌入向量）并未包含在此处——这些模型会在首次使用时由`tools/wake_word.py`通过`openwakeword.utils.download_models()`函数自动下载。

如需使用其他唤醒词短语，可自行训练模型并将`wake_word.openwakeword.model`的路径指向该模型，或选择openWakeWord提供的预置名称（如`hey_jarvis`、`alexa`、`hey_mycroft`等）。具体的训练指南请参阅唤醒词相关文档。
