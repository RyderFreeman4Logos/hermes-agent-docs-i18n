# OpenViking 内存提供器

由 Volcengine（字节跳动）开发的上下文数据库，具备类似文件系统的知识层级结构、分层检索功能以及自动内存提取能力。

## 前提条件

- 已安装 OpenViking，且可调用 `openviking-server` 命令
- OpenViking 服务器配置已完成初始化与验证（先执行 `openviking-server init`，再执行 `openviking-server doctor`）
- OpenViking 服务器正在运行，并且可从 Hermes 进行访问

## 设置步骤

首先准备 OpenViking：

```bash
openviking-server init
openviking-server doctor
openviking-server
```

接着配置 Hermes：

```bash
hermes memory setup    # select "openviking"
```

该设置可以链接到现有的 `~/.openviking/ovcli.conf` 文件，将其当前的连接参数复制到 Hermes 中；如果该文件不存在，则会自动生成一个最简版的 `ovcli.conf`。

或者也可以手动操作：

```bash
hermes config set memory.provider openviking
```

请将连接设置添加到当前激活配置文件的 `.env` 文件中。默认配置文件的路径为 `~/.hermes/.env`；若使用自定义配置文件，则路径为 `~/.hermes/profiles/<profile>/.env`。

```text
OPENVIKING_ENDPOINT=http://127.0.0.1:1933
# OPENVIKING_API_KEY=...
# OPENVIKING_ACCOUNT=default
# OPENVIKING_USER=default
# OPENVIKING_AGENT=hermes
```

## 配置

OpenViking 的服务器配置与 Hermes 是分开的：

- `ov.conf` 用于配置 OpenViking 的存储、嵌入式/VLM 模型、认证机制以及服务器行为。OpenViking 会从 `--config`、`OPENVIKING_CONFIG_FILE` 或 `~/.openviking/ov.conf` 路径读取该文件。
- `ovcli.conf` 用于存储客户端/CLI 连接相关的参数，如 `url`、`api_key`、`account` 和 `user`。这些参数可从 `OPENVIKING_CLI_CONFIG_FILE` 或 `~/.openviking/ovcli.conf` 中读取。

Hermes 端的提供程序配置则通过当前激活配置文件中的 `.env` 文件里的环境变量来加载：

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `OPENVIKING_ENDPOINT` | `http://127.0.0.1:1933` | 服务器 URL |
| `OPENVIKING_API_KEY` | （无） | 用于需要身份认证的服务器的用户/管理员 API 密钥 |
| `OPENVIKING_ACCOUNT` | `default` | 本地/可信模式下的租户账户 |
| `OPENVIKING_USER` | `default` | 本地/可信模式下的租户用户 |
| `OPENVIKING_AGENT` | `hermes` | OpenViking 中的 Hermes 对等体 ID，用于实现基于对等体的记忆存储 |

当设置了 `OPENVIKING_API_KEY` 后，Hermes 会允许 OpenViking 通过该密钥推断出账户/用户身份。在未设置 API 密钥的本地或可信部署环境中，Hermes 会通过身份标识头部信息来传递 `OPENVIKING_ACCOUNT` 和 `OPENVIKING_USER` 的值。

## 工具

| 工具 | 描述 |
|------|------|
| `viking_search` | 支持快速搜索、深度搜索和自动搜索三种模式的语义搜索工具 |
| `viking_read` | 用于读取 viking:// 格式的内容，支持摘要视图、概览视图和完整视图 |
| `viking_browse` | 提供类似文件系统的导航功能，包括列表查看、树形结构查看和统计信息查看 |
| `viking_remember` | 直接通过 OpenViking 的 `content/write` 接口存储事实信息 |
| `viking_forget` | 删除指定的一个 viking:// 格式的记忆文件 URI |
| `viking_add_resource` | 将 URL 或文档导入知识库中 |

## 记忆信息的写入与删除

`viking_remember` 工具会通过发送 `POST /api/v1/content/write` 请求并设置 `mode=create` 参数，直接将信息写入 OpenViking。这样会在 `viking://user/peers/${OPENVIKING_AGENT}/memories/...` 路径下创建属于对应对等体的记忆文件；在启用 API 密钥的模式下，OpenViking 可能会返回标准化的用户级路径，例如 `viking://user/default/peers/${OPENVIKING_AGENT}/memories/...`。通过该工具进行的显式记忆存储操作无需依赖会话提交的提取过程。

当本地的记忆操作成功完成后，Hermes 内置的 `memory` 工具所执行的操作也会同步到 OpenViking 中：

| Hermes 操作 | OpenViking 对应操作 |
|---------------|----------------------|
| `add` | 在配置好的对等体记忆命名空间下，通过 `content/write` 且设置 `mode=create` 来添加记忆信息 |

而内置的 `replace` 和 `remove` 操作则不会被同步，因为 Hermes 原生的记忆条目目前还不包含稳定的 OpenViking 文件 URI。如果用户明确要求删除某个特定的 OpenViking 记忆 URI，可使用 `viking_forget` 工具。

`viking_forget` 工具的设计范围较为有限，它仅接受具体的用户记忆文件 URI，例如 `viking://user/peers/hermes/memories/preferences/mem_abc123.md` 或标准化的路径 `viking://user/default/peers/hermes/memories/preferences/mem_abc123.md`。由于 OpenViking 支持，位于 `memories/` 目录下的文件，如 `viking://user/default/memories/profile.md`，也是可以被删除的。该工具不会接受目录、资源、技能信息、会话数据、生成的摘要文件，以及包含查询字符串或片段信息的 URI。若需要批量清理更复杂的资源和目录，建议使用 OpenViking 的 MCP、CLI 或管理 API。
