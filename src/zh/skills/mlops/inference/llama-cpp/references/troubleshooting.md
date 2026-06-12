# GGUF故障排查指南

## 安装问题

### 构建失败

**错误信息**：`make: *** 未指定目标，且未找到makefile`

**解决方案**：
```bash
# Ensure you're in llama.cpp directory
cd llama.cpp
make
```

**错误提示**：`致命错误：cuda_runtime.h：找不到该文件或目录`

**解决方案**：
```bash
# Install CUDA toolkit
# Ubuntu
sudo apt install nvidia-cuda-toolkit

# Or set CUDA path
export CUDA_PATH=/usr/local/cuda
export PATH=$CUDA_PATH/bin:$PATH
make GGML_CUDA=1
```

### Python绑定相关问题

**错误信息**：`ERROR: Failed building wheel for llama-cpp-python`

**解决方案**：
```bash
# Install build dependencies
pip install cmake scikit-build-core

# For CUDA support
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# For Metal (macOS)
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**错误提示**：`ImportError: libcudart.so.XX: 无法打开共享对象文件`

**解决方案**：
```bash
# Add CUDA libraries to path
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Or reinstall with correct CUDA version
pip uninstall llama-cpp-python
CUDACXX=/usr/local/cuda/bin/nvcc CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

## 转换问题

### 不支持的模型

**错误信息**：`KeyError: 'model.embed_tokens.weight'`

**解决方案**：
```bash
# Check model architecture
python -c "from transformers import AutoConfig; print(AutoConfig.from_pretrained('./model').architectures)"

# Use appropriate conversion script
# For most models:
python convert_hf_to_gguf.py ./model --outfile model.gguf

# For older models, check if legacy script needed
```

### 词汇表不匹配

**错误信息**：`RuntimeError: Vocabulary size mismatch`

**解决方案**：
```python
# Ensure tokenizer matches model
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("./model")
model = AutoModelForCausalLM.from_pretrained("./model")

print(f"Tokenizer vocab size: {len(tokenizer)}")
print(f"Model vocab size: {model.config.vocab_size}")

# If mismatch, resize embeddings before conversion
model.resize_token_embeddings(len(tokenizer))
model.save_pretrained("./model-fixed")
```

### 转换过程中内存不足

**错误信息**：转换过程中出现 `torch.cuda.OutOfMemoryError` 错误。

**解决方案**：
```bash
# Use CPU for conversion
CUDA_VISIBLE_DEVICES="" python convert_hf_to_gguf.py ./model --outfile model.gguf

# Or use low memory mode
python convert_hf_to_gguf.py ./model --outfile model.gguf --outtype f16
```

## 量化相关问题

### 输出文件大小异常

**问题**：量化后的文件大小超出预期

**检查步骤**：
```bash
# Verify quantization type
./llama-cli -m model.gguf --verbose

# Expected sizes for 7B model:
# Q4_K_M: ~4.1 GB
# Q5_K_M: ~4.8 GB
# Q8_0: ~7.2 GB
# F16: ~13.5 GB
```

### 量化导致的崩溃问题

**错误信息**：量化过程中出现“段错误”（Segmentation fault）

**解决方案**：
```bash
# Increase stack size
ulimit -s unlimited

# Or use less threads
./llama-quantize -t 4 model-f16.gguf model-q4.gguf Q4_K_M
```

### 量化后的质量下降问题

**问题**：模型在经过量化处理后输出无意义的乱码

**解决方案**：

1. **使用重要性矩阵**：
```bash
# Generate imatrix with good calibration data
./llama-imatrix -m model-f16.gguf \
    -f wiki_sample.txt \
    --chunk 512 \
    -o model.imatrix

# Quantize with imatrix
./llama-quantize --imatrix model.imatrix \
    model-f16.gguf model-q4_k_m.gguf Q4_K_M
```

2. **尝试使用更高精度**：
```bash
# Use Q5_K_M or Q6_K instead of Q4
./llama-quantize model-f16.gguf model-q5_k_m.gguf Q5_K_M
```

3. **检查原始模型**：
```bash
# Test FP16 version first
./llama-cli -m model-f16.gguf -p "Hello, how are you?" -n 50
```

## 推理问题

### 生成速度过慢

**问题**：内容生成速度低于预期

**解决方案**：

1. **启用 GPU 卸载功能**：
```bash
./llama-cli -m model.gguf -ngl 35 -p "Hello"
```

2. **优化批量处理大小**：
```python
llm = Llama(
    model_path="model.gguf",
    n_batch=512,        # Increase for faster prompt processing
    n_gpu_layers=35
)
```

3. **使用合适的线程**：
```bash
# Match physical cores, not logical
./llama-cli -m model.gguf -t 8 -p "Hello"
```

4. **启用 Flash Attention**（如受支持）：
```bash
./llama-cli -m model.gguf -ngl 35 --flash-attn -p "Hello"
```

### 内存不足

**错误提示**：`CUDA内存不足` 或系统卡死

**解决方案**：

1. **减少GPU层数量**：
```python
# Start low and increase
llm = Llama(model_path="model.gguf", n_gpu_layers=10)
```

2. **使用较低的量化级别**：
```bash
./llama-quantize model-f16.gguf model-q3_k_m.gguf Q3_K_M
```

3. **缩短上下文长度**：
```python
llm = Llama(
    model_path="model.gguf",
    n_ctx=2048,  # Reduce from 4096
    n_gpu_layers=35
)
```

4. **量化 KV 缓存**：
```python
llm = Llama(
    model_path="model.gguf",
    type_k=2,    # Q4_0 for K cache
    type_v=2,    # Q4_0 for V cache
    n_gpu_layers=35
)
```

### 无意义输出问题

**问题**：模型输出随机字符或无意义内容

**诊断方法**：
```python
# Check model loading
llm = Llama(model_path="model.gguf", verbose=True)

# Test with simple prompt
output = llm("1+1=", max_tokens=5, temperature=0)
print(output)
```

**解决方案**：

1. **检查模型完整性**：
```bash
# Verify GGUF file
./llama-cli -m model.gguf --verbose 2>&1 | head -50
```

2. **使用正确的聊天格式**：
```python
llm = Llama(
    model_path="model.gguf",
    chat_format="llama-3"  # Match your model: chatml, mistral, etc.
)
```

3. **检测温度**：
```python
# Use lower temperature for deterministic output
output = llm("Hello", max_tokens=50, temperature=0.1)
```

### 令牌相关问题

**错误提示**：`RuntimeError: unknown token` 或编码错误

**解决方案**：
```python
# Ensure UTF-8 encoding
prompt = "Hello, world!".encode('utf-8').decode('utf-8')
output = llm(prompt, max_tokens=50)
```

## 服务器问题

### 连接被拒绝

**错误提示**：访问服务器时出现“连接被拒绝”错误。

**解决方案**：
```bash
# Bind to all interfaces
./llama-server -m model.gguf --host 0.0.0.0 --port 8080

# Check if port is in use
lsof -i :8080
```

### 服务器在负载过高时崩溃

**问题**：在处理多个并发请求时服务器发生崩溃

**解决方案**：

1. **限制并行处理数量**：
```bash
./llama-server -m model.gguf \
    --parallel 2 \
    -c 4096 \
    --cont-batching
```

2. **设置请求超时时间**：
```bash
./llama-server -m model.gguf --timeout 300
```

3. **监控内存使用情况**：
```bash
watch -n 1 nvidia-smi  # For GPU
watch -n 1 free -h     # For RAM
```

### API 兼容性问题

**问题**：OpenAI 客户端无法与服务器正常配合使用

**解决方案**：
```python
from openai import OpenAI

# Use correct base URL format
client = OpenAI(
    base_url="http://localhost:8080/v1",  # Include /v1
    api_key="not-needed"
)

# Use correct model name
response = client.chat.completions.create(
    model="local",  # Or the actual model name
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Apple Silicon 相关问题

### Metal 功能无法使用

**问题**：未启用 Metal 加速功能

**检查步骤**：
```bash
# Verify Metal support
./llama-cli -m model.gguf --verbose 2>&1 | grep -i metal
```

**修复**：
```bash
# Rebuild with Metal
make clean
make GGML_METAL=1

# Python bindings
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --force-reinstall
```

### M1/M2 芯片上的内存使用异常

**问题**：模型占用了过多的统一内存

**解决方案**：
```python
# Offload all layers for Metal
llm = Llama(
    model_path="model.gguf",
    n_gpu_layers=99,    # Offload everything
    n_threads=1         # Metal handles parallelism
)
```

## 调试

### 启用详细输出功能

```bash
# CLI verbose mode
./llama-cli -m model.gguf --verbose -p "Hello" -n 50

# Python verbose
llm = Llama(model_path="model.gguf", verbose=True)
```

### 查看模型元数据

```bash
# View GGUF metadata
./llama-cli -m model.gguf --verbose 2>&1 | head -100
```

### 验证 GGUF 文件

```python
import struct

def validate_gguf(filepath):
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic != b'GGUF':
            print(f"Invalid magic: {magic}")
            return False

        version = struct.unpack('<I', f.read(4))[0]
        print(f"GGUF version: {version}")

        tensor_count = struct.unpack('<Q', f.read(8))[0]
        metadata_count = struct.unpack('<Q', f.read(8))[0]
        print(f"Tensors: {tensor_count}, Metadata: {metadata_count}")

        return True

validate_gguf("model.gguf")
```

## 获取帮助

1. **GitHub 问题追踪**: https://github.com/ggml-org/llama.cpp/issues  
2. **讨论区**: https://github.com/ggml-org/llama.cpp/discussions  
3. **Reddit 论坛**: r/LocalLLaMA  

### 报告问题时请提供以下信息：

- llama.cpp 的版本及提交哈希值  
- 使用的构建命令  
- 模型名称及量化格式  
- 完整的错误信息或堆栈跟踪  
- 硬件配置：CPU/GPU型号、内存容量、显存容量  
- 操作系统版本  
- 最简问题复现步骤
