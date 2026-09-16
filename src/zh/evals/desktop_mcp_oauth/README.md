# 桌面端 MCP OAuth 集成检查

请在已安装 Python MCP 相关依赖项及桌面端 Node.js 相关依赖的终端环境中运行该命令。执行结果为本地生成的凭证文件，建议将其保存在终端环境之外。这两种工具均不会使用真实的服务提供商凭据。

```bash
python3 evals/desktop_mcp_oauth/backend_http_fixture.py --repo . --output /tmp/mcp-backend.json
node evals/desktop_mcp_oauth/renderer_lifecycle.mjs "$PWD" /tmp/mcp-renderer.json approved
node evals/desktop_mcp_oauth/renderer_lifecycle.mjs "$PWD" /tmp/mcp-scope.json cancel
node evals/desktop_mcp_oauth/renderer_lifecycle.mjs "$PWD" /tmp/mcp-unmount.json unmount
```

后端集成工具会创建临时性的HOME/HERMES_HOME目录以及本地的HTTP OAuth/MCP提供者。它会模拟生产环境中的会话功能，包括服务发现、动态注册、PKCE代码交换、令牌持久化处理，以及通过重新认证来获取MCP访问权限。错误状态、回调重放、服务器异常、配置文件错误以及任务取消等场景均被用作负面测试用例。该工具会清除临时令牌存储，并仅返回布尔值或路径信息，而绝不会暴露令牌的具体内容。

前端渲染工具则会将真正的McpTab及其在Chromium中的依赖项打包在一起，通过仅支持注册功能的Electron IPC适配器来运行生产环境级的本地回环监听器，同时使用固定的WebSocket后端。`cancel`命令用于改变组件的作用域，而`unmount`命令则用于彻底移除该组件。这两种操作都必须取消原有的后端会话并关闭其本地监听器，且不得传递任何回调信息。当处于`approved`状态时，必须使用原生传输机制而非REST认证方式。如需使用现有的Chromium可执行文件，可设置`CHROMIUM_EXECUTABLE`环境变量；否则系统将自动使用Playwright已安装的浏览器。

这些工具属于互补性的集成测试用例，并非单一的端到端Electron/提供者测试。前端渲染后端与Electron注册接口之间的交互属于固定配置；Python测试用例则直接调用生产环境中的会话功能，而非通过网关RPC方式进行通信。此外，这些测试并不涉及任何原生Electron应用程序的启动，也不会请求托管提供者的授权。

在开展 A/B 测试时，只需通过替换基准结账流程的第一个参数，即可让相同的渲染器工具套件作用于该流程。在应用共享中继变更之前，已通过的断言就会失效。而在生命周期回归测试中，范围标签清理操作之前的那个结账流程会使得两项弃单断言均不通过。即便提供了会话 ID 和有效状态，后端的跨配置文件回调也必须被拒绝；原操作者仍需能够在之后完成该操作。
