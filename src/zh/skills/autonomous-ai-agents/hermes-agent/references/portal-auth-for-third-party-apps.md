# Nous Portal — 如何让第三方应用无需复制粘贴API密钥即可使用订阅服务

用户经常询问：“像Karakeep、OpenWebUI、LibreChat、OpenViking、LangChain pipeline、n8n flow等应用，能否直接通过我已有的Portal登录方式，无需手动复制API密钥就能使用我的Nous Portal订阅服务？”

其实，答案涉及三个常被混淆的架构层面。在提出解决方案之前，我们先依次了解这些层面。

---

## 第一层 — 该应用是Hermes插件，还是独立应用？

这是首先要回答的问题。尤其是“OpenViking”这类案例，常常让开发者感到困惑。

| 表面形态 | 实际本质 | 认证路径 |
|---|---|---|
| **OpenViking内存插件**（`plugins/memory/openviking/`） | 在Hermes进程内部运行的代码。其LLM调用会通过Hermes已配置的提供商完成认证。 | 若用户的Hermes已配置为使用Portal，该插件会自动使用Portal进行认证，无需额外操作。`OPENVIKING_API_KEY`是OpenViking*服务器自身*的认证密钥，与LLM认证无关。 |
| **独立的OpenViking服务器**（单独的容器） | 一个独立的上下文数据库服务。若其需要自行调用LLM，则会通过独立的HTTP客户端完成请求。 | 与任何外部应用相同，属于下方的第2/3层。 |
| **Karakeep、n8n、LibreChat、OpenWebUI以及所有自托管应用** | 运行在独立进程中，通常位于不同机器上。它们会通过HTTPS直接调用`inference-api.nousresearch.com`接口。 | 同属第2/3层。 |

**需避免的误区**：对于那些已经在Hermes内部运行的插件，不要试图用“将OAuth集成到Portal中”作为解决方案。因为这类LLM调用早已通过Hermes的提供商配置完成了认证。插件自身的服务器认证（例如用于调用OpenViking REST API的`OPENVIKING_API_KEY`）与Portal并无关联。

---

## 第二层 — 对于真正的第三方应用，Portal实际提供了什么？

位于`https://inference-api.nousresearch.com/v1`的Portal是一个兼容OpenAI的推理接口。它仅支持**bearer-token认证**，具体方式有两种：

1. 从`portal.nousresearch.com → API Keys`获取的**静态API密钥**；
2. 基于x402协议的**支付类请求头**（支持Solana USDC、匿名模式，且按每次请求计费）。

该Portal**不存在通用的OAuth 2.0授权服务器**，也没有第三方应用可以注册为客户端的“通过Nous Portal登录”的单点登录功能。此外，浏览器端的Portal登录也不会为同一台机器上的其他应用生成共享的cookie或会话。

Hermes Agent中那种看似类似OAuth的功能——即通过`hermes login --provider nous`打开浏览器，用户登录后，令牌会被保存在`~/.hermes/auth.json`中——实际上是一种**专为Hermes设计的浏览器登录流程**。其底层机制是生成一个凭证，由Hermes作为bearer token使用。这并非一种公开的OAuth提供商，因此Karakeep等应用也无法为其实现客户端功能，因为它从本质上就不属于OAuth提供商。

---

## 第三层 — 能否在不修改Portal的情况下填补这一缺口？

可以。解决方案是使用**本地凭证代理**。即便没有公开的OAuth流程，用户机器上的应用也可以：

1. 从`~/.hermes/auth.json`中读取Hermes已存储的Portal凭证；
2. 在`http://localhost:NNNN/v1`地址上提供一个兼容OpenAI的本地接口；
3. 将接收到的请求连同该bearer token一起转发至`inference-api.nousresearch.com/v1`。

这样，Karakeep、OpenWebUI等应用只需将调用地址设置为`http://localhost:NNNN/v1`，并使用任意占位密钥即可。用户无需再手动复制Portal密钥，因为代理会直接使用Hermes已存储的凭证完成认证。

在Hermes中实现该功能的可行位置包括：

- `gateway/platforms/api_server.py`已提供了类似思路——它通过本地兼容OpenAI的接口暴露Agent功能，但会完整走完Agent的调用流程（包括工具调用等）。而代理版本则仅负责**纯推理请求的转发**：不涉及Agent循环或工具调用，只需将用户存储的Portal bearer token附在请求上，直接转发至上游接口。
- 可以将其实现为一个约150行的新网关适配器，或作为`plugins/`目录下的插件。
- 令牌刷新机制：如果浏览器端的OAuth流程会生成可刷新的令牌，那么Hermes现有的凭证池刷新逻辑已经可以派上用场；若是长期有效的静态bearer token，则实现起来更为简单。这确实非常实用，值得投入开发——它正是解决“无需复制粘贴密钥即可将我的Portal订阅用于$
