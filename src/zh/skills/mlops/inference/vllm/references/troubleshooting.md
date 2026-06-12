# 故障排除指南

## 目录
- 内存不足（OOM）错误
- 性能问题
- 模型加载错误
- 网络与连接问题
- 量化问题
- 分布式服务问题
- 调试工具与命令

## 内存不足（OOM）错误

### 症状：在模型加载过程中出现 `torch.cuda.OutOfMemoryError` 错误

**原因**：模型数据与 KV 缓存占用的显存超过了可用容量

**解决方案（请按顺序尝试）**：

1. **降低 GPU 内存使用率**：
```bash
vllm serve MODEL --gpu-memory-utilization 0.7  # Try 0.7, 0.75, 0.8
```

2. **缩短最大序列长度**：
```bash
vllm serve MODEL --max-model-len 4096  # Instead of 8192
```

3. **启用量化功能**：
```bash
vllm serve MODEL --quantization awq  # 4x memory reduction
```

4. **使用张量并行技术**（多块 GPU）：
```bash
vllm serve MODEL --tensor-parallel-size 2  # Split across 2 GPUs
```

5. **降低最大并发序列数**：
```bash
vllm serve MODEL --max-num-seqs 128  # Default is 256
```

### 症状：推理过程中出现内存溢出（并非模型加载问题）

**原因**：在生成内容时 KV 缓存被占满

**解决方案**：

```bash
# Reduce KV cache allocation
vllm serve MODEL --gpu-memory-utilization 0.85

# Reduce batch size
vllm serve MODEL --max-num-seqs 64

# Reduce max tokens per request
# Set in client request: max_tokens=512
```

### 症状：量化模型导致内存溢出

**原因**：量化带来的额外开销或配置错误

**解决方案**：
```bash
# Ensure quantization flag matches model
vllm serve TheBloke/Llama-2-70B-AWQ --quantization awq  # Must specify

# Try different dtype
vllm serve MODEL --quantization awq --dtype float16
```

## 性能问题

### 症状：吞吐量过低（预期值＞100次/秒，实际值＜50次/秒）

**诊断步骤**：

1. **检查GPU使用率**：
```bash
watch -n 1 nvidia-smi
# GPU utilization should be >80%
```

如果该数值低于80%，则需增加并发请求数量：
```bash
vllm serve MODEL --max-num-seqs 512  # Increase from 256
```

2. **检查是否存在内存限制问题**：
```bash
# If memory at 100% but GPU <80%, reduce sequence length
vllm serve MODEL --max-model-len 4096
```

3. **启用优化功能**：
```bash
vllm serve MODEL \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --max-num-seqs 512
```

4. **检查张量并行设置**：
```bash
# Must use power-of-2 GPUs
vllm serve MODEL --tensor-parallel-size 4  # Not 3 or 5
```

### 症状：TTFT值过高（首次生成令牌的时间超过1秒）

**原因与解决方案**：

**提示词过长**：
```bash
vllm serve MODEL --enable-chunked-prefill
```

**不缓存前缀**：
```bash
vllm serve MODEL --enable-prefix-caching  # For repeated prompts
```

**并发请求过多**：
```bash
vllm serve MODEL --max-num-seqs 64  # Reduce to prioritize latency
```

**模型过大，无法在单块 GPU 上运行**：
```bash
vllm serve MODEL --tensor-parallel-size 2  # Parallelize prefill
```

### 症状：令牌生成速度缓慢（每秒生成的令牌数较低）

**诊断方法**：
```bash
# Check if model is correct size
vllm serve MODEL  # Should see model size in logs

# Check speculative decoding
vllm serve MODEL --speculative-model DRAFT_MODEL
```

**对于 H100 GPU**，请启用 FP8 模式：
```bash
vllm serve MODEL --quantization fp8
```

## 模型加载错误

### 症状：`OSError: MODEL未找到`

**原因**：

1. **模型名称拼写错误**：
```bash
# Check exact model name on HuggingFace
vllm serve meta-llama/Llama-3-8B-Instruct  # Correct capitalization
```

2. **私有/受限模型**：
```bash
# Login to HuggingFace first
huggingface-cli login
# Then run vLLM
vllm serve meta-llama/Llama-3-70B-Instruct
```

3. **自定义模型需要信任标志**：
```bash
vllm serve MODEL --trust-remote-code
```

### 症状：`ValueError: Tokenizer not found`

**解决方案**：
```bash
# Download model manually first
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('MODEL')"

# Then launch vLLM
vllm serve MODEL
```

### 症状：`ImportError: No module named 'flash_attn'`

**解决方案**：
```bash
# Install flash attention
pip install flash-attn --no-build-isolation

# Or disable flash attention
vllm serve MODEL --disable-flash-attn
```

## 网络与连接问题

### 症状：查询服务器时出现“连接被拒绝”错误

**诊断步骤**：

1. **检查服务器是否正在运行**：
```bash
curl http://localhost:8000/health
```

2. **检查端口绑定情况**：
```bash
# Bind to all interfaces for remote access
vllm serve MODEL --host 0.0.0.0 --port 8000

# Check if port is in use
lsof -i :8000
```

3. **检查防火墙设置**：
```bash
# Allow port through firewall
sudo ufw allow 8000
```

### 症状：网络传输导致的响应时间过慢

**解决方案**：

1. **增加超时时间**：
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
    timeout=300.0  # 5 minute timeout
)
```

2. **检查网络延迟**：
```bash
ping SERVER_IP  # Should be <10ms for local network
```

3. **使用连接池**：
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=3, backoff_factor=1)
session.mount('http://', HTTPAdapter(max_retries=retries))
```

## 量化相关问题

### 症状：`RuntimeError: Quantization format not supported`

**解决方案**：
```bash
# Ensure correct quantization method
vllm serve MODEL --quantization awq  # For AWQ models
vllm serve MODEL --quantization gptq  # For GPTQ models

# Check model card for quantization type
```

### 症状：量化后输出质量下降

**诊断步骤**：

1. **确认模型已正确完成量化**：
```bash
# Check model config.json for quantization_config
cat ~/.cache/huggingface/hub/models--MODEL/config.json
```

2. **尝试不同的量化方法**：
```bash
# If AWQ quality issues, try FP8 (H100 only)
vllm serve MODEL --quantization fp8

# Or use less aggressive quantization
vllm serve MODEL  # No quantization
```

3. **提高温度值以获得更多样化的结果**：
```python
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
```

## 分布式服务相关问题

### 症状：`RuntimeError: Distributed init failed`

**诊断步骤**：

1. **检查环境变量**：
```bash
# On all nodes
echo $MASTER_ADDR  # Should be same
echo $MASTER_PORT  # Should be same
echo $RANK  # Should be unique per node (0, 1, 2, ...)
echo $WORLD_SIZE  # Should be same (total nodes)
```

2. **检查网络连接状态**：
```bash
# From node 1 to node 2
ping NODE2_IP
nc -zv NODE2_IP 29500  # Check port accessibility
```

3. **检查 NCCL 设置**：
```bash
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=eth0  # Or your network interface
vllm serve MODEL --tensor-parallel-size 8
```

### 症状：`NCCL error: unhandled cuda error`

**解决方案**：

```bash
# Set NCCL to use correct network interface
export NCCL_SOCKET_IFNAME=eth0  # Replace with your interface

# Increase timeout
export NCCL_TIMEOUT=1800  # 30 minutes

# Force P2P for debugging
export NCCL_P2P_DISABLE=1
```

## 调试工具与命令

### 启用调试日志记录

```bash
export VLLM_LOGGING_LEVEL=DEBUG
vllm serve MODEL
```

### 监控 GPU 使用情况

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Memory breakdown
nvidia-smi --query-gpu=memory.used,memory.free --format=csv -l 1
```

### 配置文件性能表现

```bash
# Built-in benchmarking
vllm bench throughput \
  --model MODEL \
  --input-tokens 128 \
  --output-tokens 256 \
  --num-prompts 100

vllm bench latency \
  --model MODEL \
  --input-tokens 128 \
  --output-tokens 256 \
  --batch-size 8
```

### 查看指标数据

```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# Filter for specific metrics
curl http://localhost:9090/metrics | grep vllm_time_to_first_token

# Key metrics to monitor:
# - vllm_time_to_first_token_seconds
# - vllm_time_per_output_token_seconds
# - vllm_num_requests_running
# - vllm_gpu_cache_usage_perc
# - vllm_request_success_total
```

### 测试服务器运行状态检测

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/v1/models

# Test completion
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL",
    "prompt": "Hello",
    "max_tokens": 10
  }'
```

### 常见环境变量

```bash
# CUDA settings
export CUDA_VISIBLE_DEVICES=0,1,2,3  # Limit to specific GPUs

# vLLM settings
export VLLM_LOGGING_LEVEL=DEBUG
export VLLM_TRACE_FUNCTION=1  # Profile functions
export VLLM_USE_V1=1  # Use v1.0 engine (faster)

# NCCL settings (distributed)
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=eth0
export NCCL_IB_DISABLE=0  # Enable InfiniBand
```

### 收集用于错误报告的诊断信息

```bash
# System info
nvidia-smi
python --version
pip show vllm

# vLLM version and config
vllm --version
python -c "import vllm; print(vllm.__version__)"

# Run with debug logging
export VLLM_LOGGING_LEVEL=DEBUG
vllm serve MODEL 2>&1 | tee vllm_debug.log

# Include in bug report:
# - vllm_debug.log
# - nvidia-smi output
# - Full command used
# - Expected vs actual behavior
```
