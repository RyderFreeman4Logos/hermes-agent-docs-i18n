# ByteRover 内存提供器

通过 `brv` CLI 实现持久化内存功能——基于分层知识树的结构，支持多级检索（从模糊文本到由大语言模型驱动的搜索）。

## 前提条件

请先安装 ByteRover CLI：
```bash
curl -fsSL https://byterover.dev/install.sh | sh
# or
npm install -g byterover-cli
```

## 设置

```bash
hermes memory setup    # select "byterover"
```

或手动操作：
```bash
hermes config set memory.provider byterover
# Optional cloud sync:
echo "BRV_API_KEY=your-key" >> ~/.hermes/.env
```

## 配置

| 环境变量 | 是否必填 | 描述 |
|---------|----------|-------------|
| `BRV_API_KEY` | 否 | 云同步密钥（可选，默认为本地优先模式） |

工作目录：`$
