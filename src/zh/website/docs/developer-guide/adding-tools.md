---
sidebar_position: 2
title: "Adding Tools"
description: "How to add a new tool to Hermes Agent — schemas, handlers, registration, and toolsets"
---

# 添加工具

在编写工具之前，先问自己：**是否应该将其设计为 [技能](creating-skills.md) 呢？**

:::warning 仅限内置核心工具
本页面用于向仓库本身添加**内置的 Hermes 工具**。
如果您需要个人使用的、项目内部的或其他自定义工具，且不想修改 Hermes 核心代码，请使用插件机制：

- [插件](/user-guide/features/plugins)
- [构建 Hermes 插件](/guides/build-a-hermes-plugin)

对于大多数自定义工具的创建，建议优先使用插件。只有当您明确希望将新工具作为内置工具发布到 `tools/` 目录及 `toolsets.py` 文件中时，才需参考本页面。
:::

当某项功能可以通过指令、Shell 命令以及现有工具（如 arXiv 搜索、Git 工作流、Docker 管理、PDF 处理等）来实现时，应将其设计为**技能**。

而当该功能需要借助 API 密钥进行端到端集成、包含自定义处理逻辑、涉及二进制数据处理或流式操作（如浏览器自动化、文本转语音、图像分析等）时，则应将其设计为**工具**。

## 概述

添加工具会涉及**2 个文件**：

1. **`tools/your_tool.py`** —— 处理器、架构定义、校验函数以及 `registry.register()` 调用
2. **`toolsets.py`** —— 将工具名称添加到 `_HERMES_CORE_TOOLS`（或特定的工具集）中

任何在顶层包含 `registry.register()` 调用的 `tools/*.py` 文件都将在系统启动时被自动检测到——无需手动编写导入列表。

## 第 1 步：创建内置工具文件

所有工具文件都遵循相同的结构：

```python
# tools/weather_tool.py
"""Weather Tool -- look up current weather for a location."""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- Availability check ---

def check_weather_requirements() -> bool:
    """Return True if the tool's dependencies are available."""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- Handler ---

def weather_tool(location: str, units: str = "metric") -> str:
    """Fetch weather for a location. Returns JSON string."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not configured"})
    try:
        # ... call weather API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Schema ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates (e.g. 'London' or '51.5,-0.1')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (default: metric)",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- Registration ---

from tools.registry import registry

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool(
        location=args.get("location", ""),
        units=args.get("units", "metric")),
    check_fn=check_weather_requirements,
    requires_env=["WEATHER_API_KEY"],
)
```

### 核心规则

:::danger 重要提示
- 处理器**必须**通过 `json.dumps()` 返回 JSON 字符串，绝不能直接返回原始字典
- 错误**必须**以 `{"error": "message"}` 的格式返回，绝不能以异常形式抛出
- 在构建工具定义时会调用 `check_fn` 函数——如果其返回值为 `False`，则该工具将被 silently 排除
- 处理器接收的参数为 `(args: dict, **kwargs)`，其中 `args` 包含大语言模型发起工具调用的参数
:::

## 第 2 步：将内置工具添加到工具集

在 `toolsets.py` 文件中，添加该工具的名称：

```python
# If it should be available on all platforms (CLI + messaging):
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- add here
]

# Or create a new standalone toolset:
"weather": {
    "description": "Weather lookup tools",
    "tools": ["weather"],
    "includes": []
},
```

## ~~步骤 3：添加发现导入~~（已不再需要）

凡是包含顶层 `registry.register()` 调用的工具模块，都会被 `tools/registry.py` 中的 `discover_builtin_tools()` 自动识别。无需手动维护导入列表——只需在 `tools/` 目录下创建对应文件，系统即在启动时自动加载它。

## 异步处理程序

如果您的处理程序需要使用异步代码，请将其标记为 `is_async=True`：

```python
async def weather_tool_async(location: str) -> str:
    async with aiohttp.ClientSession() as session:
        ...
    return json.dumps(result)

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool_async(args.get("location", "")),
    check_fn=check_weather_requirements,
    is_async=True,  # registry calls _run_async() automatically
)
```

注册表会以透明方式处理异步桥接——您无需亲自调用 `asyncio.run()`。 

## 需要 task_id 的处理器

那些用于管理会话级状态的工具会通过 `**kwargs` 接收 `task_id`：

```python
def _handle_weather(args, **kw):
    task_id = kw.get("task_id")
    return weather_tool(args.get("location", ""), task_id=task_id)

registry.register(
    name="weather",
    ...
    handler=_handle_weather,
)
```

## 被拦截的 Agent 循环工具

某些工具（如 `todo`、`memory`、`session_search`、`delegate_task`）需要访问特定会话的 Agent 状态。在这些工具被传递到注册表之前，`run_agent.py` 会先对它们进行拦截。虽然注册表中仍保留着这些工具的架构定义，但如果拦截被绕过，`dispatch()` 函数将会返回一个备用错误信息。 

## 可选：设置向导集成

如果您的工具需要 API 密钥，请将其添加到 `hermes_cli/config.py` 文件中：

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "Weather API key for weather lookup",
        "prompt": "Weather API key",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## 检查清单

- [ ] 已创建包含处理器、架构定义、校验函数及注册信息的工具文件  
- [ ] 已将该工具添加到 `toolsets.py` 中的对应工具集中  
- [ ] 已确认该工具确实属于内置/核心工具，而非插件  
- [ ] 处理器需返回 JSON 字符串，错误信息应以 `{"error": "..."}` 的格式返回  
- [ ] 可选：已将 API 密钥添加到 `hermes_cli/config.py` 中的 `OPTIONAL_ENV_VARS` 中  
- [ ] 可选：已将该工具添加到 `toolset_distributions.py` 中以便批量处理  
- [ ] 已使用 `hermes chat -q "Use the weather tool for London"` 进行测试
