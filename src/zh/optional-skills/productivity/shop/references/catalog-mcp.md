# 直接全局目录 MCP

当无法安装 CLI 或需要查看原始请求格式时，请参考本文档。产品搜索功能必须使用 Shopify 全局目录 MCP。

端点：

```text
POST https://catalog.shopify.com/api/ucp/mcp
Content-Type: application/json
User-Agent: shop-cli/0.1.0
```

## 认证（可选，推荐）

`shop` CLI会自动处理此功能：当买家已登录时（通过执行`shop auth status`命令可查看状态），它会生成一个目录令牌并对每一次目录查询进行认证；否则则会以未认证模式进行查询。仅当无法安装CLI时，才需要手动执行以下步骤。

实际上**并不要求必须登录**——未认证的调用（仅能获取用户信息，不包含`Authorization`字段）仍然可以正常工作。如果您已拥有`access_token`（详情请参阅[direct-api.md](direct-api.md)中的设备授权部分），可将其转换为目录令牌，并在后续的MCP调用中以`Authorization: Bearer`的形式附带该令牌发送。

```text
POST https://shop.app/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
subject_token=<access_token>
subject_token_type=urn:ietf:params:oauth:token-type:access_token
requested_token_type=urn:ietf:params:oauth:token-type:access_token
audience=api.shopify.com
client_id=5c733ab2-1903-400a-891e-7ba20c09e2a3
```

返回的 `access_token` 即为目录访问令牌。请仅将其存储在内存中，并在后续请求中添加 `Authorization: Bearer <catalog_token>`；当进程重启或出现 401 错误时需重新生成该令牌。由于 `personal_agent` 已具备目录访问权限，因此无需设置作用域参数。

每次工具调用都会包含：

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "search_catalog",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/valid-with-capabilities.json"
        }
      },
      "catalog": {}
    }
  }
}
```

## 搜索

`search_catalog` 功能可用于跨不同商家查找商品。相关请求数据会被封装在 `arguments.catalog` 中。

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "search_catalog",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/valid-with-capabilities.json"
        }
      },
      "catalog": {
        "query": "trail running shoes",
        "pagination": { "limit": 10 },
        "context": {
          "address_country": "US",
          "intent": "Customer runs marathons and wants road shoes"
        },
        "filters": {
          "available": true,
          "ships_to": { "country": "US" },
          "ships_from": [{ "country": "US" }, { "country": "CA" }],
          "price": { "max": 15000 },
          "condition": ["new"],
          "attributes": [
            { "name": "Color", "values": ["White", "Blue"] },
            { "name": "Size", "values": ["M"] },
            { "name": "Target gender", "values": ["Female"] }
          ]
        },
        "view": "compact"
      }
    }
  }
}
```

重要字段：

- `catalog.query`：自由文本查询。
- `catalog.like`：通过商品编号或图片内容进行相似度搜索。仅传递用户提供的编号/图片；图片可能包含个人数据。
- `catalog.context`：用于指示相关性或定位的买家信号，例如 `address_country`、`address_region`、`postal_code`、`language`、`currency` 以及 `intent`。`address_country` 是一种上下文信号，而非发货筛选条件。仅传递用户实际提供的信号，切勿自行推断或编造。
- `catalog.filters.ships_to`：用于筛选可发送到指定地点的商品的严格筛选条件。支持 `country`（ISO 3166-1 alpha-2格式）、`region`、`postal_code`。在发货资格起关键作用时使用此字段。仅当您确实需要按目的地进行限制时才设置该值，它与 `context.address_country` 独立。
- `catalog.filters.ships_from`：按商家来源地进行筛选，形式为 `{ country }` 对象的列表（ISO 3166-1 alpha-2格式），例如 `[{ "country": "US" }, { "country": "CA" }]`。多个来源以“或”关系组合。
- `catalog.filters.price`：货币的小数单位，例如 `15000` 表示 `$150.00`。
- `catalog.filters.condition`：`new`（全新）和/或 `secondhand`（二手）。
- `catalog.filters.shop_ids` / `catalog.filters.categories`：按店铺或分类类别进行限制。
- `catalog.filters.attributes`：Shopify分类属性筛选条件，形式为 `{ name, values }` 元素的数组。CLI中的 `--color`、`--size` 和 `--gender` 参数均对应此数组。相关说明：
  - **支持的名称（精确匹配，不区分大小写）**：`Color`、`Size`、`Target gender`。它们分别对应索引字段 `predicted_attributes_primary_colors`、`predicted_attributes_sizes` 和 `predicted_attributes_genders_keyword`。
  - **组合逻辑**：同一元素内的值采用“或”关系；不同元素间的值采用“与”关系（例如白色或蓝色 **且** M码 **且** 女性）。
  - **限制**：每次请求最多包含25个属性条目，每个条目最多包含50个值。
  - **未知名称**（如 `Material`）不会导致错误——系统会 silently 忽略这些名称，并在 `result.messages[]` 中以 `info`/`not_found` 形式反馈。CLI会将这些信息显示为 `_未找到：……_` 这样的行。
  - **已知数据的注意事项**：即使按颜色（尤其是 `White`）进行筛选，仍可能返回那些首款/主推款式为其他颜色的商品，因为只要商品的任意一款式符合条件即可，且目录路径尚未重新排序至匹配的款式。请将颜色筛选结果视为初步结果，在结账前通过 `get_product` 功能确认具体款式。
- `catalog.view`：预定义的输出格式，例如 `"compact"` 表示精简后的数据格式，`"offer"` 表示用于比价的功能。CLI默认使用 `compact` 格式。需注意，`compact` 格式仍包含 `metadata`（包括 `top_features` 和 `tech_specs`）、`rating` 以及款式 `options`；`top_features` 和 `tech_specs` 以换行分隔的字符串形式返回，而非数组。
- `catalog.pagination.limit`：1-50（默认为10）。建议设置较小的数值——过大的页面会消耗更多令牌。

### 分页

搜索响应中包含一个 `pagination` 块：

```json
{ "has_next_page": true, "total_count": 649, "cursor": "eyJvZmZzZXQiOjEwLCJ0b3RhbF9jb3VudCI6NjQ5fQ" }
```

当 `has_next_page` 的值为真时，使用返回的 `cursor` 重复发送请求，从而切换到下一页（确保数据无重复，总计数值保持一致）。

```json
{
  "catalog": {
    "query": "coffee mug",
    "filters": { "available": true, "ships_to": { "country": "US" } },
    "context": { "address_country": "US", "currency": "USD" },
    "pagination": { "limit": 8, "cursor": "eyJvZmZzZXQiOjEwLCJ0b3RhbF9jb3VudCI6NjQ5fQ" }
  }
}
```

按 ID 查找相似项：

```json
{
  "catalog": {
    "like": [{ "id": "gid://shopify/ProductVariant/12345" }],
    "context": { "address_country": "US" },
    "filters": { "available": true }
  }
}
```

基于图片相似度匹配：

```json
{
  "catalog": {
    "like": [
      {
        "image": {
          "content_type": "image/jpeg",
          "data": "<base64>"
        }
      }
    ],
    "context": { "address_country": "US" }
  }
}
```

## 查找功能

对于已知的产品或变体编号，可使用 `lookup_catalog` 命令进行查询。

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "lookup_catalog",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/valid-with-capabilities.json"
        }
      },
      "catalog": {
        "ids": [
          "gid://shopify/p/7f3a2b8c1d9e",
          "gid://shopify/ProductVariant/87654321"
        ],
        "context": { "address_country": "US" }
      }
    }
  }
}
```

## 获取产品信息

使用 `get_product` 命令可查看产品的各种选项、库存状况、已选规格、卖家域名以及结账链接。

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "get_product",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/valid-with-capabilities.json"
        }
      },
      "catalog": {
        "id": "gid://shopify/p/7f3a2b8c1d9e",
        "selected": [
          { "name": "Color", "label": "Black" },
          { "name": "Size", "label": "10" }
        ],
        "preferences": ["Color", "Size"],
        "context": { "address_country": "US" }
      }
    }
  }
}
```

## 响应处理

从搜索和查询响应中读取 `result.structuredContent.products`。从 `get_product` 函数的响应中读取 `result.structuredContent.product`。搜索结果还会返回 `result.structuredContent.pagination` 信息（包括 `has_next_page`、`total_count` 和 `cursor`），详情请参阅*分页说明*。

产品变体包含 `id`、`price`、`checkout_url`、`availability`、`options` 以及卖家信息（`name`、`id` = 商家 GID、`domain`、`url`）。结账时需使用变体 ID 和卖家域名。变体的 `options` 是一个由 `{ name, label }` 对组成的数组（例如 `[{name:'Color',label:'Black'},{name:'Size',label:'6-12 months'}]`），可通过拼接这些标签来生成显示名称（如“黑色 / 6-12个月”）。请注意，`variant.title` 通常即为产品标题，因此建议优先使用选项标签作为命名依据。产品还可能包含 `metadata.top_features`、`metadata.tech_specs`、`metadata.attributes`（由机器学习推断）以及 `rating` 等信息。

向用户展示链接时，应使用响应中返回的产品页面 URL 和 `variant.checkout_url`，并附加非个人身份识别信息的追踪参数 `utm_source=shop-personal-agent&utm_medium=shop-skill`（这些参数对商家可见），同时保留任何现有的查询参数（如 `_gsid`）。切勿根据模板重新生成 `checkout_url`，而应直接使用响应中提供的原始 URL。

产品页面链接来自 `variant.url`（实际上目录服务不会返回产品级别的 URL，因此可使用第一个变体的 `url`）。它绝不是 `seller.url`，因为后者仅代表店铺的根路径。CLI 的简洁 Markdown 格式仅在调用 `get_product` 时显示每个变体的 `checkout_url` 行；而 `search_catalog` 和 `lookup_catalog` 为保持结果列表的简洁会省略这些行。如需获取变体的 `checkout_url`，可通过调用 `get_product` 函数（或使用 `--format json` 参数）来实现。
