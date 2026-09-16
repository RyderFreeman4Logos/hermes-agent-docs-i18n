# Polymarket API 接口参考

所有接口均为公开的 REST（GET）类型，返回 JSON 格式数据，且无需进行身份验证。

## Gamma API — gamma-api.polymarket.com

### 搜索市场

```
GET /public-search?q=QUERY
```

响应结构：


需完整处理整个输入内容，不得提前终止。
```json
{
  "events": [
    {
      "id": "12345",
      "title": "Event title",
      "slug": "event-slug",
      "volume": 1234567.89,
      "markets": [
        {
          "question": "Will X happen?",
          "outcomePrices": "[\"0.65\", \"0.35\"]",
          "outcomes": "[\"Yes\", \"No\"]",
          "clobTokenIds": "[\"TOKEN_YES\", \"TOKEN_NO\"]",
          "conditionId": "0xabc...",
          "volume": 500000
        }
      ]
    }
  ],
  "pagination": {"hasMore": true, "totalResults": 100}
}
```

### 列出事件

```
GET /events?limit=N&active=true&closed=false&order=volume&ascending=false
```

参数：
- `limit` — 最大返回结果数（默认值因情况而异）
- `offset` — 分页偏移量
- `active` — true/false
- `closed` — true/false
- `order` — 排序字段：`volume`、`createdAt`、`updatedAt`
- `ascending` — true/false
- `tag` — 按标签别名进行过滤
- `slug` — 根据别名获取特定事件

响应内容：事件对象数组。每个事件都包含一个 `markets` 数组。

事件字段包括：`id`、`title`、`slug`、`description`、`volume`、`liquidity`、`openInterest`、`active`、`closed`、`category`、`startDate`、`endDate`，以及 `markets`（市场对象数组）。

### 列出市场信息

```
GET /markets?limit=N&active=true&closed=false&order=volume&ascending=false
```

其过滤参数与事件相同，此外还包括：
- `slug` — 通过标识符获取特定市场

市场相关字段包括：`id`、`question`、`conditionId`、`slug`、`description`、
`outcomes`、`outcomePrices`、`volume`、`liquidity`、`active`、`closed`、
`marketType`、`clobTokenIds`、`endDate`、`category`、`createdAt`。

重要提示：`outcomePrices`、`outcomes` 以及 `clobTokenIds` 均为 JSON 字符串（经过双重编码）。在 Python 中需使用 json.loads() 函数进行解析。

### 列出标签

```
GET /tags
```

返回标签对象数组，包含 `id`、`label` 和 `slug` 字段。
在按标签筛选事件或市场时，请使用 `slug` 值。

---

## CLOB API — clob.polymarket.com

所有 CLOB 价格接口均使用市场中 `clobTokenIds` 字段所对应的 `token_id`。
索引 0 表示“是”结果，索引 1 表示“否”结果。

### 当前价格

```
GET /price?token_id=TOKEN_ID&side=buy
```

响应结果：`{"price": "0.650"}`

`side`参数的取值：`buy`或`sell`。

### 中点价格

```
GET /midpoint?token_id=TOKEN_ID
```

响应结果：`{"mid": "0.645"}`

### 扩散度

```
GET /spread?token_id=TOKEN_ID
```

响应结果：`{"spread": "0.02"}`

### 订单簿

```
GET /book?token_id=TOKEN_ID
```

响应：
```json
{
  "market": "condition_id",
  "asset_id": "token_id",
  "bids": [{"price": "0.64", "size": "500"}, ...],
  "asks": [{"price": "0.66", "size": "300"}, ...],
  "min_order_size": "5",
  "tick_size": "0.01",
  "last_trade_price": "0.65"
}
```

买卖报价是按照价格排序的。交易规模以股数表示（以 USDC 为计价单位）。

### 价格历史记录

```
GET /prices-history?market=CONDITION_ID&interval=INTERVAL&fidelity=N
```

参数：
- `market` — conditionId（以 0x 开头的十六进制字符串）
- `interval` — 时间范围：`all`、`1d`、`1w`、`1m`、`3m`、`6m`、`1y`
- `fidelity` — 需返回的数据点数量

响应：
```json
{
  "history": [
    {"t": 1709000000, "p": "0.55"},
    {"t": 1709100000, "p": "0.58"}
  ]
}
```

`t`表示Unix时间戳，`p`表示价格（概率）。

注意：非常新的市场可能没有历史数据可返回。

### CLOB市场列表

```
GET /markets?limit=N
```

响应：
```json
{
  "data": [
    {
      "condition_id": "0xabc...",
      "question": "Will X?",
      "tokens": [
        {"token_id": "123...", "outcome": "Yes", "price": 0.65},
        {"token_id": "456...", "outcome": "No", "price": 0.35}
      ],
      "active": true,
      "closed": false
    }
  ],
  "next_cursor": "cursor_string",
  "limit": 100,
  "count": 1000
}
```

## 数据 API — data-api.polymarket.com

### 最新交易记录

```
GET /trades?limit=N
GET /trades?market=CONDITION_ID&limit=N
```

交易字段包括：`side`（买入/卖出）、`size`、`price`、`timestamp`、
`title`、`slug`、`outcome`、`transactionHash`以及`conditionId`。

### 开仓量

```
GET /oi?market=CONDITION_ID
```

## 领域交叉引用

若需从 Gamma 市场获取 CLOB 数据，请按以下步骤操作：

1. 从 Gamma 获取市场信息：该信息包含 `clobTokenIds` 和 `conditionId`。
2. 解析 `clobTokenIds`（JSON 字符串）：其值为 `["YES_TOKEN", "NO_TOKEN"]`。
3. 在使用 `/price`、 `/book`、 `/midpoint`、 `/spread` 接口时，需使用 YES_TOKEN。
4. 在使用 `/prices-history` 及数据 API 接口时，需使用 `conditionId`。
