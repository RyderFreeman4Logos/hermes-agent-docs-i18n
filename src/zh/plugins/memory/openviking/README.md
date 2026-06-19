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

所有配置均通过 `.env` 文件中的环境变量进行设置：

| 环境变量 | 默认值 | 描述 |
|---------|---------|-------------|
| `OPENVIKING_ENDPOINT` | `http://127.0.0.1:1933` | 服务器地址 |
| `OPENVIKING_API_KEY` | （无） | 用于身份验证的服务器用户/管理员 API 密钥 |
| `OPENVIKING_ACCOUNT` | `default` | 本地/可信模式下的租户账户 |
| `OPENVIKING_USER` | `default` | 本地/可信模式下的租户用户 |
| `OPENVIKING_AGENT` | `hermes` | OpenViking 中的 Hermes 对等体 ID，用于基于对等体的记忆管理 |

当设置了 `OPENVIKING_API_KEY` 后，Hermes 会允许 OpenViking 根据该密钥推断出账户/用户身份。在未使用 API 密钥的本地或可信部署环境中，Hermes 会通过身份标识头传递 `OPENVIKING_ACCOUNT` 和 `OPENVIKING_USER` 的值。

## 工具

| 工具 | 描述 |
|------|-------------|
| `viking_search` | 支持快速/深度/自动模式的语义搜索功能 |
| `viking_read` | 读取 viking:// URI 指定的内容（摘要/概览/完整版） |
| `viking_browse` | 具有文件系统风格的导航功能（列表/树形结构/统计信息） |
| `viking_remember` | 存储某项事实，以便在会话结束时提取使用 |
| `viking_add_resource` | 将 URL 或文档导入知识库中 |
