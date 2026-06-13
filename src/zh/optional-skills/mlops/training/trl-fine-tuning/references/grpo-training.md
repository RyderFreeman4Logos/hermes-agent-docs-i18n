# GRPO（群体相对策略优化）——深度指南

本指南提供了高级应用模式、关键洞察以及基于 TRL 的 `GRPOTrainer` 使用自定义奖励函数微调语言模型的实战工作流。它是主技能条目中概述的 GRPO 工作流的深度参考资料。

## 何时使用 GRPO

在以下场景下可使用 GRPO：
- **强制指定输出格式**（XML 标签、JSON、结构化推理）
- **教授具有客观正确性评估指标的可验证任务**（数学、编程、事实核查等）
- **通过奖励思维链模式来提升模型的推理能力**
- **在缺乏标注偏好数据的情况下，让模型遵循特定领域的行为规范**
- **同时实现多目标优化**（格式、正确性、风格）

**以下场景请勿使用 GRPO：**
- 简单的监督微调任务 → 请使用 SFT
- 没有明确奖励信号的任务
- 已拥有高质量偏好对的数据时 → 请使用 DPO/PPO

## 核心概念

### 1. GRPO 算法基础

**核心机制：**
- 对每个提示生成**多个候选回答**（群体规模：4–16 个）
- 利用奖励函数比较同一群体内的各个候选答案
- 更新策略，使模型更倾向于选择群体中评分更高的回答

**与 PPO 的关键区别：**
- 不需要独立的奖励模型
- 样本效率更高（通过群体内部比较进行学习）
- 实现和调试更为简单

**数学原理直观解释：**
```
For each prompt p:
  1. Generate N completions: {c₁, c₂, ..., cₙ}
  2. Compute rewards: {r₁, r₂, ..., rₙ}
  3. Learn to increase probability of high-reward completions
     relative to low-reward ones in the same group
```

### 2. 奖励函数设计理念

**核心原则：**
1. **组合多个奖励函数**——每个函数负责处理某一特定方面（格式、正确性、风格）
2. **合理调整奖励权重**——权重越高，对应的信号越强
3. **采用渐进式奖励机制**——部分符合要求即可获得部分分数
4. **独立测试各奖励函数**——分别对每个奖励函数进行调试

**奖励函数类型：**

| 类型 | 适用场景 | 示例权重 |
|------|----------|----------|
| **正确性** | 可验证的任务（数学题、代码等） | 2.0（最高） |
| **格式** | 强制要求严格的结构规范 | 0.5–1.0 |
| **长度** | 鼓励表达详尽或简洁 | 0.1–0.5 |
| **风格** | 对不良表达模式予以扣分 | −0.5 至 0.5 |

## 实现流程

### 第一步：数据集准备

**关键要求：**
- 以聊天格式提供提示语（包含 `role` 和 `content` 字段的字典列表）
- 需包含用于明确要求的系统提示语
- 对于可验证的任务，还需添加真实答案作为额外列

```python
from datasets import load_dataset, Dataset

SYSTEM_PROMPT = """
Respond in the following format:
<reasoning>
[Your step-by-step thinking]
</reasoning>
<answer>
[Final answer]
</answer>
"""

def prepare_dataset(raw_data):
    """Transform raw data into GRPO-compatible format.

    Returns: Dataset with columns:
    - 'prompt': List[Dict] with role/content (system + user messages)
    - 'answer': str (ground truth, optional but recommended)
    """
    return raw_data.map(lambda x: {
        'prompt': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': x['question']}
        ],
        'answer': extract_answer(x['raw_answer'])
    })
```

**专业建议：**
- 对于结构复杂的任务，可在系统提示词中使用单次示例或少量示例
- 保持提示词简洁（最大长度：256–512个标记）
- 在训练前验证数据质量（输入质量决定输出质量）

### 第2步：奖励函数实现

**模板结构：**
```python
def reward_function_name(
    prompts,        # List[List[Dict]]: Original prompts
    completions,    # List[List[Dict]]: Model generations
    answer=None,    # Optional: Ground truth from dataset
    **kwargs        # Additional dataset columns
) -> list[float]:
    """Evaluate completions and return rewards (one per completion)."""
    responses = [comp[0]['content'] for comp in completions]
    rewards = []
    for response in responses:
        score = compute_score(response)
        rewards.append(score)
    return rewards
```

**示例 1：正确性奖励（数学/编程）**
```python
def correctness_reward(prompts, completions, answer, **kwargs):
    """Reward correct answers with high score."""
    responses = [comp[0]['content'] for comp in completions]
    extracted = [extract_final_answer(r) for r in responses]
    return [2.0 if ans == gt else 0.0
            for ans, gt in zip(extracted, answer)]
```

**示例 2：奖励格式设置（结构化输出）**
```python
import re

def format_reward(completions, **kwargs):
    """Reward XML-like structured format."""
    pattern = r'<reasoning>.*?</reasoning>\s*<answer>.*?</answer>'
    responses = [comp[0]['content'] for comp in completions]
    return [1.0 if re.search(pattern, r, re.DOTALL) else 0.0
            for r in responses]
```

**示例 3：增量格式奖励（部分得分）**
```python
def incremental_format_reward(completions, **kwargs):
    """Award partial credit for format compliance."""
    responses = [comp[0]['content'] for comp in completions]
    rewards = []

    for r in responses:
        score = 0.0
        if '<reasoning>' in r:  score += 0.25
        if '</reasoning>' in r: score += 0.25
        if '<answer>' in r:     score += 0.25
        if '</answer>' in r:    score += 0.25
        # Penalize extra text after closing tag
        if r.count('</answer>') == 1:
            extra_text = r.split('</answer>')[-1].strip()
            score -= len(extra_text) * 0.001
        rewards.append(score)

    return rewards
```

**重要提示：** 为确保训练的稳定性，建议结合使用3至5个奖励函数。相比信号类型的多样性，其排列顺序并非那么关键。

### 第3步：训练配置

**内存优化型配置（适用于小型GPU）**
```python
from trl import GRPOConfig

training_args = GRPOConfig(
    output_dir="outputs/grpo-model",

    # Learning rate
    learning_rate=5e-6,          # Lower = more stable
    adam_beta1=0.9,
    adam_beta2=0.99,
    weight_decay=0.1,
    warmup_ratio=0.1,
    lr_scheduler_type='cosine',

    # Batch settings
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,  # Effective batch = 4

    # GRPO-specific
    num_generations=8,            # Group size: 8–16 recommended
    max_prompt_length=256,
    max_completion_length=512,

    # Training duration
    num_train_epochs=1,
    max_steps=None,

    # Optimization
    bf16=True,                    # Faster on A100/H100
    optim="adamw_8bit",          # Memory-efficient optimizer
    max_grad_norm=0.1,

    # Logging
    logging_steps=1,
    save_steps=100,
    report_to="wandb",
)
```

**高性能配置（大显存GPU）**
```python
training_args = GRPOConfig(
    output_dir="outputs/grpo-model",
    learning_rate=1e-5,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    num_generations=16,           # Larger groups = better signal
    max_prompt_length=512,
    max_completion_length=1024,
    num_train_epochs=1,
    bf16=True,
    use_vllm=True,                # Fast generation with vLLM
    logging_steps=10,
)
```

**关键超参数：**

| 参数 | 影响程度 | 调优建议 |
|------|----------|----------|
| `num_generations` | 对比时的组大小 | 从 8 开始，若 GPU 硬件允许可提升至 16 |
| `learning_rate` | 收敛速度/稳定性 | 5e-6（较为安全），1e-5（收敛更快，但风险更高） |
| `max_completion_length` | 输出详细程度 | 根据任务需求调整（512 用于复杂推理，256 适用于简短回答） |
| `gradient_accumulation_steps` | 实际批量大小 | 若 GPU 内存不足，可适当增加该值 |

### 第 4 步：模型配置与训练

**标准配置（Transformers + TRL）**
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from trl import GRPOTrainer

model_name = "Qwen/Qwen2.5-1.5B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # 2–3× faster
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Optional: LoRA for parameter-efficient training
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    task_type="CAUSAL_LM",
    lora_dropout=0.05,
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[
        incremental_format_reward,
        format_reward,
        correctness_reward,
    ],
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config,   # Remove for full fine-tuning
)

trainer.train()
trainer.save_model("final_model")
```

**Unsloth 配置（速度提升 2–3 倍）**
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="google/gemma-3-1b-it",
    max_seq_length=1024,
    load_in_4bit=True,
    fast_inference=True,
    max_lora_rank=32,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    use_gradient_checkpointing="unsloth",
)

# Rest is identical to the standard setup
trainer = GRPOTrainer(model=model, ...)
trainer.train()
```

## 关键训练要点

### 1. 损失变化趋势（预期模式）
- **损失值初始接近0，并在训练过程中逐渐上升**——这是正常现象
- 损失值用于衡量模型与初始策略之间的KL散度；这说明模型正在学习（通过改变原有行为来优化奖励）
- **应关注奖励指标而非损失值，以此判断训练进展**

### 2. 奖励跟踪

需重点关注的指标：
- `reward`——所有任务完成后的平均奖励
- `reward_std`——各组数据之间的差异度（应保持大于0）
- `kl`——与参考策略的KL散度（应呈适度上升趋势）

**理想状态：**
```
Step   Reward    Reward_Std   KL
100    0.5       0.3          0.02
200    0.8       0.25         0.05
300    1.2       0.2          0.08  ← Good progression
400    1.5       0.15         0.12
```

**警告信号：**
- `reward_std` → 0（模型仅生成单一响应）
- `kl` 值激增（> 0.5）——模型收敛性过差，需降低学习率
- 奖励值停滞不前——可能是奖励函数设定过于严格或模型容量不足

### 3. 常见问题及解决方案

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **模式崩溃** | 所有生成结果完全一致 | 增加`num_generations`值，引入多样性惩罚机制 |
| **无法学习** | 奖励值保持不变 | 检查奖励函数逻辑，提高学习率 |
| **内存溢出错误** | GPU内存耗尽 | 减少`num_generations`值，启用梯度检查点功能 |
| **训练速度过慢** | 训练速度低于1 it/s | 启用`use_vllm=True`选项，使用Unsloth框架，缩短序列长度 |
| **格式未被遵循** | 模型不按指定结构生成内容 | 提高格式奖励的权重，增加增量奖励 |

## 高级用法

### 1. 多阶段训练

对于复杂任务，可采用分阶段训练的方式：

```python
# Stage 1: Format compliance
trainer_stage1 = GRPOTrainer(
    model=model,
    reward_funcs=[incremental_format_reward, format_reward],
    ...
)
trainer_stage1.train()

# Stage 2: Correctness
trainer_stage2 = GRPOTrainer(
    model=model,
    reward_funcs=[format_reward, correctness_reward],
    ...
)
trainer_stage2.train()
```

### 2. 自适应奖励缩放机制

```python
class AdaptiveReward:
    def __init__(self, base_reward_func, initial_weight=1.0):
        self.func = base_reward_func
        self.weight = initial_weight

    def __call__(self, *args, **kwargs):
        rewards = self.func(*args, **kwargs)
        return [r * self.weight for r in rewards]

    def adjust_weight(self, success_rate):
        """Increase weight if model struggling, decrease if succeeding."""
        if success_rate < 0.3:
            self.weight *= 1.2
        elif success_rate > 0.8:
            self.weight *= 0.9
```

### 3. 自定义数据集集成

```python
def load_custom_knowledge_base(csv_path):
    import pandas as pd
    df = pd.read_csv(csv_path)
    return Dataset.from_pandas(df).map(lambda x: {
        'prompt': [
            {'role': 'system', 'content': CUSTOM_SYSTEM_PROMPT},
            {'role': 'user', 'content': x['question']}
        ],
        'answer': x['expert_answer']
    })
```

## 部署与推理

### 保存并合并 LoRA 模型
```python
if hasattr(trainer.model, 'merge_and_unload'):
    merged_model = trainer.model.merge_and_unload()
    merged_model.save_pretrained("production_model")
    tokenizer.save_pretrained("production_model")
```

### 推理
```python
from transformers import pipeline

generator = pipeline("text-generation", model="production_model", tokenizer=tokenizer)

result = generator(
    [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': "What is 15 + 27?"},
    ],
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)
print(result[0]['generated_text'])
```

## 最佳实践检查清单

**训练前：**
- [ ] 验证数据集格式（提示词需为 List[Dict] 类型）
- [ ] 在样本数据上测试奖励函数
- [ ] 根据数据计算预期的 `max_prompt_length` 值
- [ ] 根据 GPU 内存容量确定 `num_generations` 的数值
- [ ] 设置日志记录功能（推荐使用 WandB）

**训练过程中：**
- [ ] 监控奖励值的变化趋势（应呈上升态势）
- [ ] 检查 `reward_std` 值（应保持在 0.1 以上）
- [ ] 注意内存不足错误（必要时减小批量大小）
- [ ] 每 50–100 步抽取一次生成结果进行采样
- [ ] 在保留数据集上验证格式合规性

**训练完成后：**
- [ ] 若使用了 PEFT 技术，则需合并 LoRA 权重
- [ ] 在多种不同的提示词上进行测试
- [ ] 与基线模型进行对比
- [ ] 记录奖励权重及超参数信息
- [ ] 保存用于复现实验的配置文件

## 故障排查

### 调试流程
1. **单独测试奖励函数** —— 逐一独立验证
2. **检查数据分布** —— 确保提示词具有多样性
3. **降低复杂度** —— 先使用单一奖励指标，再逐步增加
4. **监控生成过程** —— 每 N 步打印一次样本结果
5. **验证提取逻辑** —— 确保答案解析功能正常运行

### 快速调试奖励函数方法
```python
def debug_reward(completions, **kwargs):
    responses = [comp[0]['content'] for comp in completions]
    for i, r in enumerate(responses[:2]):
        print(f"Response {i}: {r[:200]}...")
    return [1.0] * len(responses)

# Test without training
trainer = GRPOTrainer(..., reward_funcs=[debug_reward])
trainer.generate_completions(dataset[:1])
```

## 模板

一个可直接用于生产的训练脚本位于 **`../templates/basic_grpo_training.py`**。该脚本基于 Qwen 2.5-1.5B-Instruct 模型结合 LoRA 技术，并在 GSM8K 数据集上使用了三种奖励函数（增量式、严格式和正确性评估）。您可以复制该脚本并进行以下调整：
1. `get_dataset()` 函数——替换为您自己的数据加载器；
2. 奖励函数——根据具体任务进行优化；
3. `SYSTEM_PROMPT` ——使其符合您的输出格式要求；
4. `GRPOConfig` ——根据您的 GPU 硬件调整超参数。

## 参考资料与资源

- TRL GRPO 训练器：https://huggingface.co/docs/trl/grpo_trainer
- GRPO 相关论文（DeepSeek 发表）：https://arxiv.org/abs/2402.03300
- DeepSeek R1 相关论文：https://arxiv.org/abs/2501.12948
- Open R1 实现代码：https://github.com/huggingface/open-r1
- TRL 示例代码：https://github.com/huggingface/trl/tree/main/examples
- Unsloth（加速训练工具）：https://docs.unsloth.ai/

## 重要注意事项

- **训练过程中损失值会上升**——这是正常现象（属于 KL 散度导致的）；
- **建议使用 3–5 种奖励函数**——仅依赖单一奖励函数往往难以取得理想效果；
- **在开始训练前先测试奖励函数**——需单独调试每一种奖励函数的功能；
- **密切监控 `reward_std` 值**——其数值应保持在 0.1 以上，以避免模型陷入模式崩溃；
- **初始时将 `num_generations` 设置为 4–8**——若 GPU 性能允许，可逐步增加该数值。
