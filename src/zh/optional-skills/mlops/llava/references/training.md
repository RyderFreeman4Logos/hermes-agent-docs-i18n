# LLaVA训练指南

用于指导LLaVA模型的训练与微调。

## 训练阶段

### 第一阶段：特征对齐（预训练）

**目的**：使视觉编码器与语言模型实现对齐

**数据来源**：558K组图像-文本描述对（CC3M子集）

```bash
# Download pretrained projector or train from scratch
bash scripts/v1_5/pretrain.sh
```

**配置参数：**
- 基础模型：Vicuna-7B 或 LLaMA-2-7B
- 视觉编码器：CLIP ViT-L/14
- 训练时间：在8块A100硬件上约需20小时

### 第二阶段：视觉指令微调

**目标**：让模型能够理解并执行视觉指令

**训练数据**：15万条由GPT生成的多模态指令数据

```bash
# Fine-tune with instruction data
bash scripts/v1_5/finetune.sh
```

**配置参数：**
- 训练轮数：1轮
- 批量大小：128（分配至8块GPU）
- 学习率：2e-5
- 训练时间：在8× A100硬件上约需24小时

## 数据格式

### 指令数据格式

```json
[
    {
        "id": "001",
        "image": "path/to/image.jpg",
        "conversations": [
            {
                "from": "human",
                "value": "<image>\nWhat is in this image?"
            },
            {
                "from": "gpt",
                "value": "The image shows a dog playing in a park."
            },
            {
                "from": "human",
                "value": "What breed is the dog?"
            },
            {
                "from": "gpt",
                "value": "It appears to be a Golden Retriever."
            }
        ]
    }
]
```

## 基于自定义数据进行微调

### 准备数据

```python
import json

# Create instruction data
data = []
for image_path, qa_pairs in your_dataset:
    conversations = []
    for q, a in qa_pairs:
        conversations.append({"from": "human", "value": f"<image>\n{q}"})
        conversations.append({"from": "gpt", "value": a})

    data.append({
        "id": str(len(data)),
        "image": image_path,
        "conversations": conversations
    })

# Save
with open("custom_data.json", "w") as f:
    json.dump(data, f, indent=2)
```

### 微调脚本

```bash
#!/bin/bash

# Set paths
DATA_PATH="custom_data.json"
IMAGE_FOLDER="path/to/images"
MODEL_PATH="liuhaotian/llava-v1.5-7b"
OUTPUT_DIR="./checkpoints/llava-custom"

# Fine-tune
deepspeed llava/train/train_mem.py \
    --deepspeed ./scripts/zero2.json \
    --model_name_or_path $MODEL_PATH \
    --version v1 \
    --data_path $DATA_PATH \
    --image_folder $IMAGE_FOLDER \
    --vision_tower openai/clip-vit-large-patch14-336 \
    --mm_projector_type mlp2x_gelu \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --image_aspect_ratio pad \
    --group_by_modality_length True \
    --bf16 True \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 1 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 50000 \
    --save_total_limit 1 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --dataloader_num_workers 4 \
    --lazy_preprocess True \
    --report_to wandb
```

## LoRA微调（高效内存占用）

```python
from peft import LoraConfig, get_peft_model

# LoRA config
lora_config = LoraConfig(
    r=8,  # LoRA rank
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(base_model, lora_config)

# Train with much lower memory
```

## 硬件要求

### 全量微调

- **7B模型**：8张A100显卡（40GB显存）
- **13B模型**：8张A100显卡（80GB显存）
- **训练时间**：20-48小时

### LoRA微调

- **7B模型**：1张A100显卡（40GB显存）
- **13B模型**：2张A100显卡（40GB显存）
- **训练时间**：10-24小时

## 最佳实践建议

1. **从预训练模型开始**——无需从头开始训练
2. **采用LoRA提升效率**——可节省10倍的内存占用
3. **质量重于数量**——1000个高质量样本优于1万个低质量样本
4. **多轮对话**——比单次问答更具互动性
5. **使用多样化图片**——涵盖不同场景
6. **提供清晰指令**——明确的问题能获得更好答案
7. **监控损失值**——其数值应呈平稳下降趋势
8. **保存检查点**——训练过程可能会出现失败
9. **定期测试**——在预留数据集上验证模型效果
10. **使用DeepSpeed**——实现多GPU并行训练

## 相关资源

- **训练脚本**：https://github.com/haotian-liu/LLaVA/tree/main/scripts
- **数据格式规范**：https://github.com/haotian-liu/LLaVA/blob/main/docs/Data.md
- **相关论文**：https://arxiv.org/abs/2304.08485
