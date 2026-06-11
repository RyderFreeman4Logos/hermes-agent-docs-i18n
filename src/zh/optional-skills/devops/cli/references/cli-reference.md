# CLI 参考手册

## 安装指南

```bash
curl -fsSL https://cli.inference.sh | sh
```

## 全局命令

| 命令 | 描述 |
|---------|-------------|
| `infsh help` | 显示帮助信息 |
| `infsh version` | 显示 CLI 版本号 |
| `infsh update` | 将 CLI 更新至最新版本 |
| `infsh login` | 进行身份验证 |
| `infsh me` | 显示当前用户信息 |

## 应用命令

### 应用发现

| 命令 | 描述 |
|---------|-------------|
| `infsh app list` | 列出所有可用应用 |
| `infsh app list --category <cat>` | 按类别筛选（图片、视频、音频、文本、其他） |
| `infsh app search <query>` | 搜索应用 |
| `infsh app list --search <query>` | 通过标志形式搜索应用 |
| `infsh app list --featured` | 显示精选应用 |
| `infsh app list --new` | 按最新发布顺序排序 |
| `infsh app list --page <n>` | 分页显示 |
| `infsh app list -l` | 以详细表格形式展示 |
| `infsh app list --save <file>` | 将结果保存为 JSON 文件 |
| `infsh app my` | 列出您已部署的应用 |
| `infsh app get <app>` | 获取应用详情 |
| `infsh app get <app> --json` | 以 JSON 格式获取应用详情 |

### 应用执行

| 命令 | 描述 |
|---------|-------------|
| `infsh app run <app> --input <file>` | 使用输入文件运行应用 |
| `infsh app run <app> --input '<json>'` | 使用内联 JSON 运行应用 |
| `infsh app run <app> --input <file> --no-wait` | 不等待任务完成即运行 |
| `infsh app sample <app>` | 显示示例输入内容 |
| `infsh app sample <app> --save <file>` | 将示例内容保存到文件 |

## 任务命令

| 命令 | 描述 |
|---------|-------------|
| `infsh task get <task-id>` | 获取任务状态及结果 |
| `infsh task get <task-id> --json` | 以 JSON 格式获取任务信息 |
| `infsh task get <task-id> --save <file>` | 将任务结果保存到文件 |

### 开发相关命令

| 命令 | 描述 |
|---------|-------------|
| `infsh app init` | 创建新应用（交互式方式） |
| `infsh app init <name>` | 指定名称创建新应用 |
| `infsh app test --input <file>` | 在本地测试应用 |
| `infsh app deploy` | 部署应用 |
| `infsh app deploy --dry-run` | 不实际部署，仅进行验证 |
| `infsh app pull <id>` | 拉取应用源代码 |
| `infsh app pull --all` | 拉取您所有的应用 |

## 环境变量

| 变量 | 描述 |
|----------|-------------|
| `INFSH_API_KEY` | API 密钥（优先于配置文件中的设置） |

## Shell 自动补全功能

```bash
# Bash
infsh completion bash > /etc/bash_completion.d/infsh

# Zsh
infsh completion zsh > "${fpath[1]}/_infsh"

# Fish
infsh completion fish > ~/.config/fish/completions/infsh.fish
```

## 应用名称格式

应用采用 `namespace/app-name` 的格式命名：

- `falai/flux-dev-lora` - fal.ai 的 FLUX 2 Dev
- `google/veo-3` - Google 的 Veo 3
- `infsh/sdxl` - inference.sh 的 SDXL
- `bytedance/seedance-1-5-pro` - ByteDance 的 Seedance
- `xai/grok-imagine-image` - xAI 的 Grok

版本固定方式：`namespace/app-name@version`

## 文档资源

- [CLI 设置](https://inference.sh/docs/extend/cli-setup) - 完整的 CLI 安装指南
- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [创建应用](https://inference.sh/docs/extend/creating-app) - 自行构建应用
- [部署应用](https://inference.sh/docs/extend/deploying) - 将应用部署到云端
