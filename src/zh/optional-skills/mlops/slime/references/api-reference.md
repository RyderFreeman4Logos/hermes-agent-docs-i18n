# slime API 参考手册

## 架构概览

slime 采用由 Ray 调度的三模块架构来运行：

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

## 核心数据结构

### 示例对象

`Sample` 对象是定义在 `slime/utils/types.py` 中的核心数据结构：

```python
from slime.utils.types import Sample

@dataclass
class Sample:
    # Core fields
    group_index: Optional[int]              # Group index for batching
    index: Optional[int]                    # Sample index
    prompt: str | list[dict] = ""           # Input prompt or chat history
    tokens: list[int] = field(default_factory=list)  # Token IDs
    response: str = ""                      # Generated response
    response_length: int = 0                # Response length in tokens
    label: Optional[str] = None             # Ground truth label
    reward: Optional[float | dict] = None   # RL reward signal
    loss_mask: Optional[list[int]] = None   # 1=compute loss, 0=mask
    status: Status = Status.PENDING         # Sample status
    metadata: dict = field(default_factory=dict)  # Custom data

    # Multimodal support
    multimodal_inputs: Optional[Any] = None       # Raw multimodal data (images, videos)
    multimodal_train_inputs: Optional[Any] = None # Processed multimodal data (pixel_values)

    # Rollout tracking
    weight_versions: list[str] = field(default_factory=list)
    rollout_log_probs: Optional[list[float]] = None    # Log probs from SGLang
    rollout_routed_experts: Optional[list[list[int]]] = None  # Expert routing (MoE)

    # Control fields
    remove_sample: bool = False
    generate_function_path: Optional[str] = None
    train_metadata: Optional[dict] = None
    non_generation_time: float = 0.0

    # Speculative decoding info (nested dataclass)
    @dataclass
    class SpecInfo:
        spec_accept_token_num: int = 0
        spec_draft_token_num: int = 0
        spec_verify_ct: int = 0
        completion_token_num: int = 0
```

### 状态枚举

```python
class Status(Enum):
    PENDING = "pending"           # Not yet processed
    COMPLETED = "completed"       # Successfully generated
    TRUNCATED = "truncated"       # Hit max length
    ABORTED = "aborted"           # Failed generation
    FAILED = "failed"             # Generation failed
```

## 配置系统

Slime 支持三类命令行参数：

### 1. Megatron 参数

所有 Megatron-LM 参数均可直接使用：

```bash
--tensor-model-parallel-size 2
--pipeline-model-parallel-size 1
--num-layers 32
--hidden-size 4096
--num-attention-heads 32
--seq-length 4096
--micro-batch-size 1
--global-batch-size 256
```

### 2. SGLang 参数

SGLang 参数的前缀为 `--sglang-`：

```bash
--sglang-mem-fraction-static 0.8   # GPU memory for KV cache
--sglang-context-length 8192       # Maximum context length
--sglang-log-level INFO            # Logging verbosity
--sglang-tp-size 2                 # Tensor parallelism
--sglang-disable-cuda-graph        # Disable CUDA graphs
```

### 3. slime专用参数

定义于`slime/utils/arguments.py`文件中：

```bash
# Resource Allocation
--actor-num-nodes 1                # Training nodes
--actor-num-gpus-per-node 8        # GPUs per training node
--rollout-num-gpus 8               # Total rollout GPUs
--rollout-num-gpus-per-engine 2    # GPUs per SGLang engine
--colocate                         # Share GPUs for train/inference

# Data Configuration
--prompt-data /path/to/data.jsonl  # Training data path
--input-key prompt                 # Key for prompts in JSON
--label-key label                  # Key for labels in JSON
--apply-chat-template              # Apply chat formatting

# Training Loop
--num-rollout 3000                 # Total rollout iterations
--rollout-batch-size 32            # Prompts per rollout
--n-samples-per-prompt 8           # Responses per prompt
--global-batch-size 256            # Training batch size
--num-steps-per-rollout 1          # Training steps per rollout

# RL Algorithm
--advantage-estimator grpo         # grpo, gspo, ppo, reinforce_plus_plus
--use-kl-loss                      # Enable KL loss
--kl-loss-coef 0.001               # KL coefficient
--calculate-per-token-loss         # Token-level loss

# Off-Policy Options
--use-tis                          # Truncated Importance Sampling
--tis-threshold 0.9                # TIS threshold
--true-on-policy-mode              # Force on-policy training
```

## 数据缓冲系统

### RolloutDataSource（基类）

```python
from slime.data import RolloutDataSource

class RolloutDataSource:
    def __init__(self, dataset, args):
        self.dataset = dataset
        self.args = args

    def get_samples(self, num_samples: int) -> list[Sample]:
        """Fetch prompts from dataset."""
        return [Sample(prompt=p) for p in self.dataset.sample(num_samples)]

    def add_samples(self, samples: list[Sample]) -> None:
        """Called after generation (no-op by default)."""
        pass
```

### 缓冲数据源（离线模式）

```python
from slime.data import RolloutDataSourceWithBuffer

class RolloutDataSourceWithBuffer(RolloutDataSource):
    def __init__(self, dataset, args):
        super().__init__(dataset, args)
        self.buffer = []

    def add_samples(self, samples: list[Sample]) -> None:
        """Store generated samples for reuse."""
        self.buffer.extend(samples)

    def buffer_filter(self, args, buffer, num_samples) -> list[Sample]:
        """Custom selection logic."""
        # Example: prioritized sampling based on reward
        sorted_buffer = sorted(buffer, key=lambda s: s.reward, reverse=True)
        return sorted_buffer[:num_samples]
```

## 自定义函数

### 自定义生成函数

适用于多轮对话或工具调用场景：

```python
# custom_generate.py
from slime.data import Sample

async def custom_generate(args, samples: list[Sample], evaluation: bool = False) -> list[Sample]:
    """
    Custom generation function for multi-turn interactions.

    Args:
        args: Training arguments
        samples: List of Sample objects with prompts
        evaluation: Whether this is an evaluation run

    Returns:
        List of Sample objects with responses and rewards
    """
    for sample in samples:
        conversation = sample.prompt if isinstance(sample.prompt, list) else [
            {"role": "user", "content": sample.prompt}
        ]

        for turn in range(args.max_turns):
            # Generate response
            response = await generate_single(conversation)

            # Check for tool call
            tool_call = extract_tool_call(response)
            if tool_call:
                # Execute tool
                tool_result = await execute_tool(tool_call)
                conversation.append({"role": "assistant", "content": response})
                conversation.append({"role": "tool", "content": tool_result})
            else:
                # Final response
                sample.response = response
                break

        # Compute reward
        sample.reward = compute_reward(sample)

        # Set loss mask (1 for model tokens, 0 for tool responses)
        sample.loss_mask = build_loss_mask(sample)

    return samples
```

使用方法：
```bash
python train.py \
    --custom-generate-function-path custom_generate.py \
    --max-turns 5
```

### 自定义奖励函数

```python
# custom_rm.py
from slime.data import Sample

async def reward_func(args, sample: Sample, **kwargs) -> float:
    """
    Compute reward for a single sample.

    Args:
        args: Training arguments
        sample: Sample object with response

    Returns:
        Reward score (float)
    """
    response = sample.response
    ground_truth = sample.label or sample.metadata.get("answer", "")

    # Example: exact match reward
    if response.strip() == ground_truth.strip():
        return 1.0
    return 0.0

# For batched processing (more efficient)
async def batched_custom_rm(args, samples: list[Sample]) -> list[float]:
    """Batch reward computation."""
    rewards = []
    for sample in samples:
        reward = await reward_func(args, sample)
        rewards.append(reward)
    return rewards
```

使用方法：
```bash
python train.py \
    --custom-rm-path custom_rm.py \
    --group-rm  # Enable batched processing
```

## 模型配置

### 预置模型脚本

位于 `scripts/models/` 目录下：

```bash
# List available models
ls scripts/models/
# glm4-9B.sh, qwen3-4B.sh, qwen3-30B-A3B.sh, deepseek-v3.sh, llama3-8B.sh

# Source model configuration
source scripts/models/qwen3-4B.sh
# This sets MODEL_ARGS and CKPT_ARGS arrays
```

### 模型脚本示例

```bash
# scripts/models/qwen3-4B.sh
export MODEL_ARGS=(
    --num-layers 36
    --hidden-size 2560
    --num-attention-heads 20
    --num-query-groups 4
    --ffn-hidden-size 6912
    --max-position-embeddings 32768
    --rotary-percent 1.0
    --rotary-base 1000000
    --swiglu
    --untie-embeddings-and-output-weights
    --no-position-embedding
    --normalization RMSNorm
    --tokenizer-type HuggingFaceTokenizer
    --bf16
)

export CKPT_ARGS=(
    --hf-checkpoint /path/to/qwen3-4b-hf
    --initial-megatron-checkpoint /path/to/megatron/ckpt
)
```

## 异步训练

### 启用异步模式

```bash
python train_async.py \
    --actor-num-gpus-per-node 8 \
    --rollout-num-gpus 8 \
    --async-buffer-size 4 \
    --update-weights-interval 2 \
    ${MODEL_ARGS[@]}
```

### 异步任务专用参数

```bash
--async-buffer-size 4            # Number of rollouts to buffer
--update-weights-interval 2      # Sync weights every N rollouts
```

**注意**：异步训练不支持并置模式（`--colocate`）。  

## 评估

### 多任务评估

```bash
--eval-prompt-data aime /path/to/aime.jsonl \
--eval-prompt-data gsm8k /path/to/gsm8k.jsonl \
--n-samples-per-eval-prompt 16 \
--eval-interval 50
```

### 评估配置

```bash
--eval-interval 50               # Evaluate every N rollouts
--n-samples-per-eval-prompt 16   # Samples for evaluation
--eval-temperature 0.0           # Greedy decoding for eval
```

## 支持的模型

| 模型系列 | 配置选项 |
|----------|----------|
| GLM | GLM-4.5、GLM-4.6、GLM-4.7、GLM-Z1-9B |
| Qwen | Qwen3（4B、8B、30B-A3B）、Qwen3-MoE、Qwen2.5 |
| DeepSeek | V3、V3.1、R1 |
| Llama | Llama 3（8B、70B） |
| 其他 | Kimi K2、Moonlight-16B |

## 相关资源

- 文档：https://thudm.github.io/slime/
- GitHub 仓库：https://github.com/THUDM/slime
- 博客文章：https://lmsys.org/blog/2025-07-09-slime/
- 示例代码：`examples/` 目录（包含14个以上可运行的示例）
