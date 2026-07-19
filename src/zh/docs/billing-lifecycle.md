# 计费生命周期：客户端状态、错误处理与恢复机制

本文档详细阐述了网关从 NAS 获取的各类 `billing.*`/`subscription.*` 状态信息到终端最终显示内容的映射关系，以及各类错误代码对应的用户可见文本及恢复方案。我们承诺：任何 NAS 计费状态或错误代码都不会直接显示为通用的提示信息——所有情况都在 `ui-tui/src/app/slash/commands/topup.ts`、`ui-tui/src/components/billingOverlay.tsx` 或 `ui-tui/src/components/subscriptionOverlay.tsx` 中有明确的处理分支。对于**未知**的错误代码，系统也会以优雅的方式处理：它会进入 `default` 分支，显示从服务器响应中获取的通用但具体的消息，而绝不会只显示空白提示或直接忽略错误。

## 1. `billing.state` 状态 → 显示内容

来源：`ui-tui/src/components/billingOverlay.tsx`（`OverviewScreen`、`BuyScreen`、`AutoReloadScreen`）以及 `ui-tui/src/app/slash/commands/topup.ts`（`/topup` 命令）。

| 状态类型 | 显示内容 |
|---|---|
| 已注销（`s.logged_in === false`） | 不会显示任何覆盖层。系统提示：`💳 您未登录 Nous Portal — 请先运行 /portal 登录，然后再运行 /topup。` |
| 获取 `billing.state` 的 RPC 请求失败（传输问题/超时） | **立即关闭**：通过 `.catch(ctx.guardedErr)` 处理——不会显示覆盖层，也不假设任何状态。系统提示：`error: <消息内容或“请求失败”>`。绝不会显示“无卡片”或其他推测性的状态信息；用户需重新尝试运行 `/topup`。 |
| 未保存卡片（`card: null`），且处于完整菜单模式（`is_admin && cli_billing_enabled`） | 概览界面会显示“未保存任何卡片 — ‘添加资金’功能可指导您完成添加。”点击“添加资金”后会进入**添加卡片流程**：`在 Portal 上添加卡片` / `已添加 — 请再次确认` / `返回`（不会出现金额选择器，因为否则会因 `no_payment_method` 而触发 403 错误）。 |
| 已有卡片，且指定了来源方式（`resolved_via` 设置） | 显示 `Card: {display}` 格式的内容（例如 `Visa ····4242 — 您订阅计划中使用的卡片`），该字段会体现卡片的来源信息。 |
| 已有卡片，但未指定来源方式（旧版 NAS） | 回退到通用的 `Card: {masked}` 显示格式；确认界面会额外提示“您在 Portal 上保存的卡片将被用于扣款。” |
| `auto_reload: null` | 完全不显示自动充值相关行（`autoReloadLine` 返回 `null`）——该功能不会被展示。 |
| `auto_reload.card.kind: 'canonical'` | 不会显示“卡片不同”的警告；卡片行会直接显示已保存的卡片信息。 |
| `auto_reload.card.kind: 'distinct'` | 在自动充值界面显示 `⚠ 自动充值正在使用 {brand} ••{last4} 这张卡 — 这不是您已保存的卡片。`，即提示卡片不同的通知。 |
| `auto_reload.card.kind: 'none'` | 显示方式与 `canonical` 相同——不会显示卡片不同的警告。 |
| 存在月度消费上限，且 `limit_usd != null` | 显示 `本月已使用 {spent_display}，上限为 {limit_display}`（如果 `is_default_ceiling` 为真，还会额外显示 `(默认上限)`）。 |
| 不存在月度消费上限或 `limit_usd == null` | 显示 `当前未显示月度消费上限（该设置可在 Portal 上管理）。` |
| 无计费权限的角色（`!is_admin`），菜单会折叠 | 注意：`计费操作需要具有计费权限的用户（所有者、管理员或财务管理员）执行。` 菜单将折叠为 `在 Portal 上管理` / `取消`。 |
| 组织的计费功能已关闭（`is_admin` 但 `!cli_billing_enabled`） | 注意：`该组织的终端计费功能已关闭 — 请在 Portal 上进行管理。` 菜单同样会折叠。 |

注意：`full = s.is_admin && s.cli_billing_enabled` 用于控制**组织级**的开关，而非单个终端的 `billing:manage` 范围——后者是通过动态检测实现的（若权限不足会返回 403 错误 `insufficient_scope`），此时系统会直接跳转至可继续操作的升级界面，而非进行前置检查。

## 2. 拒绝码（按代码顺序排列，通过函数 `renderBillingError` 处理）

来源：`ui-tui/src/app/slash/commands/topup.ts:37-149` 中的 `renderBillingError` 函数。只要存在 `portal_url`，无论何种错误码（包括默认情况），都会追加一行 `Portal: {portal_url}` 的提示。

| 错误代码 | 显示文本 | Portal URL | 重试间隔 |
|---|---|:-:|:-:|
| `insufficient_scope` | `需要启用终端计费功能。请先进行充值以激活该功能，然后再尝试。` | 若存在则显示 | — |
| `remote_spending_revoked`（CF-4） | `{管理员已关闭此终端的终端计费功能。\| 您自己关闭了此终端的终端计费功能。}`（会显示操作者信息）`请重新连接以恢复功能 — 请运行 /portal 来重新授权此终端。` 此时还会立即清除 `billing` 覆盖层状态，不会等待令牌刷新。 | 若存在则显示 | — |
| `session_revoked` | `您的会话已被注销。请运行 /portal 重新登录。` 此时也会清除 `billing` 覆盖层状态。 | 若存在则显示 | — |
| `cli_billing_disabled` / `remote_spending_disabled`（同时触发） | `该账户的终端计费功能已关闭 — 需要由管理员在 Portal 上重新启用。` | 若存在则显示 | — |
| `role_required` | `添加资金需要具有计费权限的用户（所有者、管理员或财务管理员），或请在 Portal 上进行管理。` | 若存在则显示 | — |
| `consent_required` | `此操作需要在 Portal 上完成一次性的卡片确认和同意步骤，之后才能继续。` | 若存在则显示 | — |
| `org_access_denied` | `该令牌未绑定到您有权管理的组织。请使用正确的组织登录，或在该组织中管理此功能。` | 若存在则显示 | — |
| `upgrade_cap_exceeded` | `🔴 已达到每日计划变更次数上限（每个组织限 5 次）——请明天再试，或在该组织中管理此功能。` | 若存在则显示 | — |
| `auto_top_up_disabled_failures` | `由于多次扣款失败，自动充值功能已被关闭。请解决卡片问题，然后通过 /topup → Auto-reload 重新启用该功能。` | 若存在则显示 | — |
| `idempotency_conflict` | `🔴 该扣款密钥已被用于其他金额的扣款。请重新开始充值。` | 若存在则显示 | — |
| `no_payment_method` | `💳 终端扣款暂未保存任何卡片。请在 Portal 上设置一张卡片（一次性信用卡购买不会生成可重复使用的卡片）。` | 若存在则显示 | — |
| `monthly_cap_exceeded` | `🔴 已达到月度消费上限 — 剩余可用额度为 ${remainingUsd}。` 若 `payload.remainingUsd` 存在则显示该值，否则显示 `🔴 已达到月度消费上限。` | 若存在则显示 | — |
| `rate_limited` / `temporarily_unavailable` | `🟡 目前扣款请求过多{（约 {N} 分钟后可重试）}。这不是支付失败。` | 若存在则显示 | **是**——分钟数计算公式为 `max(1, round(retry_after/60))` |
| `stripe_unavailable` | `🟡 Stripe 服务暂时不可用 — 请稍后再试{（约 {N} 分钟后可重试）}。` | 若存在则显示 | **是**（计算公式相同） |
| *默认/未知/其他情况* | `🔴 {消息内容 \|\| 错误信息 \|\| ‘计费请求失败。’}` — 仍然会显示服务器返回的原始信息，绝不会只显示空白提示。 | 若存在则显示 | — |

## 3. 扣款结算结果（通过 `pollCharge` / `renderChargeFailed` 处理）

来源：`pollCharge`（`ui-tui/src/app/slash/commands/topup.ts:170-258`）以及 `renderChargeFailed`（`:260-290`）。轮询间隔为 2 秒，总轮询时间为 5 分钟（`POLL_INTERVAL_MS=2000`，`POLL_CAP_MS=5*60*1000`），此限制适用于**所有**非终端相关路径（包括待处理请求和被限流的请求），因此持续的 429/503 错误也无法让轮询永远持续。

| 结果类型 | 显示文本 | 备注 |
|---|---|---|
| `status: 'settled'` | `✅ 已添加 {amount_usd} 元。`（如果没有金额则显示 `✅ 已添加积分。`） | 终端操作成功。 |
| `status: 'failed'`, `reason: 'authentication_required'` | `🔴 您的银行要求进行验证（3DS）。请在 Portal 上完成验证以完成此次购买。` | 若存在 `portalUrl`，还会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'payment_method_expired'` | `🔴 您的卡片已过期。请在 Portal 上更新卡片信息。` | 会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'card_declined'` | `🔴 您的卡片被拒付。请在 Portal 上尝试其他卡片。` | 会显示 `Portal:` 行。 |
| `status: 'failed'`, `reason: 'processing_error'` | `🔴 扣款请求未成功处理（处理错误）。` | 会显示 `Portal:` 行。 |
| `status: 'failed'`，且原因未知/缺失 | `🔴 扣款请求未成功处理（{reason \|\| ‘处理错误’}）。` | 显示方式与卡片被拒付时一致 — 与 `cli.py` 中的 `_billing_portal_hint` 实现逻辑保持一致。 |
| 轮询超时（超过 5 分钟仍为 `pending` 状态） | `🟡 5 分钟后仍在处理中 — 这是超时现象，并非失败。请稍后查看 /topup 或 Portal 页面。` | 若存在 `portalUrl`，也会显示 `Portal:` 行。明确说明这不是失败情况。 |
| 轮询过程中被撤销（在轮询时触发 `remote_spending_revoked`/`session_revoked`） | 先显示第 2 节中对应的提示文本，**然后**追加：`🟡 您上一次扣款的结果尚未确认 — 请在重试前查看账户余额和交易历史。` | 根据 CF-7 规则 4，轮询过程中出现 403 错误的情况比较模糊（因为扣款可能已经完成结算）——绝不会将其标记为“失败”。 |
| 轮询时遇到 429/503 错误（`rate_limited`/`temporarily_unavailable`/`stripe_unavailable`） | 不显示错误提示；系统会按照 `retry_after` 的间隔（默认为 5 秒，最高限制为 30 秒）等待后再次轮询，直到达到 5 分钟的总限值，之后才将其视为超时。 | 这不属于支付失败。 |
| 其他非正常的状态检查错误 | `🔴 无法查询扣款状态：{消息内容 \|\| 错误信息 \|\| ‘错误’}` | — |
| 传输丢失（轮询 RPC 请求失败或被拒绝） | `🟡 您上一次扣款的结果尚未确认 — 请在重试前查看账户余额和交易历史。`（使用常量 `UNCONFIRMED_CHARGE_MESSAGE`） | 显示方式与轮询过程中被撤销时一致 — 网络连接中断的情况绝不能被视为“失败”。 |

## 4. 订阅预览 / 待处理变更 / 升级结果

来源：`ui-tui/src/components/subscriptionOverlay.tsx` 中的 `previewAndRoute`、`applyPendingAndRoute`、`upgradeResult`、`stepUpDenialResult` 函数。

**预览阶段的 `effect` 值**（用于驱动确认界面）：

| `effect` 值 | 确认界面显示文本 | 主要操作 |
|---|---|---|
| `charge_now` | `升级到 {target} 套餐。您将立即被收取 {amount} 元费用（按比例计算）。`（还会显示月度积分变动情况，以及如果解析器能够确定的话，还会显示使用哪张卡片） | `立即支付 {amount} 元并完成升级` |
| `scheduled` | `即将更改为 {target} 套餐 — 变更将于 {date} 生效。目前无需扣款；您将继续使用当前套餐直至该日期。` | `安排在 {target} 套餐生效` |
| `no_op` | `您当前已使用 {target} 套餐 — 无需进行任何更改。` | 无操作（仅可点击“返回”） |
| `blocked` | `{preview.reason}`，或备用提示“此更改无法在此处进行 — 请在 Portal 上管理。” | `在 Portal 上管理` |
| 预览 RPC 请求返回 `null` 或传输失败 | 直接跳转至结果界面，显示“无法预览该更改。” | — |
| 预览结果为 `!ok` 且原因為 `insufficient_scope` | 跳转至 `stepup` 界面，参数为 `{kind:'preview', tierId}` | — |
| 预览结果为 `!ok` 且为其他错误 | 跳转至结果界面，显示 `errorResult(p)` 的内容（`消息内容 \|\| 错误信息 \|\| ‘出现错误。请重试或在该组织中管理。’`） | — |

**待处理变更应用后的结果**（通过 `applyPendingAndRoute` 处理）：

| `pending.kind` 类型 | 成功后的显示文本 |
|---|---|
| `cancellation` | `已安排取消 — 您的套餐将保持有效状态直至计费周期结束，之后才会被取消。今天不会有任何变化。` |
| `tier_change`（降级/延期变更） | `已安排变更 — 您的套餐今天不会发生变化。您将继续使用当前套餐直至计费周期结束，之后才会切换为新套餐。` |
| `upgrade` | 通过下方的 `upgradeResult` 函数处理 | — |
| 任何类型，但变更操作因 `insufficient_scope` 失败 | 跳转至升级界面，参数为 `{kind:'apply'}` | |**升级 `status` × `reason` 矩阵**（`upgradeResult`，按此顺序检查——先检查 `reason`，再检查 `status`）：

| 条件 | 结果 |
|---|---|
| `r === null`（充值路径上发生传输故障） | `无法确认升级结果——您的卡片可能已扣款，也可能未扣款。请先运行 /subscription 查看您的套餐，然后再试。` ——结果不明确，绝不会盲目重试。 |
| `reason: 'authentication_required'` **或** `reason: 'subscription_payment_intent_requires_action'` | `请在门户网站中验证您的卡片以完成此次升级。` → `recovery_url`。**这两种原因都会映射到相同的 SCA 消息模板**——客户端是根据 `reason` 而非 `status` 进行分支处理的，这样即使是在 #711 NAS 之前、因缺乏区分性原因而被错误标记为 `status: 'payment_failed'` 的 SCA 案例，也能被正确路由到“验证卡片”的消息模板，而不会被视为直接拒绝。 |
| `reason: 'card_declined'` | `您的卡片被拒绝——请在门户网站中使用其他卡片尝试。` → `recovery_url`。 |
| `ok && status: 'already_on_tier'` | `您已处于 {target_tier_name} 套餐。`（升级成功） |
| `ok && status: 'upgraded'` | `已升级至 {target_tier_name} 套餐。您的新的月度额度即将到账。` ——随后开始最终一致性应用轮询（见下文）。 |
| `status: 'requires_action'`（无特定原因） | `此升级需要额外验证（3DS）。请在门户网站中完成验证。` → `recovery_url`。 |
| `status: 'payment_failed'`（无特定原因） | `您的卡片被拒绝。请在门户网站中更新支付方式，然后重试。` → `recovery_url`。 |
| 其他任何情况 | `errorResult(r)`: `message \|\| error \|\| '出现错误。请重试，或通过门户网站进行管理。'` |

**最终一致性应用轮询**（`ResultScreen`，仅在 `status: 'upgraded'` 之后执行）：每隔 2 秒（`UPGRADE_CONFIRM_INTERVAL_MS`）轮询一次 `billing`/subscription 状态，最多尝试 15 次（`UPGRADE_CONFIRM_ATTEMPTS`，即约 30 秒），直到 `current.tier_id` 变为目标值。在等待期间，界面会显示“正在应用……”；如果在规定时间内仍未变化，则会显示“仍在应用中”/“您的升级已成功并仍在处理中——稍后刷新。”——即便 NAS 尚未同步，升级结果也绝不会被错误地报告为失败。

**升级拒绝消息模板**（`stepUpDenialResult`，用于订阅流程）：

| `error` | 消息模板 |
|---|---|
| `session_revoked` | `您的会话已过期——请运行 /portal 重新登录，然后再次尝试更改。` |
| `remote_spending_revoked` | `{message}` 或 `当前会话的终端消费功能已被关闭——请从门户网站重新连接，然后重试。` |
| `rate_limited` | `尝试次数过多——请稍等片刻，然后再试。` |
| 其他/未知错误 | `{message}` 或 `终端账单功能尚未启用——需要具有账单权限的人员（所有者、管理员或财务管理员）为该组织启用此功能。您也可以在门户网站中进行更改。` |

在授权后的重放过程中，如果再次出现**重复拒绝**情况，系统不会重新进入升级界面（因为该界面已加载——重新处理会导致界面冻结）；此时会设置 `allowStepUp=false`，并显示终端端的结果：`当前组织仍未启用终端账单功能——请在门户网站中启用它，然后重试。`

## 文本模式（CLI）的一致性设计

`cli.py` 中的 `_show_billing` / `_billing_overview` 以及 `_show_subscription` / `_subscription_overview` 函数会渲染相同的状态信息（余额标题、双条状图显示的金额使用情况、自动续费行、卡片信息行、月度额度上限），并且都遵循“在用户未登录或门户网站出现故障时仍保持正常运行，绝不崩溃”的设计原则。CLI 的 `/subscription` 功能为拥有付费权限的管理员/所有者提供了交互式的**完整终端内更改流程**（套餐选择器 → 预览 → 确认 → 应用，与 TUI 覆盖层功能一致）；而普通会员及非交互式环境则回退到 `_billing_portal_hint` 提供的指向 `subscription_manage_url` 的深度链接。`/topup` 功能的交互式模态框（使用 prompt_toolkit 构建）也以相同方式映射 TUI 覆盖层的内容，非交互式环境则同样采用文本信息加门户链接的显示方式，不会弹出提示。

## 向前兼容性

任何未在上述表格中列出的 `error`/`status`/`reason` 代码，都会进入 `renderBillingError`（§2）中的 `default` 分支，或 `errorResult`/`upgradeResult` 的默认处理流程（§4）：系统仍会显示服务器自身的 `message` 内容（绝不会显示空白，也绝不会导致崩溃），只是不会有定制化的消息模板或专门的恢复功能。NAS W3 引入了卡片健康状态代码（如 `card_paused`、`card_expired`、`card_mismatch`），目前这些代码尚未在此处得到专门处理——在客户端更新添加相应的分支处理之前，它们会作为未知代码出现，并退化为上述默认处理流程。
