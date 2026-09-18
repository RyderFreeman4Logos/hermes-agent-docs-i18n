---
name: evaluating-llms-harness
description: "lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.)."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [lm-eval, transformers, vllm]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Evaluation, LM Evaluation Harness, Benchmarking, MMLU, HumanEval, GSM8K, EleutherAI, Model Quality, Academic Benchmarks, Industry Standard]

---

# lm-evaluation-harness - 大语言模型基准测试工具

## 功能概述

该工具可基于60多种学术基准（如MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）对大语言模型进行评估。适用于模型质量检测、模型对比、学术成果汇报以及训练进度跟踪等场景。目前已被EleutherAI、HuggingFace及众多顶尖研究实验室视为行业标准工具，同时支持HuggingFace、vLLM及各类API接口。

## 快速入门

lm-evaluation-harness通过标准化的提示词与评估指标，能够基于60多种学术基准对大语言模型进行全面评测。

**安装方式**：
```bash
pip install lm-eval
```

**评估任意 HuggingFace 模型**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag \
  --device cuda:0 \
  --batch_size 8
```

**查看可用任务**：
```bash
lm-eval ls tasks
```

## 常见工作流程

### 工作流程 1：标准基准测试评估

在核心基准测试（MMLU、GSM8K、HumanEval）上对模型进行评估。

复制此检查清单：

```
Benchmark Evaluation:
- [ ] Step 1: Choose benchmark suite
- [ ] Step 2: Configure model
- [ ] Step 3: Run evaluation
- [ ] Step 4: Analyze results
```

**步骤 1：选择基准测试套件**

**核心推理类基准测试**：
- **MMLU**（大规模多任务语言理解）——包含57个题目，采用多项选择形式
- **GSM8K**——小学数学应用题
- **HellaSwag**——常识推理
- **TruthfulQA**——真实性与事实性判断
- **ARC**（AI2推理挑战）——科学相关问题

**代码类基准测试**：
- **HumanEval**——Python代码生成（共164道题目）
- **MBPP**（基础Python问题集）——Python编程能力测试

**标准套件**（推荐用于模型发布）：
```bash
--tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge
```

**步骤 2：配置模型**

**HuggingFace 模型**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,dtype=bfloat16 \
  --tasks mmlu \
  --device cuda:0 \
  --batch_size auto  # Auto-detect optimal batch size
```

**量化模型（4位/8位）**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,load_in_4bit=True \
  --tasks mmlu \
  --device cuda:0
```

**自定义检查点**：
```bash
lm_eval --model hf \
  --model_args pretrained=/path/to/my-model,tokenizer=/path/to/tokenizer \
  --tasks mmlu \
  --device cuda:0
```

**步骤 3：运行评估**

```bash
# Full MMLU evaluation (57 subjects)
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --num_fewshot 5 \  # 5-shot evaluation (standard)
  --batch_size 8 \
  --output_path results/ \
  --log_samples  # Save individual predictions

# Multiple benchmarks at once
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge \
  --num_fewshot 5 \
  --batch_size 8 \
  --output_path results/llama2-7b-eval.json
```

**第4步：分析结果**

结果已保存至 `results/llama2-7b-eval.json` 文件中：

```json
{
  "results": {
    "mmlu": {
      "acc": 0.459,
      "acc_stderr": 0.004
    },
    "gsm8k": {
      "exact_match": 0.142,
      "exact_match_stderr": 0.006
    },
    "hellaswag": {
      "acc_norm": 0.765,
      "acc_norm_stderr": 0.004
    }
  },
  "config": {
    "model": "hf",
    "model_args": "pretrained=meta-llama/Llama-2-7b-hf",
    "num_fewshot": 5
  }
}
```

### 工作流 2：跟踪训练进度

在训练过程中对检查点进行评估。

```
Training Progress Tracking:
- [ ] Step 1: Set up periodic evaluation
- [ ] Step 2: Choose quick benchmarks
- [ ] Step 3: Automate evaluation
- [ ] Step 4: Plot learning curves
```

**步骤 1：设置定期评估机制**

每隔 N 次训练步骤进行一次评估：

```bash
#!/bin/bash
# eval_checkpoint.sh

CHECKPOINT_DIR=$1
STEP=$2

lm_eval --model hf \
  --model_args pretrained=$CHECKPOINT_DIR/checkpoint-$STEP \
  --tasks gsm8k,hellaswag \
  --num_fewshot 0 \  # 0-shot for speed
  --batch_size 16 \
  --output_path results/step-$STEP.json
```

**步骤 2：选择快速基准测试**

适用于频繁评估的快速基准测试：
- **HellaSwag**：在 1 块 GPU 上运行约 10 分钟
- **GSM8K**：约 5 分钟
- **PIQA**：约 2 分钟

不推荐用于频繁评估（速度过慢）：
- **MMLU**：约 2 小时（包含 57 个问题）
- **HumanEval**：需要执行代码

**步骤 3：实现自动评估**

与训练脚本集成：

```python
# In training loop
if step % eval_interval == 0:
    model.save_pretrained(f"checkpoints/step-{step}")

    # Run evaluation
    os.system(f"./eval_checkpoint.sh checkpoints step-{step}")
```

或者可以使用 PyTorch Lightning 回调函数：

```python
from pytorch_lightning import Callback

class EvalHarnessCallback(Callback):
    def on_validation_epoch_end(self, trainer, pl_module):
        step = trainer.global_step
        checkpoint_path = f"checkpoints/step-{step}"

        # Save checkpoint
        trainer.save_checkpoint(checkpoint_path)

        # Run lm-eval
        os.system(f"lm_eval --model hf --model_args pretrained={checkpoint_path} ...")
```

**第4步：绘制学习曲线**

```python
import json
import matplotlib.pyplot as plt

# Load all results
steps = []
mmlu_scores = []

for file in sorted(glob.glob("results/step-*.json")):
    with open(file) as f:
        data = json.load(f)
        step = int(file.split("-")[1].split(".")[0])
        steps.append(step)
        mmlu_scores.append(data["results"]["mmlu"]["acc"])

# Plot
plt.plot(steps, mmlu_scores)
plt.xlabel("Training Step")
plt.ylabel("MMLU Accuracy")
plt.title("Training Progress")
plt.savefig("training_curve.png")
```

### 工作流 3：多模型对比

用于模型性能对比的基准测试套件。

```
Model Comparison:
- [ ] Step 1: Define model list
- [ ] Step 2: Run evaluations
- [ ] Step 3: Generate comparison table
```

**步骤 1：定义模型列表**

```bash
# models.txt
meta-llama/Llama-2-7b-hf
meta-llama/Llama-2-13b-hf
mistralai/Mistral-7B-v0.1
microsoft/phi-2
```

**步骤 2：运行评估**

```bash
#!/bin/bash
# eval_all_models.sh

TASKS="mmlu,gsm8k,hellaswag,truthfulqa"

while read model; do
    echo "Evaluating $model"

    # Extract model name for output file
    model_name=$(echo $model | sed 's/\//-/g')

    lm_eval --model hf \
      --model_args pretrained=$model,dtype=bfloat16 \
      --tasks $TASKS \
      --num_fewshot 5 \
      --batch_size auto \
      --output_path results/$model_name.json

done < models.txt
```

**第3步：生成对比表格**

```python
import json
import pandas as pd

models = [
    "meta-llama-Llama-2-7b-hf",
    "meta-llama-Llama-2-13b-hf",
    "mistralai-Mistral-7B-v0.1",
    "microsoft-phi-2"
]

tasks = ["mmlu", "gsm8k", "hellaswag", "truthfulqa"]

results = []
for model in models:
    with open(f"results/{model}.json") as f:
        data = json.load(f)
        row = {"Model": model.replace("-", "/")}
        for task in tasks:
            # Get primary metric for each task
            metrics = data["results"][task]
            if "acc" in metrics:
                row[task.upper()] = f"{metrics['acc']:.3f}"
            elif "exact_match" in metrics:
                row[task.upper()] = f"{metrics['exact_match']:.3f}"
        results.append(row)

df = pd.DataFrame(results)
print(df.to_markdown(index=False))
```

输出：
```
| Model                  | MMLU  | GSM8K | HELLASWAG | TRUTHFULQA |
|------------------------|-------|-------|-----------|------------|
| meta-llama/Llama-2-7b  | 0.459 | 0.142 | 0.765     | 0.391      |
| meta-llama/Llama-2-13b | 0.549 | 0.287 | 0.801     | 0.430      |
| mistralai/Mistral-7B   | 0.626 | 0.395 | 0.812     | 0.428      |
| microsoft/phi-2        | 0.560 | 0.613 | 0.682     | 0.447      |
```

### 工作流 4：使用 vLLM 进行评估（更快的推理速度）

通过采用 vLLM 后端，可实现快 5 到 10 倍的评估速度。

```
vLLM Evaluation:
- [ ] Step 1: Install vLLM
- [ ] Step 2: Configure vLLM backend
- [ ] Step 3: Run evaluation
```

**步骤 1：安装 vLLM**

```bash
pip install vllm
```

**步骤 2：配置 vLLM 后端**

```bash
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=1,dtype=auto,gpu_memory_utilization=0.8 \
  --tasks mmlu \
  --batch_size auto
```

**第3步：运行评估**

vLLM 的运行速度是传统 HuggingFace 方案的5到10倍：

```bash
# Standard HF: ~2 hours for MMLU on 7B model
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --batch_size 8

# vLLM: ~15-20 minutes for MMLU on 7B model
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=2 \
  --tasks mmlu \
  --batch_size auto
```

## 何时使用 lm-evaluation-harness 及其替代方案

**应在以下情况使用 lm-evaluation-harness：**
- 为学术论文进行模型基准测试
- 在标准任务中比较模型性能
- 跟踪训练进度
- 报告标准化指标（所有人使用相同的提示词）
- 需要可复现的评估结果

**可选择以下替代方案：**
- **HELM**（斯坦福大学）：涵盖更广泛的评估维度（公平性、效率、校准性）
- **AlpacaEval**：借助大语言模型作为评判者进行指令遵循能力评估
- **MT-Bench**：对话式多轮交互评估
- **自定义脚本**：针对特定领域的评估需求

## 常见问题

**问题：评估速度过慢**

建议使用 vLLM 后端：
```bash
lm_eval --model vllm \
  --model_args pretrained=model-name,tensor_parallel_size=2
```

或者减少少样本示例的数量：
```bash
--num_fewshot 0  # Instead of 5
```

或评估 MMLU 的子集：
```bash
--tasks mmlu_stem  # Only STEM subjects
```

**问题：内存不足**

请减小批次大小：
```bash
--batch_size 1  # Or --batch_size auto
```

使用量化功能：
```bash
--model_args pretrained=model-name,load_in_8bit=True
```

启用 CPU 卸载功能：
```bash
--model_args pretrained=model-name,device_map=auto,offload_folder=offload
```

**问题：结果与报告不符**

请检查少样本数量：
```bash
--num_fewshot 5  # Most papers use 5-shot
```

检查具体的任务名称：
```bash
--tasks mmlu  # Not mmlu_direct or mmlu_fewshot
```

验证模型与分词器是否匹配：
```bash
--model_args pretrained=model-name,tokenizer=same-model-name
```

**问题：HumanEval无法执行代码**

那些需要执行代码的任务（如HumanEval、MBPP等）都设有明确的确认机制——必须通过传递`--confirm_run_unsafe_code`参数才能运行它们。

```bash
lm_eval --model hf \
  --model_args pretrained=model-name \
  --tasks humaneval \
  --confirm_run_unsafe_code  # Required to run tasks that execute generated code
```

若未设置此标志，lm-eval 会拒绝执行任务，而不会默默跳过代码执行。

## 高级主题

**基准测试说明**：如需了解 60 多项任务的详细信息、其衡量指标及结果解读，请参阅 [references/benchmark-guide.md](references/benchmark-guide.md)。

**自定义任务**：如需创建针对特定领域的评估任务，请参考 [references/custom-tasks.md](references/custom-tasks.md)。

**API 模型评估**：如需对 OpenAI、Anthropic 及其他 API 模型进行评估，请参阅 [references/api-evaluation.md](references/api-evaluation.md)。

**多 GPU 策略**：如需了解数据并行与张量并行评估方法，请查看 [references/distributed-eval.md](references/distributed-eval.md)。

## 硬件要求

- **GPU**：NVIDIA（CUDA 11.8 及以上版本），在 CPU 上也可运行（但速度极慢）
- **显存**：
  - 7B 模型：16GB（bf16 格式）或 8GB（8 位格式）
  - 13B 模型：28GB（bf16 格式）或 14GB（8 位格式）
  - 70B 模型：需使用多 GPU 或进行量化处理
- **时间消耗**（以单台 A100 上的 7B 模型为例）：
  - HellaSwag：10 分钟
  - GSM8K：5 分钟
  - MMLU（完整版）：2 小时
  - HumanEval：20 分钟

## 资源链接

- GitHub 仓库：https://github.com/EleutherAI/lm-evaluation-harness
- 文档页面：https://github.com/EleutherAI/lm-evaluation-harness/tree/main/docs
- 任务库：包含 MMLU、GSM8K、HumanEval、TruthfulQA、HellaSwag、ARC、WinoGrande 等 60 多项任务
- 排名榜：https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard（该工具基于此框架构建）



