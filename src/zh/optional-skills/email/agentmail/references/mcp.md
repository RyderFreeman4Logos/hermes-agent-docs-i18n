# AgentMail MCP

仅当用户或集成框架已经需要使用 MCP 工具时，才应采用 MCP。对于 AgentMail 工作流而言，命令行界面仍是默认的选择。

托管服务器：

```text
https://mcp.agentmail.to/mcp
```

身份验证方式：

- 兼容的MCP客户端支持OAuth认证。
- 通过`?apiKey=...`参数传递API密钥。
- 通过`x-api-key`请求头传递API密钥。
