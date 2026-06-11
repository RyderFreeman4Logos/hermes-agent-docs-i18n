# SFT训练指南

这是一份关于使用TRL进行指令微调与任务特定微调的监督式微调（SFT）完整指南。

## 概述

SFT通过输入-输出对来训练模型，旨在最小化交叉熵损失。其应用场景包括：
- 指令遵循
- 任务特定微调
- 聊天机器人训练
- 领域适配

## 数据集格式

### 格式1：提示词补全

```json
[
  {
    "prompt": "What is the capital of France?",
    "completion": "The capital of France is Paris."
  }
]
```

### 第2种格式：对话式（ChatML）

```json
[
  {
    "messages": [
      {"role": "user", "content": "What is Python?"},
      {"role": "assistant", "content": "Python is a programming language."}
    ]
  }
]
```

### 格式 3：纯文本模式

```json
[
  {"text": "User: Hello\nAssistant: Hi! How can I help?"}
]
```

## 基础培训

```python
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Load model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")

# Load dataset
dataset = load_dataset("trl-lib/Capybara", split="train")

# Configure
config = SFTConfig(
    output_dir="Qwen2.5-SFT",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=2e-5,
    save_strategy="epoch"
)

# Train
trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer
)
trainer.train()
```

## 聊天模板

自动应用聊天模板：

```python
trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,  # Messages format
    tokenizer=tokenizer
    # Chat template applied automatically
)
```

或手动操作：
```python
def format_chat(example):
    messages = example["messages"]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}

dataset = dataset.map(format_chat)
```

## 提升效率的打包方式

将多个序列打包为一个，从而最大限度地提升 GPU 的利用率：

```python
config = SFTConfig(
    packing=True,  # Enable packing
    max_seq_length=2048,
    dataset_text_field="text"
)
```

**优势**：训练速度提升2至3倍  
**权衡**：批处理流程稍显复杂  

## 多GPU训练

```bash
accelerate launch --num_processes 4 train_sft.py
```

或者通过配置文件实现：
```python
config = SFTConfig(
    output_dir="model-sft",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=1
)
```

## LoRA微调

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules="all-linear",
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    peft_config=lora_config  # Add LoRA
)
```

## 超参数

| 模型规模 | 学习率 | 批量大小 | 训练轮数 |
|----------|--------|----------|----------|
| <10亿参数 | 5e-5 | 8-16 | 1-3 |
| 10亿–70亿参数 | 2e-5 | 4-8 | 1-2 |
| 70亿–130亿参数 | 1e-5 | 2-4 | 1 |
| 130亿参数以上 | 5e-6 | 1-2 | 1 |

## 参考资料

- TRL文档：https://huggingface.co/docs/trl/sft_trainer
- 示例代码：https://github.com/huggingface/trl/tree/main/examples/scripts
