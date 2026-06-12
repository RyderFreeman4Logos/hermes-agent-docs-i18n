# 轨迹格式

Hermes Agent以兼容ShareGPT的JSONL格式保存对话轨迹，这些数据可用于训练数据、调试输出以及强化学习数据集。

相关源文件：`agent/trajectory.py`、`run_agent.py`（查找 `_save_trajectory` 函数）、`batch_runner.py`

## 文件命名规则

轨迹数据会保存在当前工作目录下的相应文件中：

| 文件名 | 适用场景 |
|------|----------|
| `trajectory_samples.jsonl` | 对话成功结束的记录（`completed=True`） |
| `failed_trajectories.jsonl` | 对话失败或被中断的记录（`completed=False`） |

批量运行工具（`batch_runner.py`）会为每个批次生成包含额外元数据字段的定制输出文件（例如：`batch_001_output.jsonl`）。

您可以通过 `save_trajectory()` 函数中的 `filename` 参数来自定义文件名。

## JSONL记录格式

文件中的每一行都是一个独立的JSON对象。该格式有两种变体：

### CLI/交互式格式（来自 `_save_trajectory`）

```json
{
  "conversations": [ ... ],
  "timestamp": "2026-03-30T14:22:31.456789",
  "model": "anthropic/claude-sonnet-4.6",
  "completed": true
}
```

### 批量运行器格式（来自 `batch_runner.py`）

```json
{
  "prompt_index": 42,
  "conversations": [ ... ],
  "metadata": { "prompt_source": "gsm8k", "difficulty": "hard" },
  "completed": true,
  "partial": false,
  "api_calls": 7,
  "toolsets_used": ["code_tools", "file_tools"],
  "tool_stats": {
    "terminal": {"count": 3, "success": 3, "failure": 0},
    "read_file": {"count": 2, "success": 2, "failure": 0},
    "write_file": {"count": 0, "success": 0, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0,
    "write_file": 0
  }
}
```

`tool_stats`与`tool_error_counts`这两个字典会经过标准化处理，确保包含`model_tools.TOOL_TO_TOOLSET_MAP`中列出的所有可能工具，且默认值为零。这样一来，在加载HuggingFace数据集时，各条记录的架构就能保持一致。

## 对话数组（ShareGPT格式）

`conversations`数组遵循ShareGPT的角色规范：

| API角色 | ShareGPT `from`值 |
|----------|-----------------|
| 系统角色 | `"system"` |
| 用户角色 | `"human"` |
| 助手角色 | `"gpt"` |
| 工具角色 | `"tool"` |

### 完整示例

```json
{
  "conversations": [
    {
      "from": "system",
      "value": "You are a function calling AI model. You are provided with function signatures within <tools> </tools> XML tags. You may call one or more functions to assist with the user query. If available tools are not relevant in assisting with user query, just respond in natural conversational language. Don't make assumptions about what values to plug into functions. After calling & executing the functions, you will be provided with function results within <tool_response> </tool_response> XML tags. Here are the available tools:\n<tools>\n[{\"name\": \"terminal\", \"description\": \"Execute shell commands\", \"parameters\": {\"type\": \"object\", \"properties\": {\"command\": {\"type\": \"string\"}}}, \"required\": null}]\n</tools>\nFor each function call return a JSON object, with the following pydantic model json schema for each:\n{'title': 'FunctionCall', 'type': 'object', 'properties': {'name': {'title': 'Name', 'type': 'string'}, 'arguments': {'title': 'Arguments', 'type': 'object'}}, 'required': ['name', 'arguments']}\nEach function call should be enclosed within <tool_call> </tool_call> XML tags.\nExample:\n<tool_call>\n{'name': <function-name>,'arguments': <args-dict>}\n</tool_call>"
    },
    {
      "from": "human",
      "value": "What Python version is installed?"
    },
    {
      "from": "gpt",
      "value": "<think>\nThe user wants to know the Python version. I should run python3 --version.\n</think>\n<tool_call>\n{\"name\": \"terminal\", \"arguments\": {\"command\": \"python3 --version\"}}\n</tool_call>"
    },
    {
      "from": "tool",
      "value": "<tool_response>\n{\"tool_call_id\": \"call_abc123\", \"name\": \"terminal\", \"content\": \"Python 3.11.6\"}\n</tool_response>"
    },
    {
      "from": "gpt",
      "value": "<think>\nGot the version. I can now answer the user.\n</think>\nPython 3.11.6 is installed on this system."
    }
  ],
  "timestamp": "2026-03-30T14:22:31.456789",
  "model": "anthropic/claude-sonnet-4.6",
  "completed": true
}
```


## 标准化规则

### 推理内容标记

轨迹转换器会将所有推理内容统一转换为 `<think>` 标签，而不论模型最初是以何种形式生成这些内容的：

1. **原生推理标记**（来自 Anthropic、OpenAI o 系列等提供商的 `msg["reasoning"]` 字段）：会被包装为 `<think>\n{reasoning}\n</think>\n` 的格式，并置于内容之前。

2. **REASONING_SCRATCHPAD XML**（当禁用原生推理且模型通过系统提示指令以 XML 格式进行推理时）：`convert_scratchpad_to_think()` 函数会将 `<REASONING_SCRATCHPAD>` 标签转换为 `<think>` 标签。

3. **空的思考块**：每个 `gpt` 轮次都必定包含一个 `<think>` 块。如果未生成任何推理内容，则会插入一个空块：<think>\n</think>\n>——此举旨在确保训练数据格式的一致性。

### 工具调用标准化

API 格式的工具调用（包含 `tool_call_id`、函数名称以及作为 JSON 字符串的参数）会被转换为 XML 包装的 JSON 格式：

```
<tool_call>
{"name": "terminal", "arguments": {"command": "ls -la"}}
</tool_call>
```

- 参数会从 JSON 字符串解析为对象形式（不会进行双重编码）。
- 若 JSON 解析失败（本不应发生，因为已在对话过程中进行过验证），则使用空的 `{}` 并记录警告信息。
- 在一次助手回复中调用多个工具时，会在一个 `gpt` 消息中生成多个 `<tool_call>` 块。

### 工具响应规范化

助手消息之后的所有工具响应都会被汇总到同一个 `tool` 回复中，且响应形式为经过 XML 包装的 JSON：

```
<tool_response>
{"tool_call_id": "call_abc123", "name": "terminal", "content": "output here"}
</tool_response>
```

- 如果工具内容为 JSON 格式（以 `{` 或 `[` 开头），系统会对其进行解析，从而使 `content` 字段中存储的是 JSON 对象/数组而非字符串。
- 多个工具的返回结果会在同一条消息中通过换行符分隔。
- 工具名称会根据其在父助手的 `tool_calls` 数组中的位置进行匹配。

### 系统消息

系统消息是在数据保存时生成的（并非来自对话内容）。它遵循 Hermes 函数调用提示模板，包含以下部分：
- 用于说明函数调用协议的前置说明；
- 包含 JSON 工具定义的 `<tools>` XML 块；
- `FunctionCall` 对象的架构参考；
- `<tool_call>` 的示例。

工具定义包括 `name`、`description`、`parameters` 和 `required` 字段（如需符合标准格式，可将其值设为 `null`）。

## 加载轨迹数据

轨迹数据为标准的 JSONL 格式，可使用任何 JSON-lines 读取工具进行加载：

```python
import json

def load_trajectories(path: str):
    """Load trajectory entries from a JSONL file."""
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

# Filter to successful completions only
successful = [e for e in load_trajectories("trajectory_samples.jsonl")
              if e.get("completed")]

# Extract just the conversations for training
training_data = [e["conversations"] for e in successful]
```

### 正在加载 HuggingFace 数据集

```python
from datasets import load_dataset

ds = load_dataset("json", data_files="trajectory_samples.jsonl")
```

标准化的 `tool_stats` 结构确保所有条目都包含相同的字段，从而避免在加载数据集时出现 Arrow 结构不匹配的错误。

## 控制轨迹保存功能

在 CLI 中，轨迹保存功能可通过以下方式控制：

```yaml
# config.yaml
agent:
  save_trajectories: true  # default: false
```

或者也可以通过 `--save-trajectories` 参数来实现。当代理以 `save_trajectories=True` 的参数初始化时，每次对话轮次结束时都会调用 `_save_trajectory()` 方法。

批量运行器会始终保存对话轨迹（这正是它的核心功能）。

对于所有轮次中均无推理行为的样本，批量运行器会自动将其丢弃，以避免用这类非推理样本污染训练数据。
