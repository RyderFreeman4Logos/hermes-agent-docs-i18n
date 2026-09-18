# Chronos managed-cron — 代理 ↔ NAS 通信协议

**状态：** Chronos cron 提供方的官方通信规范。  
**适用对象：** 负责实现 `agent-cron` 接口（`nous-account-service`）的 NAS 端开发人员，以及所有调试 managed-cron 功能的人员。

Hermes 所支持的网关能够在空闲状态下将资源**完全释放至零**，同时仍能按时执行定时任务。代理不会使用进程内的 60 秒计时器，而是会在每个任务的实际触发时间，向 NAS 请求**恰好触发一次外部一次性任务**。NAS 会通过经过身份验证的 webhook 在任务触发时回调代理；代理执行该任务后，再为下一个任务准备触发。在两次触发之间，代理进程可以完全停止——仅在实际任务触发时才会重新启动。

NAS 用于实现这些一次性任务的外部调度器属于**其内部实现细节**。代理不会与该调度器进行任何通信，也不会存储其凭证或知晓其名称。代理仅需要知道以下三个 NAS 接口地址即可。

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

| 转发跳数 | 谁调用谁 | 认证机制 | 验证方 |
|---|---|---|---|
| 1 | agent → NAS（执行 `provision`/`cancel`/`list` 操作） | 使用 agent 自身的 **Nous Portal 访问令牌**（Bearer 类型）——对于托管型 agent，该令牌为 NAS 存放在 `auth.json` 文件中的 **bootstrap-session 令牌**（对应客户端 `hermes-cli-vps`），而非 `agent:*` 类型的客户端令牌 | NAS（通过其常规的 agent 令牌验证路径） |
| 2 | scheduler → NAS（执行中继操作） | 使用调度器的请求 **签名** | NAS（使用其已有的签名验证路径） |
| 3 | NAS → agent（调用 `/api/cron/fire` 接口） | 使用 NAS 生成的**短期有效 JWT 令牌**（包含 `aud=agent:{instance_id}` 和 `purpose=cron_fire` 参数） | agent（通过 PyJWT 库结合 NAS 提供的 JWKS 进行验证） |

> **究竟是哪个令牌（第1步）？** 托管型代理永远不会持有 `agent:{instance_id}` 格式的 OAuth 客户端凭证——这种格式仅由交互式控制台通过 auth-code 授权方式（即浏览器用户操作时）生成。在发起所有外部端口调用时，代理都会使用**引导会话访问令牌**（`resolve_nous_access_token`），该令牌是在专用于引导过程的客户端 `hermes-cli-vps` 下生成的，并在容器首次启动时被注入其中。因此，NAS 必须从 `agent:{id}` 格式的客户端（自托管或通过控制台发起请求的代理）那里，或者对于引导令牌而言，从与令牌会话 ID（`sid`）相匹配、具有组织级范围的 `AgentInstance.bootstrapSessionId` 中，解析出发起请求的代理的实例 ID。无论如何，第3步生成的防火墙 JWT 仍然会携带 `aud=agent:{instance_id}` 字段。（仅通过 `agent:*` 格式的客户端进行第1步的身份验证就会导致所有真正的托管代理配置操作被拒绝，详见 `src/server/agent-cron/instance-auth.ts`。）

为何采用 NAS 中介而非调度器直接与代理通信：因为调度器使用的是**NAS 的密钥**进行签名，而代理并不持有（也不应持有）这些密钥。代理只能验证由**NAS 生成的令牌**——因为这已经是它所具备的信任路径。这样一来，所有的调度器凭证都保留在 NAS 内部。（完整依据见计划文档的 DQ-4 条款。）

代理端不会引入任何新密钥：第1步会复用代理原本用于访问端口的令牌，而第3步则会复用代理已有的 NAS-JWT 验证机制。

---

## 端点 1 — `POST /api/agent-cron/provision` （代理 → NAS）

为某项任务精确地触发一次（或以幂等方式重新触发一次）一次性操作。

- **认证信息：** `Authorization: Bearer <agent Nous访问令牌>`。NAS会通过常规的代理令牌验证机制进行校验，并将相关数据范围限制在发起请求的代理/组织内。
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
  NAS 需要支持秒级精度（时间由代理节点掌控，因此不存在1分钟的调度间隔限制）。
- `agent_callback_url` — 代理节点自身可公开访问的基地址。在预定触发时间，NAS 会向该地址发送 `POST {agent_callback_url}/api/cron/fire` 请求。
- `dedup_key` — 格式为 `"{job_id}:{fire_at}"`。NAS 会按照 `(agent_id, job_id)` 进行唯一性判断并执行插入或更新操作，因此重新触发相同的任务是幂等的（不会产生重复的单次执行记录）。对于同一个 `job_id`，新的 `fire_at` 值将替换之前的调度设置。
- **操作**：为某个任务配置在 `fire_at` 时间触发的单次执行任务，该任务将通过 NAS 的**中继路由**（端点3）发送，而非直接发送给代理节点，这样 NAS 可持续处于循环状态以生成代理节点的 JWT。需将 `(agent_id, job_id, schedule_id, agent_callback_url)` 这组信息持久化存储。
- **响应**：`200 {"schedule_id": "<opaque>"}`。

## 端点 2 — `POST /api/agent-cron/cancel` （代理节点 → NAS）

- **认证方式**：与端点1相同。
- **请求体**：`{"job_id": "ab12cd34"}`。
- **操作**：取消对应 `(agent_id, job_id)` 的已配置单次执行任务，并删除相关记录。该操作是幂等的——尝试取消不存在的任务时，也会返回 200 状态码且无实际操作。
- **响应**：`200 {"ok": true}`。

## 端点 3 — `POST /api/agent-cron/relay` （调度器 → NAS，用于任务触发中继）

- **认证：**调度器会发送请求**签名**，NAS会利用自身已存储的签名路径对该签名进行验证。这一环节构成了防火墙的信任边界——任何伪造的中继调用都将在此处被拒绝。
- **操作流程：**
  1. 从持久化存储中查询`(agent_id, job_id) → agent_callback_url`的对应关系。
  2. 生成一个**短期有效**的JWT：`aud = "agent:{instance_id}"`，`iss = {portal_url}`，`purpose = "cron_fire"`，有效期较短（约60–120秒），并使用NAS通过JWKS发布的标准非对称加密密钥进行签名。
  3. 发送`POST {agent_callback_url}/api/cron/fire`请求，请求头中包含`Authorization: Bearer <该JWT>`，请求体为`{"job_id": "...", "fire_at": "..."}`。
  4. 若代理端的响应状态码非2xx，则视为**可重试**的失败（让调度器再次尝试中继请求）。由于代理端的存储系统会通过CAS机制避免重复触发任务，因此重复尝试是安全的。
- **对调度器的响应：**一旦代理端的POST请求被接收并返回202状态码，调度器就不会再对已处理的任务进行重复尝试。

---

## 入站`POST /api/cron/fire`请求（NAS → 代理）——代理端实现已完成

这正是NAS在步骤3的第3项中所调用的代理端接口。在托管部署环境中，该请求需要经过两跳传输。

1. **控制面板应用**（`hermes_cli/web_server.py`）——这是代理唯一的公开 HTTP 接口（Fly 代理仅开放一个端口，即控制面板的端口）。该接口被列入 `PUBLIC_API_PATHS` 目录，因此控制面板的 Cookie 验证机制会允许携带 JWT 的回调请求传递给验证器。控制面板会对 JWT 进行验证，获取任务的相关配置信息，随后**将请求转发**至回环网络中的第二阶段处理节点，并保留 NAS 传递的令牌信息——它本身并不执行任务。

2. **网关 `APIServerAdapter`**（位于 `gateway/platforms/api_server.py`，通过回环网络绑定，默认端口为 8642）——该组件会再次验证 JWT（属于多层防御策略），并利用网关的**实时平台适配器**来执行任务。正是这些适配器使得基于中继节点的逻辑平台以及端到端加密房间能够正常接收消息（而独立的发送路径则无法实现这一功能）。那些直接暴露 `api_server` 接口的自托管 API 服务器部署方案，会直接跳过第一阶段处理，直接进入第二阶段。

如果从第一阶段无法访问网关（例如零扩展模式仍在启动中、重启窗口期内，或 `api_server` 被禁用），控制面板将返回 **503** 错误码，此时 NAS 会尝试重新发送请求（非 2xx 状态码表示可重试，详见下文）；同时，存储系统中的 CAS 机制会用于消除可能出现的重复发送情况。设计上刻意没有在控制面板内部设置任务执行作为备用方案。验证逻辑位于 `plugins/cron/chronos/verify.py` 文件中。

- **认证信息：** `Authorization: Bearer <NAS生成的JWT>`。代理会验证以下内容：
  - 签名是否与NAS的JWKS（`cron.chronos.nas_jwks_url`）匹配；
  - `aud` 是否等于 `cron.chronos.expected_audience`（即该代理的`agent:{instance_id}`值）；
  - `iss` 是否等于 `cron.chronos.portal_url`；
  - `exp`/`nbf` 时间是否在允许范围内（允许30秒的误差）；
  - `purpose` 是否为 `"cron_fire"`——普通代理JWT（用途为其他值或无特定用途）将被拒绝，从而无法被用于向此端点发送请求。
- **请求体：** `{"job_id": "ab12cd34", "fire_at": "..."}`（实际仅使用`job_id`字段）。
- **处理行为：**
  - 若令牌无效、缺失、被篡改、已过期，或`aud`/`purpose`字段不正确，则返回**401错误**，任务不会被执行；
  - 若请求中缺少`job_id`字段，则返回**400错误**；
  - 若令牌有效，则立即返回**202状态码**及`{"status": "accepted", "job_id": "..."}`响应，任务将在后台开始运行。202状态码的提前返回意味着即使代理需要较长时间处理任务，也不会触发中继的HTTP超时机制。
- **至多执行一次机制：** 在执行任务之前，代理会通过存储级的比较并设置操作（`claim_job_for_fire`）来锁定该任务。如果在首次任务执行过程中（或执行完成后），有新的重试请求到达，那么该请求将失去对任务的锁定权限，从而避免任务被重复执行。

---

## 至多执行一次与重新启动机制

- **周期性触发（cron/间隔定时）：** 当任务被触发时，代理会在自身锁定的存储中更新`next_run_at`时间作为任务状态标记，随后执行该任务，再为新的`next_run_at`时间重新配置一次性任务。而针对旧`fire_at`时间的重复任务请求会因发现任务已被处理或时间已更新而被拒绝。
- **一次性触发（如“30分钟”、“+90秒”等）：** 仅触发一次，随后通过`mark_job_run`将任务标记为已完成，不会再次启动该任务。
- **`repeat.times = N`：** 当达到指定次数后，`mark_job_run`会删除对应任务，因此在最后一次触发后`get_job`将返回`None`。此时代理不会重新启动该任务，从而确保调度能够干净地停止，不会出现未被处理的一次性任务。
- **多副本代理：** 通过存储的CAS机制，共享同一`HERMES_HOME`的多个网关副本之间确保任务最多仅触发一次——每次触发时只会有一个副本执行任务。

## 自愈协调机制

代理会持续对比预期状态（`jobs.json`）与实际运行状态，进行协调处理，包括：
- 在`start()`阶段（网关启动或唤醒时）；
- 每次任务状态成功更新时（通过`on_jobs_changed`事件）；
- 每次任务触发后（重新启动任务时）。

该机制会修复那些未被正确启动或时间已过期的任务，并取消异常存在的任务。若因临时性NAS错误导致任务未能成功启动，也可在下一次协调时自动恢复。此外，代理不会定期唤醒处于休眠状态的任务——因为那样做反而会破坏其零资源消耗的设计理念。

## 配置选项（代理端）

所有非敏感配置项均位于`config.yaml`中的`cron.chronos.*`字段中；代理本身并不存储调度相关的凭证。对于托管型代理，NAS会在任务配置时自动设置这些值。

| 键值 | 含义 |
|---|---|
| `cron.provider` | 设置为 `"chronos"` 即可启用（留空则表示使用内置计时器） |
| `cron.chronos.portal_url` | NAS 的基础 URL，同时也是预期的 JWT `iss` 值 |
| `cron.chronos.callback_url` | 用于触发 NAS→Agent 请求的 Agent 自有公共基础 URL |
| `cron.chronos.expected_audience` | 该 Agent 的 JWT `aud` 值（格式为 `agent:{instance_id}`） |
| `cron.chronos.nas_jwks_url` | 用于验证触发请求 JWT 的 NAS JWKS 文件地址 |

如果 `callback_url` 或 `portal_url` 为空，或者 Agent 未进行 Nous 登录，`is_available()` 函数将返回 False，此时解析器会回退到内置的进程内计时器——这样就能确保定时触发功能始终可用。

## 备用方案（非默认）

入站请求 `/api/cron/fire` 的验证机制是可插拔的（通过 `get_fire_verifier()` 函数实现）。如果通过 NAS 中转的任务量达到饱和，可以切换为直接的调度器→Agent 模式，为每个任务生成专属的 NAS 生成的 cron 密钥，从而替代 NAS-JWT 验证机制，且**无需修改 webhook 处理逻辑**。默认情况下仍采用通过 NAS 中转的验证方式。
