# 服务器部署模式

## 目录
- Docker部署
- Kubernetes部署
- 使用Nginx实现负载均衡
- 多节点分布式服务架构
- 生产环境配置示例
- 健康检查与监控

## Docker部署

**基础Dockerfile**：
```dockerfile
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip
RUN pip install vllm

EXPOSE 8000

CMD ["vllm", "serve", "meta-llama/Llama-3-8B-Instruct", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--gpu-memory-utilization", "0.9"]
```

**构建与运行**：
```bash
docker build -t vllm-server .
docker run --gpus all -p 8000:8000 vllm-server
```

**Docker Compose**（支持指标功能）：
```yaml
version: '3.8'
services:
  vllm:
    image: vllm/vllm-openai:latest
    command: >
      --model meta-llama/Llama-3-8B-Instruct
      --gpu-memory-utilization 0.9
      --enable-metrics
      --metrics-port 9090
    ports:
      - "8000:8000"
      - "9090:9090"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## Kubernetes 部署

**部署清单**：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
          - "--model=meta-llama/Llama-3-8B-Instruct"
          - "--gpu-memory-utilization=0.9"
          - "--enable-prefix-caching"
        resources:
          limits:
            nvidia.com/gpu: 1
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
spec:
  selector:
    app: vllm
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  - port: 9090
    targetPort: 9090
    name: metrics
  type: LoadBalancer
```

## 使用 Nginx 进行负载均衡

**Nginx 配置**：
```nginx
upstream vllm_backend {
    least_conn;  # Route to least-loaded server
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;

    location / {
        proxy_pass http://vllm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Timeouts for long-running inference
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Metrics endpoint
    location /metrics {
        proxy_pass http://localhost:9090/metrics;
    }
}
```

**启动多个 vLLM 实例**：
```bash
# Terminal 1
vllm serve MODEL --port 8001 --tensor-parallel-size 1

# Terminal 2
vllm serve MODEL --port 8002 --tensor-parallel-size 1

# Terminal 3
vllm serve MODEL --port 8003 --tensor-parallel-size 1

# Start Nginx
nginx -c /path/to/nginx.conf
```

## 多节点分布式服务

针对那些体积过大而无法在单个节点上运行的模型：

**节点 1**（主节点）：
```bash
export MASTER_ADDR=192.168.1.10
export MASTER_PORT=29500
export RANK=0
export WORLD_SIZE=2

vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 8 \
  --pipeline-parallel-size 2
```

**节点 2**（工作节点）：
```bash
export MASTER_ADDR=192.168.1.10
export MASTER_PORT=29500
export RANK=1
export WORLD_SIZE=2

vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 8 \
  --pipeline-parallel-size 2
```

## 生产环境配置示例

**高吞吐量场景**（以批量处理为主的工作负载）：
```bash
vllm serve MODEL \
  --max-num-seqs 512 \
  --gpu-memory-utilization 0.95 \
  --enable-prefix-caching \
  --trust-remote-code
```

**低延迟**（交互式工作负载）：
```bash
vllm serve MODEL \
  --max-num-seqs 64 \
  --gpu-memory-utilization 0.85 \
  --enable-chunked-prefill
```

**内存受限场景**（70B模型需配备40GB显存）：
```bash
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95 \
  --max-model-len 4096
```

## 健康检查与监控

**健康检查端点**：
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok"}
```

**就绪状态检查**（等待模型加载完成）：
```bash
#!/bin/bash
until curl -f http://localhost:8000/health; do
    echo "Waiting for vLLM to be ready..."
    sleep 5
done
echo "vLLM is ready!"
```

**Prometheus 数据抓取**：
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'vllm'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**Grafana仪表板**（核心指标）：
- 每秒请求数：`rate(vllm_request_success_total[5m])`
- 首个token生成时间的中位数（p50）：`histogram_quantile(0.5, vllm_time_to_first_token_seconds_bucket)`
- 首个token生成时间的99百分位数（p99）：`histogram_quantile(0.99, vllm_time_to_first_token_seconds_bucket)`
- GPU缓存使用率：`vllm_gpu_cache_usage_perc`
- 正在处理的请求数：`vllm_num_requests_running`
