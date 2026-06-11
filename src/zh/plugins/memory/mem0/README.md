# Mem0 内存提供器

基于服务器端的大型语言模型事实抽取功能，具备语义搜索、重排序及自动去重能力。

## 前提条件

- 安装 `pip install mem0ai` 工具
- 从 [app.mem0.ai](https://app.mem0.ai) 获取 Mem0 API 密钥

## 配置步骤

```bash
hermes memory setup    # select "mem0"
```

或手动操作：
```bash
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

## 配置

配置文件：`$
