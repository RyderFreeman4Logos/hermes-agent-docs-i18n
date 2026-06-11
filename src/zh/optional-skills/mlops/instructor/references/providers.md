# 提供商配置

关于如何将 Instructor 与不同大语言模型提供商配合使用的指南。

## Anthropic Claude

```python
import instructor
from anthropic import Anthropic

# Basic setup
client = instructor.from_anthropic(Anthropic())

# With API key
client = instructor.from_anthropic(
    Anthropic(api_key="your-api-key")
)

# Recommended mode
client = instructor.from_anthropic(
    Anthropic(),
    mode=instructor.Mode.ANTHROPIC_TOOLS
)

# Usage
result = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    response_model=YourModel
)
```

## OpenAI

```python
from openai import OpenAI

client = instructor.from_openai(OpenAI())

result = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=YourModel,
    messages=[{"role": "user", "content": "..."}]
)
```

## 本地模型（Ollama）

```python
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ),
    mode=instructor.Mode.JSON
)

result = client.chat.completions.create(
    model="llama3.1",
    response_model=YourModel,
    messages=[...]
)
```

## 模式

- `Mode.ANTHROPIC_TOOLS`：推荐用于 Claude  
- `Mode.TOOLS`：用于调用 OpenAI 的功能  
- `Mode.JSON`：作为不支持对应提供方的备用模式
