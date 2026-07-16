# 基于配置文件的入站消息路由

> **目标受众：** 网关操作员及贡献者  
> **相关源文件：** `gateway/profile_routing.py`、`gateway/run.py`（`_profile_name_for_source`）、`gateway/platforms/base.py`（`build_source`）、`gateway/config.py`  
> **关联文档：** [会话生命周期](session-lifecycle.md)、`docs/design/profile-builder.md`

## 概述

默认情况下，单个网关实例运行时会使用一个配置文件（包含内存设置、角色设定及工具信息）。**基于配置文件的路由功能**允许同一个网关实例同时处理**多个独立的配置文件**，并根据消息的来源——即平台、服务器（`guild_id`）、频道（`chat_id`）和/或聊天线程（`thread_id`）——来决定由哪个配置文件负责处理该入站消息。

这相当于入站消息场景下的多路复用技术：无需运行多个网关，只需运行一个网关，即可根据不同的社区、频道或聊天线程将消息路由到对应的专用配置文件。每个配置文件都拥有完全独立的运行状态（包括`MEMORY.md`、`USER.md`、`SOUL.md`记录以及会话和工具信息）。

该路由功能具有**平台通用性**：不仅适用于Discord，还支持Telegram、飞书、Slack以及所有其他适配器。

## 配置路由规则

路由规则存储在`config.yaml`文件中的`profile_routes`字段内。既支持顶层配置，也支持嵌套的`gateway.profile_routes`结构（后者正是`hermes config set gateway.profile_routes ...`命令所写入的格式）。

```yaml
profile_routes:
  # Route an entire Discord server (guild) to one profile.
  - name: server-default
    platform: discord
    guild_id: "1234567890"
    profile: server-profile

  # Override a specific channel within that server with a different profile.
  - name: support-channel
    platform: discord
    guild_id: "1234567890"
    chat_id: "9876543210"
    profile: support-profile

  # Pin a Telegram group to a profile (Telegram has no guild_id — chat_id only).
  - name: tg-group
    platform: telegram
    chat_id: "-1001234567890"
    profile: tg-profile

  # Route a single Discord thread.
  - name: standup-thread
    platform: discord
    guild_id: "1234567890"
    chat_id: "9876543210"
    thread_id: "1111111111"
    profile: standup
```

### 字段

| 字段 | 是否必填 | 描述 |
|---|---|---|
| `name` | 是 | 供人类阅读的路由标识符（用于日志中）。 |
| `platform` | 是 | 接入平台：`discord`、`telegram`、`feishu`、`slack` 等。 |
| `profile` | 是 | 目标配置文件名称（必须存在于 `~/.hermes/profiles/<name>` 下）。 |
| `guild_id` | 否 | 服务器/群组（Discord 使用）。 |
| `chat_id` | 否 | 频道/群组/私信的 ID。 |
| `thread_id` | 否 | 频道内的子话题 ID。 |
| `enabled` | 否 | 默认值为 `true`；如需禁用某条路由但不删除它，可将其设置为 `false`。 |

## 匹配规则

当**路由声明的所有筛选条件均满足**时，该路由才会与传入的消息匹配（采用逻辑与关系）。未设置的字段将被忽略。

- **`platform`** 必须与消息来源的平台完全一致。
- **`thread_id`**（如已设置）必须与消息来源的子话题 ID 相同。
- **`chat_id`**（如已设置）必须与消息来源的频道**或其父级频道**匹配——对于 Discord 的论坛/子话题，其所属频道即符合路由匹配条件（采用层级匹配机制）。
- **`guild_id`**（如已设置）必须与消息来源的群组相同。

> 若某条路由同时声明了 `guild_id` 和 `chat_id`，则这两个字段都必须匹配。仅满足频道匹配条件并不足以满足群组匹配要求——这是有意为之且经过测试的机制。

当有多条路由匹配时，**最具体**的那条路由将生效。具体性的权重是累加的：

| 筛选条件 | 权重 |
|---|---|
| `thread_id` | 8 |
| `chat_id` | 4 |
| `guild_id` | 2 |
| 仅平台信息 | 0 |

因此在同一服务器内，子话题路由（权重 8）的优先级高于频道路由（权重 4），再高于群组路由（权重 2）。如果没有路由匹配，消息将使用默认/活跃的配置文件。

## 运行时的工作原理

1. 一条传入的消息到达对应的平台适配器。
2. `BasePlatformAdapter.build_source` 会为该消息构建 `SessionSource` 对象。所有适配器都持有对正在运行的 `GatewayRunner` 的引用（在 `gateway/run.py` 中注入），因此它会通过 `_profile_name_for_source` 方法请求 `GatewayRunner` 确定目标配置文件。
3. `_profile_name_for_source` 会依次调用已配置的路由并通过 `match_profile_route` 进行匹配，然后将获胜路由对应的配置文件信息设置到 `source.profile` 中（若无匹配结果，则保持该字段未设置）。
4. 在后续处理中，`_resolve_profile_home_for_source` 会选定配置文件的默认目录（`source.profile` → 活跃配置文件 → 默认配置文件），并且会为每个配置文件创建独立的会话环境，从而使不同的路由社区拥有独立的内存空间和对话状态。

由于 **所有**适配器（在 `BasePlatformAdapter` 中声明）都注入了 `gateway_runner`，因此不仅仅是 Discord，其他平台也会经过这一处理流程。

## 与多配置文件机制的关系

`profile_routes` 功能的启用依赖于 `gateway.multiplex_profiles: true` 参数。多配置文件机制负责实现基于配置文件的运行时隔离（如独立的 `HERMES_HOME` 目录、密钥隔离以及以配置文件命名的会话密钥）；而路由机制则负责决定某个群组/频道/子话题应归属于哪个配置文件。如果关闭多配置文件机制，`profile_routes` 将完全被忽略，其行为与单配置文件网关完全一致。
