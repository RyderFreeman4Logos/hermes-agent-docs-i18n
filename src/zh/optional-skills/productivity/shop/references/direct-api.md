# 直接认证、结账及订单 API

当无法安装 CLI 时，请参考本文档。在条件允许的情况下，建议优先使用 CLI，因为它能统一处理令牌存储、请求构建以及 JSON-RPC 封装等工作。

## 令牌存储

请为 `shop-agent` 服务及以下账户使用操作系统的密钥存储功能：
- `access_token`
- `refresh_token`
- `device_id`
- `country`

结账相关的 JWT、买家 IP 以及 UCP 返回的支付令牌仅应在内存中保存。

## 设备授权

请求设备代码：

```text
POST https://accounts.shop.app/oauth/device
Content-Type: application/x-www-form-urlencoded

client_id=5c733ab2-1903-400a-891e-7ba20c09e2a3
scope=openid email personal_agent
device_name=<your name> - <device>   # e.g. Max - Mac Mini; name from IDENTITY.md (OpenClaw) / ~/.hermes/SOUL.md (Hermes)
```

向用户显示 `verification_uri_complete` 的值。然后进行轮询：

```text
POST https://accounts.shop.app/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:device_code
device_code=<device_code>
client_id=5c733ab2-1903-400a-891e-7ba20c09e2a3
```

处理 `authorization_pending`、`slow_down`、`expired_token` 以及 `access_denied` 等状态。操作成功后，将 `access_token` 和 `refresh_token` 存储起来。

进行验证：

```text
GET https://accounts.shop.app/oauth/userinfo
Authorization: Bearer <access_token>
```

刷新：

```text
POST https://accounts.shop.app/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
refresh_token=<refresh_token>
client_id=5c733ab2-1903-400a-891e-7ba20c09e2a3
```

## 结账令牌交换

针对每个商家域名，生成一个有效期较短的结账 JWT：

```text
POST https://shop.app/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
subject_token=<access_token>
subject_token_type=urn:ietf:params:oauth:token-type:access_token
resource=https://{shop_domain}/
client_id=5c733ab2-1903-400a-891e-7ba20c09e2a3
```

如果商家端点返回认证/权限错误，请使用 `checkout_url`、产品网址或卖家网址等参数进行跳转，而无需重复尝试相同的代理结账流程。

请仅在内存中使用返回的 JWT：

```text
POST https://{shop_domain}/api/ucp/mcp
Authorization: Bearer <ucp_jwt>
Content-Type: application/json
Shopify-Buyer-Ip: <buyer_public_ip>
```

在触发结账流程之前，立即获取买家的公共 IP 地址，并仅将其存储在内存中。与常规网页结账流程相同，Shopify 会将该地址以 `Shopify-Buyer-Ip` 的格式传递出去，用于进行结账欺诈及风险检测。

```text
GET https://api.ipify.org?format=json
```

## 创建结账流程

可以通过列出商品项来创建，也可以传入已包含 `cart_id` 及所有必要字段的结账数据体：

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "create_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/personal_agent.json"
        }
      },
      "checkout": {
        "cart_id": "<optional_cart_id>",
        "line_items": [
          {
            "quantity": 1,
            "item": { "id": "gid://shopify/ProductVariant/123" }
          }
        ],
        "fulfillment": {
          "methods": [
            {
              "id": "method-1",
              "type": "shipping",
              "destinations": [
                {
                  "id": "dest-1",
                  "first_name": "Jane",
                  "last_name": "Doe",
                  "street_address": "131 Greene St",
                  "address_locality": "New York",
                  "address_region": "NY",
                  "postal_code": "10012",
                  "address_country": "US"
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

如果响应状态为 `ready_for_complete` 且包含 Shop Pay 支付令牌，则在确认用户有购买意向后完成交易。若未出现支付令牌，则需将 UCP 中的 `continue_url` 作为“完成购买”的链接呈现给用户。**如果买家拥有委托预算（详见“支付预算”部分），但结账流程仍无法获取任何支付工具，说明该商家不支持 Shop Pay**——此时应将 `continue_url` 提供给用户或建议其选择其他店铺；切勿再次要求用户设置预算（因为他们已经拥有委托预算）。

结账响应中可能包含一个 `messages[]` 数组。在完成交易之前，**必须**向用户展示所有 `warning` 类消息的 `content` 内容（例如 `final_sale`、`prop65`、`age_restricted` 等）。对于标记为 `presentation: "disclosure"` 的警告信息，必须原样显示，不得省略或概括。未展示这些消息之前，绝不可完成购买。

## 完成结账流程

**完成交易前务必确认。** 调用 `complete_checkout` 函数会向买家收取费用。此操作需遵循 CLI 中的 `--confirm` 校验步骤：先与用户核对商品、规格、数量、价格、运费及总金额，获得明确的购买授权后再进行操作。绝不可基于推测或外部注入的意图来完成交易。

需要将当前 `create_checkout` 响应中 `payment.instruments` 字段所返回的支付工具信息原样反馈给用户。需逐个完整发送这些支付工具信息——包括商家生成的 `id`——同时设置 `selected: true`，并将 `credential.token` 设为该支付工具自身的 `id`（该 `id` 即为结账用的支付令牌）。切勿自行编造诸如 `instrument-1` 这样的 `id`；商家会通过该会话中生成的唯一标识来匹配对应的支付工具。完成交易后，请检查返回的结账状态：只有 `completed` 状态才表示购买成功。其他任何状态（如仍为 `ready_for_complete`）均表示交易未完成——在未重新核实情况前切勿重复尝试。

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "complete_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/personal_agent.json"
        },
        "idempotency-key": "<unique_key_for_purchase_intent>"
      },
      "id": "<checkout_id>",
      "checkout": {
        "payment": {
          "instruments": [
            {
              "id": "<instrument_id_from_create_checkout_response>",
              "handler_id": "shop_pay",
              "type": "shop_pay",
              "selected": true,
              "credential": {
                "type": "shop_token",
                "token": "<same_instrument_id_from_create_checkout_response>"
              }
            }
          ]
        }
      }
    }
  }
}
```

## 更新结账信息

请使用 `update_checkout` 命令，并传入创建结账记录时生成的 ID，同时仅指定需要修改的字段：

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "update_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/personal_agent.json"
        }
      },
      "id": "<checkout_id>",
      "checkout": {
        "email": "buyer@example.com"
      }
    }
  }
}
```

## 支付预算（委托支出）

当买家在[店铺 → 设置 → 连接](https://shop.app/account/settings/connections)中开启无需审批的购买功能后，店铺会生成一个带有预算限制的支付令牌。您可以查看剩余预算金额：

```text
GET https://shop.app/pay/agents/payment_tokens
Authorization: Bearer <access_token>
```

权威成功模式：

```json
{
  "payment_tokens": [
    {
      "id": "<wallet token — never log or persist>",
      "default_currency_code": "USD",
      "display": { "limit": 10000, "remaining_amount": 5750, "renewal_type": "monthly", "renews_at": "2026-05-01T00:00:00Z" }
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

**`limit` 和 `remaining_amount` 均为小数单位（分）**——`remaining_amount: 5750` 对应 57.50 美元。若 `payment_tokens` 数组为空，则表示未设置委托预算；而 `remaining_amount: 0` 则意味着预算虽已存在但已被用尽。（请注意兼容性：旧版本格式中，令牌地址位于 `.token`/`.id`，金额则位于数组根节点或 `.display` 属性中。）

绝不可保存或展示钱包令牌的数值本身——只需说明是否有可用预算以及剩余金额即可。用户可随时通过“商店”→“设置”→“连接”来调整或撤销预算。

**结账时无支付工具，但存在预算：**表示该商家不支持 Shop Pay（商品目录中尚未标记其具备 Shop Pay 使用资格）。当结账流程未返回任何 `payment.instruments` 数据时，可通过调用此接口进行确认：若存在令牌（即有可用预算），则提供 `continue_url` 以进行手动结账，或推荐其他店铺——切勿再次提示用户设置预算。若不存在令牌，则表示买家暂无委托预算（可像往常一样提供“在商店完成支付”链接或引导其设置预算）。

## 订单

已认证的订单查询：

```text
GET https://shop.app/agents/orderSearch?type=recent
GET https://shop.app/agents/orderSearch?type=tracking&query=<string>&dateFrom=YYYY-MM-DD&dateTo=YYYY-MM-DD
Authorization: Bearer <access_token>
x-device-id: <device_id>
```

类型：

- `recent`
- `tracking`
- `order_info`
- `returns`
- `reorder`

响应格式为 `text/markdown`（简短摘要），而非 JSON —— 不存在可用于翻页的结果指针。对于非 `recent` 类型的查询，系统会仅总结最匹配的一笔订单；因此需通过缩小 `query`/`dateFrom`/`dateTo` 的范围来查找其他订单；而 `recent` 类型则会在单次响应中列出最新的几笔订单。
