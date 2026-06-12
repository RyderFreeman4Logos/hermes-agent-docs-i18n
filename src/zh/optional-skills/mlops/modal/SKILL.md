---
name: modal-serverless-gpu
description: Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access without infrastructure management, deploying ML models as APIs, or running batch jobs with automatic scaling.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [modal>=0.64.0]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Infrastructure, Serverless, GPU, Cloud, Deployment, Modal]

---

# Modal Serverless GPU

关于在Modal的无服务器GPU云平台上运行机器学习工作负载的完整指南。

## 何时选择Modal

**以下情况适合使用Modal：**
- 运行对GPU性能要求极高的机器学习任务，且无需自行管理基础设施
- 将机器学习模型部署为可自动扩展的API
- 执行批处理任务（训练、推理、数据处理）
- 需要按秒计费的GPU使用模式，避免资源闲置产生的额外成本
- 快速开发机器学习应用原型
- 运行定时任务（类似cron的任务调度）

**核心功能：**
- **无服务器GPU**：支持按需使用T4、L4、A10G、L40S、A100、H100、H200、B200等型号的GPU
- **原生Python支持**：可通过Python代码定义基础设施，无需使用YAML配置文件
- **自动扩展**：可瞬间将资源扩展至零，或扩展至100多台GPU
- **亚秒级冷启动**：基于Rust技术的基础设施，可实现快速容器启动
- **容器缓存**：对镜像层进行缓存，加快迭代速度
- **Web端点**：可将功能以REST API形式部署，并实现无停机更新

**如需其他选择，请考虑：**
- **RunPod**：适用于需要持久化状态的长时间运行的容器任务
- **Lambda Labs**：适合需要预留GPU实例的场景
- **SkyPilot**：用于多云环境下的任务编排及成本优化
- **Kubernetes**：适用于复杂的多服务架构

## 快速入门

### 安装

```bash
pip install modal
modal setup  # Opens browser for authentication
```

### 使用 GPU 实现“Hello World”示例

```python
import modal

app = modal.App("hello-gpu")

@app.function(gpu="T4")
def gpu_info():
    import subprocess
    return subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout

@app.local_entrypoint()
def main():
    print(gpu_info.remote())
```

运行命令：`modal run hello_gpu.py`

### 基本推理接口

```python
import modal

app = modal.App("text-generation")
image = modal.Image.debian_slim().pip_install("transformers", "torch", "accelerate")

@app.cls(gpu="A10G", image=image)
class TextGenerator:
    @modal.enter()
    def load_model(self):
        from transformers import pipeline
        self.pipe = pipeline("text-generation", model="gpt2", device=0)

    @modal.method()
    def generate(self, prompt: str) -> str:
        return self.pipe(prompt, max_length=100)[0]["generated_text"]

@app.local_entrypoint()
def main():
    print(TextGenerator().generate.remote("Hello, world"))
```

## 核心概念

### 主要组件

| 组件 | 功能 |
|------|------|
| `App` | 函数与资源的容器 |
| `Function` | 具有计算规格的无服务器函数 |
| `Cls` | 带有生命周期钩子的基于类的函数 |
| `Image` | 容器镜像定义 |
| `Volume` | 模型/数据的持久化存储 |
| `Secret` | 安全的凭据存储 |

### 执行模式

| 命令 | 描述 |
|------|------|
| `modal run script.py` | 执行后退出 |
| `modal serve script.py` | 支持实时热重载的开发模式 |
| `modal deploy script.py` | 持久化的云端部署 |

## GPU 配置

### 可用 GPU

| GPU | VRAM容量 | 最佳适用场景 |
|-----|---------|------------|
| `T4` | 16GB | 预算型推理任务及小型模型 |
| `L4` | 24GB | 推理任务，采用Ada Lovelace架构 |
| `A10G` | 24GB | 训练/推理任务，性能是T4的3.3倍 |
| `L40S` | 48GB | 推理任务的推荐选择（性价比最高） |
| `A100-40GB` | 40GB | 大型模型训练 |
| `A100-80GB` | 80GB | 超大型模型 |
| `H100` | 80GB | 性能最快，支持FP8格式及Transformer引擎 |
| `H200` | 141GB | 可由H100自动升级，带宽达4.8TB/s |
| `B200` | 最新款 | 采用Blackwell架构 |

### GPU规格模式

```python
# Single GPU
@app.function(gpu="A100")

# Specific memory variant
@app.function(gpu="A100-80GB")

# Multiple GPUs (up to 8)
@app.function(gpu="H100:4")

# GPU with fallbacks
@app.function(gpu=["H100", "A100", "L40S"])

# Any available GPU
@app.function(gpu="any")
```

## 容器镜像

```python
# Basic image with pip
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.0", "transformers==4.36.0", "accelerate"
)

# From CUDA base
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
    add_python="3.11"
).pip_install("torch", "transformers")

# With system packages
image = modal.Image.debian_slim().apt_install("git", "ffmpeg").pip_install("whisper")
```

## 持久化存储

```python
volume = modal.Volume.from_name("model-cache", create_if_missing=True)

@app.function(gpu="A10G", volumes={"/models": volume})
def load_model():
    import os
    model_path = "/models/llama-7b"
    if not os.path.exists(model_path):
        model = download_model()
        model.save_pretrained(model_path)
        volume.commit()  # Persist changes
    return load_from_path(model_path)
```

## Web 接口端点

### FastAPI 接口端点装饰器

```python
@app.function()
@modal.fastapi_endpoint(method="POST")
def predict(text: str) -> dict:
    return {"result": model.predict(text)}
```

### 完整的 ASGI 应用程序

```python
from fastapi import FastAPI
web_app = FastAPI()

@web_app.post("/predict")
async def predict(text: str):
    return {"result": await model.predict.remote.aio(text)}

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app
```

### Web端点类型

| 装饰器 | 使用场景 |
|-----------|----------|
| `@modal.fastapi_endpoint()` | 简单函数 → API |
| `@modal.asgi_app()` | 完整的FastAPI/Starlette应用 |
| `@modal.wsgi_app()` | Django/Flask应用 |
| `@modal.web_server(port)` | 任意HTTP服务器 |

## 动态批量处理

```python
@app.function()
@modal.batched(max_batch_size=32, wait_ms=100)
async def batch_predict(inputs: list[str]) -> list[dict]:
    # Inputs automatically batched
    return model.batch_predict(inputs)
```

## 密钥管理

```bash
# Create secret
modal secret create huggingface HF_TOKEN=hf_xxx
```

```python
@app.function(secrets=[modal.Secret.from_name("huggingface")])
def download_model():
    import os
    token = os.environ["HF_TOKEN"]
```

## 日程安排

```python
@app.function(schedule=modal.Cron("0 0 * * *"))  # Daily midnight
def daily_job():
    pass

@app.function(schedule=modal.Period(hours=1))
def hourly_job():
    pass
```

## 性能优化

### 缓解冷启动问题

```python
@app.function(
    container_idle_timeout=300,  # Keep warm 5 min
    allow_concurrent_inputs=10,  # Handle concurrent requests
)
def inference():
    pass
```

### 模型加载最佳实践

```python
@app.cls(gpu="A100")
class Model:
    @modal.enter()  # Run once at container start
    def load(self):
        self.model = load_model()  # Load during warm-up

    @modal.method()
    def predict(self, x):
        return self.model(x)
```

## 并行处理

```python
@app.function()
def process_item(item):
    return expensive_computation(item)

@app.function()
def run_parallel():
    items = list(range(1000))
    # Fan out to parallel containers
    results = list(process_item.map(items))
    return results
```

## 常见配置

```python
@app.function(
    gpu="A100",
    memory=32768,              # 32GB RAM
    cpu=4,                     # 4 CPU cores
    timeout=3600,              # 1 hour max
    container_idle_timeout=120,# Keep warm 2 min
    retries=3,                 # Retry on failure
    concurrency_limit=10,      # Max concurrent containers
)
def my_function():
    pass
```

## 调试

```python
# Test locally
if __name__ == "__main__":
    result = my_function.local()

# View logs
# modal app logs my-app
```

## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 冷启动延迟 | 增大 `container_idle_timeout` 的值，使用 `@modal.enter()` |
| GPU 内存不足 | 使用容量更大的 GPU（如 `A100-80GB`），启用梯度检查点功能 |
| 图像构建失败 | 固定依赖版本的编号，检查 CUDA 兼容性 |
| 超时错误 | 增大 `timeout` 的值，添加检查点机制 |

## 参考资料

- **[高级用法](references/advanced-usage.md)** - 多 GPU 使用、分布式训练、成本优化
- **[故障排查](references/troubleshooting.md)** - 常见问题及解决方案

## 资源链接

- **文档**：https://modal.com/docs
- **示例代码**：https://github.com/modal-labs/modal-examples
- **定价信息**：https://modal.com/pricing
- **Discord 社区**：https://discord.gg/modal
