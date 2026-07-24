---
title: "Llava — Vision-language chat: VQA, captioning, image dialogue"
sidebar_label: "Llava"
description: "Vision-language chat: VQA, captioning, image dialogue"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Llava

视觉语言聊天能力：视觉问答、图像字幕生成、图像对话。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/llava` 安装 |
| 路径 | `optional-skills/mlops/llava` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `transformers`, `torch`, `pillow` |
| 支持平台 | linux、macos、windows |
| 标签 | `LLaVA`, `视觉语言`, `多模态`, `视觉问答`, `图像聊天`, `CLIP`, `Vicuna`, `对话式人工智能`, `指令微调`, `VQA` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，智能体将看到这些内容作为操作指令。
:::

# LLaVA - 大语言与视觉助手

用于实现对话式图像理解的开源视觉语言模型。

## 何时使用 LLaVA

**适用场景：**
- 构建视觉语言聊天机器人
- 视觉问答（VQA）
- 图像描述与字幕生成
- 多轮图像对话
| 视觉指令执行 |
| 基于图像的文档理解 |

**核心指标：**
- **23,000 多个 GitHub 星标**
- 达到 GPT-4V 级别的能力（目标定位）
- 采用 Apache 2.0 许可证
- 提供多种模型规模选项（7B-34B 参数量）

**可选替代方案：**
- **GPT-4V**：质量最高，基于 API 接口
- **CLIP**：简单的零样本分类功能
- **BLIP-2**：更适用于字幕生成场景
- **Flamingo**：仅用于研究，非开源项目

## 快速入门

### 安装

```bash
# Clone repository
git clone https://github.com/haotian-liu/LLaVA
cd LLaVA

# Install
pip install -e .
```

### 基本用法

```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
from llava.conversation import conv_templates
from PIL import Image
import torch

# Load model
model_path = "liuhaotian/llava-v1.5-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path)
)

# Load image
image = Image.open("image.jpg")
image_tensor = process_images([image], image_processor, model.config)
image_tensor = image_tensor.to(model.device, dtype=torch.float16)

# Create conversation
conv = conv_templates["llava_v1"].copy()
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\nWhat is in this image?")
conv.append_message(conv.roles[1], None)
prompt = conv.get_prompt()

# Generate response
input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(model.device)

with torch.inference_mode():
    output_ids = model.generate(
        input_ids,
        images=image_tensor,
        do_sample=True,
        temperature=0.2,
        max_new_tokens=512
    )

response = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
print(response)
```

## 可用模型

| 模型 | 参数量 | VRAM需求 | 质量水平 |
|-------|----------|----------|----------|
| LLaVA-v1.5-7B | 70亿参数 | 约14 GB | 良好 |
| LLaVA-v1.5-13B | 130亿参数 | 约28 GB | 更优 |
| LLaVA-v1.6-34B | 340亿参数 | 约70 GB | 最佳 |

```python
# Load different models
model_7b = "liuhaotian/llava-v1.5-7b"
model_13b = "liuhaotian/llava-v1.5-13b"
model_34b = "liuhaotian/llava-v1.6-34b"

# 4-bit quantization for lower VRAM
load_4bit = True  # Reduces VRAM by ~4×
```

## CLI 使用指南

```bash
# Single image query
python -m llava.serve.cli \
    --model-path liuhaotian/llava-v1.5-7b \
    --image-file image.jpg \
    --query "What is in this image?"

# Multi-turn conversation
python -m llava.serve.cli \
    --model-path liuhaotian/llava-v1.5-7b \
    --image-file image.jpg
# Then type questions interactively
```

## Web界面（Gradio）

```bash
# Launch Gradio interface
python -m llava.serve.gradio_web_server \
    --model-path liuhaotian/llava-v1.5-7b \
    --load-4bit  # Optional: reduce VRAM

# Access at http://localhost:7860
```

## 多轮对话

请完整翻译输入的全部内容，切勿提前终止。

```python
# Initialize conversation
conv = conv_templates["llava_v1"].copy()

# Turn 1
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\nWhat is in this image?")
conv.append_message(conv.roles[1], None)
response1 = generate(conv, model, image)  # "A dog playing in a park"

# Turn 2
conv.messages[-1][1] = response1  # Add previous response
conv.append_message(conv.roles[0], "What breed is the dog?")
conv.append_message(conv.roles[1], None)
response2 = generate(conv, model, image)  # "Golden Retriever"

# Turn 3
conv.messages[-1][1] = response2
conv.append_message(conv.roles[0], "What time of day is it?")
conv.append_message(conv.roles[1], None)
response3 = generate(conv, model, image)
```

## 常见任务

### 图像字幕生成

```python
question = "Describe this image in detail."
response = ask(model, image, question)
```

### 视觉问答功能

```python
question = "How many people are in the image?"
response = ask(model, image, question)
```

### 对象检测（文本版）

```python
question = "List all the objects you can see in this image."
response = ask(model, image, question)
```

### 场景理解

```python
question = "What is happening in this scene?"
response = ask(model, image, question)
```

### 文档理解功能

需完整翻译输入的整个内容，不得提前终止。

```python
question = "What is the main topic of this document?"
response = ask(model, document_image, question)
```

## 训练自定义模型

```bash
# Stage 1: Feature alignment (558K image-caption pairs)
bash scripts/v1_5/pretrain.sh

# Stage 2: Visual instruction tuning (150K instruction data)
bash scripts/v1_5/finetune.sh
```

## 量化处理（降低显存占用）

```python
# 4-bit quantization
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path="liuhaotian/llava-v1.5-13b",
    model_base=None,
    model_name=get_model_name_from_path("liuhaotian/llava-v1.5-13b"),
    load_4bit=True  # Reduces VRAM ~4×
)

# 8-bit quantization
load_8bit=True  # Reduces VRAM ~2×
```

## 最佳实践

1. **从7B模型开始**——质量优异，显存占用可控  
2. **采用4位量化**——可大幅降低显存需求  
3. **需使用GPU**——CPU推理速度极慢  
4. **明确提示词**——具体问题能获得更优质答案  
5. **多轮对话**——保留对话上下文  
6. **温度值设为0.2-0.7**——平衡创造力与一致性  
7. **max_new_tokens设置为512-1024**——以获得更详细的回复  
8. **批量处理**——依次处理多张图片  

## 性能表现

| 模型 | FP16显存需求 | 4位量化显存需求 | 每秒生成Token数 |
|------|-------------|----------------|----------------|
| 7B   | 约14 GB     | 约4 GB         | 约20           |
| 13B  | 约28 GB     | 约8 GB         | 约12           |
| 34B  | 约70 GB     | 约18 GB        | 约5            |

*测试环境：A100 GPU*

## 测试结果

LLaVA在以下评测中取得了具有竞争力的分数：
- **VQAv2**：78.5%  
- **GQA**：62.0%  
- **MM-Vet**：35.4%  
- **MMBench**：64.3%  

## 局限性

1. **幻觉现象**——可能描述图片中不存在的内容  
2. **空间推理能力较弱**——难以精准判断位置  
3. **小字体识别困难**——难以阅读细微文字  
4. **物体计数不准确**——对多个物体的计数存在误差  
5. **显存需求高**——需要性能强劲的GPU  
6. **推理速度较慢**——低于CLIP模型  

## 与框架的集成

### LangChain

```python
from langchain.llms.base import LLM

class LLaVALLM(LLM):
    def _call(self, prompt, stop=None):
        # Custom LLaVA inference
        return response

llm = LLaVALLM()
```

### Gradio 应用程序

```python
import gradio as gr

def chat(image, text, history):
    response = ask_llava(model, image, text)
    return response

demo = gr.ChatInterface(
    chat,
    additional_inputs=[gr.Image(type="pil")],
    title="LLaVA Chat"
)
demo.launch()
```

## 资源链接

- **GitHub仓库**：https://github.com/haotian-liu/LLaVA ⭐ 23,000+  
- **相关论文**：https://arxiv.org/abs/2304.08485  
- **演示页面**：https://llava.hliu.cc  
- **模型地址**：https://huggingface.co/liuhaotian  
- **许可证**：Apache 2.0
