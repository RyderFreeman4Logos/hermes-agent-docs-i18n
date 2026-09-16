# 插件配置与状态桥接

**当前状态：** 通过 #64227 实现了配置及状态切片功能。

**初始设计者：** Topher Ross (@thebizfixer)，RFC 提案 #58542

**主要使用者：** kanban-advanced

## 范围

该功能模块新增了两种原生的 `PluginContext` 功能：

- 通过 `ctx.get_config()` 和 `ctx.set_config()` 实现带类型约束且受命名空间限制的配置设置；
- 通过 `ctx.state` 提供原子性、基于配置文件的运行时数据。

而原始 RFC 中涉及的配置架构注册、配置默认值设置以及 cron 接口等功能仍需后续单独实现。此外，本模块未新增任何核心模型工具。 

## 配置 API

```python
def register(ctx):
    endpoint = ctx.get_config("api_url", default="https://example.invalid")
    retries = ctx.get_config("retry.attempts", default=3)

    ctx.set_config("api_url", "https://api.example.com")
    ctx.set_config("retry.attempts", 5)
```

这些键是**相对于调用该插件的上下文而言的**。上述示例实现的是读取和写入操作：

```yaml
plugins:
  entries:
    <effective-plugin-id>:
      settings:
        api_url: https://api.example.com
        retry:
          attempts: 5
```

当存在时，`<effective-plugin-id>` 的值为 `manifest.key`，否则为 `manifest.name`。`settings` 是在 #64227/#67531 的议题讨论后确定的标准命名空间。为确保迁移安全，只有在不存在标准值时，读取操作才会回退到旧版的 `plugins.entries.<id>.config.*` 子树。写入操作始终针对 `settings`，不会重写或删除旧版本的配置值。

### 命名空间限制

该 API 不支持完整的配置路径。插件绝不能利用它来查看或修改任意的 Hermes 配置。

允许的格式：

```python
ctx.get_config("endpoint")
ctx.set_config("retry.policy", {"attempts": 3})
```

因 `ValueError` 异常及警告日志而被拒绝：

```python
ctx.get_config("security.approval_mode")
ctx.set_config("model.provider", "attacker-proxy")
ctx.set_config("plugins.entries.other.settings.token", "...")
ctx.set_config("../../security.approval_mode", "always_allow")
ctx.set_config(r"..\..\model.provider", "attacker-proxy")
```

目前并不存在全局的读取允许列表：`ctx.profile_name` 已经提供了 RFC 所要求的唯一少量主机相关信息。配置写入时会使用 Hermes 的基于配置文件的加载/保存机制以及原子化的 YAML 替换功能。在写入之前，桥接层会对现有的 YAML 文件进行验证，因此绝不会静默地替换格式错误的配置。所有操作都会基于当前有效的上下文级 `HERMES_HOME` 来执行，这样即便在多个配置文件同时启用时，也不会发生不同配置文件之间的数据交叉干扰。

## 持久化状态 API

建议将光标、去重集合及缓存等插件所管理的运行时数据存储在状态中，而不要将其放入用户自定义的配置文件中。

```python
def register(ctx):
    cursor = ctx.state.get("cursor", default={"page": 0})
    ctx.state.set("cursor", {"page": cursor["page"] + 1})
```

该前端接口在以下位置存储一个 JSON 对象：

```text
<HERMES_HOME>/plugin-data/<plugin-data-namespace>/state.json
```

便携式 Agent 插件会直接使用其原有的 `PLUGIN_DATA` 命名空间。原生插件与嵌套插件的标识符均采用相同的抗冲突、兼容 Windows 环境的命名空间算法。当插件需要查看自身的存储位置时，`ctx.state.data_dir` 用于获取对应目录，而 `ctx.state.path` 则用于获取 JSON 文件。

### 状态保障机制

- **配置隔离**：每次操作时，数据存储根路径都会根据当前上下文中的 Hermes 配置路径来确定。
- **原子性替换**：状态写入时会通过临时文件、`fsync` 操作以及 `os.replace` 函数来实现原子性更新。
- **并发安全**：通过锁文件机制确保多线程和进程之间的读写操作有序进行（POSIX 系统使用 `fcntl`，Windows 系统使用 `msvcrt`）。
- **大小限制**：每个插件序列化后的完整状态大小不得超过 10 MiB。若更新请求被拒绝，原有的文件将保持不变。
- **错误处理**：对于格式错误或非有效 JSON 数据，系统会进行报错处理，且绝不会覆盖此类文件。
- **类型要求**：所有状态值都必须是可序列化为 JSON 的类型。

状态键的长度在 1 到 128 个字符之间，可包含字母、数字、`_`、`-`、`.` 和 `:` 等字符。路径分隔符及 `..` 不被允许使用。

## 状态与配置的区别

| 数据类型 | API 接口 | 所有权归属 | 示例 |
|---|---|---|---|
| 对用户可见的行为设置 | `ctx.get_config` / `ctx.set_config` | 用户或插件在 `config.yaml` 中定义的设置 | 端点地址、超时时间、功能模式等 |
| 运行时状态管理 | `ctx.state.get` / `ctx.state.set` | 存储在 `plugin-data/` 目录下的插件数据 | 光标位置、缓存内容、去重标识等 |
这两种 API 均采用叠加式设计。那些本身已具备文件读写功能的现有插件可继续正常工作，但新插件应使用该桥接机制，以确保在 Profile 管理及 Windows 环境下的稳定性。

## 验证方案

通过真实的临时 Hermes-home 测试对实现功能进行全面验证，包括：
- fixture 插件的发现以及配置/状态数据的往返处理；
- 标准 `settings` 写入机制与旧版 `config` 读取机制的兼容性；
- 对直接全局访问、跨插件访问、POSIX 路径访问以及 Windows 路径访问行为的拦截；
- 并发写入设置时避免数据丢失的问题；
- 线程间及进程间的状态同步更新；
- 原子性配额限制机制的生效，以及异常状态/配置数据的保留；
- 环境 Profile 发生变化后的双 Profile 隔离功能；
- Unicode 字符及 Windows 风格路径值的处理。

## 相关内容
- [问题 #64227](https://github.com/NousResearch/hermes-agent/issues/64227)
- Topher Ross 提交的 [RFC PR #58542](https://github.com/NousResearch/hermes-agent/pull/58542)
- #67531 —— 独立插件设置命名空间的讨论
