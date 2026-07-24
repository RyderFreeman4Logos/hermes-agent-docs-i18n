# 命令辅助工具密钥源

你可以在启动时运行自定义的辅助命令来获取凭证——任何具备 CLI 接口的密钥管理工具均可使用：`keepassxc-cli`、`secret-tool`（GNOME Keyring）、`pass`、`gpg`、Vaultwarden 的 CLI，或是用于读取临时文件系统环境文件的脚本。该辅助工具会通过标准输出打印 `KEY=VALUE` 格式的行；Hermes 会通过与 [Bitwarden](./bitwarden) 和 [1Password](./onepassword) 相同的调度机制来应用这些凭证，因此你可以同时启用任意组合的密钥源。

## 工作原理

1. 你需要在 `config.yaml` 中配置辅助命令（切勿在 `.env` 文件中配置——命令属于配置内容，而 `.env` 文件用于存储实际值）。
2. 启动时，在加载完 `.env` 文件后，Hermes 会通过 `/bin/sh -c` 命令一次性运行该辅助工具，并将其标准输出解析为 dotenv 格式的数据块。
3. 解析后的密钥将遵循标准的优先级规则：除非设置了 `override_existing: true`，否则以 `.env` 文件和 shell 变量中的值为准；当多个来源对同一变量有定义时，映射型来源的优先级高于此批量来源；最先声明该变量的来源其值将被采用。

```yaml
secrets:
  command:
    enabled: true
    command: "cat /run/user/1000/hermes-secrets.env"
    # or any vault CLI that dumps KEY=VALUE lines:
    # command: "pass show hermes/env"
    # command: "secret-tool lookup service hermes-env"
```

## 配置选项

| 键值 | 默认值 | 功能说明 |
|---|---|---|
| `enabled` | `false` | 主开关，控制功能是否启用。 |
| `command` | `""` | 通过 `/bin/sh -c` 执行的辅助命令；必须向标准输出打印 `KEY=VALUE` 格式的行。 |
| `helper_timeout_seconds` | `3` | 单次辅助命令运行的硬性超时时间。该值设置得相对较短，旨在确保辅助命令执行迅速且为非交互式（无解锁提示，无需输入指纹或密码）。 |
| `override_existing` | `false` | 辅助命令的配置值会覆盖 `.env` 文件及Shell环境中的对应值。与 Bitwarden/1Password 不同，该选项默认处于关闭状态，因为本地辅助工具并非集中式的密码管理权威源。 |

## 安全模型

- 辅助命令字符串由您自行配置——其信任级别与您控制的 `.env` 文件相同。
- 输出数据量被严格限制在 1 MiB 以内；若辅助命令运行失控，将无法干扰系统启动（会在超时后被强制终止进程组）。
- 辅助命令的**标准错误流会被直接丢弃**——由于保险库的CLI诊断信息可能包含敏感内容，因此这类信息绝不会出现在Hermes的输出中。故障日志仅记录结构化字段（如退出码、信号类型及错误编号），而不会包含命令字符串。
- 仅包含空白字符的值将被视为“无有效值”——此类占位符内容绝不会被纳入授权请求头中。
- 该功能仅支持POSIX系统（需要 `/bin/sh`）。在Windows系统中，系统会报告配置缺失，但仍会继续启动。

## 故障处理方式

系统启动过程永远不会被阻塞。出现错误时，系统会打印一行错误信息，并附上相应的解决建议 `→`：

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `secrets.command.command is empty` | 已启用该功能但未指定命令 | 在 config.yaml 文件中设置 `secrets.command.command` 的值 |
| `helper command failed` | 命令执行非零退出、超时或启动失败 | 在Shell环境中手动运行该辅助命令，以查看真实错误信息（Hermes刻意会丢弃其标准错误流） |
| `helper output was not a KEY=VALUE map` | 辅助命令输出的仅为纯值或无效数据 | 调整辅助命令，使其输出符合 `KEY=VALUE` 格式的行 |

## 何时使用此功能而非插件

对于没有内置集成功能的保险库，命令源是一种应急解决方案。如果您发现需要编写冗长的脚本来处理复杂的CLI操作，建议考虑使用正规的[secret-source插件](/developer-guide/secret-source-plugin)——插件具备缓存功能、来源标识以及类型化配置选项。
