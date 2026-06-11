# 1Password CLI 入门指南（概要）

官方文档：https://developer.1password.com/docs/cli/get-started/

## 核心操作流程

1. 安装 `op` CLI 工具。
2. 在 1Password 应用中开启桌面应用集成功能。
3. 解锁应用。
4. 运行 `op signin` 命令并确认授权提示。
5. 使用 `op whoami` 命令验证当前登录状态。

## 多账户管理

- 使用命令 `op signin --account <subdomain.1password.com>` 指定特定账户登录。
- 或直接设置环境变量 `OP_ACCOUNT` 来指定目标账户。

## 非交互式/自动化场景

- 通过服务账户及 `OP_SERVICE_ACCOUNT_TOKEN` 实现自动化操作。
- 在运行时处理敏感信息时，建议优先使用 `op run` 和 `op inject` 命令。
