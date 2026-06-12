# Bitwarden Secrets Manager

在进程启动时从[Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/)获取API密钥，而非将其以明文形式存储在`~/.hermes/.env`文件中。只需一个引导密钥（即机器账户访问令牌）即可替代每个提供商所需的多个密钥，这样一来，更新凭证仅需在Bitwarden网页应用中进行一次操作。

## 工作原理

1. 首先在Bitwarden Secrets Manager中创建一个**机器账户**，为其授予某个项目的读取权限，然后生成一个**访问令牌**。
2. Hermes会将该令牌以`BWS_ACCESS_TOKEN`的名称存储在`~/.hermes/.env`文件中。
3. 每当`hermes`（或网关、定时任务）启动时，在加载完`~/.hermes/.env`文件后，Hermes会调用`bws secret list <project_id>`命令，并将返回的密钥设置到`os.environ`中。
4. 默认情况下，Hermes会**覆盖**环境中已存在的值，因此Bitwarden才是权威数据源——在网页应用中更新一次密钥，所有Hermes进程在下次启动时都会自动获取最新版本。如果希望以`.env`文件中的值为准，可在配置中将`override_existing`设置为`false`。

首次使用时，`bws`二进制文件会自动下载到`~/.hermes/bin/`目录中——无需使用`apt`、`brew`或`sudo`命令。

## 为何使用机器账户（以及为何无需二次验证）

Bitwarden Secrets Manager专为非交互式工作负载设计：由于没有人工操作参与，机器账户无法设置二次验证。访问令牌本身就是凭证，拥有它的人就能读取该机器账户有权访问的所有密钥，因此应将其视为一条高价值的承载令牌——将其存储在`.env`文件中（而非`config.yaml`），一旦发生泄露，可通过Bitwarden网页应用立即撤销并重新生成。

您需要在网页应用中设置机器账户，此时仍需通过常规的二次验证流程。之后，该访问令牌即可独立使用。

## 设置步骤

### 1. 创建机器账户及访问令牌

在[Bitwarden网页应用](https://vault.bitwarden.com)（欧盟用户可使用[vault.bitwarden.eu](https://vault.bitwarden.eu)）中：

1. 通过产品切换器进入**Secrets Manager**。
2. 创建或选择一个**项目**（例如“Hermes密钥”）。
3. 将各提供商的密钥作为机密信息添加进去。这些机密的**名称**将对应环境变量的名称——可使用`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY`等格式。
4. 转到**Machine accounts → New machine account → My Hermes machine**，然后在**Projects**标签页中为该项目授予读取权限。
5. 进入**Access tokens**标签页，点击**Create access token**，选择“永不过期”或设定具体过期日期，最后复制该令牌（开头为`0.`）。注意Bitwarden无法再次获取该令牌，务必妥善保存副本。

Bitwarden免费套餐已包含Secrets Manager功能，但有一定的使用限制；尝试此功能无需购买付费套餐。

### 2. 运行设置向导

```bash
hermes secrets bitwarden setup
```

它将执行以下操作：

1. 下载并验证 `bws v2.0.0`，并将其安装到 `~/.hermes/bin/bws` 目录中。
2. 提示您输入访问令牌（输入内容会隐藏处理），该令牌将以 `BWS_ACCESS_TOKEN` 的形式存储在 `~/.hermes/.env` 文件中。
3. 询问您的机器账户所属的 Bitwarden 区域——**美国云**、**欧洲云**，还是**自托管/自定义 URL**。该信息将以 `secrets.bitwarden.server_url` 的形式存储在 `config.yaml` 文件中，并作为 `BWS_SERVER_URL` 参数传递给 `bws`。
4. 列出机器账户可访问的项目列表，让您从中选择一个。所选项目的编号将以 `secrets.bitwarden.project_id` 的形式存储在 `config.yaml` 文件中。
5. 测试获取该项目的机密信息，并显示哪些环境变量能够被解析。
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

从现在开始，每次调用 `hermes` 命令时，都会在启动时获取最新的机密信息。当进程首次应用这些机密信息时，您会在标准错误流中看到一行摘要信息。

## CLI 命令

| 命令 | 功能说明 |
|---|---|
| `hermes secrets bitwarden setup` | 交互式向导：安装二进制文件、提示输入令牌、选择项目并测试数据获取功能 |
| `hermes secrets bitwarden status` | 显示配置信息、二进制版本以及令牌是否存在 |
| `hermes secrets bitwarden sync` | 模拟运行：立即获取机密信息并展示即将应用的内容 |
| `hermes secrets bitwarden sync --apply` | 获取机密信息并将其导出到当前shell的环境中 |
| `hermes secrets bitwarden install` | 仅下载已绑定的 `bws` 二进制文件（无需身份验证） |
| `hermes secrets bitwarden disable` | 将 `enabled` 设置为 `false`；同时保留原有的令牌和项目编号 |

## 配置设置

默认配置位于 `~/.hermes/config.yaml` 文件中：

```yaml
secrets:
  bitwarden:
    enabled: false
    access_token_env: BWS_ACCESS_TOKEN
    project_id: ""
    server_url: ""
    cache_ttl_seconds: 300
    override_existing: true
    auto_install: true
```

| 键值 | 默认值 | 功能说明 |
|---|---|---|
| `enabled` | `false` | 主开关。设置为 `false` 时，不会与 Bitwarden 进行任何通信。 |
| `access_token_env` | `BWS_ACCESS_TOKEN` | 用于存储启动令牌的环境变量名称。如果您已将该变量用于其他用途，请进行修改。 |
| `project_id` | `""` | 需要同步的项目的 UUID。 |
| `server_url` | `""` | Bitwarden 所在区域或自托管服务器的地址。留空则使用默认的 `bws`（美国云端，地址为 `https://vault.bitwarden.com`）。如需使用欧洲云端，请设置为 `https://vault.bitwarden.eu`；自托管环境则可使用自定义地址。该参数会作为 `BWS_SERVER_URL` 传递给 `bws` 子进程。 |
| `cache_ttl_seconds` | `300` | 进程内获取的结果可被重复使用的时长。设置为 `0` 可禁用缓存。缓存是按进程独立的；每次启动新的 `hermes` 进程时都会重新开始缓存。 |
| `override_existing` | `true` | 设置为 `true` 时，Bitwarden 提供的数值会覆盖环境变量中已有的值（这样网页应用中的令牌轮换才能真正生效）。若希望本地 `.env` 文件或 shell 导出的值优先生效，请将其设置为 `false`。 |
| `auto_install` | `true` | 设置为 `true` 时，首次使用时会自动将 `bws` 下载到 `~/.hermes/bin/` 目录中。 |

## 故障处理方式

Bitwarden 不会阻止 Hermes 的启动。一旦出现异常，您会在标准错误流中看到一行警告信息，随后 Hermes 会使用 `.env` 文件中已有的凭据继续运行：

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `BWS_ACCESS_TOKEN 未设置` | 配置中已启用该功能，但 `.env` 文件中的令牌已被清除 | 重新运行 `hermes secrets bitwarden setup` 命令 |
| `bws exited 1: invalid access token` | 令牌已被撤销或无效 | 生成新的令牌，然后重新执行设置流程 |
| `[400 Bad Request] {"error":"invalid_client"}` | 令牌对应的是与 `bws` 调用地址不同的 Bitwarden 区域（例如使用欧洲区令牌去调用美国区的身份验证端点） | 重新执行设置流程并选择正确的区域，或将 `secrets.bitwarden.server_url` 设置为 `https://vault.bitwarden.eu`（或您的自托管地址） |
| `bws timed out` | 网络连接受阻或 Bitwarden API 响应缓慢 | 检查与 `api.bitwarden.com`（或您的 `server_url`）的连接状况 |
| `bws binary not available` | `auto_install: false` 且 `bws` 不在系统路径中 | 从 [github.com/bitwarden/sdk-sm/releases](https://github.com/bitwarden/sdk-sm/releases) 手动下载该二进制文件，或重新开启 `auto_install` 功能 |
| `Checksum mismatch` | 下载的文件已损坏或被篡改 | 重新运行安装命令，系统会自动重试；如果问题依旧，请提交缺陷报告 |

## 安全注意事项

- 启动令牌（`BWS_ACCESS_TOKEN`）本身属于敏感信息——拥有该令牌的人即可读取机器账户有权访问的所有机密数据。请将其视同其他任何 API 密钥一样谨慎处理。
- 即使设置了 `override_existing: true`，Hermes 也会阻止 Bitwarden 覆盖该启动令牌本身。如果您将 `BWS_ACCESS_TOKEN` 作为项目内的机密信息存储，它在应用时会被直接忽略。
- 下载的 `bws` 二进制文件会通过相同的 GitHub 发布版本所提供的 SHA-256 校验和进行验证。若校验失败，安装过程将立即终止。
- 目前固定的版本为 `bws v2.0.0`，该版本会通过向此仓库提交 Pull Request 来更新——由于上游版本的架构可能会发生变化，Hermes 不会自动将 `bws` 升级到“最新版本”。

## 何时不宜使用此功能

- **单机个人环境**：在这种情况下，使用 `~/.hermes/.env` 文件即可满足需求。使用此功能意味着要用一个网络依赖来替代原有的凭据管理方式。
- **与外部网络断开的环境**：无法访问 `api.bitwarden.com` 的环境。
- **CI/CD 流水线**：如果已配置了现有的机密信息注入机制（如 GitHub Actions 密钥、Vault 等），则无需同时使用此功能，应选择其中一种方案。

此功能的理想应用场景是多机器集群、共享开发环境、网关型 VPS，或是任何需要在对多个 Hermes 安装实例进行集中式令牌轮换和撤销管理的场景。
