# PEFT故障排查指南

## 安装问题

### bitsandbytes CUDA错误

**错误信息**：`尽管GPU可用，但CUDA设置失败`

**解决方案**：
```bash
# Check CUDA version
nvcc --version

# Install matching bitsandbytes
pip uninstall bitsandbytes
pip install bitsandbytes --no-cache-dir

# Or compile from source for specific CUDA
git clone https://github.com/TimDettmers/bitsandbytes.git
cd bitsandbytes
CUDA_VERSION=118 make cuda11x  # Adjust for your CUDA
pip install .
```

### Triton 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'triton'`

**解决方案**：
```bash
# Install triton (Linux only)
pip install triton

# Windows: Triton not supported, use CUDA backend
# Set environment variable to disable triton
export CUDA_VISIBLE_DEVICES=0
```

### PEFT版本冲突问题

**错误信息**：`AttributeError: 'LoraConfig'对象不存在'use_dora'属性`

**解决方案**：
```bash
# Upgrade to latest PEFT
pip install peft>=0.13.0 --upgrade

# Check version
python -c "import peft; print(peft.__version__)"
```

## 训练问题

### CUDA 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存不足`

**解决方案**：

1. **启用梯度检查点机制**：
```python
from peft import prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
```

2. **减小批量处理规模**：
```python
TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16  # Maintain effective batch size
)
```

3. **使用 QLoRA**：
```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config)
```

4. **降低LoRA秩值**：
```python
LoraConfig(r=8)  # Instead of r=16 or higher
```

5. **锁定更少的模块**：
```python
target_modules=["q_proj", "v_proj"]  # Instead of all-linear
```

### 损失未下降

**问题**：训练损失保持不变或持续上升。

**解决方案**：

1. **检查学习率**：
```python
# Start lower
TrainingArguments(learning_rate=1e-4)  # Not 2e-4 or higher
```

2. **确认适配器处于激活状态**：
```python
model.print_trainable_parameters()
# Should show >0 trainable params

# Check adapter applied
print(model.peft_config)
```

3. **检查数据格式**：
```python
# Verify tokenization
sample = dataset[0]
decoded = tokenizer.decode(sample["input_ids"])
print(decoded)  # Should look correct
```

4. **提升排名**：
```python
LoraConfig(r=32, lora_alpha=64)  # More capacity
```

### NaN损失

**错误提示**：`损失值为NaN`

**解决方案**：
```python
# Use bf16 instead of fp16
TrainingArguments(bf16=True, fp16=False)

# Or enable loss scaling
TrainingArguments(fp16=True, fp16_full_eval=True)

# Lower learning rate
TrainingArguments(learning_rate=5e-5)

# Check for data issues
for batch in dataloader:
    if torch.isnan(batch["input_ids"].float()).any():
        print("NaN in input!")
```

### 适配器未进行训练

**问题**：显示“可训练参数数量：0”，或模型未发生更新。

**解决方案**：
```python
# Verify LoRA applied to correct modules
for name, module in model.named_modules():
    if "lora" in name.lower():
        print(f"Found LoRA: {name}")

# Check target_modules match model architecture
from peft.utils import TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING
print(TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING.get(model.config.model_type))

# Ensure model in training mode
model.train()

# Check requires_grad
for name, param in model.named_parameters():
    if param.requires_grad:
        print(f"Trainable: {name}")
```

## 加载问题

### 适配器加载失败

**错误信息**：`ValueError: 无法找到适配器权重`

**解决方案**：
```python
# Check adapter files exist
import os
print(os.listdir("./adapter-path"))
# Should contain: adapter_config.json, adapter_model.safetensors

# Load with correct structure
from peft import PeftModel, PeftConfig

# Check config
config = PeftConfig.from_pretrained("./adapter-path")
print(config)

# Load base model first
base_model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path)
model = PeftModel.from_pretrained(base_model, "./adapter-path")
```

### 基础模型不匹配

**错误信息**：`RuntimeError: size mismatch`

**解决方案**：
```python
# Ensure base model matches adapter
from peft import PeftConfig

config = PeftConfig.from_pretrained("./adapter-path")
print(f"Base model: {config.base_model_name_or_path}")

# Load exact same base model
base_model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path)
```

### Safetensors格式与PyTorch格式的对比

**错误提示**：`ValueError: 我们无法连接到‘https://huggingface.co’`

**解决方案**：
```python
# Force local loading
model = PeftModel.from_pretrained(
    base_model,
    "./adapter-path",
    local_files_only=True
)

# Or specify format
model.save_pretrained("./adapter", safe_serialization=True)  # safetensors
model.save_pretrained("./adapter", safe_serialization=False)  # pytorch
```

## 推理问题

### 生成速度过慢

**问题**：推理速度远低于预期。

**解决方案**：

1. **用于部署的合并适配器**：
```python
merged_model = model.merge_and_unload()
# No adapter overhead during inference
```

2. **使用优化后的推理引擎**：
```python
from vllm import LLM
llm = LLM(model="./merged-model", dtype="half")
```

3. **启用 Flash Attention**：
```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    attn_implementation="flash_attention_2"
)
```

### 输出质量问题

**问题**：微调后的模型产生的输出质量更差。

**解决方案**：

1. **检查未使用适配器的评估结果**：
```python
with model.disable_adapter():
    base_output = model.generate(**inputs)
# Compare with adapter output
```

2. **在评估过程中降低温度**：
```python
model.generate(**inputs, temperature=0.1, do_sample=False)
```

3. **使用更多数据重新训练**：
```python
# Increase training samples
# Use higher quality data
# Train for more epochs
```

### 使用了错误的适配器

**问题**：模型使用了错误的适配器，或根本没有使用适配器。

**解决方案**：
```python
# Check active adapters
print(model.active_adapters)

# Explicitly set adapter
model.set_adapter("your-adapter-name")

# List all adapters
print(model.peft_config.keys())
```

## QLoRA 相关问题

### 量化错误

**错误信息**：`RuntimeError: mat1 和 mat2 的形状无法相乘`

**解决方案**：
```python
# Ensure compute dtype matches
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # Match model dtype
    bnb_4bit_quant_type="nf4"
)

# Load with correct dtype
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    torch_dtype=torch.bfloat16
)
```

### QLoRA 内存不足问题

**错误提示**：即使采用 4 位量化格式仍会出现内存不足错误。

**解决方案**：
```python
# Enable double quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True  # Further memory reduction
)

# Use offloading
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    max_memory={0: "20GB", "cpu": "100GB"}
)
```

### QLoRA 合并失败

**错误信息**：`RuntimeError: expected scalar type BFloat16 but found Float`

**解决方案**：
```python
# Dequantize before merging
from peft import PeftModel

# Load in higher precision for merging
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,  # Not quantized
    device_map="auto"
)

# Load adapter
model = PeftModel.from_pretrained(base_model, "./qlora-adapter")

# Now merge
merged = model.merge_and_unload()
```

## 多适配器相关问题

### 适配器冲突

**错误信息**：`ValueError: Adapter with name 'default' already exists`

**解决方案**：
```python
# Use unique names
model.load_adapter("./adapter1", adapter_name="task1")
model.load_adapter("./adapter2", adapter_name="task2")

# Or delete existing
model.delete_adapter("default")
```

### 混合精度适配器

**错误**：使用不同数据类型训练的适配器。

**解决方案**：
```python
# Convert adapter precision
model = PeftModel.from_pretrained(base_model, "./adapter")
model = model.to(torch.bfloat16)

# Or load with specific dtype
model = PeftModel.from_pretrained(
    base_model,
    "./adapter",
    torch_dtype=torch.bfloat16
)
```

## 性能优化

### 内存分析

```python
import torch

def print_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")

# Profile during training
print_memory()  # Before
model.train()
loss = model(**batch).loss
loss.backward()
print_memory()  # After
```

### 性能分析

```python
import time
import torch

def benchmark_generation(model, tokenizer, prompt, n_runs=5):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Warmup
    model.generate(**inputs, max_new_tokens=10)
    torch.cuda.synchronize()

    # Benchmark
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        outputs = model.generate(**inputs, max_new_tokens=100)
        torch.cuda.synchronize()
        times.append(time.perf_counter() - start)

    tokens = outputs.shape[1] - inputs.input_ids.shape[1]
    avg_time = sum(times) / len(times)
    print(f"Speed: {tokens/avg_time:.2f} tokens/sec")

# Compare adapter vs merged
benchmark_generation(adapter_model, tokenizer, "Hello")
benchmark_generation(merged_model, tokenizer, "Hello")
```

## 获取帮助

1. **查看 PEFT GitHub 问题列表**：https://github.com/huggingface/peft/issues
2. **HuggingFace 论坛**：https://discuss.huggingface.co/
3. **PEFT 文档**：https://huggingface.co/docs/peft

### 调试模板

在报告问题时，请包含以下内容：

```python
# System info
import peft
import transformers
import torch

print(f"PEFT: {peft.__version__}")
print(f"Transformers: {transformers.__version__}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")

# Config
print(model.peft_config)
model.print_trainable_parameters()
```
