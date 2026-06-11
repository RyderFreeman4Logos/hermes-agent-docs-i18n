# Supermemory 内存提供器

这款语义长期记忆系统具备档案检索、语义搜索、显性记忆工具等功能，同时支持整场对话的导入（每场对话仅可导入一次），从而帮助构建更丰富的用户档案。

## 前提条件

- 安装 `pip install supermemory` 工具
- 获取来自 [supermemory.ai](https://supermemory.ai) 的 Supermemory API 密钥

## 设置步骤

```bash
hermes memory setup    # select "supermemory"
```

或手动操作：

```bash
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

## 配置

配置文件：`$

```json
{
  "container_tag": "hermes-{identity}"
}
```

对于名为 `coder` 的配置文件，其对应的容器标识为 `hermes-coder`；默认配置文件则对应 `hermes-default`。若未指定 `{identity}`，所有配置文件将共享同一个容器。

## 多容器模式

在较为复杂的场景下（例如类似 OpenClaw 的多工作区架构），您可以设置自定义的容器标签，从而使智能体能够在多个命名容器之间进行读写操作：

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "project-beta", "shared-knowledge"],
  "custom_container_instructions": "Use project-alpha for coding tasks, project-beta for research, and shared-knowledge for team-wide facts."
}
```

启用该功能后：
- `supermemory-search`、`supermemory-save`、`supermemory-forget` 以及 `supermemory-profile` 命令会支持可选的 `container_tag` 参数。
- 该标签必须属于白名单范围：主容器加上 `custom_containers`。
- 自动化操作（开启同步、预取、内存写入镜像、会话导入）始终仅使用**主容器**。
- 自定义容器相关指令会被注入到系统提示语中。

## 售后支持

- [Supermemory Discord](https://supermemory.link/discord)
- [support@supermemory.com](mailto:support@supermemory.com)
- [supermemory.ai](https://supermemory.ai)
