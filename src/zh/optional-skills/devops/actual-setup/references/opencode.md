# 将 actual.inc 作为 OpenCode 提供者使用

经端到端验证，适用于 2026 年 7 月（OpenCode 1.18.3，macOS 环境）。该功能将 Actual 的中继/GLM 集群作为自定义的 OpenAI 兼容提供者集成至 OpenCode 中。

## 设计思路：凭证存储在 auth.json 中，配置存储在 opencode.json 中

当 `opencode.json` 中的提供者 **id** 与 `~/.local/share/opencode/auth.json` 中的凭证 **id** 匹配时，OpenCode 会自动注入对应凭证。因此，请将密钥放入 auth.json 文件中，而绝不要在 opencode.json 中存放任何敏感信息。这种方式比使用 `options.apiKey: "{env:...}"` 的方式更为可靠，因为后者仅能在 OpenCode 启动的 shell 中导出了相应变量时才有效——而 Actual 的密钥通常仅存储在 `~/.hermes/.env` 文件中，而非 shell 配置文件中，因此使用环境变量方式在非继承终端环境中将无法正常工作。

### 1. 将凭证添加到 auth.json 中

文件路径：`~/.local/share/opencode/auth.json`。格式要求（请保留现有条目）：
```json
{
  "anthropic": { "type": "api", "key": "..." },
  "actual":    { "type": "api", "key": "ac_..." }
}
```
请通过“读取-修改-写入”（即加载 JSON 文件、添加 `actual` 键，然后再导出）的方式来操作，这样其他凭证就能保持完整——切勿覆盖该文件。

### 2. 将该提供程序添加到 opencode.json 中

文件路径为 `~/.config/opencode/opencode.json`（或 `~/.opencode.json`）。在 `provider` 键下将其与其他已存在的条目一并添加。无需设置 `apiKey` 字段——该值会通过 ID 匹配从 auth.json 中自动获取。
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "actual": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Actual (GLM cluster)",
      "options": {
        "baseURL": "https://api.actual.inc/v1",
        "headers": {
          "X-Cluster-ID": "<cluster-id-hash>"
        }
      },
      "models": {
        "glm-5.2-nvfp4": {
          "name": "GLM-5.2 (b300x8)",
          "limit": { "context": 1048576, "output": 65536 }
        }
      }
    }
  }
}
```
- `npm`：对于 `/v1/chat/completions` 功能，应使用 `@ai-sdk/openai-compatible`；仅当模型需要使用 `/v1/responses` 功能时，才可使用 `@ai-sdk/openai`。  
- `options.headers.X-Cluster-ID`：用于指定特定的集群（可选；若省略则由中继路由决定）。该值可从 Actual 控制台地址中获取哈希值（地址格式为 `console/computers?cluster=<hash>`）。  
- `models.<id>`：此 ID 必须与 `GET /v1/models` 请求的返回值一致。首先需通过以下命令查询模型 ID：`curl -s https://api.actual.inc/v1/models -H "Authorization: Bearer ac_..." -H "X-Cluster-ID: <hash>"`。  
- `limit`：用于让 OpenCode 跟踪剩余上下文长度（自定义提供程序无法从 models.dev 获取此参数）。GLM-5.2 模型的上下文限制为 1,048,576 字节。  

### 3. 验证实时运行状态（无界面模式）

```bash
opencode run -m actual/glm-5.2-nvfp4 "Reply with exactly this text: OPENCODE_ACTUAL_OK"
```
OpenCode 确实会在 CLI 中使用 `provider/model` 的斜杠格式（这与 Hermes 不同，Hermes 使用该格式时会返回 404 错误，因为无法找到自定义 provider）。因此请预期会得到这样的响应。由于 GLM-5.2 是一个具备推理能力的模型，建议再执行一次推理测试（例如“17 * 23 等于多少？”）。

## 为何此处不存在 reasoning_effort 相关问题

Actual relay 会通过 HTTP 400 错误拒绝 `reasoning_effort: xhigh` 的请求（可参考 `hermes-custom-providers` 技能中的第 2 个注意事项）。Hermes 会出现此问题，是因为它会转发全局的 `agent.reasoning_effort` 参数。而 OpenCode 的 ai-sdk 并不会发送该参数，因此 Actual 与 OpenCode 能够在无需任何推理配置的情况下正常配合工作，也无需设置类似的 `reasoning_overrides` 参数。

## 需注意的事项

- `auth.json` 与 `/connect` 命令写入的存储位置相同；直接编辑该文件也是可行的，效果一致。执行 `opencode auth list` 后，Credentials 下应会显示 `actual`。
- 如果发现 discovery/models 目录中的内容缺失，请确认 opencode.json 中的 provider id 与 auth.json 中的凭证 id 完全一致（即 `actual` == `actual`）。
- 默认配置目录（`~/.config/opencode`）并非版本控制仓库，因此不存在被 git 跟踪的风险。但为了保持习惯，仍建议将相关配置保存在 auth.json 中，而非 opencode.json 中。
