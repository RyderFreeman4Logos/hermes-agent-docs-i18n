# PEFT高级使用指南

## 高级LoRA变体

### DoRA（权重分解型低秩适配）

DoRA将权重分解为幅度和方向两个分量，通常能比标准LoRA获得更好的效果：

```python
from peft import LoraConfig

dora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    use_dora=True,  # Enable DoRA
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, dora_config)
```

**何时使用 DoRA**：
- 在指令遵循任务中始终能展现出优于 LoRA 的性能
- 由于需要存储幅度向量，内存占用略高（约高出 10%)
- 非常适合对模型质量要求极高的微调场景

### AdaLoRA（自适应秩）

会根据各层的重要性自动调整其秩值：

```python
from peft import AdaLoraConfig

adalora_config = AdaLoraConfig(
    init_r=64,              # Initial rank
    target_r=16,            # Target average rank
    tinit=200,              # Warmup steps
    tfinal=1000,            # Final pruning step
    deltaT=10,              # Rank update frequency
    beta1=0.85,
    beta2=0.85,
    orth_reg_weight=0.5,    # Orthogonality regularization
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM"
)
```

**优势**：
- 为关键层分配更高的权重
- 能在保持性能的同时减少总参数量
- 非常适合探索最优的权重分配方案

### LoRA+（非对称学习率）

为A矩阵和B矩阵设置不同的学习率：

```python
from peft import LoraConfig

# LoRA+ uses higher LR for B matrix
lora_plus_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules="all-linear",
    use_rslora=True,  # Rank-stabilized LoRA (related technique)
)

# Manual implementation of LoRA+
from torch.optim import AdamW

# Group parameters
lora_A_params = [p for n, p in model.named_parameters() if "lora_A" in n]
lora_B_params = [p for n, p in model.named_parameters() if "lora_B" in n]

optimizer = AdamW([
    {"params": lora_A_params, "lr": 1e-4},
    {"params": lora_B_params, "lr": 1e-3},  # 10x higher for B
])
```

### rsLoRA（秩稳定化 LoRA）

通过调整不同秩值来扩展 LoRA 的输出规模，从而实现训练过程的稳定性：

```python
lora_config = LoraConfig(
    r=64,
    lora_alpha=64,
    use_rslora=True,  # Enables rank-stabilized scaling
    target_modules="all-linear"
)
```

**适用场景**：
- 在测试不同量化等级时
- 有助于确保不同量化等级下的行为一致性
- 建议在 r > 32 的情况下使用

## LoftQ（支持 LoRA 微调的量化技术）

通过初始化 LoRA 权重来弥补量化带来的误差：

```python
from peft import LoftQConfig, LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# LoftQ configuration
loftq_config = LoftQConfig(
    loftq_bits=4,              # Quantization bits
    loftq_iter=5,              # Alternating optimization iterations
)

# LoRA config with LoftQ initialization
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules="all-linear",
    init_lora_weights="loftq",
    loftq_config=loftq_config,
    task_type="CAUSAL_LM"
)

# Load quantized model
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config
)

model = get_peft_model(model, lora_config)
```

**相较于标准 QLoRA 的优势**：
- 量化后的初始质量更高
- 收敛速度更快
- 在基准测试中的最终准确率提升约 1-2%

## 自定义模块定位功能

### 定位特定层

```python
# Target only first and last transformer layers
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["model.layers.0.self_attn.q_proj",
                    "model.layers.0.self_attn.v_proj",
                    "model.layers.31.self_attn.q_proj",
                    "model.layers.31.self_attn.v_proj"],
    layers_to_transform=[0, 31]  # Alternative approach
)
```

### 层级模式匹配

```python
# Target layers 0-10 only
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules="all-linear",
    layers_to_transform=list(range(11)),  # Layers 0-10
    layers_pattern="model.layers"
)
```

### 排除特定层级

```python
lora_config = LoraConfig(
    r=16,
    target_modules="all-linear",
    modules_to_save=["lm_head"],  # Train these fully (not LoRA)
)
```

## 嵌入模型训练与语言模型头部训练

### 使用 LoRA 方法训练嵌入模型

```python
from peft import LoraConfig

# Include embeddings
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "embed_tokens"],  # Include embeddings
    modules_to_save=["lm_head"],  # Train lm_head fully
)
```

### 利用 LoRA 扩展词汇量

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig

# Add new tokens
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
new_tokens = ["<custom_token_1>", "<custom_token_2>"]
tokenizer.add_tokens(new_tokens)

# Resize model embeddings
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
model.resize_token_embeddings(len(tokenizer))

# Configure LoRA to train new embeddings
lora_config = LoraConfig(
    r=16,
    target_modules="all-linear",
    modules_to_save=["embed_tokens", "lm_head"],  # Train these fully
)

model = get_peft_model(model, lora_config)
```

## 多适配器模式

### 适配器组合

```python
from peft import PeftModel

# Load model with multiple adapters
model = AutoPeftModelForCausalLM.from_pretrained("./base-adapter")
model.load_adapter("./style-adapter", adapter_name="style")
model.load_adapter("./task-adapter", adapter_name="task")

# Combine adapters (weighted sum)
model.add_weighted_adapter(
    adapters=["style", "task"],
    weights=[0.7, 0.3],
    adapter_name="combined",
    combination_type="linear"  # or "cat", "svd"
)

model.set_adapter("combined")
```

### 适配器堆叠

```python
# Stack adapters (apply sequentially)
model.add_weighted_adapter(
    adapters=["base", "domain", "task"],
    weights=[1.0, 1.0, 1.0],
    adapter_name="stacked",
    combination_type="cat"  # Concatenate adapter outputs
)
```

### 动态适配器切换

```python
import torch

class MultiAdapterModel:
    def __init__(self, base_model_path, adapter_paths):
        self.model = AutoPeftModelForCausalLM.from_pretrained(adapter_paths[0])
        for name, path in adapter_paths[1:].items():
            self.model.load_adapter(path, adapter_name=name)

    def generate(self, prompt, adapter_name="default"):
        self.model.set_adapter(adapter_name)
        return self.model.generate(**self.tokenize(prompt))

    def generate_ensemble(self, prompt, adapters, weights):
        """Generate with weighted adapter ensemble"""
        outputs = []
        for adapter, weight in zip(adapters, weights):
            self.model.set_adapter(adapter)
            logits = self.model(**self.tokenize(prompt)).logits
            outputs.append(weight * logits)
        return torch.stack(outputs).sum(dim=0)
```

## 内存优化

### 结合 LoRA 的梯度检查点技术

```python
from peft import prepare_model_for_kbit_training

# Enable gradient checkpointing
model = prepare_model_for_kbit_training(
    model,
    use_gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False}
)
```

### 训练任务的CPU卸载功能

```python
from accelerate import Accelerator

accelerator = Accelerator(
    mixed_precision="bf16",
    gradient_accumulation_steps=8,
    cpu_offload=True  # Offload optimizer states to CPU
)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)
```

### 基于LoRA的节省内存注意力机制

```python
from transformers import AutoModelForCausalLM

# Combine Flash Attention 2 with LoRA
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16
)

# Apply LoRA
model = get_peft_model(model, lora_config)
```

## 推理优化

### 合并以用于部署

```python
# Merge adapter weights into base model
merged_model = model.merge_and_unload()

# Quantize merged model for inference
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(load_in_4bit=True)
quantized_model = AutoModelForCausalLM.from_pretrained(
    "./merged-model",
    quantization_config=bnb_config
)
```

### 导出为不同格式

```python
# Export to GGUF (llama.cpp)
# First merge, then convert
merged_model.save_pretrained("./merged-model")

# Use llama.cpp converter
# python convert-hf-to-gguf.py ./merged-model --outfile model.gguf

# Export to ONNX
from optimum.onnxruntime import ORTModelForCausalLM

ort_model = ORTModelForCausalLM.from_pretrained(
    "./merged-model",
    export=True
)
ort_model.save_pretrained("./onnx-model")
```

### 批量适配器推理

```python
from vllm import LLM
from vllm.lora.request import LoRARequest

# Initialize with LoRA support
llm = LLM(
    model="meta-llama/Llama-3.1-8B",
    enable_lora=True,
    max_lora_rank=64,
    max_loras=4  # Max concurrent adapters
)

# Batch with different adapters
requests = [
    ("prompt1", LoRARequest("adapter1", 1, "./adapter1")),
    ("prompt2", LoRARequest("adapter2", 2, "./adapter2")),
    ("prompt3", LoRARequest("adapter1", 1, "./adapter1")),
]

outputs = llm.generate(
    [r[0] for r in requests],
    lora_request=[r[1] for r in requests]
)
```

## 训练方案

### 指令微调方案

```python
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules="all-linear",
    bias="none",
    task_type="CAUSAL_LM"
)

training_args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    bf16=True,
    logging_steps=10,
    save_strategy="steps",
    save_steps=100,
    eval_strategy="steps",
    eval_steps=100,
)
```

### 代码生成指南

```python
lora_config = LoraConfig(
    r=32,              # Higher rank for code
    lora_alpha=64,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
    task_type="CAUSAL_LM"
)

training_args = TrainingArguments(
    learning_rate=1e-4,        # Lower LR for code
    num_train_epochs=2,
    max_seq_length=2048,       # Longer sequences
)
```

### 对话/聊天模式配置方案

```python
from trl import SFTTrainer

lora_config = LoraConfig(
    r=16,
    lora_alpha=16,  # alpha = r for chat
    lora_dropout=0.05,
    target_modules="all-linear"
)

# Use chat template
def format_chat(example):
    messages = [
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]}
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False)

trainer = SFTTrainer(
    model=model,
    peft_config=lora_config,
    train_dataset=dataset.map(format_chat),
    max_seq_length=1024,
)
```

## 调试与验证

### 验证适配器应用

```python
# Check which modules have LoRA
for name, module in model.named_modules():
    if hasattr(module, "lora_A"):
        print(f"LoRA applied to: {name}")

# Print detailed config
print(model.peft_config)

# Check adapter state
print(f"Active adapters: {model.active_adapters}")
print(f"Trainable: {sum(p.numel() for p in model.parameters() if p.requires_grad)}")
```

### 与基础模型对比

```python
# Generate with adapter
model.set_adapter("default")
adapter_output = model.generate(**inputs)

# Generate without adapter
with model.disable_adapter():
    base_output = model.generate(**inputs)

print(f"Adapter: {tokenizer.decode(adapter_output[0])}")
print(f"Base: {tokenizer.decode(base_output[0])}")
```

### 监控训练指标

```python
from transformers import TrainerCallback

class LoRACallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if "loss" in logs:
            # Log adapter-specific metrics
            model = kwargs["model"]
            lora_params = sum(p.numel() for n, p in model.named_parameters()
                            if "lora" in n and p.requires_grad)
            print(f"Step {state.global_step}: loss={logs['loss']:.4f}, lora_params={lora_params}")
```
