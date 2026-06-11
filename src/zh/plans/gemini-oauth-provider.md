# Gemini OAuth 提供方 —— 实施方案

## 目标
构建一个一流的 `gemini` 提供方，该提供方通过 Google OAuth 进行身份验证，使用标准的 Gemini API（而非 Cloud Code Assist）。拥有 Google AI 订阅或 Gemini API 访问权限的用户无需手动复制 API 密钥，即可在浏览器中完成认证。

## 架构决策
- **方案 A（选定）：** 使用位于 `generativelanguage.googleapis.com/v1beta` 的标准 Gemini API
- **不采用方案 B：** Cloud Code Assist（`cloudcode-pa.googleapis.com`）——免费套餐存在速率限制，属于内部 API，还存在账户被封禁的风险
- 通过 OpenAI SDK 使用标准的 `chat_completions` api_mode —— 无需新增 api_mode
- 使用我们自己的 OAuth 凭证 —— 不会将令牌共享给 Gemini CLI

## OAuth 流程
- **类型：** 授权码 + PKCE（S256）——与 clawdbot/pi-mono 的流程相同
- **认证地址：** `https://accounts.google.com/o/oauth2/v2/auth`
- **令牌获取地址：** `https://oauth2.googleapis.com/token`
- **重定向地址：** `http://localhost:8085/oauth2callback`（本地回调服务器）
- **备用方案：** 对于远程/WSL/无头环境，支持手动粘贴地址
- **授权范围：** `https://www.googleapis.com/auth/cloud-platform`、`https://www.googleapis.com/auth/userinfo.email`
- **PKCE：** S256 代码挑战机制，随机生成 32 字节的验证器

## 客户端 ID
- 需要在 Nous Research 的 GCP 项目中注册“桌面应用”类型的 OAuth 客户端
- 将 client_id 和 client_secret 直接嵌入代码中（Google 认为已安装应用的密钥不属于敏感信息）
- 或者：允许用户通过环境变量提供 client_id 作为覆盖值

## 令牌生命周期管理
- 令牌存储在 `~/.hermes/gemini_oauth.json` 文件中（不会与 `~/.gemini/oauth_creds.json` 共享）
- 文件包含的字段有：`client_id`、`client_secret`、`refresh_token`、`access_token`、`expires_at`、`email`
- 文件权限设置为 0o600
- 每次调用 API 前，检查令牌是否过期；若距离过期时间不足 5 分钟，则进行刷新
- 刷新操作：通过 POST 请求发送至令牌获取地址，并设置 `grant_type=refresh_token` 参数
- 为应对多个代理会话同时访问的情况，需对文件进行加锁处理

## API 集成
- 基础 URL：`https://generativelanguage.googleapis.com/v1beta`
- 认证：由提供方适配器处理标准的 Gemini API 认证逻辑
- api_mode：设置为 `chat_completions`（在原生传输层之上构建的标准接口）
- 支持的模型包括：gemini-2.5-pro、gemini-2.5-flash、gemini-2.0-flash 等

## 需要创建/修改的文件

### 新文件
1. `agent/google_oauth.py` —— 负责处理 OAuth 流程（包括 PKCE、本地服务器、令牌交换及刷新操作）
   - `start_oauth_flow()`：打开浏览器并启动回调服务器
   - `exchange_code()`：将授权码转换为令牌
   - `refresh_access_token()`：执行令牌刷新流程
   - `load_credentials()` / `save_credentials()`：负责带加锁机制的文件读写操作
   - `get_valid_access_token()`：检查令牌有效期，必要时进行刷新
   - 文件约 200 行代码

### 需要修改的现有文件
2. `hermes_cli/auth.py`：为“gemini”提供方添加 ProviderConfig，设置 auth_type 为“oauth_google”
3. `hermes_cli/models.py`：补充 Gemini 模型目录信息
4. `hermes_cli/runtime_provider.py`：新增 gemini 分支，用于读取 OAuth 令牌并构建 OpenAI 客户端
5. `hermes_cli/main.py`：添加 `_model_flow_gemini()` 函数，并将该模型加入可用提供方列表
6. `hermes_cli/setup.py`：添加 Gemini 认证流程相关代码，用于触发浏览器中的 OAuth 认证
7. `run_agent.py`：在每次 API 调用前执行令牌刷新操作（采用与 Copilot 类似的机制）
8. `agent/auxiliary_client.py`：将 Gemini 添加到辅助模型解析链中
9. `agent/model_metadata.py`：补充 Gemini 模型的上下文长度相关信息

### 测试相关
10. `tests/agent/test_google_oauth.py`：针对 OAuth 流程编写单元测试
11. `tests/test_api_key_providers.py`：新增针对 Gemini 提供方的测试用例

### 文档更新
12. `website/docs/getting-started/quickstart.md`：在提供方列表中添加 Gemini 选项
13. `website/docs/user-guide/configuration.md`：补充 Gemini 的配置相关内容
14. `website/docs/reference/environment-variables.md`：新增与 Gemini 相关的环境变量说明

## 预计工作量
新代码约 400 行，修改代码约 150 行，测试代码约 100 行，文档编写约 50 行，总计约 700 行代码。

## 前提条件
- 拥有 Nous Research 的 GCP 项目，并已注册桌面端 OAuth 客户端
- 或者：通过 HERMES_GEMINI_CLIENT_ID 环境变量接受用户提供的客户端 ID

## 参考实现方案
- clawdbot：`extensions/google/oauth.flow.ts`（包含 PKCE 机制及本地服务器支持）
- pi-mono：`packages/ai/src/utils/oauth/google-gemini-cli.ts`（采用相同的流程）
- hermes-agent Copilot 的 OAuth 实现：`hermes_cli/main.py` 中的 `_copilot_device_flow()` 函数（流程类型不同，但生命周期管理逻辑一致）
