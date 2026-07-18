# Stripe MCP（`mcp.stripe.com`）——周期性OAuth会话撤销问题及受限密钥的解决方案

这是SKILL.md中列出的10个常见问题的第9个：某些提供商的OAuth会话会定期失效，而根本的解决办法是改用静态API密钥。

## 症状（“一段时间后就会失效”的问题）
Stripe MCP最初可以正常工作数天，之后就会显示“未连接”。在此期间自动刷新功能依然正常（访问令牌的有效期为1小时且能顺利轮换），因此看起来像是刷新令牌过期或会话时长限制所致——但实际上并非如此。大约每周一次，Stripe会**在服务器端撤销整个OAuth授权机制**。下次使用`grant_type=refresh_token`发送POST请求时，将会出现：

```
HTTP 400  {"error":"invalid_grant","error_description":"Invalid refresh token"}
```

整个授权流程已经失效——而不仅仅是那个短时效的访问令牌——因此自动刷新功能无法恢复它。这需要重新通过交互式浏览器完成授权流程，而无头远程网关根本无法实现这一操作。切勿被偶尔出现的绿色测试状态所误导：问题其实是由于授权被间歇性撤销，而非令牌永久损坏。

## 为何三种常见假设都不成立
根据 Stripe 的 OAuth 文档（https://docs.stripe.com/stripe-apps/api-authentication/oauth）：
- **访问令牌**的有效期为**1小时**。
- **刷新令牌**的有效期为**1年**，且每次交换时都会重新生成——只要每年至少刷新一次，它们就不会自然过期。
- Hermes 的自动刷新功能与是否调用 Stripe 工具无关，因此“使用工具不够频繁”这一理由并不成立。

由此可见，导致授权失效的原因既不是刷新令牌的1年有效期，也不是所谓的“最大 OAuth 会话时长”（实际上文档中并未明确限定该数值）。真正的原因是服务器端主动撤销了会话。切勿陷入无限刷新的死循环。

## 永久解决方案：放弃 OAuth，改用受限 API 密钥作为承载令牌
Stripe 的 MCP 文档（https://docs.stripe.com/mcp）明确指出，对于非交互式/代理类应用，OAuth 并非合适的选择——`mcp.stripe.com`支持将**静态受限密钥**（`rk_live_...`）作为承载令牌使用。这类受限密钥**没有会话限制、无需刷新、也不会过期**——只要未被撤销，就会一直有效，从而彻底避免重新授权的麻烦。

config.yaml 需要做的修改如下（无需任何令牌文件——可直接为该服务器省去 OAuth 相关配置）：
```yaml
mcp_servers:
  stripe:
    url: https://mcp.stripe.com
    headers:
      Authorization: *** rk_live_..."      # restricted key from Dashboard
      # Stripe-Account: "acct_xxx"            # only for Connect platform / connected-account calls
```

在 Stripe 控制台 → 开发者 → API 密钥 → **受限密钥** 中生成密钥。根据机器人的实际功能，仅授予其所需的最低权限范围：
- 读取账户信息：针对账单、客户、订阅以及优惠券/促销码，授予 **读取** 权限；
- 退款/写入操作：需添加相应的 **写入** 权限。
之后执行 `/reload-mcp` 命令（仅当故障保护机制被触发时才进行完全重启，详见注意事项 7）。

## 决策规则
对于任何会频繁出现会话失效问题的无人值守远程网关 MCP 服务器（在刷新时会收到 `invalid_grant` 错误，或在成功刷新后出现 `-32002 "Session expired"` 错误），且其服务提供商提供静态 API 密钥的情况，应优先使用静态密钥而非 OAuth。OAuth 的刷新机制是为交互式客户端设计的，对于无头网关而言反而会带来风险。Stripe（受限密钥）和 Linear（个人 API 密钥）均符合此规则。
