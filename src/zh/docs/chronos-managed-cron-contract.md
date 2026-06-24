# Chronos managed-cron — 代理 ↔ NAS 通信协议

**状态：** Chronos cron 提供方的权威通信规范。  
**目标受众：** `agent-cron` 接口（`nous-account-service`）的 NAS 端实现者，以及所有负责调试 managed-cron 功能的人员。

Hermes 所支持的网关能够在空闲状态下将资源**完全释放至零**，同时仍能定时执行 cron 任务。代理不会使用进程内的 60 秒计时器，而是会在每个任务的实际触发时间，向 NAS 请求**恰好触发一次外部一次性任务**。NAS 会通过经过身份验证的 webhook 在任务触发时回调代理；代理随即执行该任务，并为下一次触发准备。在两次触发之间，代理进程可被完全停止——只有当真正的触发时刻到来时才会重新启动。

NAS 用于实现这些一次性任务的外部调度器属于**其内部实现细节**。代理不会与该调度器进行任何交互，也不会存储其凭证或知晓其具体名称。代理仅需要知晓以下三个 NAS 接口地址即可。

```
create/update/pause/resume/remove a cron job (agent side)
  │
  ▼
ChronosCronScheduler.reconcile()        ── agent computes next_run_at
  │  POST {portal}/api/agent-cron/provision   (auth: agent's Nous access token)
  ▼
NAS arms a one-shot for fire_at         ── NAS owns the scheduler + its creds
  │
  ⏰ at fire_at
  ▼
scheduler → POST {portal}/api/agent-cron/relay   (auth: scheduler signature, NAS-verified)
  │
  ▼
NAS mints a short-lived agent-audience JWT (purpose=cron_fire)
  │  POST {agent_callback_url}/api/cron/fire        (auth: that JWT)
  ▼
agent verifies the NAS JWT → store CAS claim → run_one_job → re-arm next one-shot
```

## 信任模型（请先阅读）

| 跳数 | 谁调用谁 | 认证机制 | 验证方 |
|---|---|---|---|
| 1 | agent → NAS (`provision`/`cancel`/`list`) | agent现有的**Nous Portal访问令牌**（Bearer类型）——对于托管agent而言，该令牌为NAS植入在`auth.json`中的**bootstrap-session令牌**（客户端为`hermes-cli-vps`），而非`agent:*`类型的客户端令牌 | NAS（其常规的agent令牌验证路径） |
| 2 | scheduler → NAS (`relay`) | scheduler请求的**签名** | NAS（其已有的签名验证路径） |
| 3 | NAS → agent (`/api/cron/fire`) | 由NAS生成的**短有效期JWT**（`aud=agent:{instance_id}`，`purpose=cron_fire`） | agent（使用PyJWT工具结合NAS的JWKS进行验证） |

> **关于跳数1应使用的具体令牌。** 托管agent永远不会持有`agent:{instance_id}`格式的OAuth客户端凭证——该格式的令牌仅由交互式控制台通过auth-code授权机制（浏览器用户）生成。对于所有自身的出站Portal调用，agent都会使用在启动时植入容器中的**bootstrap-session访问令牌**（`resolve_nous_access_token`），该令牌是为专用客户端`hermes-cli-vps`生成的。因此，NAS必须从`agent:{id}`类型的客户端（自托管或控制台发起的请求）中，或者针对bootstrap令牌，从与令牌会话ID（`sid`）对应的org级`AgentInstance.bootstrapSessionId`中，确定调用agent的实例ID。无论如何，跳数3生成的fire JWT仍会携带`aud=agent:{instance_id}`字段。（仅基于`agent:*`类型的客户端进行跳数1验证会导致所有真正的托管agent配置请求被拒绝，详见`src/server/agent-cron/instance-auth.ts`。）

之所以采用NAS中介的方式而非scheduler直接调用agent，是因为scheduler使用的是**NAS的密钥**进行签名，而agent并不持有（也不应持有）这些密钥。agent只能验证由NAS生成的令牌——这是其已有的信任路径。这样一来，所有scheduler的凭证都保留在NAS内部。（完整依据：计划中的DQ-4要求。）

agent端无需引入新的密钥：跳数1重用了agent原本用于Portal访问的令牌，而跳数3则复用了agent已有的NAS-JWT验证机制。

---

## 端点1 — `POST /api/agent-cron/provision`  （agent → NAS）

为某个任务启动（或重新启动，具有幂等性）一次性的执行任务。

- **认证：** `Authorization: Bearer <agent Nous访问令牌>`。NAS通过其常规的agent令牌验证路径进行验证，并将相关记录限制在发起请求的agent或组织范围内。
- **请求体：**
  ```json
  {
    "job_id": "ab12cd34",
    "fire_at": "2026-06-18T12:34:56+00:00",
    "agent_callback_url": "https://agent-xyz.fly.dev",
    "dedup_key": "ab12cd34:2026-06-18T12:34:56+00:00"
  }
  ```
- `fire_at` — 采用 ISO 8601 格式，由**代理节点自行计算**。未来可能支持亚分钟级精度；
  NAS 必须支持秒级精度（时间由代理节点掌控，因此不存在 1 分钟为最小调度单位的限制）。
- `agent_callback_url` — 代理节点自身可公开访问的基地址。在预定触发时间，NAS 会向该地址发送 `POST {agent_callback_url}/api/cron/fire` 请求。
- `dedup_key` — 格式为 `"{job_id}:{fire_at}"`。NAS 会以 `(agent_id, job_id)` 作为键进行**插入或更新操作**，从而确保重复触发同一次任务时不会产生重复的执行记录（即单次触发仅执行一次）。对于相同的 `job_id`，新的 `fire_at` 值将替换之前的调度设置。
- **操作：** 为 NAS 的**中继路由**（端点 3）安排一次在 `fire_at` 时间触发的单次任务——而非直接发送给代理节点，这样 NAS 可持续留在循环中以生成代理节点的 JWT。需将 `(agent_id, job_id, schedule_id, agent_callback_url)` 这组信息持久化存储。
- **响应：** `200 {"schedule_id": "<opaque>"}`。

## 端点 2 — `POST /api/agent-cron/cancel`（代理节点 → NAS）

- **认证方式：** 与端点 1 相同。
- **请求体：** `{"job_id": "ab12cd34"}`。
- **操作：** 取消 `(agent_id, job_id)` 对应的已安排单次任务，并删除相关记录。该操作具有幂等性——尝试取消不存在的任务也会返回 200 状态码且无实际操作。
- **响应：** `200 {"ok": true}`。

## 端点 3 — `POST /api/agent-cron/relay`（调度器 → NAS，用于任务触发中继）

- **认证方式：** 调度器需提供请求**签名**，NAS 会使用自身已存储的签名验证信息进行校验。此环节构成了任务触发的信任边界——任何伪造的中继请求都会在此被拒绝。
- **操作步骤：**
  1. 从持久化存储中查找 `(agent_id, job_id) → agent_callback_url` 的对应关系。
  2. 生成一个**短有效期**的 JWT：`aud = "agent:{instance_id}"`，`iss = {portal_url}`，`purpose = "cron_fire"`，过期时间较短（约 60–120 秒），并使用 NAS 的常规非对称加密密钥（通过 JWKS 公开）进行签名。
  3. 使用 `Authorization: Bearer <该 JWT>` 标头，以及包含 `{"job_id": "...", "fire_at": "..."}` 请求体的数据，向 `{agent_callback_url}/api/cron/fire` 发送 `POST` 请求。
  4. 若代理节点的响应非 2xx 状态码，则视为**可重试的失败**——调度器可重新尝试触发任务。由于代理节点的存储系统会通过 CAS 机制防止重复触发，因此重复尝试是安全的。
- **对调度器的响应：** 一旦代理节点的请求被接受（返回 202 状态码），即向调度器返回 2xx 响应，这样调度器就不会对已成功触发的任务再次尝试。

---

## 入站请求 `POST /api/cron/fire`（NAS → 代理节点）——代理端已实现

这是 NAS 在端点 3 的第 3 步中调用的代理端接口。该接口由**控制台应用**（`hermes_cli/web_server.py`）提供——它是托管部署环境中代理节点始终可访问的公共 HTTP 接口（即使网关处于空闲状态或已缩容，该接口仍可用）；该接口被列入 `PUBLIC_API_PATHS` 目录，因此控制台的 Cookie 验证机制允许携带 JWT 的请求顺利传递给验证模块。（在自托管 API 服务器部署场景中，该接口也会被注册到可选的 `APIServerAdapter` 中。）验证模块为 `plugins/cron/chronos/verify.py`。

- **认证方式：** `Authorization: Bearer <NAS 生成的 JWT>`。代理节点会进行以下验证：
  - 根据 NAS 的 JWKS 文件（`cron.chronos.nas_jwks_url`）验证签名是否有效；
  - 确认 `aud` 字段与 `cron.chronos.expected_audience`（即该代理节点的 `agent:{instance_id}`）一致；
  - 确认 `iss` 字段与 `cron.chronos.portal_url` 一致；
  - 检查过期时间 `exp` 与最早生效时间 `nbf` 之间是否保留有至少 30 秒的缓冲时间；
  - 确认 `purpose` 字段为 `"cron_fire"`——若 JWT 的用途为其他类型，则会被拒绝，从而防止其被用于此接口的恶意请求。
- **请求体：** `{"job_id": "ab12cd34", "fire_at": "..."}`（实际仅使用 `job_id` 字段）。
- **处理行为：**
  - 若接收到的令牌无效、缺失、被伪造、已过期，或 `aud`/`purpose` 字段不正确，则返回 **401** 状态码，任务不会被执行；
  - 若请求体中缺少 `job_id` 字段，则返回 **400** 状态码；
  - 若令牌有效，则立即返回 **202** 状态码及响应体 `{"status": "accepted", "job_id": "..."}`，任务将在后台开始执行。返回 202 而非任务实际运行状态，是为了避免代理节点的处理时间过长而导致中继的 HTTP 超时。
- **至多执行一次机制：** 在执行任务之前，代理节点会通过存储系统级的比较-设置操作（`claim_job_for_fire`）来锁定该任务。如果在首次任务执行过程中或执行完成后，调度器或中继系统尝试再次触发该任务，由于锁已被占用或时间已提前，此次尝试将会失败，从而确保任务不会被重复执行。

---

## 至多执行一次机制与重新触发规则

- **周期性任务（cron/间隔触发）：** 当任务到达预定触发时间时，代理节点会在自身存储锁的保护下更新 `next_run_at` 时间作为锁定信息的组成部分，随后执行任务，并为新的 `next_run_at` 时间重新安排一次单次触发。对于旧有的 `fire_at` 时间对应的重复中继请求，由于会发现该任务已被锁定或时间已提前，因此会被直接忽略。
- **单次触发任务（如 `30m`、`+90s` 等格式）：** 仅执行一次，执行完成后通过 `mark_job_run` 操作标记任务为已完成，不会再次触发。
- **`repeat.times = N` 设置：** 当达到预设的触发次数 `N` 后，`mark_job_run` 操作会删除该任务，因此最终触发完成后 `get_job` 函数将返回 `None`——代理节点不会重新安排该任务的触发，从而确保调度能够干净地停止，不会留下未执行的单次任务记录。
- **多副本代理节点：** 通过存储系统中的 CAS 机制，可在共享同一个 `HERMES_HOME` 的多个网关副本之间实现至多执行一次的约束——每次只有其中一个副本会执行任务。

## 自愈机制（任务状态同步）

代理节点会定期比较预期任务列表（`jobs.json`）与当前实际已安排的任务状态，同步操作在以下时机进行：
- 网关启动或恢复运行时（`start()` 函数触发）；
- 每次任务状态发生成功变更时（通过 `on_jobs_changed` 事件触发）；
- 每次任务触发完成后（作为重新触发前的补充同步）。

该机制会处理那些状态缺失、时间已变更的任务，并取消那些不再需要的“孤儿”任务记录。若因临时性 NAS 错误导致任务未能成功安排，下次状态同步时系统会自动进行自我修复。代理节点不会被定期唤醒——因为那样做反而会破坏其零资源消耗的扩展能力。

## 配置选项（代理节点端）

所有非敏感配置项均位于 `config.yaml` 文件中的 `cron.chronos.*` 目录下；代理节点本身不存储调度器的任何凭证。对于托管部署的代理节点，NAS 会在初始化时设置这些配置项：

| 键名 | 含义 |
|---|---|
| `cron.provider` | 设置为 `"chronos"` 即可启用该计时器（留空则表示使用内置计时器） |
| `cron.chronos.portal_url` | NAS 的基地址，同时也是 JWT 中的 `iss` 字段值 |
| `cron.chronos.callback_url` | 代理节点自身用于接收 NAS 发送的触发请求的公共基地址 |
| `cron.chronos.expected_audience` | 该代理节点生成的 JWT 中的 `aud` 字段值，格式为 `agent:{instance_id}` |
| `cron.chronos.nas_jwks_url` | 用于验证任务触发相关 JWT 的 NAS JWKS 文件地址 |

如果 `callback_url` 或 `portal_url` 字段为空，或者代理节点未登录 Nous 系统，则 `is_available()` 函数会返回 False，此时调度器会回退到内置的进程内计时器——这样即使在没有外部触发源的情况下，cron 任务也不会丢失触发机会。

## 备用方案（非默认配置）

入站请求 `/api/cron/fire` 的验证模块是可插拔的（通过 `get_fire_verifier()` 函数实现）。如果通过 NAS 进行的中继请求量过大，可以切换到直接由调度器向代理节点发送请求的模式，此时每个任务都会使用 NAS 专门生成的 cron 密钥进行身份验证，而无需修改 webhook 处理逻辑。默认情况下仍采用 NAS 作为中间介导方的机制。
