---
title: "Slime Rl Training — Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework"
sidebar_label: "Slime Rl Training"
description: "Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Slime Rl Training

该技能提供了使用 Megatron+SGLang 框架 slime 对大语言模型进行强化学习后训练的指导。适用于训练 GLM 模型、实现自定义数据生成流程，或需要在强化学习训练中实现与 Megatron-LM 的深度集成以提升效率的场景。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/slime` 安装 |
| 路径 | `optional-skills/mlops/slime` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `sglang-router>=0.2.3`, `ray`, `torch>=2.0.0`, `transformers>=4.40.0` |
| 支持平台 | linux, macos |
| 标签 | `强化学习`, `Megatron-LM`, `SGLang`, `GRPO`, `训练后优化`, `GLM` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能启用时，智能体将看到这些内容作为操作指令。
:::

# slime：用于强化学习训练优化的 LLM 后训练框架

slime 是来自清华大学 THUDM 团队开发的LLM后训练框架，已被用于 GLM-4.5、GLM-4.6 和 GLM-4.7 模型的训练。它将用于训练的 Megatron-LM 与用于高效模型部署生成的 SGLang 相结合。

## 何时使用 slime

**以下情况可选择 slime：**
- 需要在 Megatron-LM 原生训练的基础上搭配 SGLang 进行推理
- 需要具备灵活数据缓冲功能的自定义数据生成流程
- 需要训练 GLM、Qwen3、DeepSeek V3 或 Llama 3 等模型
- 需要兼具研究级功能与生产环境支持（由 Z.ai 提供）的框架

**以下情况可考虑其他替代方案：**
- 需要企业级稳定性功能 → 可使用 **miles**
- 需要灵活更换后端架构 → 可使用 **verl**
- 需要 PyTorch 原生抽象层功能 → 可使用 **torchforge**

## 核心功能

- **训练**：支持全并行度的 Megatron-LM 训练（TP、PP、DP、SP 模式）
- **模型部署**：基于 SGLang 的高效生成机制，并配有路由器功能
- **数据管理**：灵活的提示词管理与样本存储功能
- **支持的模型**：GLM-4.x、Qwen3、DeepSeek V3/R1、Llama 3

## 架构概览

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────┐
│                    Data Buffer                          │
│ - Prompt initialization and management                  │
│ - Custom data generation and filtering                  │
│ - Rollout sample storage                                │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
┌─────────────▼───────────┐ ┌─────────────▼───────────────┐
│ Training (Megatron-LM)  │ │ Rollout (SGLang + Router)   │
│ - Actor model training  │ │ - Response generation       │
│ - Critic (optional)     │ │ - Reward/verifier output    │
│ - Weight sync to rollout│ │ - Multi-turn support        │
└─────────────────────────┘ └─────────────────────────────┘
```
## 安装

请完整翻译输入内容，切勿提前终止。

```bash
# Recommended: Docker
docker pull slimerl/slime:latest
docker run --rm --gpus all --ipc=host --shm-size=16g \
  -it slimerl/slime:latest /bin/bash

# Inside container
cd /root/slime && pip install -e . --no-deps
```

### 来源端

```bash
git clone https://github.com/THUDM/slime.git
cd slime
pip install -r requirements.txt
pip install -e .
```

## 快速入门：GRPO训练

```bash
# Source model configuration
source scripts/models/qwen3-4B.sh

# Launch training
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 4 \
    --rollout-num-gpus 4 \
    --advantage-estimator grpo \
    --use-kl-loss --kl-loss-coef 0.001 \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --prompt-data /path/to/data.jsonl \
    ${MODEL_ARGS[@]} ${CKPT_ARGS[@]}
```

## 工作流 1：标准 GRPO 训练

此工作流用于训练具备群体相对优势的推理模型。

### 前提条件清单
- [ ] 已安装 Docker 环境或 Megatron-LM + SGLang
- [ ] 模型检查点（HuggingFace 或 Megatron 格式）
- [ ] JSONL 格式的训练数据

### 第 1 步：准备数据

```python
# data.jsonl format
{"prompt": "What is 2 + 2?", "label": "4"}
{"prompt": "Solve: 3x = 12", "label": "x = 4"}
```

或者以聊天格式进行：
```python
{
    "prompt": [
        {"role": "system", "content": "You are a math tutor."},
        {"role": "user", "content": "What is 15 + 27?"}
    ],
    "label": "42"
}
```

### 第 2 步：配置模型

选择预配置好的模型脚本：

```bash
# List available models
ls scripts/models/
# glm4-9B.sh, qwen3-4B.sh, qwen3-30B-A3B.sh, deepseek-v3.sh, llama3-8B.sh, ...

# Source your model
source scripts/models/qwen3-4B.sh
```

### 第3步：启动训练

```bash
python train.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --advantage-estimator grpo \
    --use-kl-loss \
    --kl-loss-coef 0.001 \
    --prompt-data /path/to/train.jsonl \
    --input-key prompt \
    --label-key label \
    --apply-chat-template \
    --rollout-batch-size 32 \
    --n-samples-per-prompt 8 \
    --global-batch-size 256 \
    --num-rollout 3000 \
    --save-interval 100 \
    --eval-interval 50 \
    ${MODEL_ARGS[@]}
```

### 第4步：监控训练过程
- [ ] 查看TensorBoard日志：`tensorboard --logdir outputs/`
- [ ] 确认奖励曲线呈上升趋势
- [ ] 监控各节点的GPU使用率

---

## 工作流2：异步训练

通过并行执行推理与训练操作，利用异步模式提升处理效率。

### 适用场景
- 生成时间较长的大型模型
- 同步模式下GPU空闲时间较多
- 拥有足够内存用于缓冲数据

### 启动异步训练

```bash
python train_async.py \
    --actor-num-nodes 1 \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --advantage-estimator grpo \
    --async-buffer-size 4 \
    --prompt-data /path/to/train.jsonl \
    ${MODEL_ARGS[@]}
```

### 异步任务专用参数

```bash
--async-buffer-size 4        # Number of rollouts to buffer
--update-weights-interval 2  # Sync weights every N rollouts
```

## 工作流 3：多轮智能体训练

此工作流适用于需要具备工具使用能力或多步骤推理能力的智能体训练。

### 先决条件
- [ ] 用于实现多轮逻辑的自定义生成函数
- [ ] 工具/环境接口

### 第 1 步：定义自定义生成函数

```python
# custom_generate.py
async def custom_generate(args, samples, evaluation=False):
    """Multi-turn generation with tool calling."""
    for sample in samples:
        conversation = sample.prompt

        for turn in range(args.max_turns):
            # Generate response
            response = await generate_single(conversation)

            # Check for tool call
            tool_call = extract_tool_call(response)
            if tool_call:
                tool_result = execute_tool(tool_call)
                conversation.append({"role": "assistant", "content": response})
                conversation.append({"role": "tool", "content": tool_result})
            else:
                break

        sample.response = response
        sample.reward = compute_reward(sample)

    return samples
```

### 第二步：使用自定义功能启动代理

```bash
python train.py \
    --custom-generate-function-path custom_generate.py \
    --max-turns 5 \
    --prompt-data /path/to/agent_data.jsonl \
    ${MODEL_ARGS[@]}
```

如需查看完整的多轮搜索示例，请参阅 `examples/search-r1/`。

---

## 配置参考

### 三种参数类别

Slime 使用三种类型的参数：

**1. Megatron 参数**（直接传递）：
```bash
--tensor-model-parallel-size 2
--pipeline-model-parallel-size 1
--num-layers 32
--hidden-size 4096
```

**2. SGLang 参数**（以 `--sglang-` 为前缀）：
```bash
--sglang-mem-fraction-static 0.8
--sglang-context-length 8192
--sglang-log-level INFO
```

**3. slime 参数**：
```bash
# Resource allocation
--actor-num-nodes 1
--actor-num-gpus-per-node 8
--rollout-num-gpus 8
--colocate  # Share GPUs between training/inference

# Data
--prompt-data /path/to/data.jsonl
--input-key prompt
--label-key label

# Training loop
--num-rollout 3000
--rollout-batch-size 32
--n-samples-per-prompt 8
--global-batch-size 256

# Algorithm
--advantage-estimator grpo  # or: gspo, ppo, reinforce_plus_plus
--use-kl-loss
--kl-loss-coef 0.001
```

### 关键约束条件

```
rollout_batch_size × n_samples_per_prompt = global_batch_size × num_steps_per_rollout
```

示例：32 × 8 = 256 × 1

---

## 数据缓冲系统

Slime 的数据缓冲功能可实现灵活的数据管理：

### 基本数据源

```python
class RolloutDataSource:
    def get_samples(self, num_samples):
        """Fetch prompts from dataset."""
        return self.dataset.sample(num_samples)

    def add_samples(self, samples):
        """Called after generation (no-op by default)."""
        pass
```

### 缓冲数据源（离线模式）

```python
class RolloutDataSourceWithBuffer(RolloutDataSource):
    def __init__(self):
        self.buffer = []

    def add_samples(self, samples):
        """Store generated samples for reuse."""
        self.buffer.extend(samples)

    def buffer_filter(self, args, buffer, num_samples):
        """Custom selection logic (prioritized, stratified, etc.)."""
        return select_best(buffer, num_samples)
```

## 常见问题与解决方案

### 问题：SGLang 引擎崩溃

**症状**：推理引擎在训练过程中突然停止运行

**解决方案**：
```bash
# Enable fault tolerance
--use-fault-tolerance

# Increase memory allocation
--sglang-mem-fraction-static 0.85

# Reduce batch size
--rollout-batch-size 16
```

### 问题：权重同步超时

**症状**：部署完成后训练进程挂起

**解决方案**：
```bash
# Increase sync interval
--update-weights-interval 5

# Use colocated mode (no network transfer)
--colocate
```

### 问题：训练过程中出现内存不足

**症状**：在反向传播阶段出现 CUDA 内存不足的情况

**解决方案**：
```bash
# Enable gradient checkpointing
--recompute-activations

# Reduce micro-batch size
--micro-batch-size 1

# Enable sequence parallelism
--sequence-parallel
```

### 问题：数据加载速度缓慢

**症状**：在数据获取过程中GPU处于空闲状态

**解决方案**：
```bash
# Increase data workers
--num-data-workers 4

# Use streaming dataset
--streaming-data
```

## 支持的模型

| 模型系列 | 配置选项 |
|----------|----------|
| GLM | GLM-4.5、GLM-4.6、GLM-4.7、GLM-Z1-9B |
| Qwen | Qwen3（4B、8B、30B-A3B）、Qwen3-MoE、Qwen2.5 |
| DeepSeek | V3、V3.1、R1 |
| Llama | Llama 3（8B、70B） |
| 其他 | Kimi K2、Moonlight-16B |

所有模型在 `scripts/models/` 目录下均配有预配置脚本。

---

## 进阶主题

### 共享部署模式

通过在训练与推理之间共享 GPU 来降低内存占用：

```bash
python train.py \
    --colocate \
    --actor-num-gpus-per-node 8 \
    --sglang-mem-fraction-static 0.4 \
    ${MODEL_ARGS[@]}
```

### 自定义奖励模型

```python
# custom_rm.py
class CustomRewardModel:
    def __init__(self, model_path):
        self.model = load_model(model_path)

    def compute_reward(self, prompts, responses):
        inputs = self.tokenize(prompts, responses)
        scores = self.model(inputs)
        return scores.tolist()
```

```bash
--custom-rm-path custom_rm.py
```

### 多任务评估功能

```bash
--eval-prompt-data aime /path/to/aime.jsonl \
--eval-prompt-data gsm8k /path/to/gsm8k.jsonl \
--n-samples-per-eval-prompt 16
```

## 资源

- **文档**：https://thudm.github.io/slime/
- **GitHub 仓库**：https://github.com/THUDM/slime
- **博客文章**：https://lmsys.org/blog/2025-07-09-slime/
- **示例代码**：请查看 `examples/` 目录，其中包含 14 个以上可运行的示例。
