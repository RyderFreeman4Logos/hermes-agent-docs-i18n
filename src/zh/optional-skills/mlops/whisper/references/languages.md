# Whisper 语言支持指南

全面了解 Whisper 的多语言处理能力。

## 支持的语言（共99种）

### 顶级支持（WER < 10%）

- 英语 (en)
- 西班牙语 (es)
- 法语 (fr)
- 德语 (de)
- 意大利语 (it)
- 葡萄牙语 (pt)
- 荷兰语 (nl)
- 波兰语 (pl)
- 俄语 (ru)
- 日语 (ja)
- 韩语 (ko)
- 中文 (zh)

### 良好支持（WER 10-20%）

- 阿拉伯语 (ar)
- 土耳其语 (tr)
- 越南语 (vi)
- 瑞典语 (sv)
- 芬兰语 (fi)
- 捷克语 (cs)
- 罗马尼亚语 (ro)
- 匈牙利语 (hu)
- 丹麦语 (da)
- 挪威语 (no)
- 泰语 (th)
- 希伯来语 (he)
- 希腊语 (el)
- 印度尼西亚语 (id)
- 马来语 (ms)

### 完整列表（99种语言）

南非荷兰语、阿尔巴尼亚语、阿姆哈拉语、阿拉伯语、亚美尼亚语、阿萨姆语、阿塞拜疆语、巴什基尔语、巴斯克语、白俄罗斯语、孟加拉语、波斯尼亚语、布列塔尼语、保加利亚语、缅甸语、粤语、加泰罗尼亚语、中文、克罗地亚语、捷克语、丹麦语、荷兰语、英语、爱沙尼亚语、法罗语、芬兰语、法语、加利西亚语、格鲁吉亚语、德语、希腊语、古吉拉特语、海地克里奥尔语、豪萨语、夏威夷语、希伯来语、印地语、匈牙利语、冰岛语、印度尼西亚语、意大利语、日语、爪哇语、卡纳达语、哈萨克语、高棉语、韩语、老挝语、拉丁语、拉脱维亚语、林加拉语、立陶宛语、卢森堡语、马其顿语、马达加斯加语、马来语、马拉雅拉姆语、马耳他语、毛利语、马拉地语、摩尔多瓦语、蒙古语、缅甸语、尼泊尔语、挪威语、新挪威语、奥克西坦语、普什图语、波斯语、波兰语、葡萄牙语、旁遮普语、普什图语、罗马尼亚语、俄语、梵语、塞尔维亚语、绍纳语、信德语、僧伽罗语、斯洛伐克语、斯洛文尼亚语、索马里语、西班牙语、巽他语、斯瓦希里语、瑞典语、他加禄语、塔吉克语、泰米尔语、鞑靼语、泰卢固语、泰语、藏语、土耳其语、土库曼语、乌克兰语、乌尔都语、乌兹别克语、越南语、威尔士语、意第绪语、约鲁巴语

## 使用示例

### 自动检测语言

```python
import whisper

model = whisper.load_model("turbo")

# Auto-detect language
result = model.transcribe("audio.mp3")

print(f"Detected language: {result['language']}")
print(f"Text: {result['text']}")
```

### 指定语言（更快）

```python
# Specify language for faster transcription
result = model.transcribe("audio.mp3", language="es")  # Spanish
result = model.transcribe("audio.mp3", language="fr")  # French
result = model.transcribe("audio.mp3", language="ja")  # Japanese
```

### 英文译文

```python
# Translate any language to English
result = model.transcribe(
    "spanish_audio.mp3",
    task="translate"  # Translates to English
)

print(f"Original language: {result['language']}")
print(f"English translation: {result['text']}")
```

## 各语言专用提示

### 中文

```python
# Chinese works well with larger models
model = whisper.load_model("large")

result = model.transcribe(
    "chinese_audio.mp3",
    language="zh",
    initial_prompt="这是一段关于技术的讨论"  # Context helps
)
```

### 日语

```python
# Japanese benefits from initial prompt
result = model.transcribe(
    "japanese_audio.mp3",
    language="ja",
    initial_prompt="これは技術的な会議の録音です"
)
```

### 阿拉伯语

```python
# Arabic: Use large model for best results
model = whisper.load_model("large")

result = model.transcribe(
    "arabic_audio.mp3",
    language="ar"
)
```

## 模型规模推荐

| 语言层级 | 推荐模型 | WER值 |
|-----------|----------|-------|
| 顶级语言（英语、西班牙语、法语、德语） | base/turbo | < 10% |
| 良好语言（阿拉伯语、土耳其语、越南语） | medium/large | 10-20% |
| 资源有限的语言 | large | 20-30% |

## 各语言的性能表现

### 英语

- **tiny**：WER约15%
- **base**：WER约8%
- **small**：WER约5%
- **medium**：WER约4%
- **large**：WER约3%
- **turbo**：WER约3.5%

### 西班牙语

- **tiny**：WER约20%
- **base**：WER约12%
- **medium**：WER约6%
- **large**：WER约4%

### 中文

- **small**：WER约15%
- **medium**：WER约8%
- **large**：WER约5%

## 最佳实践建议

1. **使用仅支持英语的模型**——更适用于小型模型（tiny/base）
2. **明确指定语言**——比自动检测更快
3. **添加引导提示语**——可提升技术术语的识别准确率
4. **选用更大规模的模型**——适用于资源有限的语言
5. **通过样本进行测试**——不同口音/方言会导致质量差异
6. **注意音频质量**——清晰的音频能获得更好结果
7. **核对语言代码**——请使用ISO 639-1标准的两位字母代码

## 语言检测功能

```python
# Detect language only (no transcription)
import whisper

model = whisper.load_model("base")

# Load audio
audio = whisper.load_audio("audio.mp3")
audio = whisper.pad_or_trim(audio)

# Make log-Mel spectrogram
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# Detect language
_, probs = model.detect_language(mel)
detected_language = max(probs, key=probs.get)

print(f"Detected language: {detected_language}")
print(f"Confidence: {probs[detected_language]:.2%}")
```

## 资源参考

- **学术论文**：https://arxiv.org/abs/2212.04356  
- **GitHub仓库**：https://github.com/openai/whisper  
- **模型卡片**：https://github.com/openai/whisper/blob/main/model-card.md
