# 模态高级使用指南

## 多 GPU 训练

### 单节点多 GPU 场景

```python
import modal

app = modal.App("multi-gpu-training")
image = modal.Image.debian_slim().pip_install("torch", "transformers", "accelerate")

@app.function(gpu="H100:4", image=image, timeout=7200)
def train_multi_gpu():
    from accelerate import Accelerator

    accelerator = Accelerator()
    model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

    for batch in dataloader:
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
```

### DeepSpeed集成方案

```python
image = modal.Image.debian_slim().pip_install(
    "torch", "transformers", "deepspeed", "accelerate"
)

@app.function(gpu="A100:8", image=image, timeout=14400)
def deepspeed_train(config: dict):
    from transformers import Trainer, TrainingArguments

    args = TrainingArguments(
        output_dir="/outputs",
        deepspeed="ds_config.json",
        fp16=True,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4
    )

    trainer = Trainer(model=model, args=args, train_dataset=dataset)
    trainer.train()
```

### 多 GPU 使用注意事项

对于会重新执行 Python 入口文件的框架（如 PyTorch Lightning），建议采用以下方式：
- 使用 `ddp_spawn` 或 `ddp_notebook` 战略
- 以子进程形式运行训练任务，以避免出现相关问题

```python
@app.function(gpu="H100:4")
def train_with_subprocess():
    import subprocess
    subprocess.run(["python", "-m", "torch.distributed.launch", "train.py"])
```

## 高级容器配置

### 用于缓存的多阶段构建

```python
# Stage 1: Base dependencies (cached)
base_image = modal.Image.debian_slim().pip_install("torch", "numpy", "scipy")

# Stage 2: ML libraries (cached separately)
ml_image = base_image.pip_install("transformers", "datasets", "accelerate")

# Stage 3: Custom code (rebuilt on changes)
final_image = ml_image.copy_local_dir("./src", "/app/src")
```

### 自定义 Dockerfile 文件

```python
image = modal.Image.from_dockerfile("./Dockerfile")
```

### 通过 Git 安装

```python
image = modal.Image.debian_slim().pip_install(
    "git+https://github.com/huggingface/transformers.git@main"
)
```

### 使用 uv 实现更快速的安装

```python
image = modal.Image.debian_slim().uv_pip_install(
    "torch", "transformers", "accelerate"
)
```

## 高级类模式

### 生命周期钩子

```python
@app.cls(gpu="A10G")
class InferenceService:
    @modal.enter()
    def startup(self):
        """Called once when container starts"""
        self.model = load_model()
        self.tokenizer = load_tokenizer()

    @modal.exit()
    def shutdown(self):
        """Called when container shuts down"""
        cleanup_resources()

    @modal.method()
    def predict(self, text: str):
        return self.model(self.tokenizer(text))
```

### 并发请求处理

```python
@app.cls(
    gpu="A100",
    allow_concurrent_inputs=20,  # Handle 20 requests per container
    container_idle_timeout=300
)
class BatchInference:
    @modal.enter()
    def load(self):
        self.model = load_model()

    @modal.method()
    def predict(self, inputs: list):
        return self.model.batch_predict(inputs)
```

### 输入并发与批量处理

- **输入并发**：同时处理多个请求（异步 I/O）
- **动态批量处理**：将请求汇总后统一处理（提升 GPU 效率）

```python
# Input concurrency - good for I/O-bound
@app.function(allow_concurrent_inputs=10)
async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        return await session.get(url)

# Dynamic batching - good for GPU inference
@app.function()
@modal.batched(max_batch_size=32, wait_ms=100)
async def batch_embed(texts: list[str]) -> list[list[float]]:
    return model.encode(texts)
```

## 高级卷功能

### 卷操作

```python
volume = modal.Volume.from_name("my-volume", create_if_missing=True)

@app.function(volumes={"/data": volume})
def volume_operations():
    import os

    # Write data
    with open("/data/output.txt", "w") as f:
        f.write("Results")

    # Commit changes (persist to volume)
    volume.commit()

    # Reload from remote (get latest)
    volume.reload()
```

### 函数间的共享卷

```python
shared_volume = modal.Volume.from_name("shared-data", create_if_missing=True)

@app.function(volumes={"/shared": shared_volume})
def writer():
    with open("/shared/data.txt", "w") as f:
        f.write("Hello from writer")
    shared_volume.commit()

@app.function(volumes={"/shared": shared_volume})
def reader():
    shared_volume.reload()  # Get latest
    with open("/shared/data.txt", "r") as f:
        return f.read()
```

### 云存储桶挂载

```python
# Mount S3 bucket
bucket = modal.CloudBucketMount(
    bucket_name="my-bucket",
    secret=modal.Secret.from_name("aws-credentials")
)

@app.function(volumes={"/s3": bucket})
def process_s3_data():
    # Access S3 files like local filesystem
    data = open("/s3/data.parquet").read()
```

## 函数组合

### 函数链式调用

```python
@app.function()
def preprocess(data):
    return cleaned_data

@app.function(gpu="T4")
def inference(data):
    return predictions

@app.function()
def postprocess(predictions):
    return formatted_results

@app.function()
def pipeline(raw_data):
    cleaned = preprocess.remote(raw_data)
    predictions = inference.remote(cleaned)
    results = postprocess.remote(predictions)
    return results
```

### 并行分发

```python
@app.function()
def process_item(item):
    return expensive_computation(item)

@app.function()
def parallel_pipeline(items):
    # Fan out: process all items in parallel
    results = list(process_item.map(items))
    return results
```

### 支持多个参数的星图功能

```python
@app.function()
def process(x, y, z):
    return x + y + z

@app.function()
def orchestrate():
    args = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    results = list(process.starmap(args))
    return results
```

## 高级 Web 端点

### WebSocket 支持

```python
from fastapi import FastAPI, WebSocket

app = modal.App("websocket-app")
web_app = FastAPI()

@web_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Processed: {data}")

@app.function()
@modal.asgi_app()
def ws_app():
    return web_app
```

### 流式响应输出

```python
from fastapi.responses import StreamingResponse

@app.function(gpu="A100")
def generate_stream(prompt: str):
    for token in model.generate_stream(prompt):
        yield token

@web_app.get("/stream")
async def stream_response(prompt: str):
    return StreamingResponse(
        generate_stream.remote_gen(prompt),
        media_type="text/event-stream"
    )
```

### 认证

```python
from fastapi import Depends, HTTPException, Header

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = authorization.split(" ")[1]
    if not verify_jwt(token):
        raise HTTPException(status_code=403)
    return token

@web_app.post("/predict")
async def predict(data: dict, token: str = Depends(verify_token)):
    return model.predict(data)
```

## 成本优化

### 合理配置 GPU 资源

```python
# For inference: smaller GPUs often sufficient
@app.function(gpu="L40S")  # 48GB, best cost/perf for inference
def inference():
    pass

# For training: larger GPUs for throughput
@app.function(gpu="A100-80GB")
def training():
    pass
```

### 为保障服务可用性而采用的 GPU 备用方案

```python
@app.function(gpu=["H100", "A100", "L40S"])  # Try in order
def flexible_compute():
    pass
```

### 降至零规模

```python
# Default behavior: scale to zero when idle
@app.function(gpu="A100")
def on_demand():
    pass

# Keep containers warm for low latency (costs more)
@app.function(gpu="A100", keep_warm=1)
def always_ready():
    pass
```

### 通过批量处理提升效率

```python
# Process in batches to reduce cold starts
@app.function(gpu="A100")
def batch_process(items: list):
    return [process(item) for item in items]

# Better than individual calls
results = batch_process.remote(all_items)
```

## 监控与可观测性

### 结构化日志记录

```python
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.function()
def structured_logging(request_id: str, data: dict):
    logger.info(json.dumps({
        "event": "inference_start",
        "request_id": request_id,
        "input_size": len(data)
    }))

    result = process(data)

    logger.info(json.dumps({
        "event": "inference_complete",
        "request_id": request_id,
        "output_size": len(result)
    }))

    return result
```

### 自定义指标

```python
@app.function(gpu="A100")
def monitored_inference(inputs):
    import time

    start = time.time()
    results = model.predict(inputs)
    latency = time.time() - start

    # Log metrics (visible in Modal dashboard)
    print(f"METRIC latency={latency:.3f}s batch_size={len(inputs)}")

    return results
```

## 生产环境部署

### 环境隔离

```python
import os

env = os.environ.get("MODAL_ENV", "dev")
app = modal.App(f"my-service-{env}")

# Environment-specific config
if env == "prod":
    gpu_config = "A100"
    timeout = 3600
else:
    gpu_config = "T4"
    timeout = 300
```

### 无停机部署

Modal 能够自动实现无停机部署流程：
1. 构建并启动新的容器
2. 逐步将流量引导至新版本
3. 旧容器处理剩余请求
4. 最终终止旧容器

### 健康检查

```python
@app.function()
@modal.web_endpoint()
def health():
    return {
        "status": "healthy",
        "model_loaded": hasattr(Model, "_model"),
        "gpu_available": torch.cuda.is_available()
    }
```

## 沙箱环境

### 交互式执行环境

```python
@app.function()
def run_sandbox():
    sandbox = modal.Sandbox.create(
        app=app,
        image=image,
        gpu="T4"
    )

    # Execute code in sandbox
    result = sandbox.exec("python", "-c", "print('Hello from sandbox')")

    sandbox.terminate()
    return result
```

## 调用已部署的函数

### 从外部代码调用

```python
# Call deployed function from any Python script
import modal

f = modal.Function.lookup("my-app", "my_function")
result = f.remote(arg1, arg2)
```

### REST API 调用

```bash
# Deployed endpoints accessible via HTTPS
curl -X POST https://your-workspace--my-app-predict.modal.run \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```
