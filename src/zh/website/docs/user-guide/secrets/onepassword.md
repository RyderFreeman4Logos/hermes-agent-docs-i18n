# 1Password

在进程启动时从[1Password](https://1password.com/)获取提供程序的API密钥，而非将其以明文形式存储在`~/.hermes/.env`文件中。您可以将密钥保留在1Password中，并通过`op://vault/item/field`的形式进行引用；这样一来，更换凭证只需在1Password中进行一次操作即可。

## 工作原理

1. 首先安装官方的[1Password CLI](https://developer.1password.com/docs/cli/get-started/)（简称`op`），并通过**服务账户令牌**（无头服务器）或**交互式/桌面会话**（您的笔记本电脑）完成身份验证。
2. 在`~/.hermes/config.yaml`文件中将环境变量名称映射为`op://`格式的引用地址。
3. 每当`hermes`（或网关、定时任务）启动时，在加载完`~/.hermes/.env`文件后，Hermes会针对每个引用执行`op read`命令，并将获取到的值设置到`os.environ`中。
4. 默认情况下，Hermes会**覆盖**环境中已有的值，因此1Password才是数据来源——只需在1Password中更换一次凭证，所有Hermes进程在下次启动时都会自动使用新凭证。如果您希望以`.env`文件中的值为准，请将`override_existing`设置为`false`。

Hermes不会替您进行身份验证，也不会下载`op`命令：它会调用您已安装且已信任的CLI工具。如果`op`命令缺失、会话被锁定或引用地址有误，Hermes只会输出一行警告信息，然后继续使用`.env`文件中已有的凭证——绝不会阻止进程启动。

## 身份验证

`op`支持两种不太适合非交互式使用的模式，Hermes均能兼容：

- **服务账户**（推荐用于服务器/持续集成环境）：在 1Password 中创建一个服务账户，为其授予对应保险库的读取权限，然后将该账户的令牌以 `OP_SERVICE_ACCOUNT_TOKEN` 的形式导出到 `~/.hermes/.env` 文件中。该令牌即为核心凭证——应将其视作与其他承载令牌相同的存在。
- **桌面/交互式会话**（笔记本电脑）：运行 `op signin` 命令（或启用 1Password 应用中的 CLI 集成）。Hermes 会将您的 `OP_SESSION_*` 变量传递给 `op` 子进程。1Password 的缓存键中包含这些会话变量，因此即使登录到其他账户，也不会使用之前身份下缓存的值。

## 启动令牌

当您使用**服务账户令牌**进行身份验证时，该令牌本身就是 Hermes 在解析任何 `op://` 引用之前所需的核心凭证。它必须存在于所有用于解析机密信息的进程的 `os.environ` 环境变量中——包括定时任务（需设置 `kanban.dispatch_in_gateway: false`）、子进程调用、CLI 运行、macOS 的 launchd 代理以及 Docker 容器，而不仅限于交互式网关。共有三种方式可让该令牌可用，其优先级如下：

1. **推荐方式：在 `~/.hermes/.env` 中配置。** 使用命令 `hermes secrets onepassword setup --token <token>` 即可将令牌写入 `~/.hermes/.env` 文件，其作用类似于 Bitwarden 的 `BWS_ACCESS_TOKEN`。由于 `load_hermes_dotenv()` 函数会自动加载 `.env` 文件，因此无需任何额外配置，该令牌即可在任何地方被使用。这是最简单且可靠的方案。

2. **另一种方式：在 `~/.hermes/.op.env` 中配置（该文件会被 git 忽略）。** 如果您希望将服务账户令牌与 `.env` 文件分开存放——例如为了让 `.env` 文件能够被提交到私有的个人配置文件仓库中，而令牌则不会进入版本控制范围——可以将令牌存放在 `~/.hermes/.op.env` 文件中：

   ```bash
   echo 'OP_SERVICE_ACCOUNT_TOKEN=ops_...' > ~/.hermes/.op.env
   chmod 600 ~/.hermes/.op.env
   ```

Hermes在启动时会自动加载`.op.env`文件，且加载顺序位于`.env`之后；同时，它绝不会覆盖环境中已存在的令牌。由于`.op.env`被设置为git忽略文件，因此这些令牌永远不会被写入已提交的代码文件中。

3. **通过systemd的`EnvironmentFile`功能（Linux网关）**：如果您在systemd环境下运行网关，可以直接将令牌注入到服务的环境变量中：

   ```ini
   [Service]
   EnvironmentFile=-/home/youruser/.hermes/.op.env
   ```

以这种方式注入的令牌具有优先级——Hermes 会检测到 `OP_SERVICE_ACCOUNT_TOKEN` 已经被设置，从而完全跳过对 `.op.env` 文件的加载。

如果该令牌只能通过交互式 shell 访问（如 `op signin`、`.bashrc` 中的 `OP_SESSION_*` 导出变量等），则 cron 作业或新启动的子进程将无法继承该令牌。这些上下文会输出警告，并回退到 `.env` 文件中已存在的凭据。对于任何非交互式工作负载，请使用上述三种方式之一。

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

该操作会验证 `op` 是否已在 `PATH` 中（或使用 `--binary-path` 参数），记录您的账户/令牌设置，检查是否存在活跃会话，并将 `secrets.onepassword.enabled` 的值设置为 `true`。非交互式标志：

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

### 4. 预览与确认

```bash
hermes secrets onepassword sync     # dry-run: resolve now, show what would apply
hermes secrets onepassword status   # config + binary + references + auth
```

从现在开始，每次调用 `hermes` 命令时都会在启动阶段解析相关引用。当进程首次使用密钥时，你将在标准错误流中看到一行汇总信息。

## CLI 命令

| 命令 | 功能说明 |
|---|---|
| `hermes secrets onepassword setup` | 验证 `op`，设置账户/令牌环境变量，并启用功能 |
| `hermes secrets onepassword status` | 显示配置、二进制文件、认证信息以及已配置的引用 |
| `hermes secrets onepassword token` | 更换服务账户令牌：先通过 `op whoami` 进行验证，然后将其存储在 `.env` 文件中 |
| `hermes secrets onepassword set ENV_VAR "op://…"` | 将环境变量映射到某个引用（存储时会去除冗余信息并进行验证） |
| `hermes secrets onepassword remove ENV_VAR` | 删除某项映射关系 |
| `hermes secrets onepassword sync` | 模拟执行：立即解析引用并显示即将应用的设置 |
| `hermes secrets onepassword sync --apply` | 解析引用并将其导出到当前 shell 的环境变量中 |
| `hermes secrets onepassword disable` | 将 `enabled` 设置为 `false`；映射关系仍保持不变 |

`op` 和 `1password` 均可作为 `onepassword` 的别名使用。

## 配置文件

默认配置位于 `~/.hermes/config.yaml` 文件中：

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
| `env` | `{}` | 环境变量名与 `op://vault/item/field` 参考地址的映射关系。对于名称无效或值并非 `op://` 格式的内容，系统会发出警告并跳过处理。 |
| `account` | `""` | 用于替代 `op read --account` 参数中的账户简写/登录地址。若留空，则使用 `op` 的默认账户。 |
| `service_account_token_env` | `OP_SERVICE_ACCOUNT_TOKEN` | Hermes 用于读取服务账户令牌的环境变量名。其值会以 `op` 所期望的 `OP_SERVICE_ACCOUNT_TOKEN` 名称传递给子进程 `op`。若不设置该变量，则使用桌面/交互式会话。 |
| `binary_path` | `""` | `op` 程序的绝对路径。一旦设置，系统将直接使用该路径，而不会查询 `PATH` 环境变量——请务必明确指定此路径，以避免依赖 `PATH` 中出现的第一个 `op` 实例。 |
| `cache_ttl_seconds` | `300` | 已解析值的缓存有效期（包括内存缓存和磁盘缓存）。将其设置为 `0` 可同时禁用两种缓存机制——此时不会将任何值写入磁盘。 |
| `override_existing` | `true` | 当该值为 `true` 时，已解析的值会覆盖环境中已存在的对应内容，从而实现配置刷新。若设置为 `false`，则优先使用 `.env` 文件或 shell 导出的配置；在这些配置被调用之前，系统会先跳过它们。 |

## 失败处理方式

1Password 不会阻止 Hermes 的启动。如果出现任何问题，您将在标准错误流中看到一行警告信息，随后 Hermes 仍会继续运行。

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `the op CLI was not found on PATH` | 未安装 `op` 或其路径未加入系统环境变量 | 安装该 CLI，或设置 `secrets.onepassword.binary_path` |
| `op read failed for 'op://…': …` | 会话已锁定、令牌过期或无权限访问保险库 | 执行 `op signin`，运行 `hermes secrets onepassword token` 更换服务账户令牌，或为服务账户授予访问权限 |
| `op read returned an empty value for 'op://…'` | 所引用的字段存在但内容为空 | 在 1Password 中修正该项/字段（空值不会被应用——现有的环境变量将保持不变） |
| `… is not an op:// secret reference` | 映射值并非 `op://` 格式的引用 | 用正确的 `op://vault/item/field` 格式重新设置 |
| `op read timed out` | 网络受阻或 1Password 运行缓慢 | 检查网络连接及桌面端应用的集成情况 |

现在，启动警告中会包含一条带有 `→` 符号的解决方案说明，明确告知您应使用哪条命令来修复故障。

## 缓存机制

成功的完整数据获取结果会同时缓存在内存中以及磁盘上的 `<hermes_home>/cache/op_cache.json` 文件中（该文件以原子方式写入，权限为 `0600`）。这样一来，连续执行的短暂 `hermes` 调用无需为每个引用重新执行 `op` 命令。缓存功能如下：

- 仅存储已解析的机密**值**，绝不会保存服务账户令牌或任何原始认证信息（认证信息会以指纹形式嵌入缓存键中）；
- 当令牌、账户、`OP_SESSION_*` 变量或引用集合发生变动时，该缓存内容即失效；
- 若拉取过程中出现任何与特定引用相关的错误，则不会将该引用对应的缓存内容写入，从而避免短暂的认证失败被永久保留至缓存有效期结束；
- 当 `cache_ttl_seconds: 0` 时，缓存功能将完全被禁用，既无法读取也无法写入数据。

## 安全注意事项

- 1Password 的服务账户令牌可以读取该账户有权访问的所有机密信息。请将其存储在 `~/.hermes/.env` 文件中（而非 `config.yaml`），若令牌泄露，请在 1Password 中撤销并重新生成。
- 即使设置了 `override_existing: true`，Hermes 仍会阻止已解析的机密值覆盖令牌环境变量本身。
- `op` 子进程仅能获取经过严格限制的环境变量（包括认证/会话相关变量以及 `PATH`/`HOME` 环境变量），而非完整的 `os.environ` 复制版，因此通过 dotenv 提供的凭证不会全部被子进程继承。
- 引用内容必须以 `op://` 开头，且需在 `--` 选项之后传递，这样才能防止恶意构造的值被误解析为 `op` 标志。

## 何时不应使用此功能

- 在**单机个人环境**中，若使用 `~/.hermes/.env` 即可，无需使用此功能；
- 在**与外部网络隔绝的环境**中，无法连接到 1Password 时不宜使用；
- 在已配置好现有机密注入机制的**CI/CD 环境**中，应选择其中一种方案，而非同时使用两种。
这种方案非常适合多台机器组成的集群、共享的开发环境、网关型虚拟服务器，或是任何需要在对多个Hermes实例实现集中式轮换与撤销功能的场景。
