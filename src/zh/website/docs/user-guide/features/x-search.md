---
title: X (Twitter) Search
description: Search X (Twitter) posts and threads from within the agent using xAI's built-in x_search Responses tool — works with either a SuperGrok OAuth login or an XAI_API_KEY.
sidebar_label: X (Twitter) Search
sidebar_position: 7
---

# X（Twitter）搜索功能

`x_search` 工具允许智能体直接搜索 X（Twitter）上的帖子、个人主页及话题串。该功能基于 xAI 在 Responses API 中内置的 `x_search` 工具实现，接口地址为 `https://api.x.ai/v1/responses`——实际搜索工作在服务器端由 Grok 完成，它会返回经过整合的结果，并标注出原始帖子的来源。

当您需要获取 **X 平台上的最新讨论、反馈或观点** 时，请使用此工具而非 `web_search`。对于普通网页内容，仍建议继续使用 `web_search` 或 `web_extract`。

:::提示
如果您已经为 xAI 模型支付了 Portal 使用费用，那么实时搜索功能将消耗与聊天功能相同的 xAI 密钥对应的额度。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 认证方式

只要具备以下任意一种 xAI 凭证，即可启用 `x_search` 功能：

| 凭证类型 | 来源 | 设置方式 |
|----------|------|----------|
| **SuperGrok / X Premium+ OAuth**（推荐） | 在 `accounts.x.ai` 网页端登录，凭证会自动刷新 | 执行命令 `hermes auth add xai-oauth`，更多信息请参见 [xAI Grok OAuth（SuperGrok / X Premium+）](../../guides/xai-grok-oauth.md) |
| **`XAI_API_KEY`** | 已购买的 xAI API 密钥 | 在 `~/.hermes/.env` 文件中配置 |

两种方式都会向同一个接口发送相同格式的请求数据，唯一区别在于承载令牌的不同。**当两种凭证同时配置时，SuperGrok OAuth 会优先生效**，这样 `x_search` 功能就会消耗您的订阅额度，而非额外的 API 费用。

每当模型的工具列表被重新生成时，该工具的 `check_fn` 函数都会调用 xAI 凭证验证机制。若函数返回 `True`，则表示承载令牌可获取、内容非空，且（在过期情况下）已成功刷新。如果令牌已被撤销或刷新失败，该工具将从功能列表中消失，模型将无法使用它。

## 启用该工具

只要存在 xAI 凭证（OAuth 令牌或 `XAI_API_KEY`），该工具就会自动启用。如果您不希望其自动启用，可通过 `hermes tools` → Search → x_search 手动禁用。

```bash
hermes tools
# → 🐦 X (Twitter) Search   (press space to toggle on)
```

该选择器提供两种凭证选项：

1. **xAI Grok OAuth（SuperGrok / Premium+）**——若尚未登录，将自动打开浏览器跳转至 `accounts.x.ai` 页面；
2. **xAI API密钥**——会提示用户输入 `XAI_API_KEY`。

无论选择哪种方式，都能满足系统验证要求。您可以根据自身已拥有的凭证进行选择，两种方式的使用效果完全一致。如果同时配置了这两种凭证，在实际调用时系统会优先使用OAuth方式。 

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

`reasoning_effort` 会以 `reasoning: {effort: ...}` 的格式发送至 xAI Responses API。对于不支持可配置推理功能的模型，可将其保留为空值。无效的值会在发起 API 请求之前就被过滤掉。

## 工具参数

Agent 会使用以下参数调用 `x_search`：

| 参数 | 类型 | 描述 |
|------|------|------|
| `query` | 字符串（必填）| 在 X 平台上搜索的内容。 |
| `allowed_x_handles` | 字符串数组 | 可选列表，用于指定**仅包含**的账号标识（最多 10 个），开头的 `@` 符号会被去掉。 |
| `excluded_x_handles` | 字符串数组 | 可选列表，用于指定需要排除的账号标识（最多 10 个），与 `allowed_x_handles` 不能同时使用。 |
| `from_date` | 字符串 | 可选的起始日期，格式为 `YYYY-MM-DD`。 |
| `to_date` | 字符串 | 可选的结束日期，格式为 `YYYY-MM-DD`。 |
| `enable_image_understanding` | 布尔值 | 是否让 xAI 分析匹配帖子中附带的图片。 |
| `enable_video_understanding` | 布尔值 | 是否让 xAI 分析匹配帖子中附带的视频。 |

该工具会返回包含以下内容的 JSON 数据：

- `answer` — 由 Grok 生成的合成文本回复。
- `citations` — Responses API 返回的引用信息。
- `inline_citations` — 从消息正文中提取的 `url_citation` 注解，每个注解包含 `url`、`title`、`start_index` 和 `end_index` 字段。
- `degraded` — 当设置了任何筛选条件（`allowed_x_handles`、`excluded_x_handles`、`from_date`、`to_date`）且两种引用来源均为空时，该值为 `true`。此时回复内容是基于模型自身的知识生成的，而非来自 X 平台的索引，因此应视为无来源信息。否则为 `false`（包括未设置任何筛选条件的情况——宽泛的无来源回复仅属于普通回复，并非筛选条件未满足所致）。
- `degraded_reason` — 简短字符串，说明当前处于激活状态的筛选条件；当 `degraded` 为 `false` 时该值为 `null`。
- `credential_source` — 若通过 OAuth 验证，则为 `"xai-oauth"`；若通过 API 密钥验证，则为 `"xai"`。
- `model`、`query`、`provider`、`tool`、`success`

### 日期验证

在发起 HTTP 请求之前，客户端会对 `from_date`/`to_date` 进行验证：

- 若提供了这两个参数，都必须能解析为 `YYYY-MM-DD` 格式。
- 当两个参数都设置时，`from_date` 的日期必须不晚于 `to_date`。
- `from_date` 不能晚于当前 UTC 时间——因为尚未开始的日期区间内不可能存在帖子，此时调用必然会返回零条引用结果。
- `to_date` 可以设置为未来日期（调用方可能希望查询“从昨天到明天”的内容，以便在帖子发布时立即获取）。

验证失败时，工具会以结构化的 `{"error": "..."}` 格式返回结果，而不会向 xAI 发起 HTTP 请求。

## 示例

与 Agent 对话：

> X 平台上的用户对新的 Grok 图片功能有什么评价？重点关注 @xai 的回复。

Agent 将执行以下操作：

1. 使用 `query="reactions to new Grok image features"` 和 `allowed_x_handles=["xai"]` 调用 `x_search`。
2. 获取合成后的回复以及指向相关帖子的引用列表。
3. 将回复及引用信息一起反馈给用户。

## 故障排除

### “没有可用的 xAI 凭证”

当两种认证方式均失败时，工具会显示此错误。请在 `~/.hermes/.env` 文件中设置 `XAI_API_KEY`，或者运行 `hermes auth add xai-oauth` 并完成浏览器登录。之后重启会话，让 Agent 重新读取工具注册表。

### “该模型未启用 `x_search` 功能”

当前配置的 `x_search.model` 无法访问服务器端的 `x_search` 工具。请切换为默认的 `grok-4.5` 模型，或其他支持该功能的 Grok 模型。具体支持的模型列表可查阅 [xAI 文档](https://docs.x.ai/)。

### 工具未出现在架构图中

可能的原因有二：

1. **工具集未启用**。运行 `hermes tools`，确认“🐦 X (Twitter) Search”选项已被勾选。
2. **没有 xAI 凭证**。检查函数返回了 False，因此该工具在架构图中不会显示。运行 `hermes auth status` 检查 xai-oauth 的登录状态，同时确认已设置 `XAI_API_KEY`（若使用 API 密钥认证方式）。

### `degraded: true` — 回复中无引用信息

当您使用了 `allowed_x_handles`、`excluded_x_handles` 或日期范围进行筛选，但返回结果中显示 `degraded: true` 时，说明 xAI 的 X 平台索引未找到匹配的帖子，但 Grok 仍基于自身的训练数据生成了合成回复。此类回复属于无来源信息，不应视为真实的 X 平台搜索结果。

建议检查以下原因：

- **账号标识有误**：去掉 `@` 符号，仔细核对拼写，并确认该账号确实存在。
- **日期范围过窄**，或者覆盖的日期已过今日的帖子时间；请扩大范围后重试。
- **xAI 索引存在缺失**：部分活跃账号即便经常发帖，也偶尔不会出现在 `x_search` 的搜索结果中。可稍等几分钟后再试，或者在使用特定账号的完整发布记录时，通过 `xurl` 技能直接调用 X 平台的 API 进行查询。

## 参考资料

- [xAI Grok OAuth（SuperGrok / Premium+）](../../guides/xai-grok-oauth.md) — OAuth 配置指南
- [网页搜索与信息提取](web-search.md) — 用于常规（非 X 平台）网页搜索的功能
- [工具参考手册](../../reference/tools-reference.md) — 完整的工具目录
