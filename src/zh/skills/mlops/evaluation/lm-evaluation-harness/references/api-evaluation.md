# API评估

本指南介绍如何评估OpenAI、Anthropic以及其他基于API的语言模型。

## 概述

lm-evaluation-harness通过统一的`TemplateAPI`接口来支持对基于API的模型进行评估。借此可以对比测试以下模型：
- OpenAI模型（GPT-4、GPT-3.5等）
- Anthropic模型（Claude 3、Claude 2等）
- 本地兼容OpenAI的API
- 自定义API端点

**为何要评估API模型**：
- 对比测试闭源模型
- 将API模型与开源模型进行比较
- 验证API的性能表现
- 跟踪模型随时间的更新情况

## 支持的API模型

| 提供商 | 模型类型 | 请求类型 | 对数概率 |
|--------|----------|-----------|----------|
| OpenAI（补全型） | `openai-completions` | 全部类型 | ✅ 支持 |
| OpenAI（聊天型） | `openai-chat-completions` | 仅`generate_until` | ❌ 不支持 |
| Anthropic（补全型） | `anthropic-completions` | 全部类型 | ❌ 不支持 |
| Anthropic（聊天型） | `anthropic-chat` | 仅`generate_until` | ❌ 不支持 |
| 本地（兼容OpenAI） | `local-completions` | 视服务器配置而定 | 不固定 |

**注意**：不支持对数概率的模型仅能用于生成任务评估，无法用于困惑度或对数似然度测试。

## OpenAI模型

### 设置步骤

```bash
export OPENAI_API_KEY=sk-...
```

### 完成模型（旧版）

**可用模型**：`davinci-002`、`babbage-002`

```bash
lm_eval --model openai-completions \
  --model_args model=davinci-002 \
  --tasks lambada_openai,hellaswag \
  --batch_size auto
```

**支持功能**：
- `generate_until`：✅
- `loglikelihood`：✅
- `loglikelihood_rolling`：✅

### 聊天模型

**可用模型**：`gpt-4`、`gpt-4-turbo`、`gpt-3.5-turbo`

```bash
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu,gsm8k,humaneval \
  --num_fewshot 5 \
  --batch_size auto
```

**支持功能**：
- `generate_until`：✅
- `loglikelihood`：❌（不支持 logprobs）
- `loglikelihood_rolling`：❌

**重要提示**：聊天模型无法提供 logprobs，因此仅能用于生成任务（如 MMLU、GSM8K、HumanEval），而不适用于困惑度计算任务。

### 配置选项

```bash
lm_eval --model openai-chat-completions \
  --model_args \
    model=gpt-4-turbo,\
    base_url=https://api.openai.com/v1,\
    num_concurrent=5,\
    max_retries=3,\
    timeout=60,\
    batch_size=auto
```

**参数**：
- `model`：模型标识符（必填）
- `base_url`：API 接口地址（默认：OpenAI）
- `num_concurrent`：并发请求数量（默认：5）
- `max_retries`：失败请求的重试次数（默认：3）
- `timeout`：请求超时时间（单位：秒）（默认：60）
- `tokenizer`：要使用的分词器（默认：与模型匹配）
- `tokenizer_backend`：值为 `"tiktoken"` 或 `"huggingface"`

### 成本管理

OpenAI 按令牌数量计费。建议在运行前先估算成本：

```python
# Rough estimate
num_samples = 1000
avg_tokens_per_sample = 500  # input + output
cost_per_1k_tokens = 0.01  # GPT-3.5 Turbo

total_cost = (num_samples * avg_tokens_per_sample / 1000) * cost_per_1k_tokens
print(f"Estimated cost: ${total_cost:.2f}")
```

**节省成本的技巧**：
- 测试时请使用 `--limit N` 参数
- 先尝试使用 `gpt-3.5-turbo`，再考虑 `gpt-4`
- 将 `max_gen_toks` 设置为最低所需值
- 在可能的情况下，将 `num_fewshot` 设为 `0` 以实现零样本推理

## Anthropic 模型

### 设置步骤

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 完成模型（旧版）

```bash
lm_eval --model anthropic-completions \
  --model_args model=claude-2.1 \
  --tasks lambada_openai,hellaswag \
  --batch_size auto
```

### 聊天模型（推荐）

**可用模型**：`claude-3-5-sonnet-20241022`、`claude-3-opus-20240229`、`claude-3-sonnet-20240229`、`claude-3-haiku-20240307`

```bash
lm_eval --model anthropic-chat \
  --model_args model=claude-3-5-sonnet-20241022 \
  --tasks mmlu,gsm8k,humaneval \
  --num_fewshot 5 \
  --batch_size auto
```

**别名**：`anthropic-chat-completions`（与 `anthropic-chat` 相同）

### 配置选项

```bash
lm_eval --model anthropic-chat \
  --model_args \
    model=claude-3-5-sonnet-20241022,\
    base_url=https://api.anthropic.com,\
    num_concurrent=5,\
    max_retries=3,\
    timeout=60
```

### 成本管理

Anthropic 的定价标准（截至 2024 年）：
- Claude 3.5 Sonnet：每 100 万字符输入费用为 3.00 美元，每 100 万字符输出费用为 15.00 美元
- Claude 3 Opus：每 100 万字符输入费用为 15.00 美元，每 100 万字符输出费用为 75.00 美元
- Claude 3 Haiku：每 100 万字符输入费用为 0.25 美元，每 100 万字符输出费用为 1.25 美元

**节省成本的策略**：
```bash
# Test on small sample first
lm_eval --model anthropic-chat \
  --model_args model=claude-3-haiku-20240307 \
  --tasks mmlu \
  --limit 100

# Then run full eval on best model
lm_eval --model anthropic-chat \
  --model_args model=claude-3-5-sonnet-20241022 \
  --tasks mmlu \
  --num_fewshot 5
```

## 本地兼容 OpenAI 的 API

许多本地推理服务器都提供了兼容 OpenAI 的 API（如 vLLM、Text Generation Inference、llama.cpp、Ollama）。

### vLLM 本地服务器

**启动服务器**：
```bash
vllm serve meta-llama/Llama-2-7b-hf \
  --host 0.0.0.0 \
  --port 8000
```

**评估**：
```bash
lm_eval --model local-completions \
  --model_args \
    model=meta-llama/Llama-2-7b-hf,\
    base_url=http://localhost:8000/v1,\
    num_concurrent=1 \
  --tasks mmlu,gsm8k \
  --batch_size auto
```

### 文本生成推理（TGI）

**启动服务器**：
```bash
docker run --gpus all --shm-size 1g -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Llama-2-7b-hf
```

**评估**：
```bash
lm_eval --model local-completions \
  --model_args \
    model=meta-llama/Llama-2-7b-hf,\
    base_url=http://localhost:8080/v1 \
  --tasks hellaswag,arc_challenge
```

### Ollama

**启动服务器**：
```bash
ollama serve
ollama pull llama2:7b
```

**评估**：
```bash
lm_eval --model local-completions \
  --model_args \
    model=llama2:7b,\
    base_url=http://localhost:11434/v1 \
  --tasks mmlu
```

### llama.cpp 服务器

**启动服务器**：
```bash
./server -m models/llama-2-7b.gguf --host 0.0.0.0 --port 8080
```

**评估**：
```bash
lm_eval --model local-completions \
  --model_args \
    model=llama2,\
    base_url=http://localhost:8080/v1 \
  --tasks gsm8k
```

## 自定义 API 实现

对于自定义 API 端点，需继承 `TemplateAPI` 类：

### 创建 `my_api.py` 文件

```python
from lm_eval.models.api_models import TemplateAPI
import requests

class MyCustomAPI(TemplateAPI):
    """Custom API model."""

    def __init__(self, base_url, api_key, **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.api_key = api_key

    def _create_payload(self, messages, gen_kwargs):
        """Create API request payload."""
        return {
            "messages": messages,
            "api_key": self.api_key,
            **gen_kwargs
        }

    def parse_generations(self, response):
        """Parse generation response."""
        return response.json()["choices"][0]["text"]

    def parse_logprobs(self, response):
        """Parse logprobs (if available)."""
        # Return None if API doesn't provide logprobs
        logprobs = response.json().get("logprobs")
        if logprobs:
            return logprobs["token_logprobs"]
        return None
```

### 注册与使用

```python
from lm_eval import evaluator
from my_api import MyCustomAPI

model = MyCustomAPI(
    base_url="https://api.example.com/v1",
    api_key="your-key"
)

results = evaluator.simple_evaluate(
    model=model,
    tasks=["mmlu", "gsm8k"],
    num_fewshot=5,
    batch_size="auto"
)
```

## API与开放模型对比

### 并行评估

```bash
# Evaluate OpenAI GPT-4
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu,gsm8k,hellaswag \
  --num_fewshot 5 \
  --output_path results/gpt4.json

# Evaluate open Llama 2 70B
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-70b-hf,dtype=bfloat16 \
  --tasks mmlu,gsm8k,hellaswag \
  --num_fewshot 5 \
  --output_path results/llama2-70b.json

# Compare results
python scripts/compare_results.py \
  results/gpt4.json \
  results/llama2-70b.json
```

### 常见对比

| 模型 | MMLU | GSM8K | HumanEval | 成本 |
|-------|------|-------|-----------|------|
| GPT-4 Turbo | 86.4% | 92.0% | 67.0% | $$$$ |
| Claude 3 Opus | 86.8% | 95.0% | 84.9% | $$$$ |
| GPT-3.5 Turbo | 70.0% | 57.1% | 48.1% | $$ |
| Llama 2 70B | 68.9% | 56.8% | 29.9% | 免费（需自行托管） |
| Mixtral 8x7B | 70.6% | 58.4% | 40.2% | 免费（需自行托管） |

## 最佳实践

### 速率限制

请遵守 API 的速率限制：
```bash
lm_eval --model openai-chat-completions \
  --model_args \
    model=gpt-4-turbo,\
    num_concurrent=3,\  # Lower concurrency
    timeout=120 \  # Longer timeout
  --tasks mmlu
```

### 可重复性

将温度值设置为 0 即可获得确定性的结果：
```bash
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu \
  --gen_kwargs temperature=0.0
```

或者可以使用 `seed` 参数进行采样：
```bash
lm_eval --model anthropic-chat \
  --model_args model=claude-3-5-sonnet-20241022 \
  --tasks gsm8k \
  --gen_kwargs temperature=0.7,seed=42
```

### 缓存机制

API 模型会自动缓存响应结果，从而避免重复调用：
```bash
# First run: makes API calls
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu \
  --limit 100

# Second run: uses cache (instant, free)
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu \
  --limit 100
```

缓存路径：`~/.cache/lm_eval/`

### 错误处理

API 可能会出现故障。建议使用重试机制：
```bash
lm_eval --model openai-chat-completions \
  --model_args \
    model=gpt-4-turbo,\
    max_retries=5,\
    timeout=120 \
  --tasks mmlu
```

## 故障排除

### “认证失败”

请检查 API 密钥：
```bash
echo $OPENAI_API_KEY  # Should print sk-...
echo $ANTHROPIC_API_KEY  # Should print sk-ant-...
```

### “速率限制已达到上限”

降低并发数量：
```bash
--model_args num_concurrent=1
```

或者为各个请求之间添加延迟。

### “超时错误”

延长超时时间：
```bash
--model_args timeout=180
```

### “未找到模型”

对于本地 API，需确认服务器正在运行：
```bash
curl http://localhost:8000/v1/models
```

### 成本失控问题

如需进行测试，请使用 `--limit` 参数：
```bash
lm_eval --model openai-chat-completions \
  --model_args model=gpt-4-turbo \
  --tasks mmlu \
  --limit 50  # Only 50 samples
```

## 高级功能

### 自定义请求头

```bash
lm_eval --model local-completions \
  --model_args \
    base_url=http://api.example.com/v1,\
    header="Authorization: Bearer token,X-Custom: value"
```

### 禁用 SSL 验证（仅限开发环境使用）

```bash
lm_eval --model local-completions \
  --model_args \
    base_url=https://localhost:8000/v1,\
    verify_certificate=false
```

### 自定义分词器

```bash
lm_eval --model openai-chat-completions \
  --model_args \
    model=gpt-4-turbo,\
    tokenizer=gpt2,\
    tokenizer_backend=huggingface
```

## 参考资料

- OpenAI API：https://platform.openai.com/docs/api-reference
- Anthropic API：https://docs.anthropic.com/claude/reference
- TemplateAPI：`lm_eval/models/api_models.py`
- OpenAI 模型：`lm_eval/models/openai_completions.py`
- Anthropic 模型：`lm_eval/models/anthropic_llms.py`
