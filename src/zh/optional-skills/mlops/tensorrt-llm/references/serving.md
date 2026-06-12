# 生产环境部署指南

关于如何在生产环境中部署 TensorRT-LLM 的全面指导手册。

## 服务器模式

### trtllm-serve（推荐）

**功能特点**：
- 兼容 OpenAI 的 API
- 自动模型下载与编译
- 内置负载均衡功能
- Prometheus 指标监控
- 健康状态检查

**基本使用方法**：
```bash
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --tp_size 1 \
    --max_batch_size 256 \
    --port 8000
```

**高级配置**：
```bash
trtllm-serve meta-llama/Meta-Llama-3-70B \
    --tp_size 4 \
    --dtype fp8 \
    --max_batch_size 256 \
    --max_num_tokens 4096 \
    --enable_chunked_context \
    --scheduler_policy max_utilization \
    --port 8000 \
    --api_key $API_KEY  # Optional authentication
```

### Python LLM API（用于嵌入计算）

```python
from tensorrt_llm import LLM

class LLMService:
    def __init__(self):
        self.llm = LLM(
            model="meta-llama/Meta-Llama-3-8B",
            dtype="fp8"
        )

    def generate(self, prompt, max_tokens=100):
        from tensorrt_llm import SamplingParams

        params = SamplingParams(
            max_tokens=max_tokens,
            temperature=0.7
        )
        outputs = self.llm.generate([prompt], params)
        return outputs[0].text

# Use in FastAPI, Flask, etc
from fastapi import FastAPI
app = FastAPI()
service = LLMService()

@app.post("/generate")
def generate(prompt: str):
    return {"response": service.generate(prompt)}
```

## 兼容 OpenAI 的 API

### 聊天补全功能

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
```

**响应**：
```json
{
  "id": "chat-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "meta-llama/Meta-Llama-3-8B",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Quantum computing is..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}
```

### 流式处理

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "messages": [{"role": "user", "content": "Count to 10"}],
    "stream": true
  }'
```

**响应**（SSE 流）：
```
data: {"choices":[{"delta":{"content":"1"}}]}

data: {"choices":[{"delta":{"content":", 2"}}]}

data: {"choices":[{"delta":{"content":", 3"}}]}

data: [DONE]
```

### 补全功能

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "prompt": "The capital of France is",
    "max_tokens": 10,
    "temperature": 0.0
  }'
```

## 监控

### Prometheus 指标

**启用指标收集**：
```bash
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --enable_metrics \
    --metrics_port 9090
```

**关键指标**：
```bash
# Scrape metrics
curl http://localhost:9090/metrics

# Important metrics:
# - trtllm_request_success_total - Total successful requests
# - trtllm_request_latency_seconds - Request latency histogram
# - trtllm_tokens_generated_total - Total tokens generated
# - trtllm_active_requests - Current active requests
# - trtllm_queue_size - Requests waiting in queue
# - trtllm_gpu_memory_usage_bytes - GPU memory usage
# - trtllm_kv_cache_usage_ratio - KV cache utilization
```

### 健康检查

```bash
# Readiness probe
curl http://localhost:8000/health/ready

# Liveness probe
curl http://localhost:8000/health/live

# Model info
curl http://localhost:8000/v1/models
```

**Kubernetes探针**：
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 5
```

## 生产环境部署

### Docker 部署

**Dockerfile**：
```dockerfile
FROM nvidia/tensorrt_llm:latest

# Copy any custom configs
COPY config.yaml /app/config.yaml

# Expose ports
EXPOSE 8000 9090

# Start server
CMD ["trtllm-serve", "meta-llama/Meta-Llama-3-8B", \
     "--tp_size", "4", \
     "--dtype", "fp8", \
     "--max_batch_size", "256", \
     "--enable_metrics", \
     "--metrics_port", "9090"]
```

**运行容器**：
```bash
docker run --gpus all -p 8000:8000 -p 9090:9090 \
    tensorrt-llm:latest
```

### Kubernetes 部署

**完整部署**：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tensorrt-llm
spec:
  replicas: 2  # Multiple replicas for HA
  selector:
    matchLabels:
      app: tensorrt-llm
  template:
    metadata:
      labels:
        app: tensorrt-llm
    spec:
      containers:
      - name: trtllm
        image: nvidia/tensorrt_llm:latest
        command:
          - trtllm-serve
          - meta-llama/Meta-Llama-3-70B
          - --tp_size=4
          - --dtype=fp8
          - --max_batch_size=256
          - --enable_metrics
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          limits:
            nvidia.com/gpu: 4
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: tensorrt-llm
spec:
  selector:
    app: tensorrt-llm
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

### 负载均衡

**NGINX 配置**：
```nginx
upstream tensorrt_llm {
    least_conn;  # Route to least busy server
    server trtllm-1:8000 max_fails=3 fail_timeout=30s;
    server trtllm-2:8000 max_fails=3 fail_timeout=30s;
    server trtllm-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    location / {
        proxy_pass http://tensorrt_llm;
        proxy_read_timeout 300s;  # Long timeout for slow generations
        proxy_connect_timeout 10s;
    }
}
```

## 自动扩缩容

### 水平 Pod 自动扩缩容器（HPA）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tensorrt-llm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tensorrt-llm
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: trtllm_active_requests
      target:
        type: AverageValue
        averageValue: "50"  # Scale when avg >50 active requests
```

### 自定义指标

```yaml
# Scale based on queue size
- type: Pods
  pods:
    metric:
      name: trtllm_queue_size
    target:
      type: AverageValue
      averageValue: "10"
```

## 成本优化

### GPU选择

**A100 80GB**（每小时3-4美元）：
- 适用场景：支持FP8格式的700亿参数模型
- 处理速度：10,000-15,000个token/秒（TP=4）
- 每100万个token的成本：0.20-0.30美元

**H100 80GB**（每小时6-8美元）：
- 适用场景：支持FP8格式的700亿参数模型以及4050亿参数模型
- 处理速度：20,000-30,000个token/秒（TP=4）
- 每100万个token的成本：0.15-0.25美元（处理速度提升2倍，成本相应降低）

**L4**（每小时0.50-1美元）：
- 适用场景：70-80亿参数模型
- 处理速度：1,000-2,000个token/秒
- 每100万个token的成本：0.25-0.50美元

### 批量大小调整

**对成本的影响**：
- 批量大小为1时：处理速度为1,000个token/秒，每小时每100万个token的成本为3美元，即每百万token成本为3美元
- 批量大小为64时：处理速度提升至5,000个token/秒，每小时每500万个token的成本为3美元，即每百万token成本为0.60美元
- 通过批量处理可实现**成本降低5倍**

**建议**：为兼顾成本效益，建议将批量大小设定在32-128之间。

## 安全性

### API认证

```bash
# Generate API key
export API_KEY=$(openssl rand -hex 32)

# Start server with authentication
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --api_key $API_KEY

# Client request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "...", "messages": [...]}'
```

### 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tensorrt-llm-policy
spec:
  podSelector:
    matchLabels:
      app: tensorrt-llm
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway  # Only allow from gateway
    ports:
    - protocol: TCP
      port: 8000
```

## 故障排除

### 高延迟问题

**诊断方法**：
```bash
# Check queue size
curl http://localhost:9090/metrics | grep queue_size

# Check active requests
curl http://localhost:9090/metrics | grep active_requests
```

**解决方案**：
- 水平扩展（增加副本数量）
- 提高批量处理大小（在GPU利用率不足时）
- 启用分块上下文功能（针对过长提示词）
- 使用FP8量化格式

### 内存溢出崩溃

**解决方案**：
- 减小`max_batch_size`值
- 降低`max_num_tokens`数值
- 启用FP8或INT4量化格式
- 增加`tensor_parallel_size`值

### 超时错误

**NGINX配置**：
```nginx
proxy_read_timeout 600s;  # 10 minutes for very long generations
proxy_send_timeout 600s;
```

## 最佳实践

1. 在 H100 上使用 FP8 格式，可实现速度提升 2 倍且成本降低 50%
2. **监控各项指标**——部署 Prometheus 与 Grafana 工具
3. **设置就绪探针**——避免将请求路由到状态不佳的容器
4. **采用负载均衡机制**——在多个副本之间分配请求负载
5. **调整批量处理大小**——在延迟与吞吐量之间取得平衡
6. **启用流式处理模式**——为聊天应用提升用户体验
7. **设置自动扩缩容功能**——有效应对流量峰值
8. **使用持久卷**——缓存已编译的模型文件
9. **实现重试机制**——处理临时性故障
10. **监控成本支出**——追踪每个令牌的成本情况
