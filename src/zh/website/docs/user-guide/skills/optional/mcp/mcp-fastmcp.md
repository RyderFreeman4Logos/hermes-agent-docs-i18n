---
title: "Fastmcp — Build, test, inspect, install, and deploy MCP servers with FastMCP in Python"
sidebar_label: "Fastmcp"
description: "Build, test, inspect, install, and deploy MCP servers with FastMCP in Python"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Fastmcp

使用 Python 和 FastMCP 构建、测试、检查、安装及部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示词，以及为 Claude Code、Cursor 或 HTTP 部署准备 FastMCP 服务器。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/mcp/fastmcp` 进行安装 |
| 路径 | `optional-skills/mcp/fastmcp` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `MCP`、`FastMCP`、`Python`、`工具`、`资源`、`提示词`、`部署` |
| 相关技能 | [`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp)、[`mcporter`](/docs/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# FastMCP

使用 FastMCP 在 Python 中构建 MCP 服务器，在本地对其进行验证，将其安装到 MCP 客户端中，或作为 HTTP 端点进行部署。

## 适用场景

当需要执行以下任务时，可使用此技能：
- 用 Python 创建新的 MCP 服务器
- 将 API、数据库、CLI 或文件处理流程封装为 MCP 工具
- 除工具外还需暴露资源或提示词
- 在将服务器接入 Hermes 或其他客户端之前，使用 FastMCP CLI 进行初步测试
- 将服务器安装到 Claude Code、Claude Desktop、Cursor 或类似的 MCP 客户端中
- 为 HTTP 部署准备 FastMCP 服务器代码库

如果服务器已存在且仅需连接到 Hermes，则可使用 `native-mcp`。若目标是临时通过 CLI 访问现有的 MCP 服务器而非从头构建，则可使用 `mcporter`。

## 先决条件

首先需在工作环境中安装 FastMCP：

```bash
pip install fastmcp
fastmcp version
```

对于 API 模板，如果尚未安装 `httpx`，请先进行安装：

```bash
pip install httpx
```

## 包含的文件

### 模板

- `templates/api_wrapper.py` - 支持身份验证头部的 REST API 封装工具
- `templates/database_server.py` - 只读 SQLite 查询服务器
- `templates/file_processor.py` - 文本文件检测与搜索服务器

### 脚本

- `scripts/scaffold_fastmcp.py` - 复制起始模板并替换服务器名称占位符

### 参考资料

- `references/fastmcp-cli.md` - FastMCP CLI 工作流程、安装目标及部署检查项

## 工作流程

### 1. 选择最精简的可行服务器架构

首先选择功能最聚焦的架构：

- API 封装层：从 1-3 个高价值接口开始，而非整个 API
- 数据库服务器：仅提供只读查询功能及受限的查询路径
- 文件处理层：通过明确的路径参数实现确定性操作
- 提示词/资源模块：仅在客户端需要可复用的提示词模板或可检索文档时再添加

相比功能繁多但工具定义模糊的大型服务器，更推荐使用结构简洁、带有完整文档说明和架构规范的轻量级服务器。

### 2. 基于模板快速搭建

可直接复制模板，或使用搭建辅助工具：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py \
  --template api_wrapper \
  --name "Acme API" \
  --output ./acme_server.py
```

可用模板：

```bash
python ~/.hermes/skills/mcp/fastmcp/scripts/scaffold_fastmcp.py --list
```

如需手动复制，请将 `__SERVER_NAME__` 替换为实际的服务器名称。

### 3. 先实现工具功能

在添加资源或提示词之前，先从 `@mcp.tool` 函数开始构建。

工具设计的规则如下：

- 为每个工具赋予一个以动词构成的具体名称
- 将文档字符串编写成面向用户的工具描述
- 确保参数清晰且具有明确类型
- 尽可能返回结构化且符合 JSON 格式的数据
- 及早验证可能存在风险的输入
- 在初始版本中，默认采用只读模式

优秀的工具示例包括：

- `get_customer`
- `search_tickets`
- `describe_table`
- `summarize_text_file`

而较为欠缺的工具命名示例则为：

- `run`
- `process`
- `do_thing`

### 4. 仅在必要时添加资源与提示词

当客户端需要获取诸如架构定义、政策文档或生成的报告等稳定且只读的内容时，再添加 `@mcp.resource`。

若针对某种已知工作流程，服务器需要提供可重复使用的提示词模板，则应添加 `@mcp.prompt`。

切勿将所有文档都转化为提示词。更推荐的做法是：

- 使用工具来执行操作
- 使用资源来检索数据或文档
- 使用提示词来提供可复用的 LLM 指令

### 5. 在集成到任何系统之前先对服务器进行测试

可使用 FastMCP CLI 在本地完成验证：

```bash
fastmcp inspect acme_server.py:mcp
fastmcp list acme_server.py --json
fastmcp call acme_server.py search_resources query=router limit=5 --json
```

为实现高效的迭代式调试，建议在本地运行该服务器：

```bash
fastmcp run acme_server.py:mcp
```

要在本地测试 HTTP 传输功能：

```bash
fastmcp run acme_server.py:mcp --transport http --host 127.0.0.1 --port 8000
fastmcp list http://127.0.0.1:8000/mcp --json
fastmcp call http://127.0.0.1:8000/mcp search_resources query=router --json
```

在确认服务器正常运行之前，务必针对每个新工具至少执行一次真实的 `fastmcp call` 操作。

### 6. 本地验证通过后安装到客户端中

FastMCP 可将服务器注册到支持 MCP 的客户端中：

```bash
fastmcp install claude-code acme_server.py
fastmcp install claude-desktop acme_server.py
fastmcp install cursor acme_server.py -e .
```

可以使用 `fastmcp discover` 命令来查看机器上已配置的命名 MCP 服务器。

若目标是实现与 Hermes 的集成，可选择以下任一方式：

- 在 `~/.hermes/config.yaml` 文件中通过 `native-mcp` 技能来配置服务器；或
- 在开发阶段继续使用 FastMCP CLI 命令，直至接口稳定为止。

### 7. 当本地契约稳定后进行部署

对于托管服务，FastMCP 文档中有最直接的部署指南，即 Prefect Horizon。在部署之前：

```bash
fastmcp inspect acme_server.py:mcp
```

请确保仓库中包含以下内容：

- 包含 FastMCP 服务器对象的 Python 文件
- `requirements.txt` 或 `pyproject.toml` 文件
- 部署所需的任何环境变量相关文档

对于常规的 HTTP 托管方式，建议先在本地验证 HTTP 传输功能，然后再将其部署到任何能够开放服务器端口的兼容 Python 的平台上。

## 常见实现模式

### API 封装模式

适用于将 REST 或 HTTP API 转换为 MCP 工具的场景。

推荐的初始功能模块包括：

- 一个读取路径
- 一个列表/搜索路径
- 可选的健康检查功能

实现注意事项：

- 将认证信息存储在环境变量中，而非硬编码
- 将请求逻辑集中处理在一个辅助函数中
- 以简洁的方式展示 API 错误信息
- 在返回数据前对格式不一致的上游数据进行标准化处理

可从 `templates/api_wrapper.py` 文件开始编写。

### 数据库模式

适用于需要提供安全的查询与数据查看功能的场景。

推荐的初始功能模块包括：

- `list_tables`
- `describe_table`
- 一个带限制条件的读取查询工具

实现注意事项：

- 默认仅允许读取数据库数据
- 在早期版本中拒绝非 `SELECT` 类型的 SQL 查询
- 限制返回的记录数量
- 同时返回数据行及其列名

可从 `templates/database_server.py` 文件开始编写。

### 文件处理模式

适用于需要按需查看或转换文件内容的场景。

推荐的初始功能模块包括：

- 概要展示文件内容
- 在文件内进行搜索
- 提取确定的元数据

实现注意事项：

- 接受显式的文件路径输入
- 检查文件是否存在以及编码是否正确
- 限制预览内容和结果数量
- 除非确实需要使用外部工具，否则避免调用系统命令

可从 `templates/file_processor.py` 文件开始编写。

## 质量检查标准

在交付 FastMCP 服务器之前，请确认满足以下所有条件：

- 服务器能够正常导入依赖项
- `fastmcp inspect <file.py:mcp>` 命令可以成功执行
- `fastmcp list <server spec> --json` 命令可以成功执行
- 每个新工具都至少包含一次真实的 `fastmcp call` 调用
- 所有环境变量都有相应的文档说明
- 工具的功能结构清晰，无需猜测即可理解

## 故障排除

### FastMCP 命令缺失

请在当前激活的环境中安装相应包：

```bash
pip install fastmcp
fastmcp version
```

### `fastmcp inspect` 命令执行失败

请检查以下内容：

- 文件导入过程不会引发导致程序崩溃的副作用
- `<file.py:object>` 中的 FastMCP 实例名称是否正确
- 模板中指定的可选依赖项是否已安装

### 工具在 Python 环境中可以正常运行，但通过 CLI 无法使用

请执行以下操作：

```bash
fastmcp list server.py --json
fastmcp call server.py your_tool_name --json
```

这通常是由于名称不匹配、缺少必需参数，或是返回值不可序列化所导致的。

### Hermes 无法识别已部署的服务器

虽然服务器构建部分可能是正确的，但 Hermes 的配置可能存在问题。请加载 `native-mcp` 技能，并在 `~/.hermes/config.yaml` 中配置服务器，之后再重启 Hermes。

## 参考资料

如需了解 CLI 详细信息、目标安装方式以及部署检查相关内容，请参阅 `references/fastmcp-cli.md`。
