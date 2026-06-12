# 模态界面故障排查指南

## 安装问题

### 认证失败

**错误信息**：`modal setup` 操作未完成或令牌无效

**解决方案**：
```bash
# Re-authenticate
modal token new

# Check current token
modal config show

# Set token via environment
export MODAL_TOKEN_ID=ak-...
export MODAL_TOKEN_SECRET=as-...
```

### 包安装问题

**错误**：`pip install modal` 命令执行失败

**解决方案**：
```bash
# Upgrade pip
pip install --upgrade pip

# Install with specific Python version
python3.11 -m pip install modal

# Install from wheel
pip install modal --prefer-binary
```

## 容器镜像相关问题

### 镜像构建失败

**错误信息**：`ImageBuilderError: Failed to build image`

**解决方案**：
```python
# Pin package versions to avoid conflicts
image = modal.Image.debian_slim().pip_install(
    "torch==2.1.0",
    "transformers==4.36.0",  # Pin versions
    "accelerate==0.25.0"
)

# Use compatible CUDA versions
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04",  # Match PyTorch CUDA
    add_python="3.11"
)
```

### 依赖冲突

**错误提示**：`ERROR: 由于存在依赖冲突，无法安装该软件包`

**解决方案**：
```python
# Layer dependencies separately
base = modal.Image.debian_slim().pip_install("torch")
ml = base.pip_install("transformers")  # Install after torch

# Use uv for better resolution
image = modal.Image.debian_slim().uv_pip_install(
    "torch", "transformers"
)
```

### 大尺寸图像构建超时

**错误提示**：图像构建耗时已超过限制

**解决方案**：
```python
# Split into multiple layers (better caching)
base = modal.Image.debian_slim().pip_install("torch")  # Cached
ml = base.pip_install("transformers", "datasets")      # Cached
app = ml.copy_local_dir("./src", "/app")               # Rebuilds on code change

# Download models during build, not runtime
image = modal.Image.debian_slim().pip_install("transformers").run_commands(
    "python -c 'from transformers import AutoModel; AutoModel.from_pretrained(\"bert-base\")'"
)
```

## GPU 相关问题

### 无法使用 GPU

**错误信息**：`RuntimeError: CUDA not available`

**解决方案**：
```python
# Ensure GPU is specified
@app.function(gpu="T4")  # Must specify GPU
def my_function():
    import torch
    assert torch.cuda.is_available()

# Check CUDA compatibility in image
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
    add_python="3.11"
).pip_install(
    "torch",
    index_url="https://download.pytorch.org/whl/cu121"  # Match CUDA
)
```

### GPU 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存已耗尽`

**解决方案**：
```python
# Use larger GPU
@app.function(gpu="A100-80GB")  # More VRAM
def train():
    pass

# Enable memory optimization
@app.function(gpu="A100")
def memory_optimized():
    import torch
    torch.backends.cuda.enable_flash_sdp(True)

    # Use gradient checkpointing
    model.gradient_checkpointing_enable()

    # Mixed precision
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        outputs = model(**inputs)
```

### 分配的 GPU 错误

**错误提示**：实际分配的 GPU 与请求不一致

**解决方案**：
```python
# Use strict GPU selection
@app.function(gpu="H100!")  # H100! prevents auto-upgrade to H200

# Specify exact memory variant
@app.function(gpu="A100-80GB")  # Not just "A100"

# Check GPU at runtime
@app.function(gpu="A100")
def check_gpu():
    import subprocess
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    print(result.stdout)
```

## 冷启动问题

### 冷启动速度过慢

**问题**：首次请求耗时过长

**解决方案**：
```python
# Keep containers warm
@app.function(
    container_idle_timeout=600,  # Keep warm 10 min
    keep_warm=1                  # Always keep 1 container ready
)
def low_latency():
    pass

# Load model during container start
@app.cls(gpu="A100")
class Model:
    @modal.enter()
    def load(self):
        # This runs once at container start, not per request
        self.model = load_heavy_model()

# Cache model in volume
volume = modal.Volume.from_name("models", create_if_missing=True)

@app.function(volumes={"/cache": volume})
def cached_model():
    if os.path.exists("/cache/model"):
        model = load_from_disk("/cache/model")
    else:
        model = download_model()
        save_to_disk(model, "/cache/model")
        volume.commit()
```

### 容器持续重启

**问题**：容器频繁被终止并重新启动

**解决方案**：
```python
# Increase memory
@app.function(memory=32768)  # 32GB RAM
def memory_heavy():
    pass

# Increase timeout
@app.function(timeout=3600)  # 1 hour
def long_running():
    pass

# Handle signals gracefully
import signal

def handler(signum, frame):
    cleanup()
    exit(0)

signal.signal(signal.SIGTERM, handler)
```

## 存储卷问题

### 存储卷更改无法持久保存

**错误现象**：写入存储卷的数据会消失

**解决方案**：
```python
volume = modal.Volume.from_name("my-volume", create_if_missing=True)

@app.function(volumes={"/data": volume})
def write_data():
    with open("/data/file.txt", "w") as f:
        f.write("data")

    # CRITICAL: Commit changes!
    volume.commit()
```

### 卷读取显示过时数据

**错误提示**：正在从卷中读取过旧的数据

**解决方案**：
```python
@app.function(volumes={"/data": volume})
def read_data():
    # Reload to get latest
    volume.reload()

    with open("/data/file.txt", "r") as f:
        return f.read()
```

### 卷挂载失败

**错误信息**：`VolumeError: 无法挂载卷`

**解决方案**：
```python
# Ensure volume exists
volume = modal.Volume.from_name("my-volume", create_if_missing=True)

# Use absolute path
@app.function(volumes={"/data": volume})  # Not "./data"
def my_function():
    pass

# Check volume in dashboard
# modal volume list
```

## Web 端点问题

### 端点返回 502 错误

**错误原因**：网关超时或网关故障

**解决方案**：
```python
# Increase timeout
@app.function(timeout=300)  # 5 min
@modal.web_endpoint()
def slow_endpoint():
    pass

# Return streaming response for long operations
from fastapi.responses import StreamingResponse

@app.function()
@modal.asgi_app()
def streaming_app():
    async def generate():
        for i in range(100):
            yield f"data: {i}\n\n"
            await process_chunk(i)
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 无法访问端点

**错误提示**：404 错误或无法连接到该端点

**解决方案**：
```bash
# Check deployment status
modal app list

# Redeploy
modal deploy my_app.py

# Check logs
modal app logs my-app
```

### CORS 错误

**错误提示**：跨域请求被阻止

**解决方案**：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.function()
@modal.asgi_app()
def cors_enabled():
    return web_app
```

## 密钥相关问题

### 未找到密钥

**错误信息**：`SecretNotFound: 未找到名为 ‘my-secret’ 的密钥`

**解决方案**：
```bash
# Create secret via CLI
modal secret create my-secret KEY=value

# List secrets
modal secret list

# Check secret name matches exactly
```

### 无法访问密钥值

**错误原因**：环境变量为空

**解决方案**：
```python
# Ensure secret is attached
@app.function(secrets=[modal.Secret.from_name("my-secret")])
def use_secret():
    import os
    value = os.environ.get("KEY")  # Use get() to handle missing
    if not value:
        raise ValueError("KEY not set in secret")
```

## 计划任务相关问题

### 计划任务未运行

**错误提示**：Cron 任务未能执行

**解决方案**：
```python
# Verify cron syntax
@app.function(schedule=modal.Cron("0 0 * * *"))  # Daily at midnight UTC
def daily_job():
    pass

# Check timezone (Modal uses UTC)
# "0 8 * * *" = 8am UTC, not local time

# Ensure app is deployed
# modal deploy my_app.py
```

### 任务重复运行

**问题**：定时任务的执行次数超出预期

**解决方案**：
```python
# Implement idempotency
@app.function(schedule=modal.Cron("0 * * * *"))
def hourly_job():
    job_id = get_current_hour_id()
    if already_processed(job_id):
        return
    process()
    mark_processed(job_id)
```

## 调试技巧

### 启用调试日志记录

```python
import logging
logging.basicConfig(level=logging.DEBUG)

@app.function()
def debug_function():
    logging.debug("Debug message")
    logging.info("Info message")
```

### 查看容器日志

```bash
# Stream logs
modal app logs my-app

# View specific function
modal app logs my-app --function my_function

# View historical logs
modal app logs my-app --since 1h
```

### 在本地进行测试

```python
# Run function locally without Modal
if __name__ == "__main__":
    result = my_function.local()  # Runs on your machine
    print(result)
```

### 检查容器

```python
@app.function(gpu="T4")
def debug_environment():
    import subprocess
    import sys

    # System info
    print(f"Python: {sys.version}")
    print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout)
    print(subprocess.run(["pip", "list"], capture_output=True, text=True).stdout)

    # CUDA info
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## 常见错误信息

| 错误代码 | 原因 | 解决方案 |
|---------|------|----------|
| `FunctionTimeoutError` | 函数执行超时 | 增大 `timeout` 参数值 |
| `ContainerMemoryExceeded` | 内存不足导致进程被终止 | 增大 `memory` 参数值 |
| `ImageBuilderError` | 镜像构建失败 | 检查依赖项并锁定版本 |
| `ResourceExhausted` | 无可用 GPU | 使用 GPU 替代方案，稍后再试 |
| `AuthenticationError` | 令牌无效 | 运行 `modal token new` 命令生成新令牌 |
| `VolumeNotFound` | 存储卷不存在 | 设置 `create_if_missing=True` 参数自动创建 |
| `SecretNotFound` | 密钥不存在 | 通过 CLI 命令创建密钥 |

## 获取帮助

1. **文档中心**：https://modal.com/docs
2. **示例代码**：https://github.com/modal-labs/modal-examples
3. **Discord 社区**：https://discord.gg/modal
4. **服务状态页**：https://status.modal.com

### 报告问题时请提供以下信息：

- Modal 客户端版本：`modal --version`
- Python 版本：`python --version`
- 完整的错误堆栈信息
- 最简可复现代码示例
- 如涉及 GPU，请说明 GPU 类型 |
