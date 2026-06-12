# AudioCraft 故障排除指南

## 安装问题

### 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'audiocraft'`

**解决方案**：
```bash
# Install from PyPI
pip install audiocraft

# Or from GitHub
pip install git+https://github.com/facebookresearch/audiocraft.git

# Verify installation
python -c "from audiocraft.models import MusicGen; print('OK')"
```

### 未找到 FFmpeg

**错误信息**：`RuntimeError: ffmpeg not found`

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows (using conda)
conda install -c conda-forge ffmpeg

# Verify
ffmpeg -version
```

### PyTorch CUDA版本不匹配

**错误信息**：`RuntimeError: CUDA error: no kernel image is available`

**解决方案**：
```bash
# Check CUDA version
nvcc --version
python -c "import torch; print(torch.version.cuda)"

# Install matching PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### xformers 相关问题

**错误提示**：`ImportError: xformers` 相关错误

**解决方案**：
```bash
# Install xformers for memory efficiency
pip install xformers

# Or disable xformers
export AUDIOCRAFT_USE_XFORMERS=0

# In Python
import os
os.environ["AUDIOCRAFT_USE_XFORMERS"] = "0"
from audiocraft.models import MusicGen
```

## 模型加载问题

### 加载过程中内存不足

**错误信息**：在加载模型时出现 `torch.cuda.OutOfMemoryError` 错误

**解决方案**：
```python
# Use smaller model
model = MusicGen.get_pretrained('facebook/musicgen-small')

# Force CPU loading first
import torch
device = "cpu"
model = MusicGen.get_pretrained('facebook/musicgen-small', device=device)
model = model.to("cuda")

# Use HuggingFace with device_map
from transformers import MusicgenForConditionalGeneration
model = MusicgenForConditionalGeneration.from_pretrained(
    "facebook/musicgen-small",
    device_map="auto"
)
```

### 下载失败

**错误原因**：连接故障或下载未完成

**解决方案**：
```python
# Set cache directory
import os
os.environ["AUDIOCRAFT_CACHE_DIR"] = "/path/to/cache"

# Or for HuggingFace
os.environ["HF_HOME"] = "/path/to/hf_cache"

# Resume download
from huggingface_hub import snapshot_download
snapshot_download("facebook/musicgen-small", resume_download=True)

# Use local files
model = MusicGen.get_pretrained('/local/path/to/model')
```

### 模型类型错误

**错误提示**：为当前任务加载了错误的模型

**解决方案**：
```python
# For text-to-music: use MusicGen
from audiocraft.models import MusicGen
model = MusicGen.get_pretrained('facebook/musicgen-medium')

# For text-to-sound: use AudioGen
from audiocraft.models import AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')

# For melody conditioning: use melody variant
model = MusicGen.get_pretrained('facebook/musicgen-melody')

# For stereo: use stereo variant
model = MusicGen.get_pretrained('facebook/musicgen-stereo-medium')
```

## 生成问题

### 输出为空或无声音

**问题**：生成的音频没有声音或声音极弱

**解决方案**：
```python
import torch

# Check output
wav = model.generate(["upbeat music"])
print(f"Shape: {wav.shape}")
print(f"Max amplitude: {wav.abs().max().item()}")
print(f"Mean amplitude: {wav.abs().mean().item()}")

# If too quiet, normalize
def normalize_audio(audio, target_db=-14.0):
    rms = torch.sqrt(torch.mean(audio ** 2))
    target_rms = 10 ** (target_db / 20)
    gain = target_rms / (rms + 1e-8)
    return audio * gain

wav_normalized = normalize_audio(wav)
```

### 输出质量差

**问题**：生成的音乐听起来效果不佳或存在杂音

**解决方案**：
```python
# Use larger model
model = MusicGen.get_pretrained('facebook/musicgen-large')

# Adjust generation parameters
model.set_generation_params(
    duration=15,
    top_k=250,          # Increase for more diversity
    temperature=0.8,    # Lower for more focused output
    cfg_coef=4.0        # Increase for better text adherence
)

# Use better prompts
# Bad: "music"
# Good: "upbeat electronic dance music with synthesizers and punchy drums"

# Try MultiBand Diffusion
from audiocraft.models import MultiBandDiffusion
mbd = MultiBandDiffusion.get_mbd_musicgen()
tokens = model.generate_tokens(["prompt"])
wav = mbd.tokens_to_wav(tokens)
```

### 生成内容过短

**问题**：生成的音频长度低于预期

**解决方案**：
```python
# Check duration setting
model.set_generation_params(duration=30)  # Set before generate

# Verify in generation
print(f"Duration setting: {model.generation_params}")

# Check output shape
wav = model.generate(["prompt"])
actual_duration = wav.shape[-1] / 32000
print(f"Actual duration: {actual_duration}s")

# Note: max duration is typically 30s
```

### 旋律条件控制失败

**错误提示**：旋律条件生成出现异常

**解决方案**：
```python
import torchaudio
from audiocraft.models import MusicGen

# Load melody model (not base model)
model = MusicGen.get_pretrained('facebook/musicgen-melody')

# Load and prepare melody
melody, sr = torchaudio.load("melody.wav")

# Resample to model sample rate if needed
if sr != 32000:
    resampler = torchaudio.transforms.Resample(sr, 32000)
    melody = resampler(melody)

# Ensure correct shape [batch, channels, samples]
if melody.dim() == 1:
    melody = melody.unsqueeze(0).unsqueeze(0)
elif melody.dim() == 2:
    melody = melody.unsqueeze(0)

# Convert stereo to mono
if melody.shape[1] > 1:
    melody = melody.mean(dim=1, keepdim=True)

# Generate with melody
model.set_generation_params(duration=min(melody.shape[-1] / 32000, 30))
wav = model.generate_with_chroma(["piano cover"], melody, 32000)
```

## 内存问题

### CUDA 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存不足`

**解决方案**：
```python
import torch

# Clear cache before generation
torch.cuda.empty_cache()

# Use smaller model
model = MusicGen.get_pretrained('facebook/musicgen-small')

# Reduce duration
model.set_generation_params(duration=10)  # Instead of 30

# Generate one at a time
for prompt in prompts:
    wav = model.generate([prompt])
    save_audio(wav)
    torch.cuda.empty_cache()

# Use CPU for very large generations
model = MusicGen.get_pretrained('facebook/musicgen-small', device="cpu")
```

### 批量处理时的内存泄漏问题

**问题**：内存使用量随时间逐渐增加

**解决方案**：
```python
import gc
import torch

def generate_with_cleanup(model, prompts):
    results = []

    for prompt in prompts:
        with torch.no_grad():
            wav = model.generate([prompt])
            results.append(wav.cpu())

        # Cleanup
        del wav
        gc.collect()
        torch.cuda.empty_cache()

    return results

# Use context manager
with torch.inference_mode():
    wav = model.generate(["prompt"])
```

## 音频格式相关问题

### 样率错误

**问题**：音频播放速度异常

**解决方案**：
```python
import torchaudio

# MusicGen outputs at 32kHz
sample_rate = 32000

# AudioGen outputs at 16kHz
sample_rate = 16000

# Always use correct rate when saving
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=sample_rate)

# Resample if needed
resampler = torchaudio.transforms.Resample(32000, 44100)
wav_resampled = resampler(wav)
```

### 立体声/单声道不匹配

**问题**：通道数量错误

**解决方案**：
```python
# Check model type
print(f"Audio channels: {wav.shape}")
# Mono: [batch, 1, samples]
# Stereo: [batch, 2, samples]

# Convert mono to stereo
if wav.shape[1] == 1:
    wav_stereo = wav.repeat(1, 2, 1)

# Convert stereo to mono
if wav.shape[1] == 2:
    wav_mono = wav.mean(dim=1, keepdim=True)

# Use stereo model for stereo output
model = MusicGen.get_pretrained('facebook/musicgen-stereo-medium')
```

### 截幅与失真问题

**问题**：音频出现截幅或失真现象

**解决方案**：
```python
import torch

# Check for clipping
max_val = wav.abs().max().item()
print(f"Max amplitude: {max_val}")

# Normalize to prevent clipping
if max_val > 1.0:
    wav = wav / max_val

# Apply soft clipping
def soft_clip(x, threshold=0.9):
    return torch.tanh(x / threshold) * threshold

wav_clipped = soft_clip(wav)

# Lower temperature during generation
model.set_generation_params(temperature=0.7)  # More controlled
```

## HuggingFace Transformers 相关问题

### 处理器错误

**错误类型**：MusicgenProcessor 存在问题

**解决方案**：
```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# Load matching processor and model
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

# Ensure inputs are on same device
inputs = processor(
    text=["prompt"],
    padding=True,
    return_tensors="pt"
).to("cuda")

# Check processor configuration
print(processor.tokenizer)
print(processor.feature_extractor)
```

### 生成参数错误

**错误提示**：生成的参数无效

**解决方案**：
```python
# HuggingFace uses different parameter names
audio_values = model.generate(
    **inputs,
    do_sample=True,           # Enable sampling
    guidance_scale=3.0,       # CFG (not cfg_coef)
    max_new_tokens=256,       # Token limit (not duration)
    temperature=1.0
)

# Calculate tokens from duration
# ~50 tokens per second
duration_seconds = 10
max_tokens = duration_seconds * 50
audio_values = model.generate(**inputs, max_new_tokens=max_tokens)
```

## 性能问题

### 生成速度过慢

**问题**：内容生成耗时过长

**解决方案**：
```python
# Use smaller model
model = MusicGen.get_pretrained('facebook/musicgen-small')

# Reduce duration
model.set_generation_params(duration=10)

# Use GPU
model.to("cuda")

# Enable flash attention if available
# (requires compatible hardware)

# Batch multiple prompts
prompts = ["prompt1", "prompt2", "prompt3"]
wav = model.generate(prompts)  # Single batch is faster than loop

# Use compile (PyTorch 2.0+)
model.lm = torch.compile(model.lm)
```

### CPU 降级方案

**问题**：生成任务在 CPU 上运行而非 GPU 上

**解决方案**：
```python
import torch

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")

# Explicitly move to GPU
model = MusicGen.get_pretrained('facebook/musicgen-small')
model.to("cuda")

# Verify model device
print(f"Model device: {next(model.lm.parameters()).device}")
```

## 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `CUDA out of memory` | 模型过大 | 使用更小的模型，缩短运行时间 |
| `ffmpeg not found` | 未安装 FFmpeg | 安装 FFmpeg |
| `No module named 'audiocraft'` | 该模块未安装 | 运行 `pip install audiocraft` 进行安装 |
| `RuntimeError: Expected 3D tensor` | 输入数据形状错误 | 检查张量的维度 |
| `KeyError: 'melody'` | 选择的模型不支持旋律生成 | 使用 musicgen-melody 模型 |
| `Sample rate mismatch` | 音频格式不正确 | 将音频重采样为模型要求的采样率 |

## 获取帮助

1. **GitHub 问题追踪页**：https://github.com/facebookresearch/audiocraft/issues
2. **HuggingFace 论坛**：https://discuss.huggingface.co
3. **相关论文**：https://arxiv.org/abs/2306.05284

### 报告问题时请提供以下信息

- Python 版本
- PyTorch 版本
- CUDA 版本
- AudioCraft 版本：运行 `pip show audiocraft` 查看
- 完整的错误堆栈信息
- 最简可复现代码示例
- 硬件信息（GPU 型号、显存容量）
