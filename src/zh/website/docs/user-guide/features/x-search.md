---
title: X (Twitter) Search
description: Search X (Twitter) posts and threads from within the agent using xAI's built-in x_search Responses tool — works with either a SuperGrok OAuth login or an XAI_API_KEY.
sidebar_label: X (Twitter) Search
sidebar_position: 7
---

# X（Twitter）搜索功能

`x_search` 工具允许智能体直接搜索 X（Twitter）上的帖子、个人资料及主题串。该功能基于 xAI 在 `https://api.x.ai/v1/responses` 提供的 Responses API 中内置的 `x_search` 工具实现——实际搜索工作在服务器端由 Grok 完成，随后返回带有原始帖子引用信息的综合搜索结果。

当您需要获取 **X 平台上的最新讨论内容、用户反应或相关声明** 时，请使用此功能而非 `web_search`。对于普通网页内容，仍建议继续使用 `web_search` 或 `web_extract`。

## `x_search` 与 `xurl` 的区别

Hermes 可以提供两种不同的 X 平台访问方式：

| 访问方式 | 适用场景 | 不适用场景 |
|---------|----------|------------|
| `x_search` | 仅用于读取公开的 X 平台内容：包括最新讨论、用户反应、声明、个人资料、主题串，以及带有引用信息的综合回答。 | 发布内容、回复消息、点赞、发送私信、上传媒体文件、删除内容，或验证某个已认证的 X 账户的状态是否发生改变。 |
| `xurl` 技能 | 需要使用精确的或已认证的 X API 功能：如 `post`、`reply`、`read`、`like`、`dm`、时间线查询、提及功能、媒体上传、针对特定账户的读取操作，以及原始的 v2 接口。 | 在有 `x_search` 可用且无需已认证账户上下文的情况下，进行由 Grok 综合处理的广泛公开内容搜索。 |
对于混合工作流，可先使用 `x_search` 搜索潜在的公开帖子，待确定目标帖子、用户或操作后，再切换为 `xurl read` 或其他具体的 `xurl` 命令。任何会改变系统状态的 X 操作都必须通过 `xurl` 的输出结果或 X API 的响应来确认；`x_search` 的搜索结果绝不能作为内容已被写入的有效证据。

:::提示
如果您已经为 xAI 模型支付了 Portal 使用费用，那么实时搜索功能将按照为聊天功能配置的同一 xAI 密钥来计费。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 认证方式

当以下**任意一种** xAI 凭证路径可用时，`x_search` 即可正常注册：

| 凭证类型 | 来源 | 设置方式 |
|----------|------|----------|
| **SuperGrok / X Premium+ OAuth** | 在 `accounts.x.ai` 网页端登录，凭证会自动刷新 | 执行 `hermes auth add xai-oauth` — 详情参见 [xAI Grok OAuth (SuperGrok / X Premium+)](../../guides/xai-grok-oauth.md) |
| **`XAI_API_KEY`**（推荐） | 已购买的 xAI API 密钥 | 在 `~/.hermes/.env` 文件中配置 |

这两种方式都会向相同的接口发送相同的内容数据，唯一区别在于所使用的令牌类型。**当两种认证方式同时配置时，显式指定的 `XAI_API_KEY` 会优先生效**——基于订阅服务的 OAuth 令牌虽能授权访问 `/v1/responses` 接口，但会对 `x_search` 的查询以简化的 Grok 解释模式响应且不提供引用信息；而 API 密钥则能返回真实的帖子内容。需要注意的是，一旦设置了 API 密钥，`x_search` 将按照计费型 API 的规则进行调用；如需恢复为基于订阅额度的使用方式，请移除 `XAI_API_KEY`，但此时响应质量会受到影响。

每当模型的工具列表被重新生成时，该工具的 `check_fn` 函数就会启动 xAI 凭证解析器。若其返回值为 `True`，则表示该凭据既可获取，内容也非空，且（在已过期的情况下）已成功刷新。那些刷新失败、已被撤销的令牌会导致相关工具在架构中不可见，模型根本无法识别这些工具。

## 启用该工具

只要存在 xAI 凭证（OAuth 令牌或 `XAI_API_KEY`），该工具就会自动启用。如果您不希望如此，可通过 `hermes tools` → Search → x_search 来手动禁用它。

```bash
hermes tools
# → 🐦 X (Twitter) Search   (press space to toggle on)
```

该选择器提供两种身份验证方式：

1. **xAI Grok OAuth（SuperGrok / Premium+）**——若尚未登录，将会自动打开浏览器跳转至 `accounts.x.ai` 页面；
2. **xAI API密钥**——会提示输入 `XAI_API_KEY`。

无论选择哪种方式，都能满足系统验证要求。您可以根据自身已拥有的凭证进行选择，两种方式的使用效果完全一致。如果同时配置了这两种方式，在实际调用时系统会优先使用OAuth认证。 

## 配置说明

```yaml
# ~/.hermes/config.yaml
x_search:
  # xAI model used for the Responses call.
  # grok-4.5 is the recommended default; any Grok model
  # with x_search tool access works.
  model: grok-4.5

  # Optional reasoning effort: low, medium, high, or xhigh. When omitted,
  # the selected model's default applies. xhigh is supported only by
  # models that document it, such as grok-4.20-multi-agent.
  # reasoning_effort: low

  # Request timeout in seconds. x_search can take 60–120s for
  # complex queries — the default is generous. Minimum: 30.
  timeout_seconds: 180

  # Number of automatic retries on 5xx / ReadTimeout / ConnectionError.
  # Each retry backs off (1.5x attempt seconds, capped at 5s).
  retries: 2
```

`reasoning_effort` 会以 `reasoning: {effort: ...}` 的格式发送至 xAI Responses API。对于不支持可配置推理的模型，可将其保持未设置状态。无效值会在发起 API 请求之前被拒绝。

## 工具参数

Agent 会使用以下参数调用 `x_search`：

| 参数 | 类型 | 描述 |
|------|------|------|
| `query` | 字符串（必填） | 在 X 平台上搜索的内容。 |
| `allowed_x_handles` | 字符串数组 | 可选列表，用于指定**仅包含**的账号地址（最多 10 个）。开头的 `@` 符号会被移除。 |
| `excluded_x_handles` | 字符串数组 | 可选列表，用于指定需排除的账号地址（最多 10 个）。该参数与 `allowed_x_handles` 不能同时使用。 |
| `from_date` | 字符串 | 可选的起始日期，格式为 `YYYY-MM-DD`。 |
| `to_date` | 字符串 | 可选的结束日期，格式为 `YYYY-MM-DD`。 |
| `enable_image_understanding` | 布尔值 | 要求 xAI 分析匹配帖子中附带的图片。 |
| `enable_video_understanding` | 布尔值 | 要求 xAI 分析匹配帖子中附带的视频。 |

该工具会返回包含以下内容的 JSON 数据：

- `answer` — 由 Grok 生成的合成文本回复  
- `citations` — Responses API 返回的引用信息，属于顶层字段  
- `inline_citations` — 从消息正文中提取的 `url_citation` 注解（每个注解包含 `url`、`title`、`start_index` 和 `end_index`）  
- `degraded` — 当设置了任何筛选条件（如 `allowed_x_handles`、`excluded_x_handles`、`from_date`、`to_date`），且两个引用来源均返回空结果时，该值为 `true`。此时回复是基于模型自身的知识生成的，而非来自 X index 的数据，因此应视为无来源信息。其他情况下该值为 `false`（包括“未设置任何筛选条件”的情况——这种情况下的宽泛无来源回复仅属于普通回复，并非筛选条件未满足所致）  
- `degraded_reason` — 简要说明当前处于激活状态的筛选条件名称；当 `degraded` 为 `false` 时，该值为 `null`  
- `credential_source` — 若通过 OAuth 验证，则为 `"xai-oauth"`；若通过 API 密钥验证，则为 `"xai"`  
- `model`、`query`、`provider`、`tool`、`success`  

### 日期验证  

在发起 HTTP 请求之前，客户端会对 `from_date`/`to_date` 进行验证：  
- 若提供了这两个日期，必须能解析为 `YYYY-MM-DD` 格式。  
- 当同时设置这两个日期时，`from_date` 的值必须小于或等于 `to_date`。  
- `from_date` 不能晚于当前 UTC 时间——因为尚未开始的时段中不可能存在相关内容，此时请求必然会返回零条引用结果。  
- 允许设置未来的 `to_date` 值（调用方可能合理地要求查询“从昨天到明天”的数据，以便在内容发布时及时获取）。
验证失败会以结构化的 `{"error": "..."}` 工具结果形式呈现，而不会通过向 xAI 发送 HTTP 请求的方式来体现。

## 示例

与智能体对话：

> X 上的用户对新的 Grok 图像功能有什么评价？重点关注 @xai 的回复。

智能体将执行以下操作：

1. 调用 `x_search`，传入参数 `query="reactions to new Grok image features"` 以及 `allowed_x_handles=["xai"]`
2. 获取综合后的答案以及指向具体帖子的引用列表
3. 一并回复答案与相关参考信息

如果后续用户请求为“回复最合适的那个”或“点赞那篇帖子”，智能体应切换至 `xurl` 技能，确认目标帖子的确切内容，然后使用 X API 功能。`x_search` 仍仅作为信息检索工具使用。

## 故障排除

### “未找到 xAI 凭证”

当两种认证方式均失败时，工具会显示此错误信息。请在 `~/.hermes/.env` 文件中设置 `XAI_API_KEY`，或运行 `hermes auth add xai-oauth` 并完成浏览器登录。之后重启会话，以便智能体重新读取工具注册表。

### “当前模型未启用 `x_search` 功能”

所配置的 `x_search.model` 无法访问服务器端的 `x_search` 工具。请切换为默认的 `grok-4.5` 模型或其他支持该功能的 Grok 模型。具体支持的模型列表可查阅 [xAI 文档](https://docs.x.ai/)。

### 工具未出现在架构定义中

可能的原因有二：

1. **工具集未启用。** 请运行 `hermes tools`，并确认已勾选 `🐦 X (Twitter) Search` 选项。  
2. **缺少 xAI 凭证。** 由于 check_fn 返回 False，因此架构信息将保持隐藏状态。请运行 `hermes auth status` 查看 xai-oauth 的登录状态，并确认已设置 `XAI_API_KEY`（若您使用的是 API-key 方式）。

### `degraded: true` — 无引用答案

当您使用了 `allowed_x_handles`、`excluded_x_handles` 或时间范围，且返回结果中显示 `degraded: true` 时，意味着 xAI 的 X 索引未找到匹配的帖子，但 Grok 仍会基于自身的训练数据生成合成答案。此类答案缺乏来源信息，不可视为真实的 X 平台结果。

建议检查的原因包括：

- **账号标识符存在拼写错误。** 请去掉 `@` 符号，仔细核对拼写，并确认该账号确实存在。  
- **时间范围过窄** 或未涵盖今日的帖子；请扩大时间范围后重试。  
- **xAI 索引存在缺失。** 部分活跃账号即便经常发帖，也可能会暂时无法在 `x_search` 中显示。建议几分钟后重试；若需要获取特定账号的完整动态，可使用 `xurl` 技能直接调用 X API。

## 相关文档

- [xAI Grok OAuth（SuperGrok / Premium+）](../../guides/xai-grok-oauth.md) — OAuth 设置指南  
- [xurl 技能](../skills/bundled/social-media/social-media-xurl.md) — 用于已认证账号操作的官方 X API CLI 工具  
- [网页搜索与提取](web-search.md) — 用于常规（非 X 平台）网页搜索  
- [工具参考手册](../../reference/tools-reference.md) — 完整的工具目录
