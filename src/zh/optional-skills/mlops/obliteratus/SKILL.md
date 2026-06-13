---
name: obliteratus
description: "OBLITERATUS: abliterate LLM refusals (diff-in-means)."
version: 2.0.0
author: Hermes Agent
license: MIT
dependencies: [obliteratus, torch, transformers, bitsandbytes, accelerate, safetensors]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Abliteration, Uncensoring, Refusal-Removal, LLM, Weight-Projection, SVD, Mechanistic-Interpretability, HuggingFace, Model-Surgery]
    related_skills: [vllm, gguf, huggingface-tokenizers]
---

# OBLITERATUS 技能

## 功能概览

包含 9 种 CLI 命令、28 个分析模块、5 个计算层级下的 116 个模型预设，同时还支持比赛评估功能以及基于遥测数据的推荐服务。

无需重新训练或微调，即可消除开放权重大型语言模型中的拒绝行为（安全限制）。该技能运用多种机制可解释性技术——包括差分均值法、SVD、白化 SVD、LEACE 概念消除法、SAE 分解法、贝叶斯核投影法等——精准识别模型权重中的拒绝逻辑并将其剔除，同时保留模型的推理能力。

**许可证警告：** OBLITERATUS 采用 AGPL-3.0 许可协议。切勿将其作为 Python 库导入，必须通过 CLI（`obliteratus` 命令）或子进程的方式调用，这样才能保持 Hermes Agent 所遵循的 MIT 许可协议的纯净性。

## 视频教程

演示 Hermes Agent 如何使用 OBLITERATUS 消除 Gemma 模型的安全限制：
https://www.youtube.com/watch?v=8fG9BrNTeHs（视频标题：“OBLITERATUS：一个能够清除 Gemma 4 安全限制的 AI 智能体”）

当用户希望在亲自操作之前先直观了解整个端到端工作流程时，该视频会非常有用。

## 适用场景

在以下情况下可触发此技能：
- 用户希望“解除审查”或“消除”某个大型语言模型的限制；
- 用户询问如何移除模型中的拒绝机制或安全限制；
- 用户希望创建 Llama、Qwen、Mistral 等模型的无限制版本；
- 用户提及“去除拒绝行为”、“消除限制”、“权重投影”等术语；
- 用户希望分析模型的拒绝机制运作方式；
- 用户提到 OBLITERATUS、abliterator 或拒绝逻辑等相关内容。

## 第 1 步：安装

首先检查该技能是否已安装：
```bash
obliteratus --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

如果尚未安装，可从 GitHub 克隆并安装：
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
pip install -e .
# For Gradio web UI support:
# pip install -e ".[spaces]"
```

**重要提示：** 安装前请务必与用户确认。该操作会引入约 5-10GB 的依赖项（如 PyTorch、Transformers、bitsandbytes 等）。

## 第 2 步：检查硬件

在开始之前，先确认系统中是否有可用的 GPU：
```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('TIER: tiny (models under 1B)')
    elif vram < 8: print('TIER: small (models 1-4B)')
    elif vram < 16: print('TIER: medium (models 4-9B with 4bit quant)')
    elif vram < 32: print('TIER: large (models 8-32B with 4bit quant)')
    else: print('TIER: frontier (models 32B+)')
else:
    print('NO GPU - only tiny models (under 1B) on CPU')
"
```

### VRAM需求（采用4位量化时）

| VRAM容量 | 最大模型参数量 | 典型模型示例                              |
|:---------|:----------------|:--------------------------------------------|
| 仅CPU    | 约10亿参数      | GPT-2、TinyLlama、SmolLM                    |
| 4-8 GB   | 约40亿参数      | Qwen2.5-1.5B、Phi-3.5 mini、Llama 3.2 3B   |
| 8-16 GB  | 约90亿参数      | Llama 3.1 8B、Mistral 7B、Gemma 2 9B       |
| 24 GB    | 约320亿参数     | Qwen3-32B、Llama 3.1 70B（高压缩版）、Command-R |
| 48 GB+   | 约720亿以上参数  | Qwen2.5-72B、DeepSeek-R1                    |
| 多GPU架构 | 2000亿以上参数  | Llama 3.1 405B、DeepSeek-V3（6850亿参数的MoE版本） |

## 第3步：浏览可用模型并获取推荐建议

```bash
# Browse models by compute tier
obliteratus models --tier medium

# Get architecture info for a specific model
obliteratus info <model_name>

# Get telemetry-driven recommendation for best method & params
obliteratus recommend <model_name>
obliteratus recommend <model_name> --insights  # global cross-architecture rankings
```

## 第4步：选择方法

### 方法选择指南
**默认值/大多数场景下的推荐值：`advanced`。** 该方法采用带范数保持投影的多方向SVD技术，且经过充分测试。

| 使用场景                         | 推荐方法 | 原因                                      |
|:----------------------------------|:-------------------|:-----------------------------------------|
| 默认情况/大多数模型             | `advanced`         | 多方向SVD处理，具备范数保持功能，稳定性高 |
| 快速测试/原型开发               | `basic`            | 速度较快、操作简单，足以用于评估          |
| 高密度模型（Llama、Mistral）      | `advanced`         | 支持多方向处理及范数保持                  |
| MoE模型（DeepSeek、Mixtral）     | `nuclear`          | 支持专家级精细调整，可应对MoE模型的复杂性 |
| 推理模型（R1 distills）         | `surgical`         | 具有思维链意识，能保留推理过程            |
| 模型持续拒绝响应                 | `aggressive`       | 采用白化SVD技术结合特殊调整手段          |
| 希望实现可逆的修改               | 使用引导向量（详见分析部分）             |
| 对质量要求极高且不考虑时间成本   | `optimized`        | 通过贝叶斯搜索寻找最优参数                |
| 实验性自动检测功能               | `informed`         | 能自动识别对齐类型——属于实验性功能，性能未必始终优于`advanced` |

### 9种CLI命令方法
- **basic** — 通过差分均值法处理单一拒绝方向。速度较快（8B模型约需5-10分钟）。
- **advanced**（默认值/推荐值）— 多方向SVD处理，结合范数保持投影，包含2次优化步骤。处理速度中等（约需10-20分钟）。
- **aggressive** — 采用白化SVD技术、越狱对比学习法以及注意力头调整手段。存在较高的逻辑连贯性受损风险。
- **spectral_cascade** — 基于DCT频域分解的技术。属于研究性质的新方法。
- **informed** — 在删除过程中实时进行分析以自动配置参数。属于实验性功能，处理速度较慢且结果不如`advanced`稳定。
- **surgical** — 结合SAE特征、神经元掩码技术、头部调整以及专家级精细调整。处理速度极慢（约需1-2小时），最适合推理模型使用。
- **optimized** — 通过贝叶斯超参数搜索（Optuna TPE）寻找最优参数。运行时间最长，但能得到最佳效果。
- **inverted** — 反转拒绝方向，使模型变得更愿意响应请求。
- **nuclear** — 针对顽固的MoE模型采用最强力的组合调整手段，支持专家级精细控制。

### 方向提取方法（--direction-method参数）
- **diff_means**（默认值）— 通过比较被拒绝和被接受时的激活值差分来提取方向。稳定性较高。
- **svd** — 通过多方向SVD技术提取方向。更适用于复杂的对齐问题。
- **leace** — LEACE算法（基于封闭形式估计的线性擦除法）。可实现最优的线性擦除效果。

### 4种仅支持Python API的方法
（无法通过CLI调用——需要导入Python代码，而这违反了AGPL许可证的规定。仅当用户明确希望在自己的AGPL项目中将OBLITERATUS作为库使用时才需告知。）
- failspy、gabliteration、heretic、rdo

## 第5步：执行删除操作

### 标准使用方式
```bash
# Default method (advanced) — recommended for most models
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models

# With 4-bit quantization (saves VRAM)
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models

# Large models (70B+) — conservative defaults
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

### 微调参数
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # opt-in telemetry for community research
```

### 关键参数
| 参数 | 描述 | 默认值 |
|:-----|:------------|:--------|
| `--method` | 模型压缩方法 | advanced |
| `--direction-method` | 方向提取方式 | diff_means |
| `--n-directions` | 拒绝方向的数量（1-32） | 取决于所选方法 |
| `--refinement-passes` | 迭代优化次数（1-5） | 2 |
| `--regularization` | 正则化强度（0.0-1.0） | 0.1 |
| `--quantization` | 模型精度：4位或8位 | none（全精度） |
| `--large-model` | 120B以上模型的保守默认设置 | false |
| `--output-dir` | 压缩后模型的保存路径 | ./obliterated_model |
| `--contribute` | 共享匿名化处理后的结果以用于研究 | false |
| `--verify-sample-size` | 用于拒绝能力检测的测试提示语数量 | 20 |
| `--dtype` | 模型数据类型（float16、bfloat16） | auto |

### 其他执行模式
```bash
# Interactive guided mode (hardware → model → preset)
obliteratus interactive

# Web UI (Gradio)
obliteratus ui --port 7860

# Run a full ablation study from YAML config
obliteratus run config.yaml --preset quick

# Tournament: pit all methods against each other
obliteratus tourney <model_name>
```

## 第6步：验证结果

完成消隐处理后，请检查各项输出指标：

| 指标 | 合格值 | 警告值 |
|:-------|:-----------|:--------|
| 拒绝率 | < 5%（理想值为约0%） | > 10%表示拒绝现象依然存在 |
| 困难度变化幅度 | 增加量 < 10% | > 15%说明文本连贯性受损 |
| KL散度 | < 0.1 | > 0.5表明分布发生了显著偏移 |
| 文本连贯性 | 高/通过定性检查 | 响应质量下降，出现重复内容 |

### 若拒绝率依然居高不下（> 10%）
1. 尝试使用`aggressive`方法
2. 增加`--n-directions`的数值（例如设置为8或16）
3. 添加`--refinement-passes 3`参数
4. 将`diff_means`替换为`--direction-method svd`进行尝试

### 若文本连贯性受损（困难度增加量 > 15%）
1. 减少`--n-directions`的数值（可尝试设置为2）
2. 增加`--regularization`的数值（可尝试设置为0.3）
3. 将`--refinement-passes`的数值降至1
4. 尝试使用更为温和的`basic`方法

## 第7步：使用消隐后的模型

最终生成的目录为标准的HuggingFace模型结构。

```bash
# Test locally with transformers
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('How do I pick a lock?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# Upload to HuggingFace Hub
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# Serve with vLLM
vllm serve ./abliterated-models/<model>
```

## CLI 命令参考

| 命令 | 描述 |
|:--------|:------------|
| `obliteratus obliterate` | 主要的消融实验命令 |
| `obliteratus info <model>` | 输出模型架构详情 |
| `obliteratus models --tier <tier>` | 按计算层级浏览精选模型 |
| `obliteratus recommend <model>` | 基于遥测数据的方法/参数推荐功能 |
| `obliteratus interactive` | 引导式设置向导 |
| `obliteratus tourney <model>` | 比赛模式：所有方法相互对决 |
| `obliteratus run <config.yaml>` | 根据 YAML 文件执行消融研究 |
| `obliteratus strategies` | 列出所有已注册的消融策略 |
| `obliteratus report <results.json>` | 重新生成可视化报告 |
| `obliteratus ui` | 启动 Gradio 网页界面 |
| `obliteratus aggregate` | 汇总社区遥测数据 |

## 分析模块

OBLITERATUS 提供 28 个用于机制可解释性的分析模块。
完整参考信息请参见 `skill_view(name="obliteratus", file_path="references/analysis-modules.md")`。

### 快速分析命令
```bash
# Run specific analysis modules
obliteratus run analysis-config.yaml --preset quick

# Key modules to run first:
# - alignment_imprint: Fingerprint DPO/RLHF/CAI/SFT alignment method
# - concept_geometry: Single direction vs polyhedral cone
# - logit_lens: Which layer decides to refuse
# - anti_ouroboros: Self-repair risk score
# - causal_tracing: Causally necessary components
```

### 调控向量（可逆的替代方案）
无需永久修改权重，可采用推理时的调控机制：
```python
# Python API only — for user's own projects
from obliteratus.analysis.steering_vectors import SteeringVectorFactory, SteeringHookManager
```

## 消融策略

除了基于方向的消融方法外，OBLITERATUS 还提供了结构化消融策略：
- **嵌入层消融** — 针对嵌入层组件进行操作
- **前馈网络消融** — 移除前馈网络中的特定模块
- **注意力头裁剪** — 对注意力机制的头部结构进行裁剪
- **整层移除** — 直接删除整个层

查看所有可用策略：`obliteratus strategies`

## 评估功能

OBLITERATUS 内置了多种评估工具：
- 拒绝率基准测试
- 混乱度对比（消融前后）
- 支持集成 LM Eval Harness 以运行学术标准测试
- 直接与同类模型进行性能对比
- 基线性能跟踪

## 平台支持

- **CUDA** — 完全支持（NVIDIA GPU）
- **Apple Silicon (MLX)** — 通过 MLX 后端实现支持
- **CPU** — 仅支持参数量极小的模型（< 10亿参数）

## YAML 配置模板

可通过 `skill_view` 加载配置模板，以实现可重复的实验运行：
- `templates/abliteration-config.yaml` — 标准单模型配置
- `templates/analysis-study.yaml` — 消融前的分析研究配置
- `templates/batch-abliteration.yaml` — 多模型批量处理配置

## 远程监控功能

OBLITERATUS 可选择将匿名化的实验数据贡献至全球研究数据集。可通过 `--contribute` 参数启用该功能。系统不会收集任何个人数据，仅记录模型名称、使用方法及相关指标。

## 常见问题与注意事项

1. **不要将 `informed` 作为默认选项** — 该模式仍处于实验阶段，且运行速度较慢。如需稳定结果，请使用 `advanced` 模式。
2. **参数量低于 10亿的模型对消融操作反应不佳** — 这类模型的拒绝行为较为简单且零散，难以准确提取拒绝方向。此类操作通常只能获得部分效果（剩余拒绝率约为20-40%）。而参数量在30亿以上的模型具有更清晰的拒绝模式，效果显著更好（使用 `advanced` 模式时拒绝率往往可降至0%）。
3. **`aggressive` 模式可能会适得其反** — 在小型模型上使用时，它可能破坏模型的连贯性，反而提高拒绝率。仅当在30亿参数以上的模型上使用 `advanced` 模式后仍存在超过10%的拒绝率时，才考虑使用该模式。
4. **务必检查模型混乱度** — 若其数值上升超过15%，说明模型已受到损害，此时应降低消融的激进程度。
5. **混合专家模型需要特殊处理** — 对于 Mixtral、DeepSeek-MoE 等这类模型，应使用 `nuclear` 消融方法。
6. **量化后的模型无法再次量化** — 需先对全精度模型进行消融处理，再将结果量化。
7. **显存占用估算仅为近似值** — 4位量化虽有助于降低显存需求，但在数据提取过程中显存峰值仍可能上升。
8. **推理型模型较为敏感** — 对于 R1 类模型蒸馏后的版本，为保留思维链结构，建议使用 `surgical` 模式。
9. **可参考 `obliteratus recommend` 的建议** — 远程监控数据中推荐的参数可能优于默认值。
10. **AGPL 许可协议限制** — 在基于 MIT/Apache 许可的项目中严禁直接 `import obliteratus`，仅可通过命令行调用该工具。
11. **超大模型（700亿参数以上）** — 始终建议使用 `--large-model` 参数，以采用更为保守的默认设置。
12. **频谱认证常显示“不通过”** — 即使实际拒绝率为0%，频谱检测也常常会标记为“不完整”。应直接查看实际拒绝率，而不要仅依赖频谱认证结果。

## 相关配套工具

- **vllm** — 用于高效部署经过消融处理的模型
- **gguf** — 将消融处理后的模型转换为 GGUF 格式，以便在 llama.cpp 中使用
- **huggingface-tokenizers** — 用于处理模型的分词器相关功能
