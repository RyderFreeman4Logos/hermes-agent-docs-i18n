# 密钥管理

Hermes可在进程启动时从外部密钥管理系统中获取API密钥，而无需将其存储在`~/.hermes/.env`文件中。密钥管理系统的启动令牌存储在`.env`文件中；其他所有提供商的密钥（如OpenAI、Anthropic、OpenRouter等）则可保留在管理系统中，并由中央机构统一进行轮换。

支持的密钥管理系统包括：

- [Bitwarden Secrets Manager](./bitwarden) — 通过`bws` CLI工具实现懒加载，免费套餐也可使用。
- [1Password](./onepassword) — 通过官方的`op` CLI工具以`op://`格式引用密钥；支持服务账户或桌面会话认证。
- [Command helper](./command) — 通过用户自定义的辅助工具调用任何CLI密码管理器（如`keepassxc-cli`、`secret-tool`、`pass`或自定义脚本），该工具会输出`KEY=VALUE`格式的密钥信息。

## 同时使用多个密钥源

您可以同时启用多个密钥源——例如同时使用团队共享的Bitwarden项目和个人密码管理插件。这些密钥源会根据环境变量按既定的优先级顺序进行组合：

1. **默认情况下，您的`.env`文件/Shell配置具有最高优先级。** 只有当某个密钥源设置了`override_existing: true`时，它才会替换已存在的值（Bitwarden默认此值为true，以便实现集中式轮换）。
2. **通过映射指定的密钥源优先于批量注入的密钥源。** 即使不考虑顺序，那些明确将环境变量与引用项绑定（即使用`env:`映射）的密钥源，也会优先于那些隐式注入整个项目密钥的密钥源。
3. **先出现的密钥源优先。** 在结构相同的条件下，可选的`secrets.sources`列表中的顺序（或注册顺序）将决定优先级。对于已被其他密钥源占用的变量，后续的请求将会被跳过，并会给出启动警告，而不会静默处理。

`override_existing`机制确保某个密钥源无法覆盖另一个密钥源已占用的变量，同时任何密钥源也都无法覆盖其他密钥源的启动令牌（例如`BWS_ACCESS_TOKEN`）。

```yaml
secrets:
  sources: [bitwarden]     # optional explicit ordering
  bitwarden:
    enabled: true
    project_id: "..."
```

每个由数据源注入的凭证都会标注其来源——在设置流程及“Hermes Model”中，检测到的密钥旁会显示“(来自 Bitwarden)”的字样，这样您就能随时了解该值的来源。

## 配置文件与共享保险库

有两个位于调度器层面的参数，可确保单个共享保险库在多个[配置文件](../features/profiles)之间安全使用：

- **`secrets.preserve_existing`** — 一个环境变量名称列表，列表中的变量无论其当前的 `.env` 文件或Shell 设置值为何，都会优先被保留，即便有数据源设置了 `override_existing: true` 也是如此。此参数适用于那些需要在不同配置文件中保持差异的平台密钥（例如 `FEISHU_APP_SECRET`），而其他所有密钥则由中心统一管理并轮换：

  ```yaml
  secrets:
    preserve_existing: [FEISHU_APP_SECRET, TELEGRAM_BOT_TOKEN]
  ```

- **配置文件别名功能**（默认开启，如需禁用可设置 `secrets.profile_alias: false`）——当 Hermes 在指定配置文件下运行时，名为 `FOO_<PROFILE>` 的保险库密钥（仅支持凭证类后缀：`*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_KEY`、`*_PASSWORD`）也会被转换为标准的 `FOO` 格式。若将 `TELEGRAM_BOT_TOKEN_MILLA` 存储在共享项目中，那么使用 `milla` 配置文件的适配器就会自动读取该固定名称 `TELEGRAM_BOT_TOKEN` 并获取正确值。保险库直接以标准名称提供的变量始终优先于别名形式。

上述规则适用于所有数据源——无论是内置的还是插件式的——因为这些功能都存在于调度器中，而非后端服务中。

## 自定义后端添加

第三方密钥管理工具以独立插件的形式提供，而非作为核心代码库的一部分。自定义后端需继承 `agent.secret_sources.base.SecretSource` 类（必须实现一个方法：`fetch(cfg, home_path) -> FetchResult`），并通过插件中的 `register(ctx)` 方法调用 `ctx.register_secret_source(MySource())` 进行注册。调度器负责决定优先级、处理冲突、设置超时时间以及追踪数据来源——自定义数据源仅负责数据获取工作。关于接口规范、子进程安全辅助工具及合规性检查套件的完整指南，请参阅：[构建密钥源插件](/developer-guide/secret-source-plugin)。

内置的密钥管理工具集是刻意限制范围的（与内存提供者的策略一致）：Bitwarden 和 1Password 直接内置于系统中。其他工具——如 Infisical、Proton Pass、HashiCorp Vault、AWS Secrets Manager 以及操作系统自带的密钥存储功能——均需放在插件仓库中；相关资源可在 Nous Research 的 Discord 频道（`#plugins-skills-and-skins`）中分享。
