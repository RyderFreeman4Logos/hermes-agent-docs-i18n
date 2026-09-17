# Bitwarden Secrets Manager

在进程启动时从[Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/)获取API密钥，而非将其以明文形式存储在`~/.hermes/.env`文件中。只需一个启动专用密钥（即机器账户访问令牌）即可替代每个服务提供商所需的多个密钥，这样一来，更新凭证仅需在Bitwarden网页应用中进行一次操作。

## 工作原理

1. 首先在Bitwarden Secrets Manager中创建一个**机器账户**，为其授予某个项目的读取权限，随后生成一个**访问令牌**。
2. Hermes会将该令牌以`BWS_ACCESS_TOKEN`的格式存储在`~/.hermes/.env`文件中。
3. 每当`hermes`（或网关、定时任务）启动时，在加载完`~/.hermes/.env`文件后，Hermes会调用`bws secret list <project_id>`命令，并将返回的密钥设置到`os.environ`环境中。
4. 默认情况下，Hermes会**覆盖**环境中已存在的值，因此Bitwarden才是权威数据源——在网页应用中更新一次密钥，所有Hermes进程在下次启动时都会自动获取最新版本。若希望以`.env`文件中的值为准，可在配置中将`override_existing`设置为`false`。

首次使用时，`bws`二进制文件会自动下载到`~/.hermes/bin/`目录中，无需使用`apt`、`brew`或`sudo`等命令。

## 为何使用机器账户（以及为何无需二次验证提示）

Bitwarden Secrets Manager专为非交互式工作负载设计：由于没有人工干预，机器账户无法通过双重身份验证来控制访问。访问令牌即为相应的认证凭证，任何拥有该令牌的人都能读取该机器账户有权访问的所有机密信息，因此应将其视为一类高价值的承载令牌——请将其存储在`.env`文件中（而非`config.yaml`），若令牌泄露，需通过Bitwarden网页应用进行撤销并重新生成。

您需要在适用常规双重身份验证的**网页应用**中创建机器账户。之后，该令牌即可独立使用。

## 设置步骤

### 1. 创建机器账户及访问令牌

在[Bitwarden网页应用](https://vault.bitwarden.com)（欧盟用户可使用[vault.bitwarden.eu](https://vault.bitwarden.eu)）中：

1. 通过产品切换器进入**Secrets Manager**。
2. 创建或选择一个**项目**（例如“Hermes密钥”）。
3. 将您的提供商密钥作为机密信息添加进去。这些机密的**名称**将对应环境变量名——可使用`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY`等格式。
4. 转至**机器账户 → 新建机器账户 → 我的Hermes机器**，然后在**项目**标签页中为该项目授予读取权限。
5. 切换到**访问令牌**标签页，选择**创建访问令牌**，设置令牌**永不过期**（或指定具体日期），最后复制令牌内容（以`0.`开头）。Bitwarden无法再次获取该令牌，因此请务必妥善保存副本。

Bitwarden免费套餐已包含有限功能的Secrets Manager，无需购买付费套餐即可试用。

### 2. 运行向导

```bash
hermes secrets bitwarden setup
```

它将执行以下操作：

1. 下载并验证 `bws v2.0.0`，并将其安装至 `~/.hermes/bin/bws` 目录。
2. 提示您输入访问令牌（输入内容会隐藏处理），该令牌将以 `BWS_ACCESS_TOKEN` 的形式存储在 `~/.hermes/.env` 文件中。
3. 询问您的机器账户所属的 Bitwarden 区域——**美国云**、**欧洲云**，还是**自托管/自定义网址**。该信息将以 `secrets.bitwarden.server_url` 的形式存储在 `config.yaml` 文件中，并作为 `BWS_SERVER_URL` 参数传递给 `bws`。
4. 列出机器账户可以访问的项目，让您从中选择一个。所选项目的编号将以 `secrets.bitwarden.project_id` 的形式存储在 `config.yaml` 文件中。
5. 测试获取该项目的机密信息，并显示哪些环境变量可以被解析。
6. 将 `secrets.bitwarden.enabled` 的值设置为 `true`。

此外，还可以通过命令行参数实现非交互式设置：

```bash
hermes secrets bitwarden setup \
  --access-token "$BWS_ACCESS_TOKEN" \
  --server-url https://vault.bitwarden.eu \
  --project-id <project-uuid>
```

### 3. 确认

```bash
hermes secrets bitwarden status
```

从现在开始，每次调用 `hermes` 命令时，都会在启动阶段获取最新的机密信息。当进程首次应用这些机密信息时，您会在标准错误流中看到一行简要说明。

## CLI

| 命令 | 功能说明 |
|---|---|
| `hermes secrets bitwarden setup` | 交互式向导：安装二进制文件、提示输入令牌、选择项目并测试数据获取功能 |
| `hermes secrets bitwarden status` | 显示配置信息、二进制文件版本以及令牌是否存在及是否有效 |
| `hermes secrets bitwarden token` | 更换访问令牌：先通过 Bitwarden 验证新令牌的有效性，然后将其存储在 `.env` 文件中 |
| `hermes secrets bitwarden sync` | 模拟运行：立即获取机密信息并显示即将应用的内容 |
| `hermes secrets bitwarden sync --apply` | 获取机密信息并将其导出到当前 Shell 的环境变量中 |
| `hermes secrets bitwarden install` | 仅下载已指定的 `bws` 二进制文件（无需身份验证） |
| `hermes secrets bitwarden disable` | 将 `enabled` 设置为 `false`；同时保留原有的令牌和项目编号 |

## 更换过期或已被撤销的令牌

当机器账户令牌过期、被撤销或账户被删除时，启动过程会显示如下提示：

```
Bitwarden Secrets Manager: Bitwarden rejected the machine-account access token (BWS_ACCESS_TOKEN) — it was likely revoked, expired, or belongs to another region.  (...)
Bitwarden Secrets Manager: → Run `hermes secrets bitwarden token` to paste a fresh access token ...
```

无需重新运行整个向导即可解决问题：

```bash
hermes secrets bitwarden token                     # masked prompt
hermes secrets bitwarden token --access-token 0.…  # non-interactive
```

该命令会在执行任何操作**之前**使用新令牌对 Bitwarden 进行验证——若令牌被拒绝，当前的 `.env` 文件将保持不变。验证成功后，它会存储该令牌并清除获取的缓存，同时会提示当前配置的项目是否对新机器账户可见。

## 配置

`~/.hermes/config.yaml` 中的默认设置：

```yaml
secrets:
  bitwarden:
    enabled: false
    access_token_env: BWS_ACCESS_TOKEN
    project_id: ""
    server_url: ""
    cache_ttl_seconds: 300
    encrypted_cache:
      enabled: false
      max_stale_seconds: 0
    override_existing: true
    auto_install: true
```

| 键值 | 默认值 | 功能说明 |
|---|---|---|
| `enabled` | `false` | 主开关。若设置为 `false`，则不会与 Bitwarden 进行任何通信。 |
| `access_token_env` | `BWS_ACCESS_TOKEN` | 用于存储启动令牌的环境变量名称。如果您已将该变量用于其他用途，请进行修改。 |
| `project_id` | `""` | 需同步的项目的 UUID。 |
| `server_url` | `""` | Bitwarden 所在区域或自托管服务的端点地址。留空则使用默认的 `bws`（美国云，地址为 `https://vault.bitwarden.com`）。如需使用欧洲云，请设置为 `https://vault.bitwarden.eu`；自托管场景则可使用自定义地址。该值会作为 `BWS_SERVER_URL` 被传递给 `bws` 子进程。 |
| `cache_ttl_seconds` | `300` | 内存或磁盘中获取的缓存数据可被重复使用的时长。设置为 `0` 可禁用缓存数据的重复使用。 |
| `encrypted_cache.enabled` | `false` | 是否将最近一次成功获取的数据存储在 `~/.hermes/cache/bws_cache.enc.json` 文件中的 AES-GCM 加密缓存中。 |
| `encrypted_cache.max_stale_seconds` | `0` | 当启用加密缓存时，仅在网络连接失败或超时后，且数据未超过此时长时才允许使用该缓存。认证失败时绝不会使用过期的密钥。一旦成功执行加密写入操作，旧的明文缓存文件 `cache/bws_cache.json` 将会被删除。 |
| `override_existing` | `true` | 若设置为 `true`，Bitwarden 提供的数值将覆盖环境变量中已有的值（这样网页应用中的密钥轮换才能真正生效）。如需让 `.env` 文件或 shell 导出的值在本地优先生效，请将其设置为 `false`。 |
| `auto_install` | `true` | 若设置为 `true`，首次使用时会自动将 `bws` 工具下载到 `~/.hermes/bin/` 目录中。 |

## 故障模式

Bitwarden从不阻止Hermes的启动。如果出现任何问题，您会在标准错误输出中看到一条简短的警告信息，而Hermes会继续使用`.env`文件中已有的凭据正常运行：

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `BWS_ACCESS_TOKEN未设置` | 配置中已启用该功能，但`.env`文件中的令牌已被清除 | 重新运行`hermes secrets bitwarden setup`命令 |
| `Bitwarden拒绝了机器账户访问令牌……invalid_client` | 令牌已被撤销、过期，或机器账户已被删除——亦或是该令牌属于其他区域（例如欧盟地区的令牌试图访问美国地区的身份验证端点） | 运行`hermes secrets bitwarden token`命令以粘贴新的令牌；若为区域不匹配问题，请重新执行设置流程并选择欧盟/自托管选项（或设置`secrets.bitwarden.server_url`） |
| `bws退出代码为1：无效的访问令牌` | 令牌已被撤销或存在错误 | 使用新令牌运行`hermes secrets bitwarden token`命令 |
| `bws超时` | 网络连接被阻断或Bitwarden API响应缓慢 | 检查与`api.bitwarden.com`（或您的`server_url`）的连接状况 |
| `无法找到bws二进制文件` | `auto_install: false`且`bws`未添加到系统路径中 | 从[github.com/bitwarden/sdk-sm/releases](https://github.com/bitwarden/sdk-sm/releases)手动下载安装，或重新开启`auto_install`功能 |
| `校验和不一致` | 下载的文件已损坏或被篡改 | 重新运行命令，系统会自动重试；如果问题依旧，请提交工单报告 |

现在的启动警告信息中还包含一条带有`→`符号的解决方案指引，明确告诉您该执行哪条命令来解决问题。

## 安全注意事项

- 启动令牌（`BWS_ACCESS_TOKEN`）本身属于敏感信息——任何获取到该令牌的人都能读取机器账户所拥有的所有机密数据。应将其视同其他任何 API 密钥一样谨慎处理。
- 即使设置了 `override_existing: true`，Hermes 也会拒绝允许 Bitwarden 覆盖该启动令牌本身。如果将 `BWS_ACCESS_TOKEN` 作为机密信息存储在项目中，它在应用过程中会被直接跳过。
- 下载的 `bws` 可执行文件会通过相同的 GitHub 发布版本所公布的 SHA-256 校验和进行验证。若校验失败，安装过程将立即终止。
- 目前固定的版本为（撰写本文时为 `bws v2.0.0`），该版本会通过提交到此仓库的 Pull Request 进行更新——由于上游版本的格式可能会发生变化，Hermes 不会自动将 `bws` 升级到“最新版本”。

## 何时不宜使用此方案

- **单机个人环境**：在这种情况下，使用 `~/.hermes/.env` 文件即可满足需求。这样做只是用一种凭证替代了另一种，并且在启动时还需增加网络依赖。
- **无法访问 `api.bitwarden.com` 的隔离环境**。
- **已配置现有机密注入机制的 CI/CD 环境**（如 GitHub Actions 机密信息、Vault 等）——应选择其中一种方案，而非同时使用两种。

此方案的适用场景包括多机集群、共享开发环境、网关型 VPS，或是任何需要跨多个 Hermes 安装实现集中式令牌轮换与撤销管理的场景。
