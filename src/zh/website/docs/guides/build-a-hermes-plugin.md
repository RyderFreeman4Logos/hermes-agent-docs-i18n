---
sidebar_position: 9
sidebar_label: "Build a Plugin"
title: "Build a Hermes Plugin"
description: "Step-by-step guide to building a complete Hermes plugin with tools, hooks, data files, and skills"
---

# 构建 Hermes 插件

本指南将引导您从零开始构建一个功能完备的 Hermes 插件。完成之后，您将拥有一个具备多种工具、生命周期钩子、预置数据文件以及内置技能的可用插件——涵盖插件系统支持的所有功能。

:::info 不确定需要哪份指南？
Hermes 提供了多种不同的可插接接口——有些使用 Python 的 `register_*` API，而另一些则采用配置驱动或直接放入目录的方式。请先参考此对照表：

| 您想要添加的功能 | 需阅读的指南 |
|---|---|
| 自定义工具、钩子、斜杠命令、技能或 CLI 子命令 | **本指南**（通用插件开发指南） |
| **LLM/推理后端**（新类型的提供者） | [模型提供者插件](/developer-guide/model-provider-plugin) |
| **网关通道**（Discord/Telegram/IRC/Teams 等） | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| **内存后端**（Honcho/Mem0/Supermemory 等） | [内存提供者插件](/developer-guide/memory-provider-plugin) |
| **上下文压缩引擎** | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| **图像生成后端** | [图像生成提供者插件](/developer-guide/image-gen-provider-plugin) |
| **视频生成后端** | [视频生成提供者插件](/developer-guide/video-gen-provider-plugin) |
| **TTS 后端**（任何 CLI 工具——Piper、VoxCPM、Kokoro、语音克隆等） | [TTS 自定义命令提供者](/user-guide/features/tts#custom-command-providers) ——采用配置驱动，无需 Python |
| **STT 后端**（自定义 whisper/ASR CLI 工具） | [语音消息转写](/user-guide/features/tts#voice-message-transcription-stt) ——在配置文件中设置 `HERMES_LOCAL_STT_COMMAND` 指向 shell 模板 |
| **通过 MCP 调用外部工具**（文件系统、GitHub、Linear 以及任何 MCP 服务器） | [MCP](/user-guide/features/mcp) ——在 `config.yaml` 中声明 `mcp_servers.<name>` |
| **网关事件钩子**（在启动时、会话事件发生时或接收到命令时触发） | [事件钩子](/user-guide/features/hooks#gateway-event-hooks) ——将 `HOOK.yaml` 和 `handler.py` 文件放入 `~/.hermes/hooks/<name>/` 目录中 |
| **Shell 钩子**（在特定事件发生时运行 Shell 命令） | [Shell 钩子](/user-guide/features/hooks#shell-hooks) ——在 `config.yaml` 的 `hooks:` 部分进行配置 |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引） | [技能管理](/user-guide/features/skills) ——使用命令 `hermes skills tap add <repo>` · [发布自定义技能接入点](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| 一级核心推理提供者（不属于插件类型） | [添加提供者](/developer-guide/adding-providers) |

如需查看包含所有扩展接口的完整列表，包括配置驱动型（TTS、STT、MCP、Shell 钩子）和直接放入目录型（网关钩子）的接口，可参阅完整的[可插接接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)。
:::

## 您将构建的内容

一个包含两种工具的**计算器**插件：
- `calculate` —— 计算数学表达式（如 `2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` —— 单位转换（如 `100 F → 37.78 C`、`5 km → 3.11 mi`）

此外，该插件还包含一个用于记录每次工具调用的钩子，以及一个内置的技能文件。

## 第一步：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 第2步：编写清单文件

创建 `plugin.yaml` 文件：

```yaml
name: calculator
version: 1.0.0
description: Math calculator — evaluate expressions and convert units
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这向 Hermes 告诉它：“我是一个名为 calculator 的插件，可提供各种工具和钩子功能。”`provides_tools` 和 `provides_hooks` 字段分别列出了该插件所注册的工具与钩子。您还可以添加可选字段：
```yaml
author: Your Name
requires_env:          # gate loading on env vars; prompted during install
  - SOME_API_KEY       # simple format — plugin disabled if missing
  - name: OTHER_KEY    # rich format — shows description/url during install
    description: "Key for the Other service"
    url: "https://other.com/keys"
    secret: true
```

## 第3步：编写工具架构定义

创建 `schemas.py` 文件——LLM会读取该文件来决定何时调用您的工具：

```python
"""Tool schemas — what the LLM sees."""

CALCULATE = {
    "name": "calculate",
    "description": (
        "Evaluate a mathematical expression and return the result. "
        "Supports arithmetic (+, -, *, /, **), functions (sqrt, sin, cos, "
        "log, abs, round, floor, ceil), and constants (pi, e). "
        "Use this for any math the user asks about."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '2**10', 'sqrt(144)')",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "Convert a value between units. Supports length (m, km, mi, ft, in), "
        "weight (kg, lb, oz, g), temperature (C, F, K), data (B, KB, MB, GB, TB), "
        "and time (s, min, hr, day)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The numeric value to convert",
            },
            "from_unit": {
                "type": "string",
                "description": "Source unit (e.g., 'km', 'lb', 'F', 'GB')",
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (e.g., 'mi', 'kg', 'C', 'MB')",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为何架构设计如此重要：** `description` 字段决定了大语言模型何时调用您的工具。请明确说明该工具的功能及其适用场景。而 `parameters` 则用于定义大语言模型会传递哪些参数。

## 第 4 步：编写工具处理函数

创建 `tools.py` 文件——当大语言模型调用您的工具时，实际执行的代码就位于此文件中：

```python
"""Tool handlers — the code that runs when the LLM calls each tool."""

import json
import math

# Safe globals for expression evaluation — no file/network access
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """Evaluate a math expression safely.

    Rules for handlers:
    1. Receive args (dict) — the parameters the LLM passed
    2. Do the work
    3. Return a JSON string — ALWAYS, even on error
    4. Accept **kwargs for forward compatibility
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "No expression provided"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "Division by zero"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"Invalid: {e}"})


# Conversion tables — values are in base units
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # Normalize to Celsius
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # Convert to target
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """Convert between units."""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

    try:
        # Temperature
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # Ratio-based conversions
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"Cannot convert {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"Conversion failed: {e}"})
```

**处理程序的核心规则：**
1. **函数签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 必须始终返回 JSON 字符串，无论是成功响应还是错误信息。
3. **禁止抛出异常：** 需捕获所有异常，并返回对应的错误 JSON。
4. **支持 `**kwargs` 参数：** Hermes 未来可能会传递额外的上下文信息。

## 第 5 步：编写注册代码

创建 `__init__.py` 文件——该文件用于将架构模式与处理程序关联起来：

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# Track tool usage via hooks
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """Hook: runs after every tool call (not just ours)."""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """Wire schemas to handlers and register hooks."""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # This hook fires for ALL tool calls, not just ours
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的功能：**  
- 在启动时仅调用一次  
- `ctx.register_tool()` 会将您的工具添加到注册表中，模型可立即识别该工具  
- `ctx.register_hook()` 用于订阅生命周期事件  
- `ctx.register_cli_command()` 用于注册 CLI 子命令（例如 `hermes my-plugin <subcommand>`）  
- `ctx.register_command()` 用于注册会话内的斜杠命令（例如在 CLI 或网关聊天界面中使用 `/myplugin <args>`）——详情请参见下文的[注册斜杠命令](#register-slash-commands)  
- `ctx.dispatch_tool(name, arguments)` —— 可以使用父代理的上下文（包括审批权限、凭证及 task_id）来调用任何其他工具（无论是内置工具还是其他插件提供的工具），实现自动关联。对于需要像模型直接调用一样使用 `terminal`、`read_file` 或其他工具的斜杠命令处理程序而言，此功能非常实用。  
- 若该函数发生崩溃，相应插件将被禁用，但 Hermes 仍可正常运行  

**`dispatch_tool` 示例——用于执行工具的斜杠命令：**

```python
def handle_scan(ctx, raw_args: str):
    """Implement /scan by invoking the terminal tool through the registry."""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{raw_args}'"})
    return result  # returned to the caller's chat UI

def register(ctx):
    # Handlers receive a single raw_args string; close over ctx via a lambda.
    ctx.register_command(
        "scan",
        lambda raw: handle_scan(ctx, raw),
        description="Find files matching a glob",
    )
```

被调用的工具会经过常规的审批、脱敏以及预算审核流程——这属于真正的工具调用，而非绕过这些流程的捷径。

## 第6步：进行测试

启动Hermes：

```bash
hermes
```

在横幅显示的工具列表中，您应该能看到 `calculator: calculate, unit_convert` 这些选项。

试试这些提示词：
```
What's 2 to the power of 16?
Convert 100 fahrenheit to celsius
What's the square root of 2 times pi?
How many gigabytes is 1.5 terabytes?
```

查看插件状态：
```
/plugins
```

输出：
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

### 调试插件发现问题

如果您的插件未显示，或虽已显示但无法加载，请将 `HERMES_PLUGINS_DEBUG=1` 设置为该值，即可在标准错误流中获取详细的插件发现日志：

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

对于每一个插件来源（内置、用户自定义、项目级以及入口点），您将看到以下信息：

- 已扫描的目录列表，以及每个目录生成的清单数量；
- 每个清单的详细内容：解析后的键值、名称、类型、来源以及磁盘路径；
- 跳过该插件的原因：`通过配置禁用`、`配置中未启用`、`为独占插件`、`不存在plugin.yaml文件或已达到深度限制`；
- 加载时的信息：正在导入的插件，以及`register(ctx)`函数所注册内容的简要总结（工具、钩子、斜杠命令、CLI命令）；
- 解析失败时的信息：异常的完整堆栈跟踪信息（如YAML解析错误等）；
- `register()`函数调用失败时的信息：指向`__init__.py`文件中引发错误的具体行的完整堆栈跟踪。

这些日志始终会被记录到`~/.hermes/logs/agent.log`文件中。默认情况下，错误信息以WARNING级别记录，而所有信息则在设置了环境变量时以DEBUG级别记录。因此，如果您无法通过设置环境变量来运行程序（例如在网关内部），则可以直接查看该日志文件。

```bash
hermes logs --level WARNING | grep -i plugin
```

插件未显示的常见原因：

- **配置中未启用**——插件为可选功能。请运行 `hermes plugins enable <name>`（名称取自 `plugins list` 的输出结果，对于嵌套结构，格式可能为 `<category>/<plugin>`）。
- **目录结构错误**——路径必须是 `~/.hermes/plugins/<plugin-name>/plugin.yaml`（扁平结构），或是 `~/.hermes/plugins/<category>/<plugin-name>/plugin.yaml`（最多一层类别嵌套）。更深的嵌套结构将被忽略。
- **缺少 `__init__.py` 文件**——插件目录必须同时包含 `plugin.yaml` 文件以及包含 `register(ctx)` 函数的 `__init__.py` 文件。
- **`kind` 类型错误**——网关适配器在其清单文件中需指定 `kind: platform`。内存提供器会自动被识别为 `kind: exclusive`，并通过 `memory.provider` 配置进行路由，而非通过 `plugins.enabled`。

## 您插件的最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "I'm calculator, I provide tools and hooks"
├── __init__.py      # Wiring: schemas → handlers, register hooks
├── schemas.py       # What the LLM reads (descriptions + parameter specs)
└── tools.py         # What runs (calculate, unit_convert functions)
```

四个文件，分工明确：
- **Manifest**用于说明插件的功能
- **Schemas**用于描述面向大语言模型的工具
- **Handlers**负责实现实际逻辑
- **Registration**则负责将所有组件串联起来

## 插件还能实现哪些功能？

### 上传数据文件

只需将任意文件放入插件目录中，即可在导入时读取这些文件：

```python
# In tools.py or __init__.py
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 打包技能

插件可以提供技能文件，Agent可通过`skill_view("plugin:skill")`来加载这些文件。请在您的`__init__.py`文件中对其进行注册：

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

该智能体现在能够使用命名空间名称来加载您的技能了：

```python
skill_view("my-plugin:my-workflow")   # → plugin's version
skill_view("my-workflow")              # → built-in version (unchanged)
```

**关键属性：**
- 插件技能为**只读**属性——它们不会被保存到 `~/.hermes/skills/` 目录中，也无法通过 `skill_manage` 命令进行编辑。
- 插件技能**不会**出现在系统提示语的 `<available_skills>` 列表中——它们属于需要手动启用的加载项。
- 纯技能名称不会受到影响——命名空间可避免其与内置技能发生冲突。
- 当智能体加载插件技能时，会自动在开头显示一个捆绑上下文标识，列出同一插件的其他相关技能。

:::提示 传统模式
虽然仍可使用旧的 `shutil.copy2` 方法（将技能复制到 `~/.hermes/skills/` 目录中），但这会增加与内置技能名称冲突的风险。建议在新插件开发中使用 `ctx.register_skill()` 方法。
:::

### 基于环境变量的启用控制

如果您的插件需要 API 密钥：

```yaml
# plugin.yaml — simple format (backwards-compatible)
requires_env:
  - WEATHER_API_KEY
```

如果未设置 `WEATHER_API_KEY`，该插件将会被禁用，并同时显示明确的提示信息。代理程序不会崩溃也不会报错，只会显示“插件 weather 已禁用（缺失参数：WEATHER_API_KEY）”。

当用户运行 `hermes plugins install` 命令时，系统会**以交互方式**询问那些缺失的 `requires_env` 变量。这些数值会自动保存到 `.env` 文件中。

为获得更佳的安装体验，建议使用包含描述信息及注册链接的富格式进行配置：

```yaml
# plugin.yaml — rich format
requires_env:
  - name: WEATHER_API_KEY
    description: "API key for OpenWeather"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 是否必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 安装提示时显示给用户的文字说明 |
| `url` | 否 | 获取凭证的地址 |
| `secret` | 否 | 若设置为 `true`，输入内容将会被隐藏（类似密码字段） |

同一个列表中可以混合使用这两种格式。已设置的变量将会被直接跳过，不会产生任何提示。

### 延迟安装可选的 Python 依赖项

如果您的插件封装了并非所有用户都会安装的 SDK（如第三方 SDK、大型机器学习库或特定平台用的包），则无需在模块顶部直接 `import` 它。应在工具处理函数中使用 `tools.lazy_deps.ensure(...)` 辅助函数——Hermes 会在用户首次使用时根据其 `security.allow_lazy_installs` 配置来自动安装该包。

```python
# tools.py
from tools.lazy_deps import ensure, FeatureUnavailable

def my_tool_handler(args, **kwargs):
    try:
        ensure("my-plugin.my-backend")   # key must be in LAZY_DEPS
    except FeatureUnavailable as exc:
        return {"error": str(exc)}

    import my_backend_sdk   # safe now
    ...
```

在 `tools/lazy_deps.py` 中，安全模型规定了两条规则：

| 规则 | 原因 |
|---|---|
| 您的功能密钥必须出现在树内的 `LAZY_DEPS` 允许列表中 | 防止恶意配置诱使 Hermes 安装任意包——仅 Hermes 自带的标准包才符合条件 |
| 包规范只能通过名称在 PyPI 中指定 | 不支持使用 `--index-url`、`git+https://` 或文件路径。应在允许列表条目中使用 PEP 440 格式指定版本范围（如 `"my-sdk>=1.2,<2"`） |

对于通过 pip 分发的第三方插件，可将可选依赖作为 `[project.optional-dependencies]` 附加项在您自己的 `pyproject.toml` 中声明，并告知用户使用 `pip install your-plugin[backend]` 命令进行安装——该路径不会经过 `lazy_deps` 处理。延迟加载机制最适用于**已打包**的插件，因为若每次安装都附带硬依赖，会显著增加 Hermes 的整体体积。

当全局设置 `security.allow_lazy_installs: false` 时，`ensure()` 函数会立即抛出 `FeatureUnavailable` 异常，并附上解决方案提示——您的插件应捕获该异常并实现优雅降级（返回错误结果，而非导致工具循环崩溃）。

### 线程安全的延迟单例

插件通常会在首次使用时，通过模块级变量缓存一些资源密集型的对象，例如 SDK 客户端、HTTP 会话或连接池：

```python
_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = ExpensiveClient(...)   # ← TOCTOU race
    return _client
```

这是一种“枪击式”问题。Hermes 在单个进程内运行多个线程（用于处理委托的工具调用、后台任务以及自我优化分支），因此两个线程都可能在 `_client` 被设置之前就调用了 `get_client()` 方法。这两个线程都会通过“非空”检查，进而执行代价高昂的构建操作；而第二个线程的写入操作会覆盖第一个线程的成果，导致前者所打开的资源（连接、文件句柄或后台线程）被泄露。

切勿自行实现锁机制，请使用 `plugins/plugin_utils.py` 中提供的辅助函数：

```python
from plugins.plugin_utils import lazy_singleton, SingletonSlot

# Zero-arg accessor → decorate it:
@lazy_singleton
def get_client():
    return ExpensiveClient(load_config())   # runs exactly once

client = get_client()    # safe across threads
get_client.reset()       # drop the instance (tests / teardown)


# Accessor that takes a build argument → use a slot:
_slot: SingletonSlot = SingletonSlot()

def get_client(config=None):
    return _slot.get(lambda: ExpensiveClient(resolve(config)))

def reset_client():
    _slot.reset()
```

两者均会通过双重检查锁定机制来序列化首次并发调用，并且最多仅执行一次工厂函数。如果工厂函数抛出异常，则不会进行任何缓存处理，后续调用将会重新尝试。`honcho memory`插件（位于`plugins/memory/honcho/client.py`）即为参考实现。

> 经验法则：每当您编写类似`global _something`、随后进行`is None`检查并再执行构建操作的代码时，建议改用上述方案之一。

### 工具的条件可用性

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = tool hidden from model
)
```

### 覆盖内置工具

若想用自定义实现替换内置工具（例如将默认的浏览器工具替换为基于headed-Chrome CDP的后端，或用自定义的企业索引替代`web_search`），请设置`override=True`：

```python
def register(ctx):
    ctx.register_tool(
        name="browser_navigate",             # same name as the built-in
        toolset="plugin_my_browser",         # your own toolset namespace
        schema={...},
        handler=my_custom_navigate,
        override=True,                       # explicit opt-in
    )
```

若未设置 `override=True`，注册表会拒绝任何可能覆盖其他工具集中所存在工具的注册请求——这一机制可有效避免意外覆盖情况。相关覆盖操作会被记录为 INFO 级日志，可在 `~/.hermes/logs/agent.log` 中查看审计痕迹。由于插件会在内置工具之后加载，因此当前的注册顺序是正确的：您的处理器将替换原有的内置处理器。

### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考

每个钩子的详细文档均可在 **[事件钩子参考](/user-guide/features/hooks#plugin-hooks)** 中找到——包括回调签名、参数表、触发时机以及示例代码。以下为概要总结：

| 钩子名称 | 触发时机 | 回调签名 | 返回值 |
|----------|----------|----------|--------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行之前 | `tool_name: str, args: dict, task_id: str` | 被忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回之后 | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | 被忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮对话中，在工具调用循环之前触发一次 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮对话中，在工具调用循环之后触发一次（仅成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 被忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 创建新会话时（仅第一轮） | `session_id: str, model: str, platform: str` | 被忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次调用 `run_conversation` 之后以及 CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 被忽略 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI 或网关终止正在运行的会话时 | `session_id: str \| None, platform: str` | 被忽略 |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关更换新的会话密钥时（通过 `/new` 或 `/reset` 命令） | `session_id: str, platform: str` | 被忽略 |
| `kanban_task_claimed` | 有看板任务被领取时（调度器进程，在工作进程启动之前） | `task_id: str, board: str \| None, assignee: str \| None, run_id: int \| None, profile_name: str` | 被忽略 |
| `kanban_task_completed` | 看板任务完成时（工作进程） | `task_id, board, assignee, run_id, profile_name, summary: str \| None` | 被忽略 |
| `kanban_task_blocked` | 看板任务被阻塞时（工作进程） | `task_id, board, assignee, run_id, profile_name, reason: str \| None` | 被忽略 |

大多数钩子均为“触发即忘”型观察器——其返回值会被直接忽略。唯一例外是 `pre_llm_call`，它可以将上下文注入到对话中。

为确保向后兼容性，所有回调都应支持接受 `**kwargs` 参数。如果某个钩子回调发生崩溃，系统会记录日志并跳过该回调，其他钩子及智能体仍可正常运行。

看板生命周期钩子会在看板数据库更改提交之后触发，因此回调始终能获取持久化的状态，且不会持有 SQLite 写锁。由于看板任务工作进程是以独立的 `hermes -p <profile> chat -q` 子进程形式运行的，`kanban_task_claimed` 会在**调度器**进程中触发，而 `kanban_task_completed`/`kanban_task_blocked` 则在**工作进程**中触发——你可以在调度器进程中添加钩子以集中监控所有状态转换，或在工作进程中添加钩子以获取每项任务的会话上下文。

### `pre_llm_call` 上下文注入功能

这是唯一一个返回值具有重要意义的钩子。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或普通字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这一机制可用于内存插件、RAG 集成、内容过滤规则，以及任何需要向模型提供额外上下文的插件。

#### 返回格式

```python
# Dict with context key
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# Plain string (equivalent to the dict form above)
return "Recalled memories:\n- User prefers dark mode"

# Return None or don't return → no injection (observer-only)
return None
```

任何非 `None` 且非空、包含 `"context"` 键（或为纯非空字符串）的返回值都会被收集起来，并追加到当前轮次的用户消息中。

#### 注入机制的工作原理

被注入的上下文会被追加到**用户消息**中，而非系统提示词。这是经过精心设计的选择：

- **保持提示词缓存不变**——系统提示词在各个轮次中都保持一致。Anthropic 和 OpenRouter 会缓存系统提示词的前缀，因此保持其稳定性可在多轮对话中节省75%以上的输入标记量。如果插件修改了系统提示词，每轮对话都会导致缓存未命中。
- **临时性**——注入操作仅在 API 调用时发生。对话历史中的原始用户消息永远不会被修改，也不会有任何内容被持久化到会话数据库中。
- **系统提示词属于 Hermes 的专属领域**——它包含针对特定模型的指导方针、工具使用规则、角色设定以及缓存的技能内容。插件仅能与用户输入一起提供上下文，而无法更改智能体的核心指令。

#### 示例：记忆回溯插件

```python
"""Memory plugin — recalls relevant context from a vector store."""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """Called before each LLM turn. Returns recalled memories."""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # nothing to inject

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # fail silently, don't break the agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：Guardrails插件

```python
"""Guardrails plugin — enforces content policies."""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """Injects policy text into every turn."""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅用于观察的钩子（无注入功能）

```python
"""Analytics plugin — tracks turn metadata without injecting context."""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """Fires before each LLM call. Returns None — no context injected."""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # No return → no injection

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文的情况

当多个插件在 `pre_llm_call` 阶段返回上下文时，它们的输出会通过双换行符连接起来，并一同附加到用户消息中。这些输出的顺序遵循插件发现顺序（按插件目录名称的字母顺序排列）。

### 注册 CLI 命令

插件可以自行添加 `hermes <plugin>` 子命令结构：

```python
def _my_command(args):
    """Handler for hermes my-plugin <subcommand>."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """Build the argparse tree for hermes my-plugin."""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show plugin status")
    subs.add_parser("config", help="Show plugin config")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="Manage my plugin",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册完成后，用户即可运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**内存提供者插件**则采用基于约定的方式：在插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。内存插件发现系统会自动识别该函数，无需调用 `ctx.register_cli_command()`。详情请参阅[内存提供者插件指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活动提供者限制**：只有当配置中的活动 `memory.provider` 为对应的内存插件提供者时，其 CLI 命令才会显示。如果用户尚未启用该提供者，相关的 CLI 命令就不会出现在帮助输出中。

### 注册斜杠命令

插件可以注册会话内的斜杠命令——即用户在对话过程中输入的命令（如 `/lcm status` 或 `/ping`）。这类命令既可在 CLI 环境中使用，也可在 Telegram、Discord 等网关环境中使用。

```python
def _handle_status(raw_args: str) -> str:
    """Handler for /mystatus — called with everything after the command name."""
    if raw_args.strip() == "help":
        return "Usage: /mystatus [help|check]"
    return "Plugin status: all systems nominal"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="Show plugin status",
    )
```

注册完成后，用户可在任意会话中输入 `/mystatus`。该命令会显示在自动补全选项、/help 输出结果以及 Telegram 机器人菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "", args_hint: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 去掉开头斜杠后的命令名称（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 接收原始参数字符串作为输入，也可为异步函数形式 |
| `description` | `str` | 显示在 /help 输出、自动补全选项以及 Telegram 机器人菜单中 |

**与 `register_cli_command()` 的主要区别：**

| 对比项 | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 会话中的 `/name` | 终端中的 `hermes name` |
| 支持的平台 | CLI 会话、Telegram、Discord 等 | 仅终端 |
| 处理器接收的参数 | 原始参数字符串 | argparse 的 `Namespace` 对象 |
| 典型应用场景 | 状态查询、诊断及快速操作 | 复杂的子命令结构、设置向导 |

**冲突处理机制：** 若某个插件尝试注册与内置命令（如 `help`、`model`、`new` 等）冲突的名称，系统会通过日志警告默默拒绝该注册请求。内置命令始终具有优先级。

**异步处理器支持：** 网关调度系统可自动检测并等待异步处理器的执行，因此您既可以使用同步函数，也可以使用异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"Check result: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="Run async check")
```

### 通过斜杠命令调用工具

那些需要协调各类工具的斜杠命令处理程序（例如通过 `delegate_task` 启动子代理、调用 `file_edit` 等功能），应使用 `ctx.dispatch_tool()` 方法，而非直接操作框架的内部机制。父代理的上下文环境（如工作区相关配置、加载状态指示器以及模型继承关系等）都会被自动关联到位。

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="Delegate a goal to a subagent",
    )
```

**签名：** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| 参数 | 类型 | 说明 |
|-----------|------|------|
| `name` | `str` | 在工具注册表中登记的工具名称（例如 `"delegate_task"`、`"file_edit"`） |
| `args` | `dict` | 工具参数，格式与模型发送的参数一致 |
| `parent_agent` | `Agent \| None` | 可选覆盖值。若未指定，则从当前 CLI 代理获取（在网关模式下会以兼容方式处理） |

**运行时行为：**

- **CLI 模式：** `parent_agent` 从当前活跃的 CLI 代理中获取，因此工作区提示、加载指示器以及模型选择功能都能按预期正常工作。
- **网关模式：** 由于不存在 CLI 代理，相关功能会以兼容方式降级处理——工作区内容将从配置的终端工作目录读取，且不会显示加载指示器。
- **显式覆盖：** 如果调用方明确传入 `parent_agent=`，则该值将被直接采用，不会被覆盖。

这是插件命令用于调度工具的公开、稳定接口。插件不应尝试访问 `ctx._cli_ref.agent` 或类似的私有状态。

### 在钩子函数内部执行操作（配置文件 + 工具）

`ctx._cli_ref` 仅在**交互式 CLI**会话中会被填充。在网关模式、非交互式的 `hermes chat -q` 运行方式以及**看板生成的 worker 会话**中，该值为 `None`——因此任何试图通过 `_cli_ref` 访问数据的插件逻辑在这些场景下都会静默失效。实际上，有两个稳定且与会话无关的 API 可以满足钩子函数的需求：

- **`ctx.profile_name`** — 当前活跃的配置文件名称（例如 `"default"`，或在看板 worker 中的负责人配置文件）。该值源自 `HERMES_HOME`，因此无需依赖 `_cli_ref`，在任何环境中都能正常使用。
- **`ctx.dispatch_tool(name, args)`** — 调用任何已注册的工具（包括内置工具和插件工具），如 `kanban_*` 工具、`delegate_task`、`terminal`、`read_file` 等。无论钩子函数在哪个进程中被触发，均可通过该接口执行操作。

通过以上两种方式，看板生命周期钩子便能够在不触及框架内部实现的情况下，观察状态变化并对看板执行相应操作。

```python
def register(ctx):
    def on_blocked(*, task_id, reason=None, **kw):
        # Runs in the worker process; ctx._cli_ref is None here.
        ctx.dispatch_tool("kanban_comment", {
            "task_id": task_id,
            "comment": f"[{ctx.profile_name}] auto-noted block: {reason}",
        })
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

若要运行完整的 `hermes <subcommand>` 命令（例如 `hermes kanban show`），可通过 `ctx.dispatch_tool("terminal", {"command": "hermes kanban show ..."})` 来调用 `terminal` 工具——无头工作进程会话并不支持进程内的斜杠命令桥接，而工具则是从钩子函数中启动 Hermes 的常用方式。

### 处理 Slack Block Kit 按钮点击事件

那些能够发送包含交互元素（如按钮、下拉菜单、日期选择器等）的 Block Kit 消息的插件，可直接在 Slack 适配器中注册点击处理函数——无需对 `slack_bolt.AsyncApp` 进行任何恶意修改。

```python
def register(ctx):
    async def _on_approve(ack, body, action):
        # ack within 3 seconds — slack_bolt requirement.
        await ack()
        # body["channel"]["id"], body["user"]["id"], body["message"]["ts"]
        # action["action_id"], action["value"]
        sweep_id = (action.get("value") or "").split("|", 1)[-1]
        # ...do the deterministic work, then post a follow-up.

    ctx.register_slack_action_handler("inbox_sweep_approve", _on_approve)
```

**签名：** `ctx.register_slack_action_handler(action_id, callback) -> None`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `action_id` | `str \| re.Pattern \| dict` | 与 `slack_bolt.App.action()` 的要求一致：可以是具体的 `action_id`，也可以是用于匹配多个 ID 的正则表达式，或是类似 `{"action_id": "...", "block_id": "..."}` 这样的约束字典 |
| `callback` | async 可调用对象 | 按照 `slack_bolt` 的规范，接收 `(ack, body, action)` 三个参数 |

**运行时行为：**

- 处理函数会在插件加载时被放入队列中，当 Slack 平台建立连接后，它会被集成到适配器的 `slack_bolt.AsyncApp` 中。
- 每个回调函数都会被添加防御性处理：如果处理函数抛出异常，网关会记录错误，并尽力确认点击操作，从而防止 Slack 重复尝试。
- 需遵循标准的 `slack_bolt` 规则——必须在 3 秒内调用 `await ack()`，之后才能执行耗时更长的操作。
- 在多工作区部署场景下，无论来自哪个已连接的工作区的点击都会触发处理函数；如果需要限定处理范围，可使用 `body["team"]["id"]`。

这是插件参与 Slack 交互的官方方式。旧版插件可能修改了 `SlackAdapter.connect` 函数，建议优先使用此 API。

:::提示
本指南主要介绍**通用插件**（工具、钩子、斜杠命令、CLI 命令）。以下各节将概述每种专用插件类型的开发模式；每节都附有完整指南链接，可供查阅相关细节和示例。
:::

## 专用插件类型

除了通用插件之外，Hermes 还提供了五种专用插件类型。它们分别存储在 `plugins/<类别>/<名称>/`（已打包）或 `~/.hermes/plugins/<类别>/<名称>/`（用户自定义）目录下。不同类别的插件具有不同的接口规范——请选择所需的类型，然后阅读其完整指南。

### 模型提供者插件——添加大语言模型后端

只需将相关配置文件放入 `plugins/model-providers/<名称>/` 目录即可：

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme Inference",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
```

当首次有代码调用 `get_provider_profile()` 或 `list_providers()` 时，该功能会自动被启用——`auth.py`、`config.py`、`doctor.py`、`models.py`、`runtime_provider.py` 以及聊天补全传输模块都会自动关联到此功能。用户自定义的插件可通过名称覆盖内置插件。

**完整指南：** [模型提供程序插件](/developer-guide/model-provider-plugin)——字段参考、可覆盖的钩子函数（`prepare_messages`、`build_extra_body`、`build_api_kwargs_extras`、`fetch_models`）、API模式选择、认证类型及测试方法。

### 平台插件——添加网关通道

只需将适配器放入 `plugins/platforms/<名称>/` 目录即可：

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # Auto-populate PlatformConfig.extra from env so env-only setups
        # show up in `hermes gateway status` without SDK instantiation.
        env_enablement_fn=_env_enablement,
        # Opt in to cron delivery: `deliver=myplatform` routes to this var.
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="You are chatting via MyPlatform. Keep responses concise.",
    )
```

```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform gateway adapter
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "Bot token from the MyPlatform console"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

**完整指南：** [添加平台适配器](/developer-guide/adding-platform-adapters)——涵盖完整的 `BasePlatformAdapter` 接口定义、消息路由机制、认证控制以及设置向导集成。如需仅使用标准库的示例，可查看 `plugins/platforms/irc/` 目录。

### 内存提供者插件——构建跨会话知识后端

只需将 `MemoryProvider` 的实现文件放入 `plugins/memory/<名称>/` 目录即可：

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_content, assistant_content, *,
                  session_id="", messages=None) -> None:
        ...

    def prefetch(self, query, *, session_id="") -> str:
        ...

    def get_tool_schemas(self) -> list[dict]:
        return []   # required @abstractmethod — see full guide

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

内存提供器采用单选机制——同一时间仅有一个处于激活状态，可通过 `config.yaml` 中的 `memory.provider` 参数进行指定。

**完整指南：** [内存提供器插件](/developer-guide/memory-provider-plugin) — 包含完整的 `MemoryProvider` ABC 接口、线程模型规范、进程隔离机制，以及通过 `cli.py` 进行 CLI 命令注册的相关内容。

### 上下文引擎插件——用于替代上下文压缩器

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def update_from_response(self, usage) -> None: ...
    def should_compress(self, prompt_tokens: int = None) -> bool: ...
    def compress(self, messages, current_tokens=None, focus_topic=None) -> list: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

上下文引擎为单选类型，需通过 `config.yaml` 中的 `context.engine` 参数进行指定。

**完整指南：** [上下文引擎插件](/developer-guide/context-engine-plugin)。

### 图像生成后端

只需将对应提供商放入 `plugins/image_gen/<名称>/` 目录即可：

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, aspect_ratio="landscape", **kwargs) -> dict:
        # returns success_response(...) / error_response(...)
        ...

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: Custom image generation backend
```

**完整指南：** [图像生成提供者插件](/developer-guide/image-gen-provider-plugin)——包含完整的 `ImageGenProvider` ABC 类、`list_models()` / `get_setup_schema()` 元数据函数、`success_response()`/`error_response()` 辅助函数、Base64 格式与 URL 格式的输出方式、用户自定义设置以及通过 pip 分发插件。

**参考示例：** `plugins/image_gen/openai/`（通过 OpenAI SDK 实现的 DALL-E / GPT-Image 功能）、`plugins/image_gen/openai-codex/`、`plugins/image_gen/xai/`（Grok 图像生成功能）。

## 非 Python 扩展接口

Hermes 还支持完全非 Python 插件的扩展形式。这些扩展会在[可插件化接口列表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)中列出；以下内容将简要介绍每种开发方式的特点。

### MCP 服务器——注册外部工具

模型上下文协议（MCP）服务器无需编写任何 Python 插件，即可将自己的工具注册到 Hermes 中。只需在 `~/.hermes/config.yaml` 文件中声明这些工具即可：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

在启动时，Hermes 会连接到每台服务器，列出其提供的工具，并将这些工具与内置工具一同注册。大语言模型会将它们视作与其他工具完全相同的存在。**完整指南：** [MCP](/user-guide/features/mcp)。

### 网关事件钩子——在生命周期事件触发时执行操作

只需将清单文件及处理程序放入 `~/.hermes/hooks/<名称>/` 目录中即可：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Send a push notification when a long task finishes
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # send notification …
        pass
```

事件包括 `gateway:startup`、`session:start`、`session:end`、`session:reset`、`agent:start`、`agent:step`、`agent:end`，以及通配符 `command:*`。钩子中的错误会被捕获并记录，而不会阻塞主处理流程。

**完整指南：** [网关事件钩子](/user-guide/features/hooks#gateway-event-hooks)。

### Shell 钩子——在工具调用时执行 shell 命令

如果您仅希望在工具触发时（如通知、审计日志、桌面提醒、自动格式化器等）运行脚本，可直接在 `config.yaml` 中使用 Shell 钩子——无需编写 Python 代码：

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send 'Tool ran: {tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

支持与 Python 插件钩子完全相同的事件（`pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`、`pre_gateway_dispatch`），同时为 `pre_tool_call` 中的阻塞决策提供结构化的 JSON 输出。

**完整指南：** [Shell 钩子](/user-guide/features/hooks#shell-hooks)。

### 技能来源 —— 添加自定义技能注册表

如果您维护有技能相关的 GitHub 仓库（或希望从内置来源之外的社区索引中获取技能），可将其作为 **tap** 源进行添加：

```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

创建属于自己的技能插件仅需一个包含 `skills/<skill-name>/SKILL.md` 目录的 GitHub 仓库——无需搭建服务器或注册任何平台。

**完整指南：** [Skills Hub](/user-guide/features/skills#skills-hub) · [发布自定义技能插件](/user-guide/features/skills#publishing-a-custom-skill-tap)（仓库结构、最小示例、非默认路径及信任级别设置）。

### 通过命令模板实现文本转语音/语音转文本功能

任何能够读写音频或文本的 CLI 工具均可通过 `config.yaml` 文件进行集成——无需编写任何 Python 代码：

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

对于文本转语音功能，需将 `HERMES_LOCAL_STT_COMMAND` 指向一个 shell 模板。支持的占位符包括：TTS 功能的 `{input_path}`、`{output_path}`、`{format}`、`{voice}`、`{model}`、`{speed}`；文本转语音功能则包括 `{input_path}`、`{output_dir}`、`{language}`、`{model}`。任何涉及路径操作的 CLI 命令都会自动被视为插件。

**完整指南：** [TTS 自定义命令插件](/user-guide/features/tts#custom-command-providers) · [文本转语音](/user-guide/features/tts#voice-message-transcription-stt)。

## 通过 pip 分发

若要公开共享插件，需在您的 Python 包中添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# Plugin auto-discovered on next hermes startup
```

## 在 NixOS 上进行分发

如果您提供了包含入口点的 `pyproject.toml` 文件，NixOS 用户便可以以声明式方式安装您的插件：

**入口点插件**（推荐用于分发）：
```nix
# User's configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

**目录插件**（无需 `pyproject.toml` 文件）：
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

如需包含叠加层使用方法及冲突检测等完整文档，请参阅[Nix 设置指南](/getting-started/nix-setup#plugins)。

## 常见错误

**处理器未返回 JSON 字符串：**
```python
# Wrong — returns a dict
def handler(args, **kwargs):
    return {"result": 42}

# Right — returns a JSON string
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理程序签名中缺少 `**kwargs` 参数：**
```python
# Wrong — will break if Hermes passes extra context
def handler(args):
    ...

# Right
def handler(args, **kwargs):
    ...
```

**处理程序抛出异常：**
```python
# Wrong — exception propagates, tool call fails
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# Right — catch and return error JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**模式描述过于模糊：**
```python
# Bad — model doesn't know when to use it
"description": "Does stuff"

# Good — model knows exactly when and how
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```
