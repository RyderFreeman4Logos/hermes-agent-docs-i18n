# 会话生命周期

> **目标受众：** 网关开发者和维护人员  
> **相关源文件：** `gateway/session.py`（约1444行）、`gateway/run.py`（约16800行）、`gateway/config.py`  
> **最后更新时间：** 2026-06-16  

## 概述

**会话**指的是智能体与消息平台上的一个或多个用户之间持续的对话。会话生命周期决定了对话何时保持有效、何时重置、如何在网关重启后继续运行，以及在高并发操作期间消息如何排队处理。

会话系统主要存在于以下两个模块中：

- `gateway/session.py` — 数据模型（`SessionSource`、`SessionEntry`、`SessionContext`）、密钥生成函数（`build_session_key`）以及主存储结构（`SessionStore`）。
- `gateway/run.py` — 网关运行器（`GatewayRunner`），它将会话集成到消息处理流程中，负责监控会话过期时间、实现智能体缓存、处理重启恢复以及管理消息队列。

---

## 1. SessionSource — 消息来源描述符

`SessionSource` 是用于记录*消息来源*的固定结构体。它会被附加到每一个传入的 `MessageEvent` 上，用于路由、隔离以及上下文注入。

### 字段说明

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `platform` | `Platform` | *(必填)* | 用于标识消息平台的枚举值（如 telegram、discord、slack、signal、whatsapp、matrix、本地等）。 |
| `chat_id` | `str` | *(必填)* | 平台级别的聊天/群组/频道标识符。会通过适配器的 `chat_id_key` 转换函数进行处理。 |
| `chat_name` | `Optional[str]` | `None` | 聊天或群组的可读名称。 |
| `chat_type` | `str` | `"dm"` | 取值包括 `"dm"`、`"group"`、`"channel"`、`"thread"`。用于控制会话密钥的生成方式及隔离策略。 |
| `user_id` | `Optional[str]` | `None` | 平台特定的用户标识符，用于授权及实现按用户隔离会话。 |
| `user_name` | `Optional[str]` | `None` | 消息发送者的显示名称，会被注入到系统提示语中。 |
| `thread_id` | `Optional[str]` | `None` | 论坛主题/Discord 线程/Slack 线程的标识符，用于区分多线程对话。 |
| `chat_topic` | `Optional[str]` | `None` | 频道的主题或描述内容（如 Discord 频道主题、Slack 频道用途）。 |
| `user_id_alt` | `Optional[str]` | `None` | 平台特定的稳定替代标识符（如 Signal UUID、飞书 union_id）。当 `user_id` 为临时值时使用。 |
| `chat_id_alt` | `Optional[str]` | `None` | Signal 群组的内部标识符，用于将 Signal V2 格式的群组标识转换为标准格式。 |
| `is_bot` | `bool` | `False` | 当消息发送者为机器人或 Webhook（如 Discord 机器人）时为 `True`。 |
| `guild_id` | `Optional[str]` | `None` | Discord 社群/Slack 工作空间/Matrix 服务器级别的标识符。 |
| `parent_chat_id` | `Optional[str]` | `None` | 当 `chat_id` 指向线程时，对应的父频道标识。 |
| `message_id` | `Optional[str]` | `None` | 触发本次对话的消息编号，用于固定消息、回复或反应操作，以及注入 Discord ID。 |
| `role_authorized` | `bool` | `False` | 当适配器通过平台角色（而非单个用户 ID）授予访问权限时为 `True`。 |

### 主要方法

- **`description`**（属性：`str`）—— 可读性摘要，例如 `"与 Alice 的私信"`、`"群组：我的群组，线程：12345"`。
- **`to_dict()` / `from_dict()`** — 用于在 `sessions.json` 中进行序列化与反序列化的操作。

---

## 2. SessionEntry — 活跃会话记录

`SessionEntry` 是存储在内存中并持久化到 `{sessions_dir}/sessions.json` 的每会话元数据记录。每个记录都将一个 `session_key` 对应到其当前的 `session_id`。

### 字段说明

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `session_key` | `str` | *(必填)* | 用于唯一标识对话路径的确定性密钥（详见第4节）。 |
| `session_id` | `str` | *(必填)* | 该次对话实例的唯一标识符，格式为 `YYYYMMDD_HHMMSS_<8位十六进制数>`。 |
| `created_at` | `datetime` | *(必填)* | 该次会话实例创建的时间。 |
| `updated_at` | `datetime` | *(必填)* | 最后一次活动的时间戳，用于计算空闲超时时间以及检查会话是否过期。 |
| `origin` | `Optional[SessionSource]` | `None` | 创建该会话的来源，用于消息传递路由。 |
| `display_name` | `Optional[str]` | `None` | 聊天的显示名称，取自 `SessionSource.chat_name`。 |
| `platform` | `Optional[Platform]` | `None` | 平台枚举值，会被保存下来以便在重启后查询过期策略。 |
| `chat_type` | `str` | `"dm"` | 聊天类型，同样会被保存以供策略查询使用。 |
| `input_tokens` | `int` | `0` | 智能体已消耗的累计输入（提示词）token数。 |
| `output_tokens` | `int` | `0` | 智能体已生成的累计输出（回复内容）token数。 |
| `cache_read_tokens` | `int` | `0` | 提示词缓存中已读取的累计 token数。 |
| `cache_write_tokens` | `int` | `0` | 提示词缓存中已写入的累计 token数。 |
| `total_tokens` | `int` | `0` | 所有轮次对话中消耗的 token 总数。 |
| `estimated_cost_usd` | `float` | `0.0` | 预估的累计美元费用。 |
| `cost_status` | `str` | `"unknown"` | 费用跟踪状态标签。 |
| `last_prompt_tokens` | `int` | `0` | 上次 API 返回的提示词 token 数，用于进行更精确的压缩预检查。 |

### 布尔标志位（状态机）

`SessionEntry` 包含多个布尔标志位，它们共同构成一个简单的状态机，用于控制下次访问时会话的行为。

| 标志位 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `was_auto_reset` | `bool` | `False` | 当会话因策略限制（如空闲超时或每日限制）而自动重置时被设置。该标志仅会被使用一次，用于注入上下文提示。 |
| `auto_reset_reason` | `Optional[str]` | `None` | 值为 `"idle"` 或 `"daily"`，表示会话为何自动重置。 |
| `reset_had_activity` | `bool` | `False` | 表示已过期的会话中是否还有消息存在（即 `total_tokens > 0`）。 |
| `is_fresh_reset` | `bool` | `False` | 当通过 `/new` 或 `/reset` 显式指令重置会话时被设置。会在收到第一条消息时触发主题/频道技能的重新注入。该标志与 `was_auto_reset` 相区分，以避免出现误导性的“会话已过期”提示。 |
| `expiry_finalized` | `bool` | `False` | 在调用 `on_session_finalize` 回调函数、清理工具资源并移除缓存的智能体之后，由后台过期监控器设置该标志，以防止在重启过程中重复执行最终化操作。 |
| `suspended` | `bool` | `False` | 表示强制清除会话的信号，通常由 `/stop` 指令或连续多次重启失败导致的死循环升级触发。在下一次调用 `get_or_create_session()` 时，无论 `resume_pending` 的状态如何，都会强制生成新的 `session_id`。 |
| `resume_pending` | `bool` | `False` | 表示软恢复标记，由 `suspend_recently_active()`（崩溃恢复）或超时处理功能设置。在下一次访问时，会保留现有的 `session_id`，使用户能够继续沿用相同的对话记录。该标志会在下一次成功完成对话轮次后被清除。 |
| `resume_reason` | `Optional[str]` | `None` | 标记恢复原因，可能为 `"restart_timeout"`、`"shutdown_timeout"`、`"restart_interrupted"` 等。 |
| `last_resume_marked_at` | `Optional[datetime]` | `None` | 上次标记为待恢复的时间戳。 |

### 状态转换逻辑（get_or_create_session）

```
                    ┌──────────┐
                    │  Incoming │
                    │  Message  │
                    └────┬─────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  session_key exists  │──── No ──► Create fresh SessionEntry
              │  AND !force_new      │
              └──────────┬───────────┘
                         │ Yes
                         ▼
              ┌──────────────────────┐
              │  entry.suspended?    │──── Yes ──► Auto-reset: new session_id
              └──────────┬───────────┘           (reason="suspended")
                         │ No
                         ▼
              ┌──────────────────────┐
              │ entry.resume_pending?│──── Yes ──► Return existing entry
              └──────────┬───────────┘           (preserve session_id)
                         │ No                     Clear flag on next successful turn
                         ▼
              ┌──────────────────────┐
              │   Policy says reset? │──── Yes ──► Auto-reset: new session_id
              └──────────┬───────────┘           (reason="idle"/"daily")
                         │ No
                         ▼
              ┌──────────────────────┐
              │  Return existing     │
              │  entry, bump         │
              │  updated_at          │
              └──────────────────────┘
```

**`get_or_create_session()` 中的优先级顺序：**
1. `suspended=True` → 始终强制重置（彻底清除数据）
2. `resume_pending=True` → 保留 session_id（软恢复）
3. 策略过期（闲置/每日）→ 自动重置
4. 无触发条件 → 返回现有记录并更新 `updated_at` 时间戳

---

## 3. SessionStore — 存储与操作

`SessionStore` 是主要的存储层。它通过内存中的字典 `_entries` 来管理会话数据，并将这些数据持久化到 `sessions.json` 文件中；而会话元数据及消息记录则由 SQLite 数据库（`SessionDB`）进行标准化存储。

### 构造函数

```python
SessionStore(sessions_dir: Path, config: GatewayConfig, has_active_processes_fn=None)
```

- `sessions_dir` — 存放 `sessions.json` 文件的目录。  
- `config` — 用于查询重置策略的 `GatewayConfig` 实例。  
- `has_active_processes_fn` — 可选的基于 `session_key` 的回调函数，用于检测是否有正在运行的后台进程。包含活跃进程的会话不会被过期或删除。  

### 操作（方法）

| 方法 | 描述 |
|---|---|
| `get_or_create_session(source, force_new=False)` | 核心入口函数。返回现有的会话或创建新的 `SessionEntry`，并评估会话的 `suspended`、`resume_pending` 状态以及重置策略。同时创建或删除 SQLite 记录。 |
| `update_session(session_key, last_prompt_tokens=None)` | 交互结束后对元数据进行轻量级更新，更新 `updated_at` 时间戳，可选择性地记录 `last_prompt_tokens`。 |
| `reset_session(session_key, display_name=None)` | 显式重置会话（通过 `/new` 或 `/reset` 调用）。生成新的 `session_id`，设置 `is_fresh_reset=True`，终止旧的 SQLite 会话并创建新的会话。 |
| `switch_session(session_key, target_session_id)` | 切换到另一个现有的会话 ID（通过 `/resume` 调用）。终止当前的 SQLite 会话，并重新打开目标会话。 |
| `suspend_session(session_key)` | 将会话标记为 `suspended=True`（通过 `/stop` 调用），确保下次访问时自动重置会话。 |
| `mark_resume_pending(session_key, reason)` | 将会话标记为 `resume_pending=True`（因超时而暂停后调用），下次访问时保留该会话的 `session_id`，但不会覆盖已设置的 `suspended=True` 状态。 |
| `clear_resume_pending(session_key)` | 在成功恢复会话对话后清除 `resume_pending` 状态。在 `run_conversation()` 执行完毕后的网关端调用此函数。 |
| `suspend_recently_active(max_age_seconds=120)` | 故障恢复功能：将近期活跃的会话标记为 `resume_pending=True`，跳过已处于暂停或待恢复状态的会话。在非正常关闭后启动时调用。 |
| `prune_old_entries(max_age_days)` | 删除超过 `max_age_days` 天的记录（依据 `updated_at` 时间判断），同时跳过已暂停的记录及包含活跃进程的会话。 |
| `list_sessions(active_minutes=None)` | 返回所有会话，可根据近期活动情况筛选，结果按 `updated_at` 时间从新到旧排序。 |
| `lookup_by_session_id(session_id)` | 根据持久化的会话 ID 查找对应的活跃 `SessionEntry`。 |
| `has_any_sessions()` | 检查是否曾经创建过任何会话（基于 SQLite 记录历史，而不仅限于内存中的字典）。 |
| `append_to_transcript(session_id, message, skip_db=False)` | 将消息追加到 SQLite 中的对话记录中。若设置 `skip_db=True`，则在代理已保存记录时避免重复写入。 |
| `rewrite_transcript(session_id, messages)` | 完全替换会话的对话记录（用于 `/retry`、 `/undo`、 `/compress` 等操作）。 |
| `load_transcript(session_id)` | 从会话的 SQLite 对话记录中加载所有消息。 |
| `rewind_session(session_id, n=1)` | 通过软删除方式撤销最近 `n` 条用户输入（保留审计日志），返回 `{rewound_count, turns_undone, target_text}`。 |

### 内部辅助函数

- `_ensure_loaded()` / `_ensure_loaded_locked()` — 将 `sessions.json` 的内容加载到 `_entries` 字典中。  
- `_save()` — 通过临时文件结合 `atomic_replace` 方法对 `sessions.json` 进行原子级写入。  
- `_generate_session_key(source)` — 调用 `build_session_key()` 函数，并传入相关配置参数以生成会话键。  
- `_is_session_expired(entry)` — 仅根据会话条目本身进行策略判断（无需源数据），由后台过期监控模块使用。  
- `_should_reset(entry, source)` — 根据策略判断返回 `"idle"`、`"daily"` 或 `None`，指示是否需要重置会话。  

### 存储结构 |

```
{sessions_dir}/
  sessions.json          # In-memory _entries dict, persisted as JSON
                           Maps session_key → SessionEntry (metadata only)
  {session_id}.jsonl     # (Legacy, removed in spec 002)
```

默认的会话转录存储采用基于 `SessionDB`（来自 `hermes_state`）的 SQLite 数据库。`sessions.json` 文件用于保存 `session_key → session_id` 的映射关系以及相关元数据（如标志位、时间戳、令牌计数等）。若 SQLite 不可用，系统将退而使用 JSONL 格式进行存储，但这属于降级方案。

---

## 4. SessionKey 生成规则

SessionKey 是用于标识特定对话通道的确定性字符串，它由函数 `build_session_key(source, group_sessions_per_user, thread_sessions_per_user)` 生成。

### 键格式

```
agent:main:{platform}:{chat_type}[:{chat_id}][:{thread_id}][:{participant_id}]
```

### 私信规则

| 场景 | 键值 |
|---|---|
| 使用 chat_id 的私信 | `agent:main:telegram:dm:12345` |
| 同时使用 chat_id 和线程标识的私信 | `agent:main:telegram:dm:12345:thread_678` |
| 不使用 chat_id、仅使用参与者 ID 的私信 | `agent:main:signal:dm:user_abc` |
| 既不使用 chat_id 也不使用参与者 ID 的私信 | `agent:main:telegram:dm` |
| WhatsApp 私信（标准化格式） | `agent:main:whatsapp:dm:{canonical_number}` |

- 只要存在 `chat_id`，就会为每段私人对话创建独立标识。
- `thread_id` 用于区分同一私信对话中的不同线程。
- 若没有 `chat_id`，系统会自动使用 `user_id_alt` 或 `user_id` 作为参与者 ID。
- 若完全不提供任何标识符，该平台上的所有私信将被合并为同一个共享会话。

### 群组/频道规则

| 场景 | 键值 |
|---|---|
| 普通群聊 | `agent:main:telegram:group:-10012345` |
| 需为每位用户独立维护会话的群聊 | `agent:main:telegram:group:-10012345:user_abc` |
| 群组内的共享线程 | `agent:main:discord:group:12345:thread_678` |
| 群组内的用户专属线程 | `agent:main:discord:group:12345:thread_678:user_abc` |
| 频道 | `agent:main:slack:channel:C12345` |
| WhatsApp 群组（标准化格式） | `agent:main:whatsapp:group:{canonical_id}:{participant}` |

- `chat_id` 用于标识父级群组或频道。
- `thread_id` 用于区分该群组或频道内的不同线程。
- **用户独立会话模式**（通过添加 `participant_id` 实现）由以下参数控制：
  - `group_sessions_per_user`（默认值为 `True`）——群组/频道会话为每位用户独立创建。
  - `thread_sessions_per_user`（默认值为 `False`）——线程默认为**共享模式**
   （Telegram 论坛主题、Discord 线程以及 Slack 线程均共享同一个会话）。
- `participant_id` 的优先级为：先使用 `user_id_alt`，再使用 `user_id`。
- WhatsApp 相关标识符会经过标准化处理，以应对 JID/LID 别名变化的问题。

### 特殊情况：WhatsApp

WhatsApp 电话号码会经过 `canonical_whatsapp_identifier()` 处理，该函数会移除 `@s.whatsapp.net` 后缀并将号码转换为 E.164 格式。这样即便桥接服务返回同一电话号码的不同别名形式，也能避免会话碎片化问题。

---

## 5. 多用户隔离策略

多用户隔离机制决定了同一聊天中的多名用户是共享同一个对话会话，还是各自拥有独立的私人会话。

### 决策逻辑 (`is_shared_multi_user_session`)

```python
def is_shared_multi_user_session(source, *, group_sessions_per_user, thread_sessions_per_user):
    if source.chat_type == "dm":
        return False  # DMs are always private
    if source.thread_id:
        return not thread_sessions_per_user  # Threads: shared unless per-user
    return not group_sessions_per_user       # Groups: isolated unless shared
```

### 摘要

| 聊天类型 | 默认设置 | 配置控制 |
|---|---|---|
| 私信 | 私有（绝不共享） | 无 |
| 群组/频道 | 每用户独立会话 | `group_sessions_per_user`（默认值：True） |
| 线索讨论（论坛、Discord） | 共享（所有参与者可见相同上下文） | `thread_sessions_per_user`（默认值：False） |

### 对系统提示语的影响

当 `shared_multi_user_session=True` 时，系统提示语将不再包含固定用户名，而是显示为：*“多用户 {线程|会话} —— 消息前会标注[发送者姓名]。允许多名用户参与。”* 在运行时，网关会在每条用户消息前添加对应的发送者姓名，从而保留提示语缓存功能（系统提示语不会随对话轮次变化）。

---

## 6. 重置策略

重置策略用于控制会话何时自动丢失上下文（并获得新的 `session_id`）。

### 策略模式 (`SessionResetPolicy`)

| 模式 | 行为 | 默认配置 |
|---|---|---|
| `"none"` | 绝不自动重置。仅通过压缩机制管理上下文。 | — |
| `"idle"` | 自 `updated_at` 时间起，经过 N 分钟无活动后重置。 | `idle_minutes: 1440`（24小时） |
| `"daily"` | 每天在特定时间（本地时间）重置。 | `at_hour: 4`（凌晨4点） |
| `"both"` | 以先满足的条件为准——达到每日时间限制或闲置超时。 | **（默认值）** |

### 策略评估逻辑

```python
# Idle check
idle_deadline = entry.updated_at + timedelta(minutes=policy.idle_minutes)
if now > idle_deadline: return "idle"

# Daily check
today_reset = now.replace(hour=policy.at_hour, minute=0, second=0, microsecond=0)
if now.hour < policy.at_hour:
    today_reset -= timedelta(days=1)  # Reset hasn't happened yet today
if entry.updated_at < today_reset: return "daily"
```

### 按平台/按类型配置策略

可通过 `config.get_reset_policy()` 根据不同的平台和会话类型来配置重置策略。
这样一来，不同平台就可以拥有不同的过期规则（例如，Telegram 私信在24小时无操作后会被重置，而 Slack 群组则不会过期）。

### 排除项

包含正在运行的后台进程的会话**绝不会**过期或被重置。`has_active_processes_fn` 回调函数会在评估策略时会检查是否有进程正在运行。

### 重置后的影响

当触发重置时，将会发生以下操作：

1. 在 SQLite 中终止旧会话，并记录原因为 `"session_reset"`。
2. 生成新的 `session_id`（格式为 `YYYYMMDD_HHMMSS_<8位十六进制数>`）。
3. 创建新的 `SessionEntry` 对象，设置 `was_auto_reset=True` 并注明重置原因。
4. 如果旧会话有过任何轮次交互（即 `total_tokens > 0`），则设置 `reset_had_activity` 为真。
5. 在下一次过期检查时，旧的 AIAgent 缓存条目将被清除。
6. 在重置后的第一条消息中，会插入一条上下文提示：“会话因长时间无操作/每日自动重置而过期。”

---

## 7. 重启恢复流程

重启恢复系统能够确保在网关重启、崩溃或超时断开等情况下，正在处理的会话不会丢失。该机制正是为了解决问题 #7536 而设计的。

### 启动恢复步骤

```
Gateway starts
       │
       ▼
┌───────────────────────────────┐
│ Check for .clean_shutdown     │── Exists? ──► Skip suspension (clean exit)
│ marker                        │
└───────────────────────────────┘
       │ Missing
       ▼
┌───────────────────────────────┐
│ session_store                 │── Marks sessions updated within
│ .suspend_recently_active()    │   last 120 seconds as resume_pending
└───────────────────────────────┘
       │
       ▼
┌───────────────────────────────┐
│ _suspend_stuck_loop_sessions()│── Suspends sessions that have been
│                               │   active across 3+ restarts
└───────────────────────────────┘
       │
       ▼
┌───────────────────────────────┐
│ Queue inbound messages while  │
│ startup restore runs          │
│ (_startup_restore_in_progress)│
└───────────────────────────────┘
       │
       ▼
┌───────────────────────────────┐
│ For each adapter, find        │
│ resume_pending sessions →     │
│ synthesize MessageEvent and   │
│ run _handle_message to let    │
│ the agent auto-continue       │
└───────────────────────────────┘
```

### suspend_recently_active(max_age_seconds=120)

当网关启动时，若不存在`.clean_shutdown`标记（表示系统崩溃或意外退出），则会调用此函数。对于过去120秒内有过更新的会话，将会执行以下操作：

- 设置`resume_pending=True`、`resume_reason="restart_interrupted"`以及`last_resume_marked_at=现在时间`。
- 跳过那些已经标记为`resume_pending=True`的会话（避免重复标记）。
- 跳过那些被明确标记为`suspended=True`的会话（此类会话应保持已清除状态）。

### 死循环检测（`_suspend_stuck_loop_sessions`）

该功能通过JSON文件`{HERMES_HOME}/restart_counts.json`来统计连续重启次数。如果某个会话在3次及以上连续重启后仍然处于活跃状态，系统会自动将其暂停，从而为用户提供全新的对话环境。

### 数据清除超时标记

在平滑关闭或重启过程中，数据清除机制会针对那些在清除操作触发时正处于对话处理中的会话调用`mark_resume_pending()`函数。标记的原因包括：

- `"restart_timeout"` — 在重启数据清除期间被终止
- `"shutdown_timeout"` — 在关闭操作数据清除期间被终止
- `"restart_interrupted"` — 系统崩溃后的恢复（由`suspend_recently_active`功能触发）

以上三种原因均被记录在 `_AUTO_RESUME_REASONS` 中，符合条件的会话可在系统启动时自动恢复。

### 下次访问时自动恢复

当`get_or_create_session()`函数检测到某个会话的`resume_pending=True`时，将会执行以下操作：

1. 直接返回现有的会话记录，**不会**创建新的`session_id`。
2. 完整保留原有的对话记录内容。
3. 此时不会清除该标记——它会一直保留，直到下一次成功的对话轮次结束（只有在`run_conversation()`函数返回实际响应后，网关才会调用`clear_resume_pending()`函数来清除标记）。
4. 如果再次中断正在恢复的对话轮次，`resume_pending`标志仍会保持启用状态，系统会在下一次重启时尝试继续。死循环计数器则用于处理极端情况——若连续尝试3次仍无法解决，则该会话将被暂停。

### 平滑关闭标记（`.clean_shutdown`）

该标记在平滑关闭操作结束时生成。在下次系统启动时：

- 若存在此标记：将完全跳过`suspend_recently_active()`函数的执行。因为活跃的智能体早已完成数据清除，所以不会有任何会话处于挂起状态。
- 随后即可删除该标记。

此举可避免在执行`hermes update`、`hermes gateway restart`或 `/restart`命令后出现不必要的自动恢复现象。

---

## 8. 消息队列处理流程

消息队列系统主要处理两种场景：

1. **中断后的后续消息** — 当用户在与智能体对话的过程中发送多条消息时，后续的消息会被作为单次处理的待处理消息放入队列中。
2. **`/queue`命令的FIFO处理** — 对于显式发送的 `/queue` 命令，系统会按顺序依次让智能体完成完整的对话处理，不会合并处理多个命令。

### 数据结构

```
adapter._pending_messages: Dict[session_key, MessageEvent]
    └── Single "next-up" slot per session. Overwritten on repeat sends
        (burst collapse). Shared with photo-burst follow-ups.

self._queued_events: Dict[session_key, List[MessageEvent]]
    └── Overflow buffer. Each /queue invocation appends here when the
        slot is occupied. Promoted one-at-a-time after each drain.
```

### 排队处理（`_enqueue_fifo`）

```
_enqueue_fifo(session_key, event, adapter)
       │
       ▼
┌───────────────────────────────────────┐
│ Is slot free?                         │
│ (session_key NOT in _pending_messages)│── Yes ──► Place event in slot
└───────────────────────────────────────┘
       │ No
       ▼
Append to _queued_events[session_key] (overflow tail)
```

### 出队/升级操作（`_promote_queued_event`）

在资源槽被占用后，于数据排出端调用此函数。若存在溢出项：

- 当 `pending_event` 为 `None`（即资源槽为空）时，将溢出项的头部作为新事件返回。
- 当 `pending_event` 存在时，将该溢出项的头部暂存于资源槽中，以备下一次递归处理。
- 若没有可用的适配器，则将该溢出项重新放入 `_queued_events` 中（不可静默丢弃）。

### 队列深度

`_queue_depth(session_key, adapter)` 的返回值为 `len(overflow) + (1 若资源槽被占用，否则为 0)`。

### 清空操作

通过 `/new` 和 `/reset` 命令（经由 `_handle_reset_command`），可清空该会话的队列中的事件。

### FIFO 定律

每次调用 `/queue` 都会按照 FIFO 顺序触发一次完整的智能体处理周期，且不会发生数据合并。单资源槽的 `_pending_messages` 与溢出队列 `_queued_events` 设计确保了在当前处理周期内重复发送消息时，仍能保持处理顺序的正确性。

---

## 9. 会话上下文注入

`SessionContext` 是由 `SessionSource` 和 `GatewayConfig` 组合生成的，随后会被注入到智能体的系统提示语中。它向智能体提供以下信息：

- 当前消息的来源
- 已连接的平台列表
- 智能体可输出 scheduled task 结果的位置
- 当前是否为共享的多用户会话

### 构建过程（`build_session_context`）

```python
def build_session_context(source, config, session_entry=None) -> SessionContext
```

1. 从配置中收集已连接的平台信息。  
2. 为每个平台收集其主频道列表。  
3. 通过 `is_shared_multi_user_session()` 函数确定是否使用 `shared_multi_user_session`。  
4. 若提供了 `session_entry`，则附加会话元数据（键、ID及时间戳）。

### 个人身份信息脱敏（`build_session_context_prompt`）

动态系统提示部分（`## Current Session Context`）在发送给大型语言模型之前，可选择性地对以下内容进行个人身份信息脱敏处理：  
- 用户 ID → `user_<12位十六进制>`（带有 SHA-256 前缀）  
- 聊天 ID → `<平台名>:<12位十六进制>` 或仅 `<12位十六进制>`  

无需脱敏的平台包括：Discord（因需原始 ID 以实现 `@mentions` 功能），以及所有未被标记为 `pii_safe` 的插件注册平台。  
脱敏操作仅适用于系统提示文本；路由信息、会话密钥及适配器操作始终使用原始值。

---

## 10. 会话过期监控器

`_session_expiry_watcher` 任务会在网关事件循环中每 300 秒（5 分钟）执行一次。

### 主要职责

1. **处理已过期的会话** —— 对于那些满足 `_is_session_expired()` 返回 `True` 且 `expiry_finalized` 为 `False` 的会话条目，执行以下操作：  
   - 调用 `on_session_finalize` 插件钩子（用于清理资源及发送通知）。  
   - 清理缓存的 AIAgent 资源（关闭工具相关资源，停止内存提供器运行）。  
   - 删除该会话的缓存条目。  
   - 清除针对该会话的各类覆盖设置（如 `_session_model_overrides`、推理规则覆盖等）。  
   - 将 `expiry_finalized` 设为 `True` 并将相关数据持久化存储到 `sessions.json` 和 `state.db` 中。  
   - 通过 `promote_to_session_reset()` 函数将该会话在 `state.db` 中的状态标记为 `end_reason='session_reset'` —— 该操作有条件限制：仅那些处于活跃状态或因可恢复的意外原因（如 `agent_close`、`ws_orphan_reap`）而结束的会话才会被标记，因此由明确边界条件触发的会话（如 `compression`、`session_switch` 等）不会被覆盖。这样即可永久记录会话重置情况，防止旧路由恢复机制利用完整历史记录重新启动已过期的会话（参见编号 #61220、#61993、#63539）。

2. **清理闲置的缓存代理** —— 调用 `_sweep_idle_cached_agents()` 函数，移除那些已闲置超过 `_AGENT_CACHE_IDLE_TTL_SECS`（3600 秒/1 小时）的代理，无论其会话重置策略如何。此举可避免在存在长期运行会话的网关中内存持续增长。

3. **删除过期的会话条目** —— 根据 `config.session_store_max_age_days` 的设置，每小时调用 `session_store.prune_old_entries()` 函数删除过期条目，防止 `sessions.json` 文件体积无限增大。

### 故障处理机制

- 每个会话的重试次数：每次失败的处理操作最多连续重试 3 次。  
- 若连续 3 次尝试均失败，则强制将该会话标记为 `expiry_finalized=True`，以避免无限循环的重试。

---

## 11. 代理缓存

网关会维护一个基于 `session_key` 的 LRU 缓存，用于存储 `AIAgent` 实例，从而在多轮对话之间保持提示语的缓存效果。

### 缓存属性

- **最大容量**：128 个条目（由 `_AGENT_CACHE_MAX_SIZE` 控制）。  
- **淘汰策略**：最近最少使用（通过 `OrderedDict` 实现 LRU 机制）。  
- **闲置超时时间**：3600 秒（1 小时），由 `_session_expiry_watcher` 负责监控。  
- **线程安全锁**：使用 `_agent_cache_lock` 确保多线程环境下的操作安全。

### 缓存生命周期

```
Message arrives
    │
    ▼
get_or_create_session()  →  session_key obtained
    │
    ▼
Lookup _agent_cache[session_key]
    │
    ├── Hit → move_to_end(), reuse AIAgent (preserves prompt cache)
    │
    └── Miss → create new AIAgent, store in cache
                (if at capacity, popitem(last=False) evicts LRU entry)
    │
    ▼
run_conversation()  →  agent processes message
    │
    ▼
Session expiry watcher evicts agent when session finalizes
```

### 清理流程

当会话过期时：
1. `_cleanup_agent_resources(agent)` —— 关闭内存提供器，释放工具资源。
2. `_evict_cached_agent(key)` —— 从 `_agent_cache` 中移除该会话，以便对智能体进行垃圾回收。

---

## 附录：关键配置项

| 配置键 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `group_sessions_per_user` | `bool` | `true` | 按用户隔离群组/频道会话 |
| `thread_sessions_per_user` | `bool` | `false` | 按用户隔离线程会话 |
| `session_store_max_age_days` | `int` | `0` | 删除超过 N 天的会话（0 表示禁用） |
| `agent.gateway_auto_continue_freshness` | `int` | `3600` | 恢复会话的有效期时长（单位：秒） |
| `agent.gateway_timeout` | `int` | `1800` | 智能体响应超时时间（默认为 30 分钟） |

### 重置策略（在 config.yaml 中按平台/类型设置）

```yaml
session_reset:
  mode: both            # none | idle | daily | both
  at_hour: 4            # daily reset hour (local time)
  idle_minutes: 1440    # idle timeout (24h)
  notify: true          # notify user on auto-reset
```

针对特定平台的覆盖设置，可在 `platforms.<name>.session_reset` 下进行配置。
