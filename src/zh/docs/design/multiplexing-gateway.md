# 多路复用网关

单个网关进程可服务于安装包中的所有配置文件。该功能为可选模式（`gateway.multiplex_profiles`，默认值为 `false`），且一旦关闭该选项，所有相关设置都会恢复原状。本文档基于 `agent/secret_scope.py` 中的“工作流 A”设计理念编写，详细说明了每个配置文件所隔离的内容、实现隔离的机制，以及那些有意保持进程级共享的内容。

## 概述

在不采用多路复用机制的情况下，单个网关进程仅能服务一个配置文件——包括其 `.env` 文件、会话、技能及平台适配器——而多配置文件安装则需为每个配置文件单独启动一个进程。多路复用机制将这种架构整合为单一进程：默认配置文件以及所有被启用的命名配置文件都将拥有独立的适配器、密钥、会话和定时任务，同时共享同一个事件循环、HTTP 监听器、进程锁及状态接口。

决定以下所有设计原则的核心约束是：**配置文件 A 绝不能感知配置文件 B 的状态**。密钥、主目录、会话及适配器通道均按配置文件独立隔离；那些目前尚无法实现隔离的功能要么被限制使用，要么会在本文档末尾作为已知限制进行说明。

## 模式标志位

- 配置项：`gateway.multiplex_profiles: true`（也可在顶层配置）。该值在`gateway/config.py`中被解析，优先级为环境变量 > 配置文件 > 默认值。
- 环境变量覆盖：`GATEWAY_MULTIPLEX_PROFILES`仅接受明确的真/假值；空白值或无法识别的值将返回“无覆盖”，因此空的部署密钥无法替代配置项中的开启设置。
- 在启动时，`GatewayRunner.__init__`会调用`agent.secret_scope.set_multiplex_active(...)`一次。`_MULTIPLEX_ACTIVE`是一个普通的模块级全局变量，而非上下文变量：它用于描述部署模式，而非每个任务的特定值。其唯一作用是为`get_secret()`中的故障关闭机制做好准备。

## 范围组合

在任何特定配置文件对应的代码执行之前，每个传入的事件都会先组合出两个基于上下文的范围：

```
platform event
   │
   ▼
profile_routes match ──► served-set check ──► SessionSource.profile stamped
   │                                           (gateway/profile_routing.py)
   ▼
_profile_runtime_scope(profile_home)           (gateway/run.py)
   ├── set_hermes_home_override(home)          config / state.db / skills /
   │                                           memory / sessions resolve here
   └── set_secret_scope(profile .env + secret sources)
   │                                           provider keys, platform tokens
   ▼
agent turn (worker thread via copy_context())
   │
   ▼
scope unwound in finally
```

`_profile_runtime_scope` 会包裹所有执行属于该配置文件的代码的环节：次级适配器的启动与重新连接、主平台事件处理程序、输入数据预处理、`/model` 请求及会话信息解析、后台任务，以及智能体自身的运行流程。配置重载会在默认配置文件的作用域内执行，从而确保全局网关设置（`#64674`）能够始终以一致的方式被加载。

这两个作用域均基于 `contextvars` 实现，因此会通过 `copy_context()` 机制传递到执行器工作线程中，并以确定性的方式被清理——绝不会有任何内容被写入 `os.environ` 中。

## 工作流 A：上下文本地密钥作用域

之所以需要 `agent/secret_scope.py`，是因为显而易见的实现方式——即将所有配置文件中的 `.env` 内容合并到 `os.environ` 中——会导致配置文件 A 中的密钥泄露到配置文件 B 的处理阶段，以及所有通过 `env=dict(os.environ)` 创建的子进程中。

- `build_profile_secret_scope(home)` 会将配置文件中的 `.env` 内容与已设置的密钥来源合并，同时跳过全局密钥。
- `set_secret_scope(mapping)` 为当前任务配置相应的密钥作用域。
- `get_secret(name)` 的解析顺序为：全局允许列表 → 当前激活的作用域 → 备用方案。其中备用方案起着关键作用：
  - 当多路复用功能**关闭**时，系统会读取 `os.environ`，因此单配置文件网关以及所有非网关调用方的行为都与之前完全一致；
  - 当多路复用功能**开启**但未设置任何作用域时，系统会**抛出 `UnscopedSecretError` 异常**，而不会悄悄读取进程环境变量。此时，未完成迁移的调用站点会在出错行直接报错，而不会泄露其他配置文件中的密钥值。
- 有一小部分允许列表项（如 `HERMES_HOME`、`HERMES_PROFILE`、代理设置、`API_SERVER_*` 监听器设置——但刻意排除了 `API_SERVER_KEY`）仍属于全局范围，因为这些项描述的是进程整体属性，而非特定配置文件的内容。

由于在多路复用模式下，每轮对话都会重新加载 `.env` 文件实际上并无实际作用，因此轮换后的凭证会在下一轮通过配置文件的作用域来加载，而绝不会通过 `os.environ` 加载。这一机制不仅适用于网关的重新加载功能，也体现在加载器层面：只要多路复用功能处于开启状态且已设置了配置文件路径覆盖（导入时和定时任务调用时都会触发该情况），`hermes_cli.env_loader.load_hermes_dotenv` 函数就会跳过对进程全局变量的读取，同时仍将配置文件中的外部密钥来源加载到其私有快照中（参见 #77562）。而无作用域启动时的加载方式则保持不变。

同一条作用域权威规则同样适用于路由转换所能到达的其他 `os.environ` 资源：当已安装特定作用域时（参见 `#84079`），配置文件 `config.yaml` 中的 `${VAR}` / `${env:VAR}` 引用会通过 `get_secret` 函数进行解析；而在该作用域下执行的 `.env` 文件写入操作（如通过 `/pair` 授权镜像进行的 `save_env_value` 操作）则只会更新已安装的作用域映射，而不会影响进程环境变量（参见 `#88441`）。

## HERMES_HOME 变量的覆盖机制

`hermes_constants.py` 中存储了由 `get_hermes_home()` 函数在查询 `HERMES_HOME` 环境变量之前所参考的、与当前上下文相关的覆盖值。所有通过该函数解析路径的内容——包括配置文件、`state.db` 数据库、智能体能力、内存数据、SOUL 系统、会话信息、看板任务、目标设置、插件发现功能以及 MCP 启动流程——都会自动遵循当前激活的配置文件设置。对于那些必须不受此覆盖机制影响的少数机器级资源，系统提供了 `get_process_hermes_home()` 函数。`hermes_home_key()` 函数则为每个独立作用域生成稳定的标识键。如果在预期需要应用覆盖值的情况下，配置文件相关的代码却在没有该覆盖值的情况下运行，系统会发出一次性警告（参见 `#18594`）。

## 入站路由机制

`gateway.profile_routes` 字典将 `(platform, guild_id, chat_id, thread_id)` 组合映射到特定的配置文件；匹配规则为“与所有条件同时满足”，且优先选择最具体的匹配项，对于线程而言还会进行父链聊天的匹配。路由处理仅在多路复用功能启用时才会执行，如果找到的匹配路由的目标不在服务范围内，该路由将被拒绝（相关事件会被丢弃，而不会被错误地传递）。完整的架构说明及匹配规则可参见 `docs/profile-routing.md` 文档。

## 选定配置文件的服务机制

`hermes_cli/profiles.py` 中的 `profiles_to_serve(multiplex, profile_allowlist)` 函数是决定多路复用器为哪些配置文件提供服务的唯一控制点：默认情况下会包含所有有效的配置文件目录，还可根据允许列表进行筛选。若允许列表格式错误，则会安全地回退为仅使用默认配置。所服务的配置文件集决定了适配器是否启动、定时任务（`#69377`）的运行、/p/<profile>/路径下的 HTTP 访问授权、路由匹配规则以及运行时状态展示方式。而被排除在外的配置文件虽仍会保持安装状态，但无法再运行其独立的网关。

## 每个配置文件的持久化机制

`SessionStore` 在初始化时不会绑定任何数据库连接（`#88532`）。数据库连接会在调用时根据当前生效的 HERMES_HOME 环境变量来确定——每个已解析的 `profiles/<name>/state.db` 文件对应一个缓存的连接实例——因此即便存储对象本身被共享，会话数据仍会存储在对应的配置文件所关联的存储中。不同的服务配置文件会分别创建独立的存储实例。

## 每个机器人的会话通道机制

会话键会根据配置文件进行命名空间隔离（默认为 `agent:main`，自定义配置文件则为 `agent:<name>`）。适配器会在配置阶段（即任何入站事件处理之前）绑定 `_owner_profile` 参数，因为适配器的请求处理会在 `SessionSource.profile` 被设置之前开始；而 `_session_key_profile` 则用于根据来源标识确定所属配置文件及对应的存储解析方式。文本/媒体数据的分批处理、活跃会话跟踪以及忙碌会话保护功能均按通道独立运作，因此即使两个机器人正在进行对话，它们的会话通道也是相互独立的。

## 控制平面

桌面端插件仅能通过 WS JSON-RPC 接口与网关通信，因此配置文件的枚举与相关操作都集中在 `tui_gateway/methods_profiles.py` 文件中，包括 `profiles.list`、`profiles.create`、`profiles.describe`、`profiles.configure`、`profiles.set_asset` 和 `profiles.get_asset` 等函数。这些操作的读写均在目标配置文件所定义的 HERMES_HOME 环境下进行。资产写入操作是原子的，并且受到类型和大小的限制。

## 故障模式

- 启动时崩溃：多路复用配置错误以及某个启用端口绑定功能的辅助配置文件出现问题（`MultiplexConfigError`、`SecondaryPortBindingConfigError`），因为只有一个共享的 HTTP 监听器由默认配置文件控制。
- 被跳过但不会导致崩溃：若存在单个配置错误的辅助适配器，系统会仅发出警告并跳过该适配器，而不会使整个多路复用功能失效。
- 强制关闭：在多路复用模式下调用未加作用域限制的 `get_secret()` 函数时会引发异常；针对未被支持配置文件的路由事件会被丢弃；未加作用域限制的 `/p/` 请求会进入默认配置文件的作用域（`#61276`），而非其他未定义的作用域。
- 回退机制：若外部 `cron.provider` 不支持多路复用功能，系统会发出警告并回退到内置的计时器功能。

## 已知限制

目前尚不存在按配置文件作用域划分的全进程全局状态：

| 维度 | 编写时的状态 |
| --- | --- |
| MCP发现与工具注册 | 全进程全局；最先构建代理的配置文件将获得发现优先权。各配置文件独立的MCP注册信息记录在`#67605`中。 |
| 终端/沙箱环境（`TERMINAL_*`） | 通过白名单实现全局控制；工具会从进程环境中读取该信息。 |
| 内置工具注册表 | 内置工具为全进程全局；通过`hermes_home_key()`按配置文件实现插件注册工具的独立管理。 |
| 提供者/能力注册表 | 采用相同的混合叠加模式（浏览器、图像生成、文本转语音、语音转文字、视频生成、网络搜索、机密信息源）。 |
| HTTP监听器、中继入口与进程锁 | 每个进程各有一个，由默认/活跃配置文件管理。仍会为每个配置文件写入`runtime_status.json`文件。 |

## 不涵盖的内容

Multiplexing机制仅用于隔离不同配置文件，不负责对最终用户进行身份验证或授权。配置文件是一种配置设置，而非具体人员：网关依赖其传输层和路由表来判断某个事件属于哪个配置文件。本文档不涉及配置文件层级之上的请求级身份识别及用户级授权机制。

## 相关内容

- `docs/profile-routing.md` — 入站路由架构与匹配规则。  
- `website/docs/user-guide/multi-profile-gateways.md` — 面向用户的指南，其中包括“每个配置文件对应一个网关”的独立方案。  
- `agent/secret_scope.py`、`hermes_constants.py`、`gateway/profile_routing.py`、`gateway/run.py`（包含`_profile_runtime_scope`）、`hermes_cli/profiles.py`（包含`profiles_to_serve`）、`gateway/session.py`、`tui_gateway/methods_profiles.py`。
