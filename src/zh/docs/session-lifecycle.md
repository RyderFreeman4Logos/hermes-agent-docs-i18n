# 会话生命周期

> **目标受众：** 网关开发人员与维护人员  
> **相关源文件：** `gateway/session.py`（约1200行代码及相关的`session_*.py`文件）、`gateway/run.py`（约5500行的前端接口代码及相关的`run_*.py`处理阶段文件）、`gateway/config.py`  
> **最后更新时间：** 2026-06-16  

## 概述

**会话**指的是智能体与消息平台上的一个或多个用户之间持续的对话。会话生命周期决定了对话何时会被保留、何时重置、如何在网关重启后依然保持状态，以及在执行并发操作时消息该如何排队处理。

会话系统主要存在于以下两个模块中：

- `gateway/session.py` — 数据模型（`SessionSource`、`SessionEntry`、`SessionContext`）、密钥生成函数（`build_session_key`）以及主存储结构（`SessionStore`）。  
- `gateway/run.py` — 网关运行器（`GatewayRunner`）作为前端接口，负责将会话整合到消息处理流程中；各处理阶段则分布在`run_*.py`文件中，包括会话维护（`run_watchers.py`）、智能体缓存（`run_agent_cache.py`）、重启恢复（`session_recovery.py`）以及消息排队（`run_busy.py`）。

---

## 1. SessionSource — 消息来源描述符

`SessionSource`是一种用于记录*消息来源*的固定结构。它会被附加到每一个传入的`MessageEvent`上，用于实现消息路由、隔离处理以及上下文注入等功能。

### 字段

| Field | Type | Default | Description |
|---|---|---|---|
| `platform` | `Platform` | *(required)* | Enum identifying the messaging platform (telegram, discord, slack, signal, whatsapp, matrix, local, etc.). |
| `chat_id` | `str` | *(required)* | Platform-level chat/group/channel identifier. Routed through the adapter's `chat_id_key` transform. |
| `chat_name` | `Optional[str]` | `None` | Human-readable name of the chat or group. |
| `chat_type` | `str` | `"dm"` | One of `"dm"`, `"group"`, `"channel"`, `"thread"`. Controls session key generation and isolation. |
| `user_id` | `Optional[str]` | `None` | Platform-specific user identifier. Used for authorization and per-user session isolation. |
| `user_name` | `Optional[str]` | `None` | Display name of the message author. Injected into system prompt. |
| `thread_id` | `Optional[str]` | `None` | Forum topic / Discord thread / Slack thread identifier. Differentiates threaded conversations. |
| `chat_topic` | `Optional[str]` | `None` | Channel topic or description (Discord channel topic, Slack channel purpose). |
| `user_id_alt` | `Optional[str]` | `None` | Platform-specific stable alternative ID (Signal UUID, Feishu union_id). Used when `user_id` is ephemeral. |
| `chat_id_alt` | `Optional[str]` | `None` | Signal group internal ID — maps a Signal group V2 identifier to its canonical form. |
| `is_bot` | `bool` | `False` | True when the message author is a bot or webhook (Discord bots). |
| `guild_id` | `Optional[str]` | `None` | Discord guild / Slack workspace / Matrix server scope identifier. |
| `parent_chat_id` | `Optional[str]` | `None` | Parent channel when `chat_id` refers to a thread. |
| `message_id` | `Optional[str]` | `None` | ID of the triggering message. Used for pin/reply/react operations and Discord ID injection. |
| `role_authorized` | `bool` | `False` | True when adapter granted access via a platform role (not individual user ID). |

### 主要方法

- **`description`**（属性类型：`str`）—— 供人类阅读的摘要，例如 `"与Alice私信"`、`"群组：我的群组，主题：12345"`。
- **`to_dict()` / `from_dict()`** —— 用于序列化与反序列化的操作，以便将数据持久保存到 `sessions.json` 中。

---

## 2. SessionEntry — 活动会话记录

`SessionEntry` 是存储在内存中的会话级元数据记录，并会被持久化到 `{sessions_dir}/sessions.json` 文件中。每个记录都将一个 `session_key` 对应到其当前的 `session_id`。

### 字段

| Field | Type | Default | Description |
|---|---|---|---|
| `session_key` | `str` | *(required)* | Deterministic key identifying the conversation lane (see §4). |
| `session_id` | `str` | *(required)* | Unique identifier for this specific conversation incarnation. Format: `YYYYMMDD_HHMMSS_<8hex>`. |
| `created_at` | `datetime` | *(required)* | When this session incarnation was created. |
| `updated_at` | `datetime` | *(required)* | Last activity timestamp used for resource housekeeping. |
| `origin` | `Optional[SessionSource]` | `None` | The source that created this session, used for delivery routing. |
| `display_name` | `Optional[str]` | `None` | Chat display name (sourced from `SessionSource.chat_name`). |
| `platform` | `Optional[Platform]` | `None` | Platform enum persisted for routing across restarts. |
| `chat_type` | `str` | `"dm"` | Chat type, also persisted for policy lookup. |
| `input_tokens` | `int` | `0` | Cumulative LLM input (prompt) tokens consumed. |
| `output_tokens` | `int` | `0` | Cumulative LLM output (completion) tokens consumed. |
| `cache_read_tokens` | `int` | `0` | Cumulative prompt cache read tokens. |
| `cache_write_tokens` | `int` | `0` | Cumulative prompt cache write tokens. |
| `total_tokens` | `int` | `0` | Total token count across all turns. |
| `estimated_cost_usd` | `float` | `0.0` | Estimated cumulative USD cost. |
| `cost_status` | `str` | `"unknown"` | Cost tracking status label. |
| `last_prompt_tokens` | `int` | `0` | Last API-reported prompt token count. Used for accurate compression pre-check. |

### 布尔标志（状态机）

SessionEntry 包含多个布尔标志，这些标志共同构成一个简单的状态机，用于控制下一次访问时会话的行为。

| 标志位 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `was_auto_reset` | `bool` | `False` | 当显式暂停导致会话被替换时设置。同时也会被保留以用于历史记录。 |
| `auto_reset_reason` | `Optional[str]` | `None` | 显式暂停时值为 `"suspended"`；旧记录中可能仍保留历史上的重置原因。 |
| `reset_had_activity` | `bool` | `False` | 被替换的会话之前是否有过活动。 |
| `is_fresh_reset` | `bool` | `False` | 通过显式的 `/new` 或 `/reset` 指令设置。在收到第一条消息时会触发主题/频道技能的重新注入。该标志与 `was_auto_reset` 相区分，以避免出现误导性的“会话已过期”提示。 |
| `expiry_finalized` | `bool` | `False` | 为恢复操作而保留的历史最终状态标记，不由定时器写入。 |
| `suspended` | `bool` | `False` | 强制清除信号。由 `/stop` 指令或连续多次重启失败导致的死循环升级触发。在下一次调用 `get_or_create_session()` 时，无论 `resume_pending` 的值如何，都会强制生成新的 `session_id`。 |
| `resume_pending` | `bool` | `False` | 软恢复标记。由 `suspend_recently_active()`（崩溃恢复）或资源耗尽超时触发。在下一次访问时，会保留现有的 `session_id`，使用户能够继续在相同的对话记录中进行交流。在完成下一次成功对话轮次后会被清除。 |
| `resume_reason` | `Optional[str]` | `None` | 标记为恢复的原因：`"restart_timeout"`、`"shutdown_timeout"`、`"restart_interrupted"`。 |
| `last_resume_marked_at` | `Optional[datetime]` | `None` | 上次标记为待恢复的时间戳。 |
### 状态转换逻辑（获取或创建会话）

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
3. 无触发条件 → 返回现有记录（仅更新 `updated_at` 时间戳）

---

## 3. SessionStore — 存储与操作

`SessionStore` 是主要的存储层。它通过内存字典 `_entries` 来管理会话数据，并将这些数据持久化到 `sessions.json` 文件中；而会话元数据及消息记录则由 SQLite 数据库（`SessionDB`）进行规范存储。

### 构造函数

```python
SessionStore(sessions_dir: Path, config: GatewayConfig, has_active_processes_fn=None)
```

- `sessions_dir` — 存放 `sessions.json` 文件的目录。
- `config` — 用于路由设置及系统维护配置的 `GatewayConfig` 实例。
- `has_active_processes_fn` — 可选的基于 `session_key` 的回调函数，用于检测正在运行的后台进程。包含活跃进程的会话不会被纳入路由入口裁剪范围。

### 操作（方法）

| Method | Description |
|---|---|
| `get_or_create_session(source, force_new=False)` | Core entry point. Returns existing or creates new `SessionEntry`. Evaluates explicit suspension and restart recovery state. Creates/ends SQLite records. |
| `update_session(session_key, last_prompt_tokens=None)` | Lightweight metadata update after an interaction. Bumps `updated_at`, optionally records `last_prompt_tokens`. |
| `reset_session(session_key, display_name=None)` | Explicit reset (from `/new` or `/reset`). Creates new `session_id`, sets `is_fresh_reset=True`. Ends old SQLite session, creates new one. |
| `switch_session(session_key, target_session_id)` | Switch to a different existing session ID (from `/resume`). Ends current SQLite session, reopens target. |
| `suspend_session(session_key)` | Mark session as `suspended=True` (from `/stop`). Forces auto-reset on next access. |
| `mark_resume_pending(session_key, reason)` | Mark session as `resume_pending=True` (from drain timeout). Preserves session_id on next access. Will NOT override `suspended=True`. |
| `clear_resume_pending(session_key)` | Clear `resume_pending` after a successful resumed turn. Called from gateway after `run_conversation()` returns. |
| `suspend_recently_active(max_age_seconds=120)` | Crash recovery: mark recently-active sessions as `resume_pending=True`. Skips already-pending and already-suspended entries. Called on startup after unclean shutdown. |
| `prune_old_entries(max_age_days)` | Drop entries older than `max_age_days` (based on `updated_at`). Skips `suspended` entries and sessions with active processes. |
| `list_sessions(active_minutes=None)` | Return all sessions, optionally filtered by recent activity. Sorted by `updated_at` descending. |
| `lookup_by_session_id(session_id)` | Find the active `SessionEntry` for a persisted session ID. |
| `has_any_sessions()` | Check if any sessions have ever been created (uses SQLite for history, not just in-memory dict). |
| `append_to_transcript(session_id, message, skip_db=False)` | Append a message to SQLite transcript. `skip_db=True` prevents duplicate writes when the agent already persisted. |
| `rewrite_transcript(session_id, messages)` | Full replacement of session transcript (used by `/retry`, `/undo`, `/compress`). |
| `load_transcript(session_id)` | Load all messages from a session's SQLite transcript. |
| `rewind_session(session_id, n=1)` | Back up `n` user turns via soft-delete (keeps audit trail). Returns `{rewound_count, turns_undone, target_text}`. |

### 内部辅助函数

- `_ensure_loaded()` / `_ensure_loaded_locked()` — 将 `sessions.json` 的内容加载到 `_entries` 字典中。
- `_save()` — 通过临时文件结合 `atomic_replace` 方法，对 `sessions.json` 进行原子级写入。
- `_generate_session_key(source)` — 根据配置参数调用 `build_session_key()` 函数。

### 存储结构

```
{sessions_dir}/
  sessions.json          # In-memory _entries dict, persisted as JSON
                           Maps session_key → SessionEntry (metadata only)
  {session_id}.jsonl     # (Legacy, removed in spec 002)
```

默认的会话转录存储机制为通过 `SessionDB`（来自 `hermes_state`）实现的 SQLite 数据库。`sessions.json` 文件用于保存 `session_key → session_id` 的映射关系以及相关元数据（如标志位、时间戳、令牌计数等）。若无法使用 SQLite，系统会回退至 JSONL 格式进行存储，但这属于降级方案。

---

## 4. SessionKey 生成规则

SessionKey 是用于标识特定对话通道的确定性字符串，它由 `build_session_key(source, group_sessions_per_user, thread_sessions_per_user)` 函数生成。

### 键格式

```
agent:main:{platform}:{chat_type}[:{chat_id}][:{thread_id}][:{participant_id}]
```

### 私信规则

| 使用场景 | 键值 |
|---|---|
| 指定 chat_id 的私信 | `agent:main:telegram:dm:12345` |
| 指定 chat_id 及对话线程的私信 | `agent:main:telegram:dm:12345:thread_678` |
| 未指定 chat_id、仅指定参与者 ID 的私信 | `agent:main:signal:dm:user_abc` |
| 既未指定 chat_id 也未指定参与者 ID 的私信 | `agent:main:telegram:dm` |
| WhatsApp 私信（标准化格式） | `agent:main:whatsapp:dm:{canonical_number}` |

- 只要存在 `chat_id`，即可将每段私人对话独立区分开。
- `thread_id` 用于进一步区分同一私信对话中的不同线程。
- 若未提供 `chat_id`，系统会自动使用 `user_id_alt` 或 `user_id` 作为参与者 ID。
- 若完全不指定任何标识符，该平台上的所有私信将被视为同一个共享会话。

### 群组/频道规则

| 使用场景 | 键值 |
|---|---|
| 普通群聊 | `agent:main:telegram:group:-10012345` |
| 需按用户隔离的群聊 | `agent:main:telegram:group:-10012345:user_abc` |
| 群组内的共享对话线程 | `agent:main:discord:group:12345:thread_678` |
| 群组内的用户专属对话线程 | `agent:main:discord:group:12345:thread_678:user_abc` |
| 频道 | `agent:main:slack:channel:C12345` |
| WhatsApp 群组（标准化格式） | `agent:main:whatsapp:group:{canonical_id}:{participant}` |

- `chat_id` 用于标识父群组/频道。  
- `thread_id` 用于区分该父群组内的不同讨论线程。  
- **用户级隔离**（需添加 `participant_id`）由以下参数控制：  
  - `group_sessions_per_user`（默认值为 `True`）——群组/频道会话为独立隔离状态。  
  - `thread_sessions_per_user`（默认值为 `False`）——默认情况下各讨论线程**共享**同一个会话  
   （Telegram 论坛主题、Discord 线程以及 Slack 线程均采用此机制，即每个线程共享一个会话）。  
- `participant_id` 的取值优先级为 `user_id_alt`，其次为 `user_id`。  
- WhatsApp 的标识符会经过标准化处理，以应对 JID/LID 别名形式的变更。  

### 特殊情况：WhatsApp

WhatsApp 电话号码会通过 `canonical_whatsapp_identifier()` 函数进行处理，该函数会移除 `@s.whatsapp.net` 后缀，并将其转换为 E.164 格式。这样一来，即便桥接服务返回同一电话号码的不同别名形式，也能避免会话碎片化问题。  

---

## 5. 多用户隔离策略

多用户隔离机制决定了同一聊天中的多个用户是共享同一个对话会话，还是各自拥有独立的私人会话。  

### 决策逻辑（`is_shared_multi_user_session`）

```python
def is_shared_multi_user_session(source, *, group_sessions_per_user, thread_sessions_per_user):
    if source.chat_type == "dm":
        return False  # DMs are always private
    if source.thread_id:
        return not thread_sessions_per_user  # Threads: shared unless per-user
    return not group_sessions_per_user       # Groups: isolated unless shared
```

### 摘要

| 聊天类型 | 默认值 | 配置控制 |
|---|---|---|
| 私信 | 私有（绝不共享） | 无 |
| 群组/频道 | 每用户独立会话 | `group_sessions_per_user`（默认值为 True） |
| 主题讨论区（论坛、Discord） | 共享（所有参与者可见相同上下文） | `thread_sessions_per_user`（默认值为 False） |

### 对系统提示语的影响

当 `shared_multi_user_session=True` 时，系统提示语将不再包含固定用户名，而是显示为：*“多用户 {主题讨论区|会话} —— 消息前会标注[发送者姓名]。允许多名用户参与。”* 在运行时，网关会在每条用户消息前添加对应的发送者姓名，从而保持提示语的缓存效果（系统提示语不会在每轮对话中发生变化）。

---

## 6. 显式对话边界

无论是否活跃或经过多少时间，对话都不会自动切换。使用 `/new` 和 `/reset` 命令可设置显式边界；上下文压缩机制仍可用于管理较长的对话历史记录。旧的计时器配置将被忽略。现有的 `SessionResetPolicy` 数据类型仅用于兼容性考虑，而非运行时策略。

即使主动暂停对话，下一次收到新消息时也会形成新的边界。恢复对话时会优先遵循显式设置的边界以及历史上的已确定边界，而不会重新开启旧边界。仅基于资源限制的会话移除以及 WebSocket 孤儿节点清理操作，均允许对话后续继续进行。

---

## 7. 重启恢复流程

重启恢复系统可确保在网关重启、崩溃或超时断开等情况下，正在进行的对话能够得以保留。该机制正是为解决问题 #7536 而设计的。

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

当网关启动时，若不存在`.clean_shutdown`标记（表明系统发生崩溃或意外退出），则会调用此函数。对于过去120秒内有过更新的会话，将会执行以下操作：

- 将`resume_pending`设置为`True`，`resume_reason`设为“restart_interrupted”，`last_resume_marked_at`设为当前时间。
- 跳过那些已标记为`resume_pending=True`的会话（避免重复标记）。
- 跳过那些明确被标记为`suspended=True`的会话（此类会话应保持已暂停状态）。

### 死循环检测（`_suspend_stuck_loop_sessions`）

该功能通过JSON文件`{HERMES_HOME}/restart_counts.json`来统计连续重启的次数。如果某个会话在3次及以上连续重启中仍保持活跃状态，系统会自动将其暂停，从而为用户提供全新的会话环境。

### 清理超时标记

在平滑关闭/重启过程中，清理系统会对那些在清理超时发生时正处于处理中的会话调用`mark_resume_pending()`函数。标记原因包括：

- `"restart_timeout"` — 重启清理期间被终止
- `"shutdown_timeout"` — 关闭清理期间被终止
- `"restart_interrupted"` — 系统崩溃后的恢复（由`suspend_recently_active`功能触发）

以上三种原因均被记录在 `_AUTO_RESUME_REASONS` 中，符合条件的会话可在系统启动时自动恢复。

### 下次访问时自动恢复

当`get_or_create_session()`函数检测到某个会话的`resume_pending`值为`True`时：

1. 它会直接返回现有的记录，而不会创建新的 `session_id`。
2. 现有的对话记录会被完整加载。
3. 此处不会清除标记——该标记会一直保留，直到下一次成功的轮次处理完成（即 `run_conversation()` 返回实际响应后，网关会调用 `clear_resume_pending()`）。
4. 如果再次中断正在恢复的轮次，`resume_pending` 标志仍会保持启用状态，下次重启时会自动重试。死循环计数器用于处理终端升级机制（尝试3次后进入暂停状态）。

### 清洁关闭标记（`.clean_shutdown`）

该标记在平滑关闭时写入。下次启动时：

- 若存在该标记：则完全跳过 `suspend_recently_active()` 操作。因为活跃的智能体早已被释放，所以不会有任何会话陷入停滞状态。
- 随后删除该标记。

这样可以避免在执行 `hermes update`、`hermes gateway restart` 或 `/restart` 操作后出现不必要的自动重启。

---

## 8. 消息队列流程

消息队列系统用于处理两种场景：

1. **中断后的后续消息**——当智能体正在处理消息时用户又发送了多条消息，这些后续消息会被作为单槽待处理消息放入队列。
2. **`/queue` FIFO模式**——显式的 `/queue` 命令必须依次独立触发完整的智能体处理轮次，不得合并处理。

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

在资源槽被占用后于数据排出端调用此函数。若存在溢出项：

- 当 `pending_event` 为 `None`（即资源槽为空）时，将溢出项的首项作为新事件返回。
- 当 `pending_event` 存在时，将该溢出项的首项暂存于资源槽中，以备下一次递归处理。
- 若没有可用的适配器，则将该项重新放入 `_queued_events` 中（不可直接丢弃）。

### 队列深度

`_queue_depth(session_key, adapter)` 函数的返回值为 `len(overflow) + (1 若资源槽被占用，否则为 0)`。

### 清空操作

通过 `/new` 和 `/reset` 命令（经由 `_handle_reset_command` 处理），可清空某个会话的队列中的事件。

### FIFO 原则

每次调用 `/queue` 都会按照 FIFO 顺序触发一次完整的智能体处理流程，且不会发生数据合并。单资源槽的 `_pending_messages` 与溢出项存储区 `_queued_events` 的设计，可确保在当前处理流程进行中重复发送数据时，不会导致处理顺序混乱。

---

## 9. 会话上下文注入

`SessionContext` 是由 `SessionSource` 和 `GatewayConfig` 组合生成的，随后会被注入到智能体的系统提示语中。它向智能体提供以下信息：

- 当前消息的来源
- 已连接的平台列表
- 智能体可将调度任务的结果发送至何处
- 当前是否为多用户共享会话

### 构建过程（`build_session_context`）

```python
def build_session_context(source, config, session_entry=None) -> SessionContext
```

1. 从配置文件中收集已连接的平台信息。  
2. 为每个平台收集其主频道列表。  
3. 通过 `is_shared_multi_user_session()` 函数判断是否使用 `shared_multi_user_session`。  
4. 若提供了 `session_entry`，则会附加会话元数据（键、ID及时间戳）。  

### 个人身份信息遮蔽（`build_session_context_prompt`）  

在将动态系统提示内容（`## Current Session Context`）发送给大语言模型之前，可选择性对其进行个人身份信息遮蔽处理：  
- 用户 ID → `user_<12位十六进制>`（前缀为 SHA-256 值）  
- 聊天 ID → `<平台名>:<12位十六进制>` 或仅 `<12位十六进制>`  
- 不进行遮蔽的平台：Discord（因需原始 ID 以实现 `@mentions` 功能），以及所有未被标记为 `pii_safe` 的插件注册平台。  

此类遮蔽操作仅适用于系统提示文本；路由信息、会话密钥及适配器操作始终使用原始数据。  

---

## 10. 后台维护机制  

`_session_housekeeping_watcher` 会定期清理闲置的缓存代理，当内存压力增大时删除相应的缓存条目，并每小时修剪过时的路由记录。该机制绝不会因用户无活动或时间原因而终止对话记录。

在软释放客户端之前，TTL、LRU以及基于资源压力的淘汰机制会先将实时对话记录写入内存提供者中。当前正在处理的对话仍会受到保护；终端、浏览器及后台进程的资源也不会因软释放而丢失。路由条目的修剪功能会保留标准化的SQLite格式对话记录，而正在运行的进程则会保护自身的路由条目免于被修剪。历史上的`expiry_finalized`标记虽仍可作为恢复边界，但不会再由定时器监控器进行写入。

---

## 11. Agent缓存

网关会按`session_key`为键维护一个LRU缓存的`AIAgent`实例，以此在多轮对话之间保留提示词缓存。

### 缓存属性

- **最大容量**：128个条目（`agent.agent_cache.max_size`，默认值为 `_AGENT_CACHE_MAX_SIZE`）。
- **淘汰策略**：最近最少使用（通过`OrderedDict`实现LRU机制）。
- **空闲TTL**：3600秒（1小时）——由`agent.agent_cache.idle_ttl_secs`设定，并由`_session_housekeeping_watcher`负责监控。
- **内存预算**：`agent.agent_cache.memory_high_mb`（默认值为`auto`）——详情见下文。
- **锁机制**：为确保线程安全，会使用`_agent_cache_lock`（基于线程锁定）。

### 由内存压力触发的淘汰

缓存的Agent实例会固定存储`_session_messages`，即包含工具输出在内的完整实时对话记录——在进行了100次以上工具调用的对话中，其大小可达数十MB。然而，无论是容量上限还是空闲TTL机制都不会对此加以限制：负责处理大量对话的网关会保留所有处于活跃状态的对话记录（在TTL时间内有过操作的Agent实例不会被纳入空闲清理范围），因此进程的RSS值会持续上升，直到cgroup开始限流，且SIGTERM信号也无法在systemd的停止超时时间范围内完成数据清除（参见#80764）。

`_sweep_agent_cache_under_pressure()` 是控制这一过程的“阀门”。每个监控周期中，它都会将进程的匿名 RSS 值与 `memory_high_mb` 的阈值进行比较；一旦超出限制，它就会通过限流机制所使用的相同软路径（`_commit_then_release_soft`）来移除 LRU 级别的代理，随后运行 `malloc_trim` 函数，确保释放出的内存空间真正归还给操作系统。被移除的会话会在下一个周期从持久化的会话数据中重新生成对话记录。

有三类会话是绝不会被移除的：
- 当前正处于处理中的会话（其客户端和沙箱仍在使用中）；
- 属于 `protect_recent` 保护范围的最近使用的会话（这类会话的提示词缓存价值最高）；
- 实时对话记录尚未完全写入磁盘的会话——函数 `transcript_persistence_caught_up()` 会通过比较 `_last_flushed_db_idx` 和 `len(_session_messages)` 的值来判断，这一判断逻辑与 FTS 写入错误防护机制相同，后者正是通过该逻辑在实时记录与延迟生成的记录之间存在差异时优先保留实时记录。

`memory_high_mb: auto` 模式会根据网关所运行的 cgroup 限制来自动确定内存阈值（依次为 `memory.high`、`memory.max` 以及 cgroup v1 的设置），若未设置上限则直接使用总内存容量。用户可以指定具体数值来固定阈值，或设置为 `0`/`off` 以完全禁用该功能。相关辅助函数位于 `gateway/agent_cache_pressure.py` 文件中。

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
Housekeeping soft-releases idle agents without ending transcripts
```

### 清理流程

资源驱逐机制会先移除缓存中的智能体并释放内存，之后才对客户端进行软释放。而完整执行 `_cleanup_agent_resources(agent)` 清理操作，则会在对话真正结束或系统关闭时使用。

---

## 附录：关键配置参数

| 配置键 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `group_sessions_per_user` | `bool` | `true` | 是否为每位用户隔离群组/频道会话 |
| `thread_sessions_per_user` | `bool` | `false` | 是否为每位用户隔离线程会话 |
| `session_store_max_age_days` | `int` | `0` | 删除超过 N 天的会话（0 表示禁用） |
| `agent.gateway_auto_continue_freshness` | `int` | `3600` | 恢复会话的有效时长（秒） |
| `agent.gateway_timeout` | `int` | `1800` | 智能体轮次超时时间（默认为 30 分钟） |
| `agent.agent_cache.max_size` | `int` | `128` | 缓存的 AIAgents 的 LRU 存储上限 |
| `agent.agent_cache.idle_ttl_secs` | `int` | `3600` | 长时间处于空闲状态的智能体将被移除的时间阈值 |
| `agent.agent_cache.memory_high_mb` | `int`/`str` | `auto` | 当匿名 RSS 资源使用量超过此阈值时，将优先移除 LRU 状态的转录内容 |
| `agent.agent_cache.max_evictions_per_pass` | `int` | `16` | 每次清理操作最多可移除的会话数量上限 |
| `agent.agent_cache.protect_recent` | `int` | `8` | 清理操作不会触及的 MRU 状态会话数量 |

## 状态数据库与 FTS 恢复机制

标准对话记录存储在 `sessions` 和 `messages` 表中。FTS5 表及其同步触发器属于派生索引，即便将其分离或重建，也不会导致标准消息丢失。有关受限实时故障模式及具体的修复流程，请参阅 [`docs/state-db-recovery.md`](state-db-recovery.md)。

### 对话生命周期

系统不支持闲置时间设置或每日自动重置功能。通过显式的 `/new` 和 `/reset` 指令、数据压缩操作、暂停功能以及崩溃恢复机制，各自承担着独立的生命周期管理职责。
