# 量化指南

## 目录
- 量化方法对比
- AWQ 的设置与使用
- GPTQ 的设置与使用
- FP8 量化（H100）
- 模型准备
- 精度与压缩度的权衡

## 量化方法对比

| 方法 | 压缩率 | 精度损失 | 速度 | 最佳适用场景 |
|------|--------|-----------|------|--------------|
| **AWQ** | 4位（75%） | <1% | 快 | 70B级模型，生产环境 |
| **GPTQ** | 4位（75%） | 1-2% | 快 | 广泛的模型支持 |
| **FP8** | 8位（50%） | <0.5% | 最快 | 仅适用于H100 GPU |
| **SqueezeLLM** | 3-4位（75-80%） | 2-3% | 中等 | 极高压缩率需求 |

**推荐方案**：
- **生产环境**：对于70B级模型，使用AWQ
- **H100 GPU**：为获得最佳速度，使用FP8
- **最大兼容性**：选择GPTQ
- **极高压缩需求**：使用SqueezeLLM

## AWQ 的设置与使用

**AWQ**（基于激活值的权重量化）在4位量化下能实现最佳精度。

**步骤1：查找预量化模型**

在HuggingFace上搜索AWQ相关的模型：
```bash
# Example: TheBloke/Llama-2-70B-AWQ
# Example: TheBloke/Mixtral-8x7B-Instruct-v0.1-AWQ
```

**第2步：使用AWQ启动**

```bash
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95
```

**内存节省**：
```
Llama 2 70B fp16: 140GB VRAM (4x A100 needed)
Llama 2 70B AWQ: 35GB VRAM (1x A100 40GB)
= 4x memory reduction
```

**第3步：验证性能**

检查输出结果是否合格：
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

# Test complex reasoning
response = client.chat.completions.create(
    model="TheBloke/Llama-2-70B-AWQ",
    messages=[{"role": "user", "content": "Explain quantum entanglement"}]
)

print(response.choices[0].message.content)
# Verify quality matches your requirements
```

**自行量化模型**（需配备 80GB 以上显存的 GPU）：

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "meta-llama/Llama-2-70b-hf"
quant_path = "llama-2-70b-awq"

# Load model
model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Quantize
quant_config = {"zero_point": True, "q_group_size": 128, "w_bit": 4}
model.quantize(tokenizer, quant_config=quant_config)

# Save
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
```

## GPTQ 的配置与使用方法

**GPTQ** 支持的最模型种类最为丰富，且具备出色的压缩效果。

**步骤 1：查找 GPTQ 模型**

```bash
# Example: TheBloke/Llama-2-13B-GPTQ
# Example: TheBloke/CodeLlama-34B-GPTQ
```

**第2步：使用GPTQ启动**

```bash
vllm serve TheBloke/Llama-2-13B-GPTQ \
  --quantization gptq \
  --dtype float16
```

**GPTQ 配置选项**：
```bash
# Specify GPTQ parameters if needed
vllm serve MODEL \
  --quantization gptq \
  --gptq-act-order \  # Activation ordering
  --dtype float16
```

**自定义模型量化**：

```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

model_name = "meta-llama/Llama-2-13b-hf"
quantized_name = "llama-2-13b-gptq"

# Load model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoGPTQForCausalLM.from_pretrained(model_name, quantize_config)

# Prepare calibration data
calib_data = [...]  # List of sample texts

# Quantize
quantize_config = BaseQuantizeConfig(
    bits=4,
    group_size=128,
    desc_act=True
)
model.quantize(calib_data)

# Save
model.save_quantized(quantized_name)
```

## FP8量化（H100）

**FP8**（8位浮点格式）能够在H100显卡上实现最佳运行速度，同时仅带来极小的精度损失。

**系统要求**：
- H100或H800显卡
- CUDA 12.3及以上版本（推荐12.8）
- 支持Hopper架构

**步骤1：启用FP8功能**

```bash
vllm serve meta-llama/Llama-3-70B-Instruct \
  --quantization fp8 \
  --tensor-parallel-size 2
```

**在 H100 上的性能提升**：
```
fp16: 180 tokens/sec
FP8: 320 tokens/sec
= 1.8x speedup
```

**步骤 2：验证精度**

FP8 数据格式的精度损失通常低于 0.5%：
```python
# Run evaluation suite
# Compare FP8 vs FP16 on your tasks
# Verify acceptable accuracy
```

**动态 FP8 量化**（无需预量化模型）：

```bash
# vLLM automatically quantizes at runtime
vllm serve MODEL --quantization fp8
# No model preparation required
```

## 模型准备

**预量化模型（最简单）**：

1. 在 HuggingFace 上搜索：`[模型名称] AWQ` 或 `[模型名称] GPTQ`
2. 直接下载或使用现有资源：`TheBloke/[模型名称]-AWQ`
3. 使用相应的 `--quantization` 参数启动模型

**自行对模型进行量化**：

**AWQ**：
```bash
# Install AutoAWQ
pip install autoawq

# Run quantization script
python quantize_awq.py --model MODEL --output OUTPUT
```

**GPTQ**：  
Hermes Agent 的技术文档、命令行使用指南、智能体功能、插件、提供程序以及开发者指南。
```bash
# Install AutoGPTQ
pip install auto-gptq

# Run quantization script
python quantize_gptq.py --model MODEL --output OUTPUT
```

**校准数据**：
- 使用来自目标领域的128至512个多样化示例
- 需能代表实际应用中的输入数据
- 校准质量越高，精度越好

## 精度与压缩之间的权衡

**实证结果**（基于Llama 2 70B模型在MMLU基准测试上的表现）：

| 量化格式 | 精度 | 内存占用 | 运行速度 | 是否适合生产环境 |
|----------|------|----------|----------|------------------|
| FP16（基准值） | 100% | 140GB | 1.0倍 | ✅（若有足够内存） |
| FP8 | 99.5% | 70GB | 1.8倍 | ✅（仅支持H100芯片） |
| AWQ 4位 | 99.0% | 35GB | 1.5倍 | ✅（70B模型最佳选择） |
| GPTQ 4位 | 98.5% | 35GB | 1.5倍 | ✅（兼容性良好） |
| SqueezeLLM 3位 | 96.0% | 26GB | 1.3倍 | ⚠️（需检测精度是否达标） |

**各量化格式的适用场景**：

**不进行量化（使用FP16）**：
- GPU内存充足
- 需要达到最高精度
- 模型参数量小于130亿

**FP8格式**：
- 使用H100/H800芯片
- 在尽可能减少精度损失的前提下追求最快运行速度
- 用于生产环境部署

**AWQ 4位格式**：
- 需要将70B模型加载到40GB内存的GPU中
- 用于生产环境部署
- 可接受1%以内的精度损失

**GPTQ 4位格式**：
- 需要支持多种模型类型
- 不使用H100芯片（此时建议选择FP8格式）
- 可接受1-2%的精度损失

**测试策略**：

1. **建立基准**：在评估数据集上测量FP16格式的模型精度
2. **进行量化**：生成量化后的模型版本
3. **性能评估**：在相同任务下对比量化后模型与基准模型的表现
4. **决策判断**：若精度下降幅度低于预设阈值（通常为1-2%），则该版本可用

**示例评估流程**：
```python
from evaluate import load_evaluation_suite

# Run on FP16 baseline
baseline_score = evaluate(model_fp16, eval_suite)

# Run on quantized
quant_score = evaluate(model_awq, eval_suite)

# Compare
degradation = (baseline_score - quant_score) / baseline_score * 100
print(f"Accuracy degradation: {degradation:.2f}%")

# Decision
if degradation < 1.0:
    print("✅ Quantization acceptable for production")
else:
    print("⚠️ Review accuracy loss")
```
