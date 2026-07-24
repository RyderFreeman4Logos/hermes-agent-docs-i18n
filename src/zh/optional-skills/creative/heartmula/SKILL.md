---
name: heartmula
description: "HeartMuLa: Suno-like song generation from lyrics + tags."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [music, audio, generation, ai, heartmula, heartcodec, lyrics, songs]
    related_skills: [audiocraft-audio-generation, songwriting-and-ai-music]
---

# HeartMuLa——开源音乐生成工具

## 概述
HeartMuLa是一系列基于Apache-2.0协议的开源音乐基础模型，能够根据歌词和标签生成音乐，并支持多语言处理。它可从歌词及标签直接生成完整歌曲，在开源领域可视为Suno的替代方案。该系列包括以下组件：
- **HeartMuLa**——用于根据歌词和标签生成音乐的文本语言模型（3B/7B版本）
- **HeartCodec**——12.5Hz音乐编码解码器，可实现高保真音频重建
- **HeartTranscriptor**——基于Whisper技术的歌词转录工具
- **HeartCLAP**——音频与文本对齐模型

## 适用场景
- 用户希望根据文字描述生成音乐或歌曲
- 用户需要开源版本的Suno替代品
- 用户需要进行本地/离线音乐生成
- 用户想了解HeartMuLa、heartlib或AI音乐生成相关技术

## 硬件要求
- **最低配置**：8GB显存，需启用`--lazy_load true`选项（按顺序加载/卸载模型）
- **推荐配置**：16GB以上显存，以便在单GPU上更流畅地运行
- **多GPU部署**：可使用`--mula_device cuda:0 --codec_device cuda:1`参数将任务分配到不同GPU上
- 启用lazy_load功能的3B模型最多需约6.2GB显存

## 安装步骤

### 1. 克隆代码仓库
```bash
cd ~/  # or desired directory
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
```

### 2. 创建虚拟环境（需使用 Python 3.10）
```bash
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
```

### 3. 解决依赖兼容性问题

**重要提示**：截至2026年2月，已固定的依赖项与更新版本的软件包存在冲突。请应用以下修复方案：

```bash
# Upgrade datasets (old version incompatible with current pyarrow)
uv pip install --upgrade datasets

# Upgrade transformers (needed for huggingface-hub 1.x compatibility)
uv pip install --upgrade transformers
```

### 4. 修复源代码（transformers 5.x版本必需）

**修复1——RoPE缓存问题**，位于`src/heartlib/heartmula/modeling_heartmula.py`文件中：

在`HeartMuLa`类的`setup_caches`方法中，在`reset_caches`的try/except代码块之后、`with device:`代码块之前，添加RoPE重置逻辑：

```python
# Re-initialize RoPE caches that were skipped during meta-device loading
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**原因**：`from_pretrained` 会首先在元设备上创建模型；而 `Llama3ScaledRoPE.rope_init()` 会跳过对元张量的缓存构建，且在权重加载到实际设备后也不会再次进行构建。

位于 `src/heartlib/pipelines/music_generation.py` 中的 **Patch 2 - HeartCodec 加载修复**：

需在所有 `HeartCodec.from_pretrained()` 调用中添加 `ignore_mismatched_sizes=True` 参数（共有两处调用：即 `__init__` 方法中的即时加载，以及 `codec` 属性中的延迟加载）。

**原因**：检查点文件中的 VQ 代码本已初始化缓冲区的形状为 `[1]`，而模型中的相应缓冲区形状为 `[]`。尽管数据相同，但前者为标量值，后者为 0 维张量，因此可以安全地忽略这种尺寸差异。

### 5. 下载模型检查点
```bash
cd heartlib  # project root
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

这三者可以同时下载，总大小约为数GB。

## GPU / CUDA

HeartMuLa默认使用CUDA（通过`--mula_device cuda --codec_device cuda`参数指定）。只要用户拥有安装了PyTorch CUDA支持的NVIDIA GPU，即无需额外设置。

- 已安装的`torch==2.4.1`版本可直接支持CUDA 12.1
- `torchtune`工具显示的版本信息可能为`0.4.0+cpu`——这只是软件包的元数据，实际仍通过PyTorch使用CUDA
- 要确认是否使用了GPU，可查看输出结果中的“CUDA内存”相关行（例如“卸载前CUDA内存：6.20 GB”）
- **没有GPU？** 可以通过`--mula_device cpu --codec_device cpu`参数在CPU上运行，但生成速度会**极其缓慢**（处理一首歌曲可能需要30到60分钟甚至更久，而使用GPU仅需约4分钟）。CPU模式还需要大量内存（建议至少有12GB以上空闲内存）。如果用户没有NVIDIA GPU，建议使用云GPU服务（如Google Colab的免费T4版本、Lambda Labs等），或访问在线演示地址https://heartmula.github.io/进行试用。

## 使用方法

### 基本生成流程
```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### 输入格式

**标签**（以逗号分隔，不可包含空格）：
```
piano,happy,wedding,synthesizer,romantic
```
或
```
rock,energetic,guitar,drums,male-vocal
```

**歌词**（请使用括号内的结构标签）：
```
[Intro]

[Verse]
Your lyrics here...

[Chorus]
Chorus lyrics...

[Bridge]
Bridge lyrics...

[Outro]
```

### 关键参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--max_audio_length_ms` | 240000 | 最大长度，以毫秒为单位（240秒 = 4分钟） |
| `--topk` | 50 | Top-k采样策略 |
| `--temperature` | 1.0 | 采样温度系数 |
| `--cfg_scale` | 1.5 | 无分类器引导系数 |
| `--lazy_load` | false | 按需加载/卸载模型（可节省显存） |
| `--mula_dtype` | bfloat16 | HeartMuLa的数据类型（推荐使用bf16） |
| `--codec_dtype` | float32 | HeartCodec的数据类型（为保证音质，推荐使用fp32） |

### 性能表现
- 实时因子（RTF）约为1.0——一首4分钟的歌曲大约需要4分钟的时间来生成
- 输出格式：MP3，48kHz立体声，128kbps比特率

## 常见问题与注意事项
1. **切勿对HeartCodec使用bf16格式**——这会降低音频质量。请使用默认的fp32格式。
2. **标签信息可能会被忽略**——这是已知的问题（编号#90）。歌词内容往往占据主导，可尝试调整标签的顺序。
3. **macOS系统不支持Triton框架**——GPU加速功能仅适用于Linux系统及CUDA环境。
4. 有报告指出RTX 5080显卡可能存在兼容性问题。
5. 由于依赖项版本冲突，需按照上文所述进行手动升级和打补丁操作。

## 相关链接
- 代码仓库：https://github.com/HeartMuLa/heartlib
- 模型页面：https://huggingface.co/HeartMuLa
- 相关论文：https://arxiv.org/abs/2601.10547
- 许可协议：Apache-2.0
