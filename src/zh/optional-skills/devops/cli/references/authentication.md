# 认证与设置

## 安装 CLI 工具

```bash
curl -fsSL https://cli.inference.sh | sh
```

## 登录

```bash
infsh login
```

这将打开浏览器以进行身份验证。登录成功后，相关凭证会存储在本地。

## 检查认证状态

```bash
infsh me
```

若已完成身份验证，将显示您的用户信息。

## 环境变量

对于 CI/CD 流水线或脚本，需设置您的 API 密钥：

```bash
export INFSH_API_KEY=your-api-key
```

环境变量会覆盖配置文件中的设置。

```bash
infsh update
```

或者重新安装：

```bash
curl -fsSL https://cli.inference.sh | sh
```

## 故障排除

| 错误信息 | 解决方案 |
|---------|----------|
| “未通过身份验证” | 运行 `infsh login` 命令 |
| “命令未找到” | 重新安装 CLI 或将其添加到 PATH 环境变量中 |
| “API 密钥无效” | 检查 `INFSH_API_KEY` 的设置或重新登录 |

## 文档参考

- [CLI 设置](https://inference.sh/docs/extend/cli-setup) - 完整的 CLI 安装指南
- [API 身份验证](https://inference.sh/docs/api/authentication) - API 密钥管理方法
- [机密信息管理](https://inference.sh/docs/secrets/overview) - 凭证安全管理指南
