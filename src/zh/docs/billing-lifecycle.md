# 计费生命周期：客户端状态、错误处理与恢复机制

本文档详细梳理了网关从 NAS 获取的各类 `billing.*`/`subscription.*` 状态信息到终端最终显示内容的映射关系，同时明确了每种错误代码对应的用户可见文本及相应的恢复方案。我们承诺：任何 NAS 计费状态或错误代码都不会仅以通用的提示信息呈现——下面列出的每种情况都在 `ui-tui/src/app/slash/commands/topup.ts`、`ui-tui/src/components/billingOverlay.tsx` 或 `ui-tui/src/components/subscriptionOverlay.tsx` 中有明确的处理分支。对于**未知**的错误代码，系统也会以优雅的方式处理：它会进入 `default` 分支，显示从服务器响应中获取的通用但具体的提示信息，而绝不会仅显示空白提示或直接忽略错误。

## 1. `billing.state` 状态 → 显示内容

来源：`ui-tui/src/components/billingOverlay.tsx`（`OverviewScreen`、`BuyScreen`、`AutoReloadScreen`）以及 `ui-tui/src/app/slash/commands/topup.ts`（`/topup` 命令）。

| 状态类型 | 显示内容 |
|---|---|
| 已登出（`s.logged_in === false`） | 不会显示任何覆盖层。系统提示：`💳 您尚未登录 Nous Portal — 请先运行 /portal 登录，然后再运行 /topup。` |
| 获取 `billing.state` 的 RPC 请求失败（传输问题/超时） | **立即终止处理**：通过 `.catch(ctx.guardedErr)` 处理错误——不会显示覆盖层，也不假设任何状态。系统提示：`error: <错误信息或“请求失败”>`。绝不会显示“无卡片”或其他推测性的状态信息；用户需重新运行 `/topup`。 |
| 未保存卡片（`card: null`），且处于完整菜单模式（`is_admin && cli_billing_enabled`） | 概览界面会显示“未保存任何卡片 — ‘添加资金’功能可指导您完成添加。”点击“添加资金”后会进入**添加卡片流程**：`在 Portal 上添加卡片` / `已添加 — 请再次确认` / `返回`（不会出现金额选择器，因为该操作会因“无支付方式”而触发 403 错误）。 |
| 已有卡片，且指定了来源（`card` 存在，`resolved_via` 设置） | 显示 `Card: {display}` 格式的内容（例如 `Visa ····4242 — 您订阅计划所使用的卡片`），其中会使用能体现卡片来源的 `display` 字段。 |
| 已有卡片，但未指定来源（旧版 NAS） | 回退到通用的 `Card: {masked}` 显示格式；确认界面会补充提示“您在 Portal 上保存的卡片将会被扣款。” |
| 未启用自动续费（`auto_reload: null`） | 完全不会显示自动续费相关行（`autoReloadLine` 返回 `null`）——该功能不会对外展示。 |
| 自动续费卡片的类型为“标准型”（`auto_reload.card.kind: 'canonical'`） | 不会显示卡片不同的警告信息；卡片行会直接显示已保存的卡片信息。 |
| 自动续费卡片的类型为“独立型”（`auto_reload.card.kind: 'distinct'`） | 在自动续费界面会显示提示 `⚠ 自动充值正在使用 {brand} ••{last4} 这张卡片 — 这并非您已保存的卡片。`（即提示卡片来源不同）。 |
| 自动续费卡片的类型为“无”（`auto_reload.card.kind: 'none'`） | 显示方式与“标准型”相同——不会显示卡片来源不同的警告。 |
| 存在月度消费限额，且 `limit_usd` 不为空 | 显示 `本月已使用 {spent_display}，总限额为 {limit_display}`（如果启用了默认上限，还会额外显示 `(默认上限)`）。 |
| 不存在月度消费限额或 `limit_usd` 为空 | 显示 `当前未显示月度消费限额（该设置可在 Portal 上管理）。` |
| 无计费权限的角色（`!is_admin`，菜单会折叠） | 注意：`计费操作需要具有计费权限的用户（账户所有者、管理员或财务管理员）执行。`菜单会折叠为“在 Portal 上管理”/“取消”。 |
| 组织的远程消费功能已关闭（`is_admin` 但 `!cli_billing_enabled`） | 注意：`该组织的远程消费功能已关闭 — 计费管理员可在 Portal 的 Hermes Agent 页面重新开启此功能。`菜单同样会折叠。 |

注意：`full = s.is_admin && s.cli_billing_enabled` 这一条件控制的是**组织级**的开关，而非单个终端的 `billing:manage` 范围——后者是通过动态检测来实现的（如果权限不足会触发 403 错误 `insufficient_scope`），此时系统会引导用户进入可继续操作的升级界面，而非直接进行前置检查。

## 2. 拒绝码（按代码顺序排列，通过函数 `renderBillingError` 处理）

来源：`ui-tui/src/app/slash/commands/topup.ts:37-149` 中的 `renderBillingError` 函数。只要存在 `portal_url`，无论哪种错误代码（包括默认情况），都会追加一行 `Portal: {portal_url}` 的提示。

| 错误代码 | 显示文本 | Portal URL | 重试间隔 |
|---|---|:-:|:-:|
| `insufficient_scope` | `此操作需要开启远程消费功能。请先进行充值以启用该功能，然后再尝试。` | 若存在则显示 | — |
| `remote_spending_revoked`（CF-4） | `{管理员已关闭此终端的远程消费功能。\| 您自己已关闭此终端的远程消费功能。}`（会显示操作者身份）`请重新连接以恢复功能 — 请运行 /portal 为该终端重新授权。`同时会立即清除 `billing` 覆盖层状态（不会等待令牌刷新）。 | 若存在则显示 | — |
| `session_revoked` | `您的会话已失效。请运行 /portal 重新登录。`同时会清除 `billing` 覆盖层状态。 | 若存在则显示 | — |
| `cli_billing_disabled` / `remote_spending_disabled`（两种错误会同时显示） | `该账户的远程消费功能已关闭 — 计费管理员可在 Portal 的 Hermes Agent 页面重新开启此功能。` | 若存在则显示 | — |
| `role_required` | `添加资金需要具有计费权限的用户（账户所有者、管理员或财务管理员），或需在 Portal 上进行管理。` | 若存在则显示 | — |
| `consent_required` | `此操作需要在 Portal 上完成一次性的卡片确认和同意步骤，之后才能继续。` | 若存在则显示 | — |
| `org_access_denied` | `该令牌未绑定到您有权管理的组织。请使用正确的组织登录，或可在 Portal 上进行管理。` | 若存在则显示 | — |
| `upgrade_cap_exceeded` | `🔴 已达到每日计划变更次数上限（每个组织最多5次）——请明天再试，或可在 Portal 上进行管理。` | 若存在则显示 | — |
| `auto_top_up_disabled_failures` | `由于多次扣款失败，自动续费功能已被关闭。请解决卡片问题，然后通过 /topup → Auto-reload 重新启用该功能。` | 若存在则显示 | — |
| `idempotency_conflict` | `🔴 该扣款密钥已被用于其他金额的扣款操作。请重新开始充值。` | 若存在则显示 | — |
| `no_payment_method` | `💳 该终端尚未保存可用于扣款的卡片。请在 Portal 上设置一张卡片（一次性信用卡购买不会生成可重复使用的卡片）。` | 若存在则显示 | — |
| `monthly_cap_exceeded` | `🔴 已达到月度消费限额 — 剩余可用额度为 ${remainingUsd}。`若 `payload.remainingUsd` 存在则显示该值，否则直接显示 `🔴 已达到月度消费限额。` | 若存在则显示 | — |
| `rate_limited` / `temporarily_unavailable` | `🟡 目前扣款请求过多{（约 {N} 分钟后可重试）}。这不是支付失败。` | 若存在则显示 | **是**——分钟数计算公式为 `max(1, round(retry_after/60))` |
| `stripe_unavailable` | `🟡 Stripe 服务当前出现故障 — 请稍后再试{（约 {N} 分钟后可重试）}。` | 若存在则显示 | **是**（计算公式相同） |
| *默认情况（未知/其他错误）* | `🔴 {message \|\| error \|\| '计费请求失败。'}` — 仍会显示服务器返回的原始信息，绝不会仅显示空白提示。 | 若存在则显示 | — |

## 3. 扣款处理结果（通过 `pollCharge` / `renderChargeFailed` 处理）

来源：`pollCharge`（`ui-tui/src/app/slash/commands/topup.ts:170-258`）和 `renderChargeFailed`（`:260-290`）。轮询间隔为2秒，总轮询时间为5分钟（`POLL_INTERVAL_MS=2000`，`POLL_CAP_MS=5*60*1000`），该限制适用于**所有**非终端相关路径（包括处于待处理状态和被限流的请求），因此持续的429/503错误也无法让轮询永远持续。

| 处理结果 | 显示文本 | 备注 |
|---|---|---|
| `status: 'settled'` | `✅ 已添加 {amount_usd} 元。`（如果没有金额则显示 `✅ 已添加积分。`） | 终端操作成功。 |
| `status: 'failed'`, `reason: 'authentication_required'` | `🔴 您的银行要求进行验证（3DS安全验证）。请在 Portal 上完成验证以完成此次购买。`若存在 `portalUrl`，还会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'payment_method_expired'` | `🔴 您的卡片已过期。请在 Portal 上更新卡片信息。` | 若存在 `portalUrl`，也会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'card_declined'` | `🔴 您的卡片被拒绝。请在 Portal 上尝试其他卡片。` | 若存在 `portalUrl`，也会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'processing_error'` | `🔴 扣款请求未成功（处理错误）。` | 若存在 `portalUrl`，也会显示 `Portal:` 行。 |
| `status: 'failed'`, 未知/缺失原因 | `🔴 扣款请求未成功（{reason \|\| 'processing_error'}）。`提示方式与卡片被拒绝时一致——与 `cli.py` 的 `_billing_portal_hint` 实现保持一致。 |
| 轮询超时（超过5分钟仍为待处理状态） | `🟡 5分钟后仍在处理中 — 这是超时现象，并非失败。请稍后查看 /topup 或 Portal 页面。`若存在 `portalUrl`，也会显示 `Portal:` 行。明确说明这不是失败情况。 |
| 轮询过程中被撤销权限（如 `remote_spending_revoked`/`session_revoked`） | 先显示第2节中对应的提示文本，**然后**追加提示：`🟡 您上一次扣款的结果尚未确认 — 请在重试前查看您的账户余额和交易记录。`根据 CF-7 规则4，轮询过程中被撤销权限后出现的403错误属于模糊情况（因为扣款可能已经完成处理）——绝不会将其标记为“失败”。 |
| 轮询时遇到429/503错误（如 `rate_limited`/`temporarily_unavailable`/`stripe_unavailable`） | 不显示任何错误提示；系统会按照 `retry_after` 设置的间隔时间（默认5秒，上限30秒）延迟后再次尝试，并持续轮询直到5分钟限制到期，之后才将其视为超时。这不是支付失败。 |
| 其他非正常状态检查错误 | `🔴 无法检查扣款状态：{message \|\| error \|\| 'error'}` | 无其他说明。 |
| 传输中断（轮询 RPC 请求失败或被拒绝） | `🟡 您上一次扣款的结果尚未确认 — 请在重试前查看您的账户余额和交易记录。`（使用 `UNCONFIRMED_CHARGE_MESSAGE` 模板）提示方式与轮询过程中被撤销权限时一致——连接中断的情况绝不能被标记为“失败”。 |

## 4. 订阅预览/待处理变更/升级结果

来源：`ui-tui/src/components/subscriptionOverlay.tsx` 中的 `previewAndRoute`、`applyPendingAndRoute`、`upgradeResult`、`stepUpDenialResult` 函数。

**预览 `effect` 值**（用于驱动确认界面）：

| `effect` 值 | 确认界面显示文本 | 主要操作 |
|---|---|---|
| `charge_now` | `升级到 {target} 套餐。您将立即被收取 {amount} 元费用（按比例计算）。`（若能确定使用哪张卡片，还会同时显示卡片信息） | `立即支付 {amount} 元并完成升级` |
| `scheduled` | `将套餐更改为 {target} 套餐 — 新规则将于 {date} 生效。目前无需扣款；您将继续使用当前套餐直至该日期。` | `安排在 {target} 套餐生效` |
| `no_op` | `您当前已使用 {target} 套餐 — 无需进行任何更改。` | 无操作（仅可返回） |
| `blocked` | `{preview.reason}` 或备用提示 `此更改无法在此处完成 — 请在 Portal 上进行管理。` | `在 Portal 上管理` |
| 预览 RPC 请求返回 `null`/传输失败 | 直接跳转至结果界面，显示 `无法预览该更改。` | — |
| 预览结果为 `!ok` 且原因為 `insufficient_scope` | 跳转至 `stepup` 界面，参数为 `{kind:'preview', tierId}` | — |
| 预览结果为 `!ok` 且为其他错误 | 跳转至结果界面，并显示 `errorResult(p)` 的提示内容（`{message \|\| error \|\| '出现错误。请重试或到 Portal 上进行管理。'}`） | — |

**待处理变更应用结果**（通过 `applyPendingAndRoute` 处理）：| `pending.kind` | 成功提示文本 |
|---|---|
| `cancellation` | `已安排——您的套餐将在计费周期结束前保持有效状态，之后才会取消。今日无需进行任何操作。` |
| `tier_change`（降级/延期） | `已安排——您的套餐今日不会发生变化。您将继续使用当前套餐，直到计费周期结束，届时才会切换。` |
| `upgrade` | 通过下方的 `upgradeResult` 处理 |
| 任意类型，且突变值为 `insufficient_scope` | 转发至 `stepup`（`{kind:'apply'}`）处理 |

**升级 `status` × `reason` 对应关系表**（按此顺序检查 `upgradeResult`——先检查 `reason`，再检查 `status`）：

| 条件 | 结果 |
|---|---|
| `r === null`（充值路径上传输失败） | `无法确认升级操作——您的卡片可能已扣款，也可能未扣款。请先运行 /subscription 查看当前套餐，然后再试。` ——信息不明确，切勿盲目重试。 |
| `reason: 'authentication_required'` **或** `reason: 'subscription_payment_intent_requires_action'` | `请在门户网站上验证您的卡片以完成升级。` → `recovery_url`。**这两种原因都会映射到相同的 SCA 提示文本**——客户端是根据 `reason` 而非 `status` 进行分支处理的，这样即使是在 #711 NAS 之前、因缺乏区分性原因而被错误标记为 `status: 'payment_failed'` 的情况，也会被正确引导至“验证卡片”的提示，而不会被视为直接拒绝。 |
| `reason: 'card_declined'` | `您的卡片被拒绝——请在门户网站上尝试使用其他卡片。` → `recovery_url`。 |
| `ok && status: 'already_on_tier'` | `您当前已处于 {target_tier_name} 套餐。`（表示成功） |
| `ok && status: 'upgraded'` | `已升级至 {target_tier_name} 套餐。您的新的月度额度即将到账。` ——随后开始最终一致性应用轮询（见下方说明）。 |
| `status: 'requires_action'`（无具体原因） | `此升级需要额外验证（3DS）。请在门户网站上完成操作。` → `recovery_url`。 |
| `status: 'payment_failed'`（无具体原因） | `您的卡片被拒绝。请在门户网站上更新支付方式后再试。` → `recovery_url`。 |
| 其他所有情况 | `errorResult(r)`: `message \|\| error \|\| '出现错误。请重试，或通过门户网站进行管理。'` |

**最终一致性应用轮询**（`ResultScreen`，仅在 `status: 'upgraded'` 后触发）：每隔 2 秒（`UPGRADE_CONFIRM_INTERVAL_MS`）轮询一次 `billing`/subscription 状态，最多尝试 15 次（`UPGRADE_CONFIRM_ATTEMPTS`，即约 30 秒），直到 `current.tier_id` 变更为目标值。在等待期间，界面会显示“正在应用……”；如果在规定时间内仍未变化，则会显示“仍在应用中”或“您的升级已成功并仍在处理中——稍后再试。”——即便 NAS 尚未同步到最新状态，升级也不会被误判为失败。

**升级拒绝提示文本**（`stepUpDenialResult`，用于套餐变更流程）：

| `error` | 提示文本 |
|---|---|
| `session_revoked` | `您的会话已过期——请运行 /portal 重新登录，然后再尝试更改。` |
| `remote_spending_revoked` | `{message}` 或 `此终端的远程消费功能已被暂停——请从门户网站重新连接后再试。` |
| `rate_limited` | `尝试次数过多——请稍等片刻后再试。` |
| 其他/未知错误 | `{message}` 或 `不允许进行远程消费——必须由具有账单管理权限的用户（所有者、管理员或财务管理员）进行批准。您也可以在门户网站上进行此更改。` |

在授权后的重试过程中，如果再次出现**重复**的拒绝情况，系统不会重新进入升级界面（因为该界面已加载中——重新加载会导致程序卡住）；此时会通过 `allowStepUp=false` 显示终端端的结果：`此终端的远程消费功能仍未启用——授权请求未通过。请重试，或通过门户网站进行更改。`

## 文本模式（CLI）一致性

`cli.py` 中的 `_show_billing` / `_billing_overview` 以及 `_show_subscription` / `_subscription_overview` 函数会以相同的方式展示状态信息（余额标题、双条状图显示的金额使用情况、自动充值行、卡片信息行、月度额度上限），并且都遵循“在用户未登录或门户网站出现故障时仍保持正常运行，绝不崩溃”的设计原则。CLI 的 `/subscription` 功能允许付费管理员/所有者在一个交互式环境中体验**完整的终端内更改流程**（套餐选择器 → 预览 → 确认 → 应用，与 TUI 覆盖层功能一致）；而普通用户及非交互式环境则会回退到 `_billing_portal_hint` 提供的深度链接，引导用户前往 `subscription_manage_url`。`/topup` 功能的交互式模态框（使用 prompt_toolkit 构建）也与 TUI 覆盖层功能保持一致，非交互式环境则同样采用文本信息加门户网站链接的形式展示，不会弹出提示。

## 前向兼容性

上述表格中未列出的任何 `error`/`status`/`reason` 代码，都会被路由到 `renderBillingError`（§2）中的 `default` 分支，或 `errorResult`/`upgradeResult` 的默认处理流程（§4）：系统仍会显示服务器自身生成的 `message`（绝不会显示空白内容，也绝不会导致程序崩溃），只是不会有针对特定情况的定制化提示文本，也不会提供专门的恢复功能。NAS W3 引入了一些卡片状态代码（如 `card_paused`、`card_expired`、`card_mismatch`），目前这些代码尚未在此处有专门的处理逻辑——在客户端更新添加相应的处理分支之前，它们会被视为未知代码，从而回退到此默认处理路径。
