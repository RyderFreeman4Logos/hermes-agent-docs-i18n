# 服务器部署指南

基于兼容 OpenAI API 的方式部署 llama.cpp 服务器以用于生产环境。

## 直接从 Hugging Face Hub 部署

建议首先查看模型仓库的 local-app 页面：

```text
https://huggingface.co/<repo>?local-app=llama.cpp
```

如果页面上显示了完整的代码片段，请直接复制它。若未显示，则可使用以下任一格式：

```bash
# Choose a quant label directly from the Hub repo
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

```bash
# Pin an exact GGUF file from the repo tree
llama-server \
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf \
    -c 4096
```

当代码仓库采用自定义命名规则，或您已通过 tree API 获取到确切的文件名时，请使用针对该文件的专用表单。

## 服务器模式

### llama-server

```bash
# Basic server
./llama-server \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -c 4096  # Context size

# With GPU acceleration
./llama-server \
    -m models/llama-2-70b.Q4_K_M.gguf \
    -ngl 40  # Offload 40 layers to GPU
```

## 兼容 OpenAI 的 API

### 聊天内容补全功能
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-2",
    "messages": [
      {"role": "system", "content": "You are helpful"},
      {"role": "user", "content": "Hello"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### 流式处理
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-2",
    "messages": [{"role": "user", "content": "Count to 10"}],
    "stream": true
  }'
```

## Docker 部署

**Dockerfile**：
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y git build-essential
RUN git clone https://github.com/ggerganov/llama.cpp
WORKDIR /llama.cpp
RUN make LLAMA_CUDA=1
COPY models/ /models/
EXPOSE 8080
CMD ["./llama-server", "-m", "/models/model.gguf", "--host", "0.0.0.0", "--port", "8080"]
```

**运行**：
```bash
docker run --gpus all -p 8080:8080 llama-cpp:latest
```

## 监控功能

```bash
# Server metrics endpoint
curl http://localhost:8080/metrics

# Health check
curl http://localhost:8080/health
```

**指标**：
- requests_total
- tokens_generated
- prompt_tokens
- completion_tokens
- kv_cache_tokens

## 负载均衡

**NGINX**：
```nginx
upstream llama_cpp {
    server llama1:8080;
    server llama2:8080;
}

server {
    location / {
        proxy_pass http://llama_cpp;
        proxy_read_timeout 300s;
    }
}
```

## 性能调优

**并行请求**：
```bash
./llama-server \
    -m model.gguf \
    -np 4  # 4 parallel slots
```

**连续批处理**：
```bash
./llama-server \
    -m model.gguf \
    --cont-batching  # Enable continuous batching
```

**上下文缓存**：
```bash
./llama-server \
    -m model.gguf \
    --cache-prompt  # Cache processed prompts
```
