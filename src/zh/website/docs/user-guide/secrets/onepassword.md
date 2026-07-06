# 1Password

在进程启动时从[1Password](https://1password.com/)获取提供程序API密钥，而非将其以明文形式存储在`~/.hermes/.env`文件中。您可以将密钥保留在1Password中，并通过`op://vault/item/field`格式来引用它们；这样一来，更换凭证只需在1Password中进行一次操作即可。

## 工作原理

1. 首先安装官方的[1Password CLI](https://developer.1password.com/docs/cli/get-started/)（简称`op`），并通过**服务账户令牌**（用于无头服务器）或**交互式/桌面会话**（用于笔记本电脑）完成身份验证。
2. 在`~/.hermes/config.yaml`文件中将环境变量名称映射为`op://`格式的引用地址。
3. 每当`hermes`（或网关、定时任务）启动时，在加载完`~/.hermes/.env`文件后，Hermes会针对每个引用执行`op read`命令，并将解析后的值设置到`os.environ`中。
4. 默认情况下，Hermes会**覆盖**环境中已有的值，因此1Password才是权威数据源——只需更换一次凭证，所有Hermes进程在下次启动时都会自动使用新凭证。如果希望以`.env`文件中的值为准，可将`override_existing`设置为`false`。

Hermes不会替您进行身份验证，也不会下载`op`命令：它会调用您已安装且可信的CLI工具。如果缺少`op`、会话被锁定或引用地址有误，Hermes只会输出一行警告信息，然后继续使用`.env`文件中已有的凭证——绝不会阻止进程启动。

## 身份验证

`op`支持两种不太适合非交互式使用的模式，Hermes均可兼容：

- **服务账户**（推荐用于服务器/持续集成环境）：在1Password中创建一个服务账户，为其授予对应保险库的读取权限，然后将该账户的令牌以`OP_SERVICE_ACCOUNT_TOKEN`的格式导出到`~/.hermes/.env`文件中。该令牌即为凭证，可像其他承载令牌一样使用。
- **桌面/交互式会话**（用于笔记本电脑）：运行`op signin`命令（或在1Password应用中启用CLI集成）。Hermes会将您的`OP_SESSION_*`变量传递给`op`子进程。1Password的缓存机制会包含这些会话变量，因此切换到其他账户时，不会使用之前账户的缓存数据。

## 启动令牌

当您使用**服务账户令牌**进行身份验证时，该令牌本身就是Hermes在解析任何`op://`引用之前所需的启动凭证。它必须存在于所有用于解析机密信息的进程的`os.environ`中——包括定时任务（需将`kanban.dispatch_in_gateway`设置为`false`）、子进程调用、CLI命令执行、macOS的launchd代理以及Docker容器，而不仅限于交互式网关。以下是三种获取该令牌的方法，按优先级排序：

1. **在`~/.hermes/.env`文件中（推荐）**。使用命令`hermes secrets onepassword setup --token <token>`将令牌写入`~/.hermes/.env`文件，其用法与Bitwarden的`BWS_ACCESS_TOKEN`类似。由于`load_hermes_dotenv()`函数会自动加载`.env`文件，因此无需额外配置，该令牌即可在所有地方使用。这是最简单且可靠的方案。

2. **在`~/.hermes/.op.env`文件中（该文件会被git忽略）**。如果您不想将服务账户令牌放入`.env`文件中——例如希望将`.env`文件提交到私有个人配置仓库，而避免令牌被纳入版本控制——可将其保存在`~/.hermes/.op.env`文件中：

   ```bash
   echo 'OP_SERVICE_ACCOUNT_TOKEN=ops_...' > ~/.hermes/.op.env
   chmod 600 ~/.hermes/.op.env
   ```

Hermes在启动时会自动加载`.op.env`文件，其加载顺序位于`.env`之后，并且**绝不会**覆盖环境中已存在的令牌。由于`.op.env`被设置为git忽略文件，因此该令牌永远不会被写入已提交的代码文件中。

3. **通过systemd的`EnvironmentFile`功能（Linux网关）**。如果您在systemd环境下运行网关，可以直接将令牌注入到服务的环境变量中：

   ```ini
   [Service]
   EnvironmentFile=-/home/youruser/.hermes/.op.env
   ```

以这种方式注入的令牌具有优先级——Hermes 会检测到 `OP_SERVICE_ACCOUNT_TOKEN` 已经被设置，从而完全跳过对 `.op.env` 文件的加载。

如果该令牌只能通过交互式 Shell 获取（如 `op signin`、`.bashrc` 中的 `OP_SESSION_*` 导出值等），则 cron 作业或新启动的子进程将无法继承该令牌。这些环境会输出警告，并回退到 `.env` 文件中已存在的凭据。对于任何非交互式工作负载，请使用上述三种方案之一。

## 设置

### 1. 安装并登录 `op`

请参考 [1Password CLI 入门指南](https://developer.1password.com/docs/cli/get-started/)。验证其功能是否正常：

```bash
op whoami
```

### 2. 启用集成功能

```bash
hermes secrets onepassword setup
```

该步骤用于验证 `op` 是否已添加到 `PATH` 环境变量中（或使用 `--binary-path` 参数），记录您的账户/令牌设置，检查是否存在活跃会话，并将 `secrets.onepassword.enabled` 的值设置为 `true`。非交互式参数：

```bash
hermes secrets onepassword setup \
  --account my.1password.com \
  --token-env OP_SERVICE_ACCOUNT_TOKEN \
  --token "$OP_SERVICE_ACCOUNT_TOKEN"
```

### 3. 配置您的凭证映射

参考格式为 `op://<vault>/<item>/<field>`：

```bash
hermes secrets onepassword set OPENAI_API_KEY    "op://Private/OpenAI/api key"
hermes secrets onepassword set ANTHROPIC_API_KEY "op://Private/Anthropic/credential"
```

### 4. 预览并确认

```bash
hermes secrets onepassword sync     # dry-run: resolve now, show what would apply
hermes secrets onepassword status   # config + binary + references + auth
```

从现在开始，每次调用 `hermes` 命令时都会在启动阶段解析相关引用。当进程首次使用密钥时，您会在标准错误流中看到一行简要摘要。

## CLI 命令

| 命令 | 功能说明 |
|---|---|
| `hermes secrets onepassword setup` | 验证 `op` 参数，设置账户/令牌环境变量，并启用功能 |
| `hermes secrets onepassword status` | 显示配置信息、二进制文件、认证信息以及已配置的引用 |
| `hermes secrets onepassword set ENV_VAR "op://…"` | 将环境变量映射到某个引用（存储时会去除敏感信息并进行验证） |
| `hermes secrets onepassword remove ENV_VAR` | 删除该映射关系 |
| `hermes secrets onepassword sync` | 模拟运行：立即解析引用并显示即将应用的设置 |
| `hermes secrets onepassword sync --apply` | 解析引用并将其导出到当前shell的环境中 |
| `hermes secrets onepassword disable` | 将 `enabled` 参数设置为 `false`；保留原有的映射关系 |

`op` 和 `1password` 都可作为 `onepassword` 的别名使用。

## 配置文件

`~/.hermes/config.yaml` 文件中的默认设置：

```yaml
secrets:
  onepassword:
    enabled: false
    env:
      OPENAI_API_KEY: "op://Private/OpenAI/api key"
      ANTHROPIC_API_KEY: "op://Private/Anthropic/credential"
    account: ""
    service_account_token_env: OP_SERVICE_ACCOUNT_TOKEN
    binary_path: ""
    cache_ttl_seconds: 300
    override_existing: true
```

| 键值 | 默认值 | 功能说明 |
|---|---|---|
| `enabled` | `false` | 主开关。当该值为 `false` 时，`op` 函数将永远不会被调用。 |
| `env` | `{}` | 环境变量名与 `op://vault/item/field` 引用之间的映射关系。若某个键值既不是有效的环境变量名，其值也不是 `op://` 格式的引用，则会发出警告并被跳过。 |
| `account` | `""` | 用于替代 `op read --account` 参数中的账户简写或登录地址。若留空，则使用 `op` 的默认账户。 |
| `service_account_token_env` | `OP_SERVICE_ACCOUNT_TOKEN` | Hermes 用于读取服务账户令牌的环境变量名称。该变量的值会以 `op` 所期望的 `OP_SERVICE_ACCOUNT_TOKEN` 名称形式传递给子进程 `op`。若不设置该变量，则使用桌面/交互式会话的账户。 |
| `binary_path` | `""` | `op` 程序的绝对路径。一旦设置，将直接使用该路径，且不会查询 `PATH` 环境变量——请务必明确指定此路径，以避免依赖 `PATH` 中出现的第一个 `op` 程序。 |
| `cache_ttl_seconds` | `300` | 已解析值的缓存时长（在内存及磁盘中均有效）。将其设置为 `0` 可同时禁用内存缓存和磁盘缓存——此时不会有任何值被写入磁盘。 |
| `override_existing` | `true` | 当该值为 `true` 时，已解析的值会覆盖环境中已存在的对应内容，从而实现密钥轮换。若将其设置为 `false`，则优先使用 `.env` 文件或 shell 导出的配置；这些引用会在调用 `op` 之前被跳过。 |

## 失败场景

1Password 永不会阻止 Hermes 的启动。一旦出现异常，你将在标准错误流中看到一行警告信息，随后 Hermes 仍会继续运行：

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `the op CLI was not found on PATH` | 未安装 `op` 程序或其路径未被添加到 `PATH` 中 | 安装该 CLI，或手动设置 `secrets.onepassword.binary_path` 参数。 |
| `op read failed for 'op://…': …` | 会话已锁定、令牌过期或无权限访问保险库 | 执行 `op signin` 操作，刷新令牌，或为服务账户授予相应访问权限。 |
| `op read returned an empty value for 'op://…'` | 引用的字段存在但内容为空 | 在 1Password 中修改对应项/字段的值（空值不会被应用，原有的环境变量将保持不变）。 |
| `… is not an op:// secret reference` | 映射值并非 `op://` 格式的引用 | 重新设置该值为正确的 `op://vault/item/field` 格式。 |
| `op read timed out` | 网络连接受阻或 1Password 运行缓慢 | 检查网络连接情况或桌面端应用的集成状态。 |

## 缓存机制

成功获取的完整数据会同时存储在内存及磁盘中，文件路径为 `<hermes_home>/cache/op_cache.json`（以原子方式写入，权限设置为 `0600`）。这样一来，连续快速调用的 `hermes` 命令无需为每个引用都重新执行 `op` 函数。该缓存具有以下特点：

- 仅存储已解析的密钥**值**，绝不保存服务账户令牌或任何原始认证信息（认证信息会以指纹形式嵌入缓存键中）；
- 当令牌、账户信息、`OP_SESSION_*` 变量或引用列表发生变更时，缓存即失效；
- 若某次数据获取过程中出现针对特定引用的错误，缓存将不会被写入，因此短暂的认证失败不会被永久保留；
- 当 `cache_ttl_seconds` 设置为 `0` 时，缓存功能将被完全禁用，此时既无法读取也无法写入数据。

## 安全注意事项

- 1Password 的服务账户令牌拥有读取该账户所能访问的所有密钥的权限。请将该令牌存储在 `~/.hermes/.env` 文件中（而非 `config.yaml`），若令牌泄露，请在 1Password 中撤销并重新生成。
- 即使设置了 `override_existing: true`，Hermes 也禁止已解析的值覆盖令牌相关的环境变量本身。
- 子进程 `op` 只会获得一个精简的允许列表式环境（包含认证/会话相关变量以及 `PATH`、`HOME` 环境变量），而非完整的 `os.environ` 复制版，因此通过 dotenv 方式设置的提供程序凭证不会全部被子进程继承。
- 所有引用都会被验证是否以 `op://` 开头，且引用值会放在 `--` 选项之后，从而防止恶意构造的字符串被误解析为 `op` 的命令参数。

## 何时不应使用此方案

- **单机个人环境**：在这种情况下，直接使用 `~/.hermes/.env` 即可。
- **与外部网络隔离的环境**：无法访问 1Password 的环境。
- **CI/CD 流水线**：若已存在现成的密钥注入机制，则无需再使用此方案——应选择其中一种方式，而非同时使用两种。

此方案的理想应用场景是多机集群、共享开发环境、网关虚拟服务器，或是需要跨多个 Hermes 安装实现集中式密钥轮换与撤销管理的场景。
