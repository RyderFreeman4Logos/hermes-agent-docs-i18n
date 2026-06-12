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
  # grok-4.20-reasoning is the recommended default; any Grok model
  # with x_search tool access works.
  model: grok-4.20-reasoning

  # Request timeout in seconds. x_search can take 60–120s for
  # complex queries — the default is generous. Minimum: 30.
  timeout_seconds: 180

  # Number of automatic retries on 5xx / ReadTimeout / ConnectionError.
  # Each retry backs off (1.5x attempt seconds, capped at 5s).
  retries: 2
```

## 工具参数

Agent会使用以下参数调用`x_search`函数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | 字符串（必填） | 在X平台上搜索的内容。 |
| `allowed_x_handles` | 字符串数组 | 可选参数，用于指定**仅包含**的账号列表（最多10个）。开头的`@`符号会被去掉。 |
| `excluded_x_handles` | 字符串数组 | 可选参数，用于指定需要排除的账号列表（最多10个）。该参数与`allowed_x_handles`不能同时使用。 |
| `from_date` | 字符串 | 可选参数，格式为`YYYY-MM-DD`，表示起始日期。 |
| `to_date` | 字符串 | 可选参数，格式为`YYYY-MM-DD`，表示结束日期。 |
| `enable_image_understanding` | 布尔值 | 是否让xAI分析匹配帖子中附带的图片。 |
| `enable_video_understanding` | 布尔值 | 是否让xAI分析匹配帖子中附带的视频。 |

该工具会返回包含以下内容的JSON数据：

- `answer` — 由Grok生成的合成文本回复。
- `citations` — 通过Responses API获取的引用信息。
- `inline_citations` — 从消息正文中提取的`url_citation`注释，每个注释包含`url`、`title`、`start_index`和`end_index`字段。
- `degraded` — 当设置了任何筛选条件（`allowed_x_handles`、`excluded_x_handles`、`from_date`、`to_date`），且两种引用渠道均无结果时，该值为`true`。此时回复内容是基于模型自身的知识生成的，而非来自X平台的索引，因此应视为无来源信息。其他情况下该值为`false`（包括未设置任何筛选条件的情况——这种情况下的宽泛无来源回复仅属于普通回复，并非筛选条件未满足所致）。
- `degraded_reason` — 简短字符串，说明当前处于激活状态的筛选条件；当`degraded`为`false`时该值为`null`。
- `credential_source` — 若通过OAuth认证，则为`"xai-oauth"`；若通过API密钥认证，则为`"xai"`。
- `model`、`query`、`provider`、`tool`、`success`

### 日期验证

在发起HTTP请求之前，客户端会对`from_date`/`to_date`进行验证：

- 若提供了这两个参数，必须能解析为`YYYY-MM-DD`格式。
- 当两个参数都设置时，`from_date`的日期必须不晚于`to_date`。
- `from_date`不能晚于当前UTC时间——因为尚未开始的日期区间内不可能存在帖子，此时请求必然会返回零条引用结果。
- `to_date`可以设置为未来日期（调用方可能希望查询“从昨天到明天”的内容，以便及时获取新发布的帖子）。

验证失败时，工具会以结构化的`{"error": "..."}`格式返回结果，而不会向xAI发起HTTP请求。

## 示例

与Agent对话：

> X平台上的用户对新的Grok图片功能有什么评价？重点关注@xai账号的回复。

Agent将执行以下操作：

1. 使用`query="reactions to new Grok image features"`和`allowed_x_handles=["xai"]`调用`x_search`。
2. 获取合成后的回复以及指向具体帖子的引用列表。
3. 将回复及引用信息一起反馈给用户。

## 故障排除

### “无xAI认证凭证可用”

当两种认证方式均失败时，工具会显示此错误。请在`~/.hermes/.env`文件中设置`XAI_API_KEY`，或运行`hermes auth add xai-oauth`并完成浏览器登录。之后重启会话，让Agent重新读取工具注册表。

### “当前模型未启用`x_search`功能”

配置的`x_search.model`无法访问服务器端的`x_search`工具。请切换为`grok-4.20-reasoning`（默认模型）或其他支持该功能的Grok模型。可查看[xAI文档](https://docs.x.ai/)获取当前支持的模型列表。

### 工具未出现在架构图中

可能的原因有二：

1. **工具集未启用**。运行`hermes tools`，确认“🐦 X (Twitter) Search”选项已被勾选。
2. **无xAI认证凭证**。检查函数返回值为False，因此该工具在架构图中不可见。运行`hermes auth status`查看xai-oauth的登录状态，并确认已设置`XAI_API_KEY`（若使用API密钥认证路径）。

### `degraded: true` — 回复中无引用信息

当您使用了`allowed_x_handles`、`excluded_x_handles`或日期范围进行筛选，但返回结果中`degraded: true`时，说明xAI的X平台索引未找到匹配的帖子，但Grok仍基于自身训练数据生成了合成回复。此类回复无来源信息，不应视为真实的X平台搜索结果。

建议检查以下原因：

- **账号名称有误**：去掉`@`符号，仔细核对拼写，并确认该账号确实存在。
- **日期范围过窄**或覆盖了今日之后的帖子；请扩大范围后重试。
- **xAI索引存在缺失**：某些活跃账号即便经常发帖，也偶尔不会出现在`x_search`的结果中。可稍等几分钟后再试，或者在使用特定账号的完整发布记录时，通过`xurl`技能直接调用X平台API获取数据。

## 相关文档

- [xAI Grok OAuth（SuperGrok / Premium+）](../../guides/xai-grok-oauth.md) — OAuth认证设置指南
- [网页搜索与信息提取](web-search.md) — 用于常规（非X平台）网页搜索的功能
- [工具参考手册](../../reference/tools-reference.md) — 完整的工具目录
