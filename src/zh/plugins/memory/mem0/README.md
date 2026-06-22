# Mem0 内存提供器

基于服务器端的大语言模型事实提取功能，具备语义搜索、重排序及自动去重能力。

同时支持 [Mem0 Cloud](https://app.mem0.ai) 服务以及自托管实例。

## 前提条件

- 安装 `pip install mem0ai` 工具
- Mem0 Cloud API 密钥 **或** 自托管的 Mem0 服务器

## 设置指南

### 云服务版本

```bash
hermes memory setup    # select "mem0"
```

或手动操作：

```bash
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

### 自托管模式

```bash
hermes config set memory.provider mem0
echo "MEM0_HOST=http://your-mem0-server:24220" >> ~/.hermes/.env
echo "MEM0_API_KEY=your-api-key" >> ~/.hermes/.env   # if auth is enabled
```

## 配置

配置文件：`$
