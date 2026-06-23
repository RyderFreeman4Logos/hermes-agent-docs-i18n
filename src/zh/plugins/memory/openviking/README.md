# OpenViking 内存提供器

由 Volcengine（字节跳动）开发的上下文数据库，具备类似文件系统的知识层级结构、分层检索功能以及自动内存提取能力。

## 前提条件

- 已安装 `pip install openviking`
- OpenViking 服务器正在运行（`openviking-server`）
- 在 `~/.openviking/ov.conf` 文件中已配置好嵌入模型与 VLM 模型

## 设置步骤

```bash
hermes memory setup    # select "openviking"
```

该设置可以链接到现有的 `~/.openviking/ovcli.conf` 文件，将其当前的连接参数复制到 Hermes 中；如果该文件不存在，则会自动生成一个最简版的 `ovcli.conf`。

或者也可以手动操作：
```bash
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

## 配置

所有配置均通过 `.env` 文件中的环境变量设置：

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `OPENVIKING_ENDPOINT` | `http://127.0.0.1:1933` | 服务器地址 |
| `OPENVIKING_API_KEY` | （无） | 用于身份验证的服务器用户/管理员 API 密钥 |
| `OPENVIKING_ACCOUNT` | `default` | 本地/可信模式下的租户账户 |
| `OPENVIKING_USER` | `default` | 本地/可信模式下的租户用户 |
| `OPENVIKING_AGENT` | `hermes` | 在 OpenViking 中的 Hermes 对等体 ID，用于基于对等体的记忆存储 |

当设置了 `OPENVIKING_API_KEY` 后，Hermes 允许 OpenViking 从该密钥中推断出账户/用户身份。在未使用 API 密钥的本地或可信部署环境中，Hermes 会通过身份标识头传递 `OPENVIKING_ACCOUNT` 和 `OPENVIKING_USER`。

## 工具

| 工具 | 描述 |
|------|------|
| `viking_search` | 支持快速/深度/自动模式的语义搜索功能 |
| `viking_read` | 读取 viking:// URI 对应的内容（摘要/概览/完整内容） |
| `viking_browse` | 具有文件系统风格的导航功能（列表/树形结构/统计信息） |
| `viking_remember` | 直接通过 OpenViking 的 `content/write` 接口存储事实信息 |
| `viking_forget` | 删除指定的 viking:// 记忆文件 URI |
| `viking_add_resource` | 将 URL 或文档导入知识库 |

## 记忆存储的写入与删除

`viking_remember` 通过发送 `POST /api/v1/content/write` 请求并设置 `mode=create` 参数，直接将数据写入 OpenViking。它会在 `viking://user/peers/${OPENVIKING_AGENT}/memories/...` 路径下创建基于对等体的记忆文件；在启用 API 密钥的模式下，OpenViking 可能会返回标准化的用户级路径，例如 `viking://user/default/peers/${OPENVIKING_AGENT}/memories/...`。显式存储的记忆数据无需依赖会话提交过程。

当本地记忆操作成功后，Hermes 内置的 `memory` 工具所执行的操作也会同步到 OpenViking：

| Hermes 操作 | OpenViking 对应操作 |
|---------------|----------------------|
| `add` | 在配置好的对等体记忆命名空间下执行 `content/write` 操作，且设置 `mode=create` |

内置的 `replace` 和 `remove` 操作则不会被同步，因为 Hermes 原生的记忆条目目前还不包含稳定的 OpenViking 文件 URI。如果用户明确要求删除某个特定的 OpenViking 记忆 URI，可使用 `viking_forget` 工具。

`viking_forget` 的功能范围较为有限，它仅接受具体的用户记忆文件 URI，例如 `viking://user/peers/hermes/memories/preferences/mem_abc123.md` 或标准化的路径 `viking://user/default/peers/hermes/memories/preferences/mem_abc123.md`。由于 OpenViking 支持，直接位于 `memories/` 目录下的文件，如 `viking://user/default/memories/profile.md`，也是可以被删除的。该工具不会处理目录、资源、技能、会话、生成的摘要文件，以及包含查询字符串或片段路径的 URI。如需更全面地清理资源和目录，可使用 OpenViking 的 MCP、CLI 或管理 API。
