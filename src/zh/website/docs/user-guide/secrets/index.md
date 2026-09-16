# 密钥管理

Hermes可在进程启动时从外部密钥管理系统中获取API密钥，而无需将其存储在`~/.hermes/.env`文件中。密钥管理系统的启动令牌存储在`.env`文件中；其他所有提供商的密钥（如OpenAI、Anthropic、OpenRouter等）则可保留在管理系统中，并由系统统一进行轮换。

支持的密钥管理系统包括：

- [Bitwarden密钥管理器](./bitwarden) — 通过`bws` CLI工具实现懒加载，免费套餐也可使用。
- [1Password](./onepassword) — 通过官方的`op` CLI工具以`op://`格式引用密钥；支持服务账户或桌面会话认证。
- [命令辅助工具](./command) — 通过用户自定义的辅助工具调用任何CLI密码管理器（如`keepassxc-cli`、`secret-tool`、`pass`或自定义脚本），该工具会输出`KEY=VALUE`格式的密钥信息。

## 同时使用多个密钥源

您可以同时启用多个密钥源——例如同时使用团队共享的Bitwarden项目和个人密码管理插件。这些密钥源会根据环境变量按既定的优先级顺序进行组合。

1. **默认情况下，您的 `.env` 文件/Shell 环境优先。** 只有当某个数据源设置了 `override_existing: true` 时，它才能替换已存在的值（Bitwarden 默认该值为 true，以便实现集中式密钥轮换）。
2. **映射型数据源优于批量型数据源。** 通过显式将环境变量绑定到引用项（即 `env:` 映射）的形式构成的数据源，无论其出现顺序如何，都比那些隐式注入整个项目级机密信息的数据源更具优先级。
3. **第一个被加载的数据源获胜。** 在结构相同的情况下，可选的 `secrets.sources` 列表中的顺序（或注册顺序）将决定优先级。对于已被其他数据源占用的变量，后续的请求将会被跳过，并会发出启动警告，而绝不会悄无声息地忽略。

`override_existing` 机制确保任何数据源都无法覆盖另一个数据源已占用的变量，同时也没有任何数据源能够覆盖其他数据源的启动令牌（例如 `BWS_ACCESS_TOKEN`）。

```yaml
secrets:
  sources: [bitwarden]     # optional explicit ordering
  bitwarden:
    enabled: true
    project_id: "..."
```

每个由数据源注入的凭证都会标注其来源——在设置流程以及“Hermes Model”中，检测到的密钥旁会显示“(来自 Bitwarden)”的字样，这样您就能随时了解该值的来源。

## 配置文件与共享保险库

有两个位于调度器层面的参数，可确保单个共享保险库在多个[配置文件](../profiles)之间依然安全：

- **`secrets.preserve_existing`** — 一个环境变量名称列表，列表中的变量其现有的 `.env`/Shell 值将始终优先生效，即便对应的数据源设置了 `override_existing: true` 也是如此。此参数适用于那些在各个配置文件中需保持不同的平台密钥（例如 `FEISHU_APP_SECRET`），而其他所有密钥则由中心统一管理并定期轮换：

  ```yaml
  secrets:
    preserve_existing: [FEISHU_APP_SECRET, TELEGRAM_BOT_TOKEN]
  ```

- **配置文件别名功能**（默认启用，如需禁用可设置 `secrets.profile_alias: false`）——当 Hermes 在指定配置文件下运行时，名为 `FOO_<PROFILE>` 的保险库密钥（仅支持凭证类后缀：`*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_KEY`、`*_PASSWORD`）也会被转换为标准的 `FOO` 格式。若将 `TELEGRAM_BOT_TOKEN_MILLA` 存储在共享项目中，那么使用 `milla` 配置文件的自定义适配器就会自动读取固定的名称 `TELEGRAM_BOT_TOKEN` 并获取正确的值。直接以标准名称提供的密钥始终优先于别名形式。

上述规则适用于所有数据源——无论是内置的还是插件式的——因为它们都运行在调度器中，而非后端服务中。

## 自定义后端添加方式

第三方密钥管理工具通常以独立插件的形式提供，而非作为核心代码库的一部分。自定义后端需继承 `agent.secret_sources.base.SecretSource` 类（必须实现一个方法：`fetch(cfg, home_path) -> FetchResult`），并通过插件中的 `register(ctx)` 方法调用 `ctx.register_secret_source(MySource())` 进行注册。调度器负责决定优先级、处理冲突、设置超时时间以及追踪数据来源——而自定义数据源仅负责执行数据获取操作。关于合约规则、子进程安全辅助工具及合规性检查套件的完整指南，请参阅：[构建密钥源插件](/developer-guide/secret-source-plugin)。

该预集成套件被刻意设置为封闭式结构（遵循与内存型密钥提供程序相同的策略）：Bitwarden和1Password直接内置在系统中。其余的方案——如Infisical、Proton Pass、HashiCorp Vault、AWS Secrets Manager以及操作系统自带的密钥存储功能——均需存放在插件仓库中；您可以在Nous Research的Discord频道（`#plugins-skills-and-skins`）中分享这些插件。
