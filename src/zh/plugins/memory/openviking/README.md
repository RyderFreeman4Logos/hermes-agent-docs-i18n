# OpenViking 内存提供程序

由 Volcengine（字节跳动）开发的上下文数据库，具备文件系统式的知识层级结构、分层检索功能以及自动内存提取能力。

## 前提条件

- 已安装 OpenViking，并且可以调用 `openviking-server` 命令
- OpenViking 服务器配置已完成初始化并通过验证（先执行 `openviking-server init`，再执行 `openviking-server doctor`）
- OpenViking 服务器正在运行，且可从 Hermes 进行访问

建议使用 OpenViking 0.2.10 或更高版本。为确保向后兼容性，Hermes 能够识别那些仅返回传统状态信息的旧版服务器，但前提是匿名 OpenAPI 元数据也将该服务标识为 OpenViking。对于此集成而言，OpenViking 0.2.6 及更早版本已不再被支持；请升级到最新版本以获得当前的健康检查接口及兼容性修复。

## 设置步骤

首先需要准备 OpenViking：

```bash
openviking-server init
openviking-server doctor
openviking-server
```

接下来配置 Hermes：

```bash
hermes memory setup    # select "openviking"
```

该设置可以链接到现有的 `~/.openviking/ovcli.conf` 文件，将其当前的连接参数复制到 Hermes 中；如果该文件不存在，则会自动生成一个最简版的 `ovcli.conf`。

或者也可以手动操作：

```bash
hermes config set memory.provider openviking
```

请将连接设置添加到当前激活配置文件的 `.env` 文件中。默认配置文件位于 `~/.hermes/.env`；若使用自定义配置文件，则路径为 `~/.hermes/profiles/<profile>/.env`。

```text
OPENVIKING_ENDPOINT=http://127.0.0.1:1933
# OPENVIKING_API_KEY=...
# OPENVIKING_ACCOUNT=default
# OPENVIKING_USER=default
```

## 配置

OpenViking 的服务器配置与 Hermes 是相互独立的：

- `ov.conf` 用于配置 OpenViking 的存储系统、嵌入式/VLM 模型、认证机制以及服务器运行行为。该文件可从 `--config`、`OPENVIKING_CONFIG_FILE` 或 `~/.openviking/ov.conf` 路径读取。
- `ovcli.conf` 则用于存储客户端/CLI 连接相关的参数，如 `url`、`api_key`、`account` 和 `user`。这些参数可从 `OPENVIKING_CLI_CONFIG_FILE` 或 `~/.openviking/ovcli.conf` 路径读取。

Hermes 端的提供程序配置则通过当前激活配置文件中的 `.env` 文件里的环境变量来加载：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENVIKING_ENDPOINT` | `http://127.0.0.1:1933` | 服务器地址 |
| `OPENVIKING_API_KEY` | （无） | 用于需要身份验证的服务器的用户/管理员 API 密钥 |
| `OPENVIKING_ACCOUNT` | `default` | 本地/可信模式下的租户账户 |
| `OPENVIKING_USER` | `default` | 本地/可信模式下的租户用户 |
| `OPENVIKING_AGENT` | （无） | 用于创建独立助手上下文的可选对等体标识 |

当设置了 `OPENVIKING_API_KEY` 后，Hermes 会允许 OpenViking 根据该密钥推断出账户/用户身份。在未使用 API 密钥的本地或可信模式下，Hermes 会通过身份标识头部字段传递 `OPENVIKING_ACCOUNT` 和 `OPENVIKING_USER`。此外，在向 OpenViking 发送请求时，Hermes 还会附加 `User-Agent: openviking-memory-hermes/<版本号>` 这一标准标识符。该标识符包含 Hermes 的版本信息，但不包含特定用户的标识，也不会产生额外的请求。

### 可选的对等体身份标识

默认情况下，新建立的连接会使用 OpenViking 用户的内存目录。设置过程中无需输入对等方 ID。若未配置对等方，Hermes 将不会发送 `X-OpenViking-Actor-Peer` 头部信息，也不会包含 `peer_id` 的助手消息。

如需为不同的助手设置独立上下文，请在当前激活配置文件的 `config.yaml` 中修改现有的 `agent` 字段：

```yaml
memory:
  openviking:
    agent: work-assistant
```

现有的非空 `OPENVIKING_AGENT`、YAML 格式的 `agent` 配置，以及已关联的 OpenViking `actor_peer_id` 或旧版 `agent_id` 值，其原有功能均保持不变。配置解析的优先级仍为：环境设置 → 已关联的 OpenViking 配置 → Hermes YAML 文件。若不想使用任何对等节点，可从所有已配置的来源中移除对应的对等节点信息，然后启动一个新的 Hermes 会话。

升级操作不会移动或删除现有的记忆体数据。那些原本依赖旧版隐式 `hermes` 对等节点的实例，在进行新数据写入时将使用用户记忆体。在没有对等节点 ID 的情况下，默认的 OpenViking 搜索功能会同时检索用户记忆体以及同一 OpenViking 用户下的现有对等节点记忆体。旧的对等节点记忆体仍会保留在原有路径中，并可继续被搜索。返回哪些记忆体由排序规则和结果数量限制决定。如果需要更精确的检索结果，建议保留对等节点 ID。

将 `agent: hermes` 设置为该值，即可恢复基于对等节点范围的写入功能。在此设置变更之前以用户范围写入的记忆体仍会保留在原处且可被搜索。此设置仅影响后续的写入操作，不会改变现有记忆体的存储位置。

## 工具

| 工具 | 描述 |
|------|------|
| `viking_search` | 支持快速/深度/自动三种模式的语义搜索功能 |
| `viking_read` | 读取 viking:// URI 格式的内容（摘要/概览/完整版） |
| `viking_browse` | 提供类似文件系统的导航功能（列表/树形结构/统计信息） |
| `viking_remember` | 通过 OpenViking 会话中的记忆体提取功能提交新事实 |
| `viking_forget` | 删除一个特定的 viking:// 记忆体文件 URI |
| `viking_add_resource` | 将网址或文档导入知识库中 |

## 记忆体的写入与删除

`viking_remember`功能会创建一个一次性的`hermes-remember-<随机字符串>`格式的OpenViking会话，将该事实作为一条消息添加进去，随后关闭该会话且不保留任何历史记录。该会话仍保存在OpenViking中以便后续审计。之后，OpenViking会对该内容进行分类，并通过其常规提取流程来决定是新增记忆、合并现有记忆还是跳过处理。当服务器提供相应信息时，该工具会返回此次一次性会话的ID以及提取任务ID；在工具返回后，提取工作会以异步方式继续进行。

该工具返回`status: submitted`状态，是因为提取过程可能仅完成记忆的新增、将相关事实合并到现有记忆中，或者根本不执行任何记忆操作。它并不保证OpenViking一定会生成独立的记忆文件。该事实会以未被修改的`user`消息形式被提交，因此最终的分类工作由OpenViking决定。虽然现有的调用方仍可使用旧版的`category`参数，但该参数既不会在文档中提及，也不会被实际使用。由于这种一次性会话与正在进行的Hermes对话是相互独立的，因此执行“记住”操作并不会保存或切换当前的对话会话。

如果消息请求或提交失败，错误信息中会包含标准的会话 URI、失败的阶段、当前消息的状态，以及一条 `ov session commit <session-id>` 的恢复命令。首先需检查该会话状态。若存在归档记录，则表示提交已成功完成；而若存在非空的实时 `messages.jsonl` 文件但无归档记录，则说明消息虽已被接收，但仍需进行提交操作。若实时文件为空且无归档记录，则状态不明确，不得触发自动重新提交。如需手动恢复，请使用与 Hermes 相同的 OpenViking 配置文件及凭据。默认情况下，OpenViking 服务器会禁用自动提交功能，因此那些虽已被接收但明确提交失败的消息通常会保持在线状态且未被提取，直至手动完成提交。

当本地内存操作成功后，Hermes 内置的 `memory` 工具操作结果也会同步到 OpenViking 中：

| Hermes 操作 | OpenViking 操作 |
|---------------|----------------------|
| `add`         | 在用户内存或配置好的对等节点内存目录下执行 `content/write` 操作，且设置 `mode=create` |

由于 Hermes 原生的内存条目目前还不具备稳定的 OpenViking 文件 URI，因此内置的 `replace` 和 `remove` 操作不会被同步。若用户明确要求删除某个特定的 OpenViking 内存 URI，则可使用 `viking_forget` 命令。

`viking_forget` 的功能设计较为有限。它仅能处理具体的用户记忆文件 URI，例如 `viking://user/default/peers/hermes/memories/preferences/mem_abc123.md`（任何明确的用户 ID 均可使用；在服务器会自动解析主目录别名的部署场景中，输入的 `viking://~/...` 格式地址将原样传递）。由于 OpenViking 支持此类格式，直接位于 `memories/` 目录下的文件，如 `viking://user/default/memories/profile.md`，也同样可以被处理。该工具不会接受目录、资源、技能信息、会话数据、自动生成的摘要文件，以及包含查询字符串或片段标识的 URI。若需清理更广泛的资源和目录，建议使用 OpenViking 的 MCP、CLI 或管理 API。
