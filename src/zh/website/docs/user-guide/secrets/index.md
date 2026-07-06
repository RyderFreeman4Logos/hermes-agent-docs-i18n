# 密钥管理

Hermes可在进程启动时从外部密钥管理系统中获取API密钥，而无需将其存储在`~/.hermes/.env`文件中。密钥管理系统的启动令牌存储在`.env`文件中；其他所有提供商的密钥（如OpenAI、Anthropic、OpenRouter等）则可保留在该管理系统中，并由系统统一进行轮换。

目前支持以下系统：

- [Bitwarden密钥管理系统](./bitwarden) — 通过`bws` CLI工具实现懒加载，免费套餐也可使用。
- [1Password](./onepassword) — 通过官方`op` CLI工具的`op://`格式引用；支持服务账户或桌面会话认证。

## 同时使用多个密钥源

您可以同时启用多个密钥源——例如同时使用团队共享的Bitwarden项目和个人加密箱插件。这些密钥源会根据环境变量以确定的优先级顺序进行组合：

1. **默认情况下，您的`.env`文件/Shell配置具有最高优先级。** 只有当某个密钥源设置了`override_existing: true`时，它才会替换已存在的值（Bitwarden默认该值为true，以便实现集中式轮换）。
2. **通过映射指定的密钥源优先于批量注入的密钥源。** 通过`env:`映射表明确将环境变量与引用项关联的密钥源，无论其出现顺序如何，都比那些隐式注入整个项目密钥的密钥源具有更高优先级。
3. **优先级由第一个出现的密钥源决定。** 在结构相同的情况下，可选的`secrets.sources`列表中的顺序（或注册顺序）将决定优先级。对于已被其他密钥源占用的变量，后续的引用将被忽略——系统会发出启动警告，而不会默默跳过。

`override_existing`机制确保某个密钥源无法覆盖另一个密钥源已占用的变量，同时任何密钥源也都无法覆盖其他密钥源的启动令牌（例如`BWS_ACCESS_TOKEN`）。

```yaml
secrets:
  sources: [bitwarden]     # optional explicit ordering
  bitwarden:
    enabled: true
    project_id: "..."
```

每个由数据源注入的凭证都会标注其来源信息——在设置流程以及“Hermes Model”中，检测到的密钥旁会显示“(来自 Bitwarden)”的提示，这样你就能随时了解该值的来源。

## 自定义后端添加方式

第三方密钥管理工具以独立插件的形式提供，而非作为核心组件。此类后端需继承 `agent.secret_sources.base.SecretSource` 类（必须实现一个方法：`fetch(cfg, home_path) -> FetchResult`），并在插件的 `register(ctx)` 方法中通过 `ctx.register_secret_source(MySource())` 进行注册。调度器负责处理优先级排序、冲突解决、超时控制以及数据来源追踪——你的数据源仅负责数据获取工作。相关规范要求：`fetch()` 方法不得抛出异常，也不得弹出提示，且必须在规定的超时时间内返回结果；请参照 `tests/secret_sources/conformance.py` 中的合规性测试套件来验证你的实现是否符合标准。

默认提供的插件集是封闭式的（与内存提供器的策略一致）：Bitwarden 和 1Password 直接内置在系统中。其余工具，如 Infisical、Proton Pass、HashiCorp Vault、AWS Secrets Manager 以及操作系统自带的密钥存储功能，都需放在插件仓库中；你可以在 Nous Research 的 Discord 频道（`#plugins-skills-and-skins`）里分享这些插件。
