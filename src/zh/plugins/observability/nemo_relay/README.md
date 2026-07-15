# NeMo Relay 可观测性功能

这是一个可选的 Hermes 可观测性插件，它可将 Hermes 的观察者钩子映射到 NeMo Relay 的作用域、LLM 时间段、工具时间段、标记事件、ATOF 以及 ATIF 中。

NeMo Relay 是 NVIDIA 专为定义智能体执行边界而设计的运行时层。它并不会替代 Hermes Agent 的规划器、工具模块、内存管理、模型提供者路由功能或 CLI 用户界面。相反，该插件允许 Hermes 为其已处理的任务——如会话、轮次、提供者/API 调用、工具调用、审批提示以及委派的子智能体——生成 NeMo Relay 生命周期事件。

启用此插件后，Hermes Agent 可以实现以下功能：

- 将 Hermes 的执行过程以 NeMo Relay 的作用域、LLM 时间段、工具时间段及标记事件的形式进行记录。
- 以智能体轨迹可观测性格式（ATOF）的 JSONL 格式导出原始生命周期事件，便于调试和离线分析。
- 导出智能体轨迹交换格式（ATIF）的轨迹数据，用于回放、评估以及工作流分析。
- 通过共享的会话元数据、轮次元数据及轨迹元数据，实现父会话、委派子智能体、工具调用与提供者调用之间的关联。

如需了解更完整的运行时模型架构，请参阅 NeMo Relay 概述文档：
https://docs.nvidia.com/nemo/relay/about-nemo-relay/overview

ATOF 是 NVIDIA 为 NeMo Relay 生命周期事件规定的标准 JSONL 事件流格式。其详细规范可见 NeMo Agent Toolkit 文档：
https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/develop/packages/nvidia_nat_atif/atof-event-format.md

ATIF 则是由这些事件生成的轨迹表示格式。NVIDIA 与 Harbor 共同开发了 ATIF v1.7 版本，该版本支持复杂的任务编排工作流，包括子智能体轨迹嵌入、轨迹标识、多 LLM 调用步骤的元数据记录，以及无需使用 LLM 的确定性编排步骤：
https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md

## 启用方式

请在设置导出选项之前先启用该插件：

```bash
hermes plugins enable observability/nemo_relay
```

以下的 `HERMES_NEMO_RELAY_*` 环境变量仅用于配置已启用的插件，其本身并不具备启用插件发现的功能。

对于独立的测试环境，需在代理程序运行的相同 `HERMES_HOME` 中启用该插件：

```bash
env HERMES_HOME=/tmp/hermes-nemo-relay-test \
  hermes plugins enable observability/nemo_relay
```

使用 `--ignore_user_config` 参数启动的进程会忽略 `HERMES_HOME` 中记录的已启用插件状态。因此，除非测试框架以其他方式显式加载了 `observability/nemo_relay`，否则本地端到端测试应避免使用该参数。

`HERMES_HOME` 是 `hermes plugins enable ...` 命令以及后续的 `hermes chat ...` 命令所共同使用的 Hermes 配置文件所在目录。如果未设置该参数，Hermes 会使用用户的默认配置目录，通常为 `~/.hermes`。对于独立的冒烟测试，可任选一个可写的临时目录，并在该测试中的所有命令中统一使用该路径。

```bash
export HERMES_HOME=/tmp/hermes-nemo-relay-test
hermes plugins enable observability/nemo_relay
hermes chat --query 'Reply exactly ok' --provider custom --model qwen3.6:35b
```

在执行代码检出操作时，请确保您使用的 `hermes` 命令是基于包含该插件的版本构建的。如果使用的是全局安装的旧版 CLI，它将无法识别工作目录中新增的插件。

```bash
uv sync --extra nemo-relay
uv run hermes plugins enable observability/nemo_relay
uv run hermes chat --query 'Reply exactly ok' --provider custom --model qwen3.6:35b
```

若要将更新后的 CLI 部署到其他环境中，需从当前代码库构建并安装全新的 wheel 包，随后再安装官方的 NeMo Relay 运行时扩展组件：

```bash
uv build --wheel
python -m pip install --force-reinstall dist/hermes_agent-*.whl
python -m pip install "nemo-relay>=0.5,<1.0"
hermes plugins enable observability/nemo_relay
```

如果未安装 `nemo-relay`，该插件将无法正常启动。请安装版本号在 0.5 及以上、且经过官方支持的 NeMo Relay 0.x 系列版本。

```bash
pip install "nemo-relay>=0.5,<1.0"
```

## 导出配置

该插件可直接通过 `HERMES_NEMO_RELAY_*` 环境变量来配置导出器，也可将导出器设置委托给 NeMo Relay 的 `plugins.toml` 组件配置。

在本地测试、CI 任务以及一次性 CLI 运行场景中，建议使用环境变量。而当希望用一份 NeMo Relay 配置文件统一管理 ATOF、ATIF、OpenTelemetry 和 OpenInference 等可观测性组件时，则应使用 `plugins.toml`。

### 环境变量

插件启用后可用于设置的常用本地导出参数：

```bash
export HERMES_NEMO_RELAY_ATOF_ENABLED=1
export HERMES_NEMO_RELAY_ATOF_OUTPUT_DIRECTORY=.nemo-relay/atof
export HERMES_NEMO_RELAY_ATIF_ENABLED=1
export HERMES_NEMO_RELAY_ATIF_OUTPUT_DIRECTORY=.nemo-relay/atif
```

可选的覆盖参数：

- `HERMES_NEMO_RELAY_ATOF_FILENAME`
- `HERMES_NEMO_RELAY_ATOF_MODE`（`append` 或 `overwrite`）
- `HERMES_NEMO_RELAY_ATIF_FILENAME_TEMPLATE`
- `HERMES_NEMO_RELAY_ATIF_AGENT_NAME`
- `HERMES_NEMO_RELAY_ATIF_AGENT_VERSION`
- `HERMES_NEMO_RELAY_ATIF_MODEL_NAME`
- `HERMES_NEMO_RELAY_ATIF_SUBAGENT_EXPORT_MODE`（默认为 `embedded`；如需同时生成独立的子文件，请设置为 `all`）

### NeMo Relay 组件配置

若要通过组件配置来初始化 NeMo Relay，需创建一个 `plugins.toml` 文件，并将 Hermes 指向该文件：

```bash
export HERMES_NEMO_RELAY_PLUGINS_TOML=.nemo-relay/plugins.toml
```

最小化的 ATOF 与 ATIF 配置：

```toml
version = 1

[[components]]
kind = "observability"
enabled = true

[components.config]
version = 1

[components.config.atof]
enabled = true
output_directory = ".nemo-relay/atof"
filename = "events.jsonl"
mode = "overwrite"

[components.config.atif]
enabled = true
output_directory = ".nemo-relay/atif"
filename_template = "trajectory-{session_id}.json"
agent_name = "Hermes Agent"
agent_version = "local"
```

当`HERMES_NEMO_RELAY_PLUGINS_TOML`被设置且初始化成功后，NeMo Relay将通过该配置来管理导出器的整个生命周期，从而跳过直接的`HERMES_NEMO_RELAY_ATOF_*`备用设置。如果同一个`plugins.toml`中的可观测性配置已启用了`atif`功能，那么直接的`HERMES_NEMO_RELAY_ATIF_*`备用设置也会被跳过，以避免Hermes在任务终止时重复导出轨迹数据。若`plugins.toml`的初始化失败，Hermes仍会保持针对该次运行的直接环境变量备用设置处于激活状态。

若要为提供商和工具调用启用由NeMo Relay管理的执行拦截功能，需在同一个`plugins.toml`文件中添加相应的自适应组件：

```toml
[[components]]
kind = "adaptive"
enabled = true

[components.config.tool_parallelism]
mode = "observe_only"
```

当启用自适应组件且已安装的 NeMo Relay 运行时提供了 `llm.execute(...)` / `tools.execute(...)` 接口时，Hermes 会通过这些中间件边界来路由大语言模型及工具的执行流程。观察者钩子仍会发送会话、轮次、审批以及子代理相关的标记；而对于那些已由 NeMo Relay 承担管理的执行任务，插件则无需再手动发起 `llm.call` 和 `tools.call` 操作。将 `tool_parallelism.mode` 设置为 `"observe_only"` 可以在保持对工具调度过程进行观察的同时，依然封装真实的执行边界。

### 动态插件

Hermes 能够识别 NeMo Relay 0.6 及更高版本中提供的动态插件激活 API。可通过 Hermes 自带的 `[[dynamic_plugins]]` 配置项来定义原生插件或工作进程插件，这些配置项需与 Python 绑定的激活规范字段相匹配：

```toml
[[dynamic_plugins]]
plugin_id = "example-plugin"
kind = "rust_dynamic"
manifest_ref = "./example-plugin/relay-plugin.toml"

[dynamic_plugins.config]
mode = "enabled"
```

对于 Worker 插件，还需提供由生命周期管理的 `environment_ref`：

```toml
[[dynamic_plugins]]
plugin_id = "example-worker"
kind = "worker"
manifest_ref = "./example-worker/relay-plugin.toml"
environment_ref = "/absolute/path/from-nemo-relay-plugins-inspect"

[dynamic_plugins.config]
mode = "enabled"
```

首先使用 `nemo-relay plugins add` 命令为工作节点配置插件，然后从 `nemo-relay plugins inspect <plugin-id> --json` 的 JSON 输出中复制 `data.source.environment_ref`。Relay 会在启动时拒绝任何自定义的 Python 环境。

`manifest_ref` 和 `environment_ref` 的相对路径是相对于实际的 `plugins.toml` 文件来确定的。

Relay 中的标准化网关 `[[plugins.dynamic]]` 记录无法与 Hermes 自有的相关部分互换。该网关会将这些记录与用于启用功能、定义信任策略以及管理工作节点环境的独立生命周期状态相结合；目前的 Python 绑定尚未提供相应的解析功能。Hermes 会针对 `[[plugins.dynamic]]` 提供可操作的诊断信息而非直接忽略或绕过生命周期策略。在 Relay 能够为嵌入主机提供共享的文件与生命周期解析功能之前，请继续使用 `[[dynamic_plugins]]`。

Hermes 会在注册其管理的大型语言模型及工具执行中间件之前先激活这些插件，并在整个运行时期间保持其激活状态。在关闭系统时，它会先关闭会话导出器、清空 Relay 的订阅者列表，随后关闭插件激活状态，从而在卸载插件代码之前移除回调函数。

NeMo Relay 0.5 版本的 Python 绑定不支持动态激活功能。当存在动态插件配置但对应的绑定缺少激活 API 时，Hermes 会记录一条可操作的警告信息，并继续执行常规的静态组件配置，因此 ATOF 和 ATIF 监控功能依然可用。在这种降级模式下不会加载任何动态插件。

如需查看完整的 Hermes 中间件通用规范，请参阅 [`docs/middleware/README.md`](../../../docs/middleware/README.md)。

## 标准化本地示例

本节中的仅观察类示例使用了从 0.5 版开始支持的 NeMo Relay 0.x 发行版，以及通过兼容 OpenAI 的 API 提供服务的本地 Ollama 模型。

```bash
pip install "nemo-relay>=0.5,<1.0"

export HERMES_HOME=/tmp/hermes-nemo-relay-docs/hermes-home
mkdir -p "$HERMES_HOME"

cat > "$HERMES_HOME/config.yaml" <<'YAML'
model:
  provider: custom
  default: qwen3.6:35b
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
plugins:
  enabled:
    - observability/nemo_relay
delegation:
  max_spawn_depth: 2
  max_concurrent_children: 2
  child_timeout_seconds: 180
  model: qwen3.6:35b
  provider: custom
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
YAML
```

### 委托子代理工具调用

该运行会启动一个父级Hermes会话，将任务委托给子代理，由子代理执行`terminal`命令，并同时生成ATOF与ATIF格式的输出。

```bash
export HERMES_NEMO_RELAY_ATOF_ENABLED=1
export HERMES_NEMO_RELAY_ATOF_OUTPUT_DIRECTORY=/tmp/hermes-nemo-relay-docs/subagent/atof
export HERMES_NEMO_RELAY_ATOF_FILENAME=nested-subagent-atof.jsonl
export HERMES_NEMO_RELAY_ATOF_MODE=overwrite
export HERMES_NEMO_RELAY_ATIF_ENABLED=1
export HERMES_NEMO_RELAY_ATIF_OUTPUT_DIRECTORY=/tmp/hermes-nemo-relay-docs/subagent/atif
export HERMES_NEMO_RELAY_ATIF_FILENAME_TEMPLATE='nested-subagent-atif-{session_id}.json'
export HERMES_NEMO_RELAY_ATIF_AGENT_NAME='Hermes Agent E2E'
export HERMES_NEMO_RELAY_ATIF_AGENT_VERSION=docs-example
export HERMES_NEMO_RELAY_ATIF_SUBAGENT_EXPORT_MODE=all

hermes chat \
  --query 'Use delegate_task exactly once. Ask the child subagent to use the terminal tool exactly once to run printf docs_nested_leaf_function. After the child returns, reply with exactly: parent received nested subagent result.' \
  --provider custom \
  --model qwen3.6:35b \
  --toolsets delegation,terminal \
  --max-turns 10 \
  --quiet \
  --accept-hooks
```

命令行输出：

```text
session_id: docs-parent-session
parent received nested subagent result.
```

已过滤的 ATOF 摘要：

```jsonl
{"kind":"scope","category":"tool","name":"delegate_task","scope_category":"start","metadata":{"session_id":"docs-parent-session","tool_call_id":"call_delegate"},"data":{"goal":"Run the command `printf docs_nested_leaf_function` using the terminal tool.","toolsets":["terminal"]}}
{"kind":"mark","name":"hermes.subagent.start","metadata":{"parent_session_id":"docs-parent-session","session_id":"docs-child-session","subagent_id":"sa-0-docs","child_role":"leaf"}}
{"kind":"scope","category":"tool","name":"terminal","scope_category":"end","metadata":{"session_id":"docs-child-session","tool_call_id":"call_terminal","status":"ok"},"data":"{\"output\":\"docs_nested_leaf_function\",\"exit_code\":0,\"error\":null}"}
{"kind":"scope","category":"tool","name":"delegate_task","scope_category":"end","metadata":{"session_id":"docs-parent-session","tool_call_id":"call_delegate","status":"ok"}}
```

已过处理的 ATIF 摘要：

```json
{
  "schema_version": "ATIF-v1.7",
  "session_id": "docs-parent-session",
  "agent": {"name": "Hermes Agent E2E", "version": "docs-example", "model_name": "qwen3.6:35b"},
  "steps": [
    {
      "source": "agent",
      "tool_calls": [{"function_name": "delegate_task"}],
      "observation": {
        "results": [
          {
            "subagent_trajectory_ref": [{"session_id": "docs-child-session"}],
            "content": "{\"results\":[{\"status\":\"completed\",\"tool_trace\":[{\"tool\":\"terminal\",\"status\":\"ok\"}]}]}"
          }
        ]
      }
    },
    {"source": "agent", "message": "parent received nested subagent result."}
  ],
  "subagent_trajectories": [
    {
      "session_id": "docs-child-session",
      "steps": [
        {
          "source": "agent",
          "tool_calls": [{"function_name": "terminal", "arguments": {"command": "printf docs_nested_leaf_function"}}],
          "observation": {"results": [{"content": "{\"output\":\"docs_nested_leaf_function\",\"exit_code\":0,\"error\":null}"}]}
        }
      ]
    }
  ]
}
```

### 并行工具调用

该运行任务要求模型在同一条助手消息中发起两次 `read_file` 工具调用。Hermes会将这些只读工具作为一批进行处理，而 NeMo Relay则会记录下这两次工具调用。

```bash
mkdir -p /tmp/hermes-nemo-relay-docs/workdir
printf 'docs_parallel_alpha_function\n' > /tmp/hermes-nemo-relay-docs/workdir/alpha.txt
printf 'docs_parallel_beta_function\n' > /tmp/hermes-nemo-relay-docs/workdir/beta.txt
cd /tmp/hermes-nemo-relay-docs/workdir

export HERMES_NEMO_RELAY_ATOF_ENABLED=1
export HERMES_NEMO_RELAY_ATOF_OUTPUT_DIRECTORY=/tmp/hermes-nemo-relay-docs/parallel/atof
export HERMES_NEMO_RELAY_ATOF_FILENAME=parallel-tools-atof.jsonl
export HERMES_NEMO_RELAY_ATOF_MODE=overwrite
export HERMES_NEMO_RELAY_ATIF_ENABLED=1
export HERMES_NEMO_RELAY_ATIF_OUTPUT_DIRECTORY=/tmp/hermes-nemo-relay-docs/parallel/atif
export HERMES_NEMO_RELAY_ATIF_FILENAME_TEMPLATE='parallel-tools-atif-{session_id}.json'
export HERMES_NEMO_RELAY_ATIF_AGENT_NAME='Hermes Agent E2E'
export HERMES_NEMO_RELAY_ATIF_AGENT_VERSION=docs-example

hermes chat \
  --query 'Use exactly two read_file tool calls in the same assistant message. Read alpha.txt and beta.txt. Do not call terminal. After both tool results are available, reply with exactly: parallel tools complete.' \
  --provider custom \
  --model qwen3.6:35b \
  --toolsets file \
  --max-turns 8 \
  --quiet \
  --accept-hooks
```

命令行输出：

```text
session_id: docs-parallel-session
parallel tools complete.
```

已过滤的 ATOF 摘要：

```jsonl
{"kind":"scope","category":"llm","name":"custom","scope_category":"end","data":{"assistant_message":{"tool_calls":[{"id":"call_alpha","name":"read_file","arguments":"{\"path\":\"alpha.txt\"}"},{"id":"call_beta","name":"read_file","arguments":"{\"path\":\"beta.txt\"}"}]},"finish_reason":"tool_calls"}}
{"kind":"scope","category":"tool","name":"read_file","scope_category":"start","timestamp":"2026-05-31T00:15:08.956732+00:00","metadata":{"session_id":"docs-parallel-session","tool_call_id":"call_alpha"},"data":{"path":"alpha.txt"}}
{"kind":"scope","category":"tool","name":"read_file","scope_category":"start","timestamp":"2026-05-31T00:15:08.956804+00:00","metadata":{"session_id":"docs-parallel-session","tool_call_id":"call_beta"},"data":{"path":"beta.txt"}}
{"kind":"scope","category":"tool","name":"read_file","scope_category":"end","metadata":{"session_id":"docs-parallel-session","tool_call_id":"call_beta","status":"ok"},"data":"{\"content\":\"     1|docs_parallel_beta_function\\n\"}"}
{"kind":"scope","category":"tool","name":"read_file","scope_category":"end","metadata":{"session_id":"docs-parallel-session","tool_call_id":"call_alpha","status":"ok"},"data":"{\"content\":\"     1|docs_parallel_alpha_function\\n\"}"}
```

已过处理的 ATIF 摘要：

```json
{
  "schema_version": "ATIF-v1.7",
  "session_id": "docs-parallel-session",
  "agent": {"name": "Hermes Agent E2E", "version": "docs-example", "model_name": "qwen3.6:35b"},
  "steps": [
    {
      "source": "agent",
      "tool_calls": [
        {"tool_call_id": "call_alpha", "function_name": "read_file", "arguments": {"path": "alpha.txt"}},
        {"tool_call_id": "call_beta", "function_name": "read_file", "arguments": {"path": "beta.txt"}}
      ],
      "observation": {
        "results": [
          {"source_call_id": "call_beta", "content": "{\"content\":\"     1|docs_parallel_beta_function\\n\"}"},
          {"source_call_id": "call_alpha", "content": "{\"content\":\"     1|docs_parallel_alpha_function\\n\"}"}
        ]
      }
    },
    {"source": "agent", "message": "parallel tools complete."}
  ]
}
```

## ATOF 映射机制

该插件保留了 NeMo Relay 的原生事件模型：

- Hermes 会话对应 `agent` 范围。
- Hermes API 请求钩子对应 `llm` 范围的开始/结束事件。
- Hermes 工具钩子对应 `tool` 范围的开始/结束事件。
- 转换、审批、子代理以及诊断回退事件则对应 `mark` 事件。

为实现子代理间的关联，mark 元数据会包含父会话 ID 和子会话 ID、子代理 ID（如有）、角色/状态字段，以及计算得到的 `parent_trajectory_id` / `child_trajectory_id` 值。这样一来，ATOF 流式数据便能保持无损，便于后续进行 ATIF 转换，从而将子代理整合为独立的轨迹。

## 自适应中间件示例

当启用自适应组件时，`observability/nemo_relay` 插件会利用 Hermes 执行中间件，将 LLM 和工具调用交由 NeMo Relay 管理的执行引擎处理。

最简的 `plugins.toml` 配置如下：

```toml
version = 1

[[components]]
kind = "adaptive"
enabled = true

[components.config.tool_parallelism]
mode = "observe_only"
```

为 Hermes 启用该功能：

```bash
export HERMES_NEMO_RELAY_PLUGINS_TOML=/tmp/hermes-middleware-test/plugins.toml
```

当自适应组件处于启用状态，且已安装的 NeMo Relay 运行时提供了 `llm.execute(...)` 和 `tools.execute(...)` 接口时，Hermes 会通过这些接口来路由执行任务。

```text
Hermes provider call
  -> llm_execution middleware
    -> nemo_relay.llm.execute(...)
      -> Hermes provider adapter next_call(...)

Hermes tool call
  -> tool_execution middleware
    -> nemo_relay.tools.execute(...)
      -> Hermes tool dispatcher next_call(...)
```

该插件仍会为会话、轮次、审批以及子代理生成观察者标记。当启用自适应托管执行模式时，它会跳过手动调用的 `llm.call` 和 `tools.call` 观察者时间跨度，从而避免针对同一执行过程产生重复的 LLM/工具事件。

### 本地自适应端到端模式

该示例可在本地运行 Hermes 的同时，实现 NeMo Relay 可观测性数据的导出以及自适应执行中间件功能。此方案需要使用支持 `[components.config.tool_parallelism]` 配置的 NeMo Relay 运行时，目前从 0.5 版本开始的相应 0.x 系列版本均满足该要求。

```bash
export HERMES_HOME=/tmp/hermes-middleware-test/hermes-home
mkdir -p "$HERMES_HOME" /tmp/hermes-middleware-test/nemo-relay

cat > "$HERMES_HOME/config.yaml" <<'YAML'
model:
  provider: custom
  default: qwen3.6:35b
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
plugins:
  enabled:
    - observability/nemo_relay
YAML

cat > /tmp/hermes-middleware-test/nemo-relay/plugins.toml <<'TOML'
version = 1

[[components]]
kind = "observability"
enabled = true

[components.config]
version = 1

[components.config.atof]
enabled = true
output_directory = "/tmp/hermes-middleware-test/atof"
filename = "middleware-events.jsonl"
mode = "overwrite"

[components.config.atif]
enabled = true
output_directory = "/tmp/hermes-middleware-test/atif"
filename_template = "middleware-trajectory-{session_id}.json"
agent_name = "Hermes Middleware E2E"
agent_version = "local"

[[components]]
kind = "adaptive"
enabled = true

[components.config.tool_parallelism]
mode = "observe_only"
TOML

export HERMES_NEMO_RELAY_PLUGINS_TOML=/tmp/hermes-middleware-test/nemo-relay/plugins.toml

hermes chat \
  --query 'Use the terminal tool exactly once to run printf middleware_execution_ok. Then reply with exactly the command output.' \
  --provider custom \
  --model qwen3.6:35b \
  --toolsets terminal \
  --max-turns 4 \
  --quiet \
  --accept-hooks
```

预期的 CLI 输出结果：

```text
session_id: middleware-demo-session
middleware_execution_ok
```

预期的 ATOF 形状：

```jsonl
{"kind":"scope","category":"llm","name":"custom","scope_category":"start","metadata":{"session_id":"middleware-demo-session"},"data":{"mode":"observe_only"}}
{"kind":"scope","category":"tool","name":"terminal","scope_category":"start","metadata":{"session_id":"middleware-demo-session","tool_call_id":"call_terminal"},"data":{"mode":"observe_only"}}
{"kind":"scope","category":"tool","name":"terminal","scope_category":"end","metadata":{"session_id":"middleware-demo-session","tool_call_id":"call_terminal","status":"ok"},"data":"{\"output\":\"middleware_execution_ok\",\"exit_code\":0,\"error\":null}"}
```

预期的 ATIF 格式：

```json
{
  "schema_version": "ATIF-v1.7",
  "session_id": "middleware-demo-session",
  "agent": {
    "name": "Hermes Middleware E2E",
    "version": "local",
    "model_name": "qwen3.6:35b"
  },
  "steps": [
    {
      "source": "agent",
      "tool_calls": [
        {
          "function_name": "terminal",
          "arguments": {"command": "printf middleware_execution_ok"}
        }
      ],
      "observation": {
        "results": [
          {
            "source_call_id": "call_terminal",
            "content": "{\"output\":\"middleware_execution_ok\",\"exit_code\":0,\"error\":null}"
          }
        ]
      }
    },
    {
      "source": "agent",
      "message": "middleware_execution_ok"
    }
  ]
}
```
