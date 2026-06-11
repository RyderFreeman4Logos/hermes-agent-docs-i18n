# 多网关部署

Hermes 支持同时运行多个网关进程——每个配置文件对应一个网关（默认、writer、admin、coder、researcher）。每个网关都会建立独立的连接来访问平台 API，并为其所在配置文件的订阅者传递消息。

## 单调度器模式

仅有一个网关拥有看板调度器权限。该网关会保持 `kanban.dispatch_in_gateway: true` 的设置（为默认值）；其他所有网关则将其设置为 `false`。

**原因如下：** 当某个网关的 `dispatch_in_gateway: true` 时，它将为调度器和通知监听器分别打开针对每个看板的 SQLite 连接。若多个网关同时这样做，会导致每个 `kanban.db` 文件的打开文件描述符数量增加，进而加剧 WAL `-shm` 读取端的竞争。通过同一个标志控制这两条路径，可确保仅有单个进程能够访问看板数据库。

## 配置方式

对于拥有调度器权限的网关（通常是 `default` 配置文件），无需进行任何修改。对于其他所有配置文件的网关，请在 `~/.hermes/config.yaml` 中添加相应配置：

```yaml
kanban:
  dispatch_in_gateway: false
```

或者设置环境变量：`HERMES_KANBAN_DISPATCH_IN_GATEWAY=false`

## 各种网关的功能说明

| 网关角色 | dispatch_in_gateway | 是否为每张看板创建独立数据库？ | 是否运行调度器与通知器？ |
|---|---|---|---|
| 默认角色（调度负责人） | true（默认值） | 是 | 是 |
| 编辑者、管理员、开发者等 | false | 否 | 否 |

非调度型网关仍会为其所属的平台适配器（如 Telegram、Discord 等）传递消息——只是不会轮询看板状态。
