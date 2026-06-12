---
sidebar_position: 5
title: "Using Hermes as a Python Library"
description: "Embed AIAgent in your own Python scripts, web apps, or automation pipelines — no CLI required"
---

# 将 Hermes 作为 Python 库使用

Hermes 不仅是一款命令行工具。您可以直接导入 `AIAgent`，并在自己的 Python 脚本、Web 应用程序或自动化流程中以编程方式加以使用。本指南将为您展示具体操作方法。

---

## 安装

直接从仓库安装 Hermes：

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git
```

或者使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv pip install git+https://github.com/NousResearch/hermes-agent.git
```

您也可以将其添加到 `requirements.txt` 文件中：

```text
hermes-agent @ git+https://github.com/NousResearch/hermes-agent.git
```

:::提示
当将 Hermes 作为库使用时，需要使用与 CLI 相同的环境变量。至少需设置 `OPENROUTER_API_KEY`（如果直接通过提供商访问，则需设置 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`）。
:::

---

## 基本用法

使用 Hermes 最简单的方法就是调用 `chat()` 方法——传入消息，即可获得返回的字符串：

```python
from run_agent import AIAgent

agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)
response = agent.chat("What is the capital of France?")
print(response)
```

`chat()` 函数会内部处理整个对话流程——包括工具调用、重试等所有操作——并仅返回最终的文本响应。

:::warning
在将 Hermes 集成到自定义代码中时，务必设置 `quiet_mode=True`。如果不设置该参数，代理将会输出 CLI 旋转指示器、进度条以及其他终端信息，从而导致应用程序的输出变得杂乱无章。
:::

---

## 完整的对话控制

如需对对话进行更精细的控制，可直接使用 `run_conversation()` 函数。该函数会返回一个包含完整响应、消息历史记录以及元数据的字典：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)

result = agent.run_conversation(
    user_message="Search for recent Python 3.13 features",
    task_id="my-task-1",
)

print(result["final_response"])
print(f"Messages exchanged: {len(result['messages'])}")
```

返回的字典包含以下内容：
- **`final_response`** — 智能体的最终文本回复
- **`messages`** — 完整的消息历史记录（系统消息、用户消息、助手消息以及工具调用记录）

（您传入的 `task_id` 会存储在智能体实例中以实现虚拟机隔离，但不会出现在返回的字典中。）

您还可以传入自定义的系统消息，以此覆盖该次调用的临时系统提示语：

```python
result = agent.run_conversation(
    user_message="Explain quicksort",
    system_message="You are a computer science tutor. Use simple analogies.",
)
```

## 配置工具

通过 `enabled_toolsets` 或 `disabled_toolsets` 来控制代理可访问的工具集：

```python
# Only enable web tools (browsing, search)
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    enabled_toolsets=["web"],
    quiet_mode=True,
)

# Enable everything except terminal access
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    disabled_toolsets=["terminal"],
    quiet_mode=True,
)
```

:::提示
若需创建功能极简且受到严格限制的智能体（例如仅用于研究的网页搜索机器人），请使用 `enabled_toolsets` 参数。若希望保留大部分功能但需限制某些特定功能（例如在共享环境中禁止使用终端），则应使用 `disabled_toolsets` 参数。
:::

---

## 多轮对话

通过将消息历史记录传递回去，从而在多轮对话中保持上下文状态：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)

# First turn
result1 = agent.run_conversation("My name is Alice")
history = result1["messages"]

# Second turn — agent remembers the context
result2 = agent.run_conversation(
    "What's my name?",
    conversation_history=history,
)
print(result2["final_response"])  # "Your name is Alice."
```

`conversation_history` 参数可接收之前结果中的 `messages` 列表。智能体会在内部复制该列表，因此您的原始列表绝不会被修改。

---

## 保存对话轨迹

启用轨迹保存功能，即可以 ShareGPT 格式保存对话内容——这有助于生成训练数据或进行调试：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    save_trajectories=True,
    quiet_mode=True,
)

agent.chat("Write a Python function to sort a list")
# Saves to trajectory_samples.jsonl in ShareGPT format
```

每段对话都会以一条独立的 JSONL 行形式被记录下来，从而便于从自动化运行中收集数据集。  

---

## 自定义系统提示词

可使用 `ephemeral_system_prompt` 设置自定义系统提示词，用以引导智能体的行为，但此类提示词**不会**被保存到轨迹文件中（从而保持训练数据的纯净性）：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    ephemeral_system_prompt="You are a SQL expert. Only answer database questions.",
    quiet_mode=True,
)

response = agent.chat("How do I write a JOIN query?")
print(response)
```

这非常适合构建各类专用智能体——无论是代码审查员、文档编写工具，还是SQL助手——所有这些智能体都可以共享相同的底层技术框架。

---

## 批量处理

为支持并行执行多个提示词，Hermes提供了`batch_runner.py`工具。该工具能够对多个`AIAgent`实例进行管理，并通过有效的资源隔离机制确保各实例之间的独立运行：

```bash
python batch_runner.py --input prompts.jsonl --output results.jsonl
```

每个提示词都会拥有独立的 `task_id` 以及隔离的运行环境。如果您需要自定义批量处理逻辑，可以直接使用 `AIAgent` 来构建相应的功能：

```python
import concurrent.futures
from run_agent import AIAgent

prompts = [
    "Explain recursion",
    "What is a hash table?",
    "How does garbage collection work?",
]

def process_prompt(prompt):
    # Create a fresh agent per task for thread safety
    agent = AIAgent(
        model="anthropic/claude-sonnet-4",
        quiet_mode=True,
        skip_memory=True,
    )
    return agent.chat(prompt)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))

for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}\nA: {result}\n")
```

:::warning
请务必为每个线程或任务创建一个**新的 `AIAgent` 实例**。该智能体会维护内部状态（对话历史、工具会话、迭代计数器），这些状态并不适合在多个线程之间共享。
:::

---

## 集成示例

### FastAPI 接口

```python
from fastapi import FastAPI
from pydantic import BaseModel
from run_agent import AIAgent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "anthropic/claude-sonnet-4"

@app.post("/chat")
async def chat(request: ChatRequest):
    agent = AIAgent(
        model=request.model,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )
    response = agent.chat(request.message)
    return {"response": response}
```

### Discord机器人

```python
import discord
from run_agent import AIAgent

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hermes "):
        query = message.content[8:]
        agent = AIAgent(
            model="anthropic/claude-sonnet-4",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            platform="discord",
        )
        response = agent.chat(query)
        await message.channel.send(response[:2000])

client.run("YOUR_DISCORD_TOKEN")
```

### CI/CD 流水线步骤

```python
#!/usr/bin/env python3
"""CI step: auto-review a PR diff."""
import subprocess
from run_agent import AIAgent

diff = subprocess.check_output(["git", "diff", "main...HEAD"]).decode()

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
    skip_context_files=True,
    skip_memory=True,
    disabled_toolsets=["terminal", "browser"],
)

review = agent.chat(
    f"Review this PR diff for bugs, security issues, and style problems:\n\n{diff}"
)
print(review)
```

---

## 主要构造函数参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `model` | `str` | `""` | OpenRouter 格式的模型名称（默认为空；会在运行时从您的 hermes 配置中读取） |
| `quiet_mode` | `bool` | `False` | 是否抑制 CLI 输出 |
| `enabled_toolsets` | `List[str]` | `None` | 允许使用的工具集白名单 |
| `disabled_toolsets` | `List[str]` | `None` | 禁用的工具集黑名单 |
| `save_trajectories` | `bool` | `False` | 是否将对话内容保存为 JSONL 格式 |
| `ephemeral_system_prompt` | `str` | `None` | 自定义系统提示词（不会被保存到对话记录中） |
| `max_iterations` | `int` | `90` | 每次对话中工具调用的最大迭代次数 |
| `skip_context_files` | `bool` | `False` | 是否跳过加载 AGENTS.md 文件 |
| `skip_memory` | `bool` | `False` | 是否禁用持久内存的读写功能 |
| `api_key` | `str` | `None` | API 密钥（如未提供则自动从环境变量中读取） |
| `base_url` | `str` | `None` | 自定义 API 接口地址 |
| `platform` | `str` | `None` | 平台标识（如 `"discord"`、`"telegram"` 等） |

---

## 重要注意事项

:::tip
- 如果不希望将工作目录中的 `AGENTS.md` 文件内容加载到系统提示词中，请设置 **`skip_context_files=True`**。
- 若需防止智能体读取或写入持久内存，可设置 **`skip_memory=True`**——这对无状态 API 接口尤为推荐。
- `platform` 参数（例如 `"discord"`、`"telegram"`）会注入特定于平台的格式化提示，以便智能体调整输出风格。
:::

:::warning
- **线程安全性**：每个线程或任务应创建一个独立的 `AIAgent` 实例。切勿在并发调用之间共享同一个实例。
- **资源清理**：当对话结束时，智能体会自动清理相关资源（如终端会话、浏览器窗口）。如果在长期运行的进程中使用该功能，请确保每次对话都能正常结束。
- **迭代次数限制**：默认的 `max_iterations=90` 值已较为宽松。对于简单的问答场景，建议降低该值（例如设置为 `max_iterations=10`），以避免工具调用陷入无限循环并控制成本。
:::
