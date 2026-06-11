# FastMCP CLI 参考手册

当任务需要严格遵循 FastMCP CLI 的工作流程，而非仅参考 `SKILL.md` 中的更高层级指导时，请使用本文档。

## 安装与验证

```bash
pip install fastmcp
fastmcp version
```

FastMCP的官方文档将`pip install fastmcp`以及`fastmcp version`列为基础的安装与版本验证步骤。

## 启动服务器

通过Python脚本来启动服务器对象：

```bash
fastmcp run server.py:mcp
```

通过 HTTP 启动相同的服务器：

```bash
fastmcp run server.py:mcp --transport http --host 127.0.0.1 --port 8000
```

## 检查服务器信息

查看 FastMCP 将暴露的内容：

```bash
fastmcp inspect server.py:mcp
```

这同样是 FastMCP 在部署到 Prefect Horizon 之前建议进行的检查项。

## 列出并调用工具

从 Python 文件中列出工具：

```bash
fastmcp list server.py --json
```

从 HTTP 接口列出工具：

```bash
fastmcp list http://127.0.0.1:8000/mcp --json
```

使用键值参数调用工具：

```bash
fastmcp call server.py search_resources query=router limit=5 --json
```

使用完整的 JSON 输入数据来调用工具：

```bash
fastmcp call server.py create_item '{"name": "Widget", "tags": ["sale"]}' --json
```

## 查找已命名的 MCP 服务器

查找已在支持 MCP 的本地工具中配置好的命名服务器：

```bash
fastmcp discover
```

FastMCP文档介绍了针对Claude Desktop、Claude Code、Cursor、Gemini、Goose以及`./mcp.json`的基于名称的解析机制。

## 安装到MCP客户端中

在常用客户端中注册服务器：

```bash
fastmcp install claude-code server.py
fastmcp install claude-desktop server.py
fastmcp install cursor server.py -e .
```

FastMCP指出，客户端安装是在隔离环境中运行的，因此需要在必要时通过`--with`、`--env-file`等参数或可编辑安装方式明确指定依赖项。

## 部署检查

### Prefect Horizon

在推送到Horizon之前：

```bash
fastmcp inspect server.py:mcp
```

FastMCP的Horizon文档要求提供以下内容：

- 一个GitHub仓库  
- 包含FastMCP服务器对象的Python文件  
- 在`requirements.txt`或`pyproject.toml`中列明的依赖项  
- 类似`main.py:mcp`这样的程序入口点  

### 通用HTTP托管方案

在将应用部署到其他主机之前，请先执行以下步骤：

1. 使用HTTP传输方式在本地启动服务器。  
2. 通过访问本地的 `/mcp` URL，使用`fastmcp list`命令进行验证。  
3. 确认至少能成功执行一次`fastmcp call`操作。  
4. 记录所有必需的环境变量。
