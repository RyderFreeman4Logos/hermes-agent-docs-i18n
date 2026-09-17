# ComfyUI REST + WebSocket API 参考手册

ComfyUI 提供了 REST + WebSocket 接口，用于工作流的执行与管理。**本地运行与 Comfy Cloud 上的接口形式相同，仅认证方式和路径存在差异。**

## 连接信息

| | 本地 ComfyUI | Comfy Cloud |
|---|---|---|
| 基础 URL | `http://127.0.0.1:8188` | `https://cloud.comfy.org` |
| API 路径前缀 | 无（如 `/prompt`、`/view` 等） | `/api/...`（如 `/api/prompt`、`/api/view` 等） |
| 认证方式 | 无需认证（如已配置则使用承载令牌） | `X-API-Key` 请求头 |
| WebSocket 连接地址 | `ws://host:port/ws?clientId={uuid}` | `wss://cloud.comfy.org/ws?clientId={uuid}&token={API_KEY}` |
| `/api/view` 的响应形式 | 直接返回字节数据 | 302 重定向至带签名的 URL（需使用 `curl -L` 命令） |

技能脚本会通过 `_common.resolve_url()` 函数自动处理 URL 路由。

## Comfy Cloud 上的端点差异

Comfy Cloud 的接口在多个方面与本地 ComfyUI 不同。技能脚本能够透明地处理这些差异；此处对这些差异进行说明，以便直接使用 `curl` 命令的用户能够了解。

| 本地路径 | 云端路径 | 备注 |
|----------|----------|------|
| `/system_stats` | `/api/system_stats` | 云端版本为**公开访问**（无需认证） |
| `/object_info` | `/api/object_info` | **仅限付费套餐** — 免费套餐会返回403错误 |
| `/queue` | `/api/queue` | 仅限付费套餐 |
| `/userdata` | `/api/userdata` | 仅限付费套餐 |
| `/prompt` (POST) | `/api/prompt` (POST) | 仅限付费套餐 |
| `/upload/image` | `/api/upload/image` | 仅限付费套餐；支持子文件夹，但会被忽略 |
| `/upload/mask` | `/api/upload/mask` | 与上述相同 |
| `/view` | `/api/view` | 仅限付费套餐；会**返回302重定向**至签名后的URL |
| `/history` | `/api/history_v2` | **已重命名**；旧路径会返回404错误 |
| `/history/{id}` | `/api/history_v2/{id}` 或 `/api/jobs/{id}` | 两种路径均可使用；通过 `/jobs` 路径可获取完整任务信息 |
| `/models` | `/api/experiment/models` | **已重命名** |
| `/models/{folder}` | `/api/experiment/models/{folder}` | **已重命名**；响应格式有所不同（见下文） |

### 云端模型列表的响应格式

- **本地版本**：`["a.safetensors", "b.safetensors", …]` — 为简单的字符串列表。
- **云端版本**：`[{"name": "a.safetensors", "pathIndex": 0}, …]` — 为对象列表。
- **云端返回404错误且包含 `code: "folder_not_found"`** — 表示该文件夹为空或不存在，并非“端点缺失”错误。可通过查看响应内容来区分。  
  `_common.parse_model_list()` 函数可对这两种格式进行标准化处理。

## 工作流执行

### 提交工作流

```bash
# Local
curl -X POST "http://127.0.0.1:8188/prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": '"$(cat workflow_api.json)"', "client_id": "'"$(uuidgen)"'"}'

# Cloud
curl -X POST "https://cloud.comfy.org/api/prompt" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": '"$(cat workflow_api.json)"'}'
```

**响应：**
```json
{"prompt_id": "abc-123-def", "number": 1, "node_errors": {}}
```

如果 `node_errors` 不为空，说明工作流存在验证错误（节点缺失或输入数据有误）。

### 查看任务状态（云端）

```bash
curl -X GET "https://cloud.comfy.org/api/job/{prompt_id}/status" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY"
```

| 状态        | 描述                              |
| ------------- | ---------------------------------- |
| `pending`     | 任务已排队，正在等待启动            |
| `in_progress` | 任务当前正在执行中                |
| `completed`   | 任务已成功完成                    |
| `failed`      | 任务执行过程中出现错误              |
| `cancelled`   | 任务已被用户取消                    |

### 带输出结果的任务详情（云端版）

```bash
curl -X GET "https://cloud.comfy.org/api/jobs/{prompt_id}" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY"
```

响应中会包含以节点 ID 为键的 `outputs` 字段。在云端环境中，输出结构中使用的是单数形式的 `video`；而在本地环境中，则使用复数形式的 `videos`。这些技能脚本能够接受这两种格式。

### 查看历史记录（本地模式）

```bash
curl -s "http://127.0.0.1:8188/history"          # all
curl -s "http://127.0.0.1:8188/history/{id}"     # one prompt_id
```

本地条目格式：
```json
{
  "<prompt_id>": {
    "prompt": [...],
    "outputs": {"<node_id>": {"images": [...]}},
    "status": {
      "status_str": "success" | "error",
      "completed": true | false,
      "messages": [["execution_start", {...}], ["execution_error", {...}], …]
    }
  }
}
```

**重要提示：**在查看任务状态时，请先检查`status_str == "error"`，然后再查看`completed`，因为任务执行失败时这两个值都可能为真。

### 下载结果

```bash
# Local (direct bytes)
curl -s "http://127.0.0.1:8188/view?filename=ComfyUI_00001_.png&subfolder=&type=output" \
  -o output.png

# Cloud (302 → signed URL; -L follows; STRIP X-API-Key for the second hop)
curl -L "https://cloud.comfy.org/api/view?filename=...&type=output" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -o output.png
```

该技能的 `run_workflow.py` 会在跨主机重定向时自动移除 `X-API-Key`，因此经过签名的 URL 永远不会包含您的认证信息。

## WebSocket 监控

连接以获取实时的执行事件。

```bash
# Local
wscat -c "ws://127.0.0.1:8188/ws?clientId=MY-UUID"

# Cloud
wscat -c "wss://cloud.comfy.org/ws?clientId=MY-UUID&token=$COMFY_CLOUD_API_KEY"
```

**注意：**在云端环境中，`clientId` 参数目前会被忽略——该用户的所有消息都会被广播给所有连接。建议通过 `data.prompt_id` 在客户端对消息进行过滤。

### JSON消息类型

| 类型 | 触发场景 | 关键字段 |
|------|----------|----------|
| `status` | 队列状态变化 | `status.exec_info.queue_remaining` |
| `notification` | 友好的状态描述字符串 | `value` |
| `execution_start` | 工作流开始执行 | `prompt_id` |
| `executing` | 节点正在运行（若本地环境中 `node` 为 `null`，则表示运行结束） | `node`, `prompt_id` |
| `progress` | 正在执行采样步骤 | `node`, `value`, `max` |
| `progress_state` | 包含各节点详细信息的扩展进度信息 | `nodes`（字典格式） |
| `executed` | 节点输出已准备好 | `node`, `output`（可能包含 `images`/`video` 等内容） |
| `execution_cached` | 因缓存原因跳过的节点 | `nodes`（节点ID列表） |
| `execution_success` | 全部执行完成 | `prompt_id` |
| `execution_error` | 执行失败 | `exception_type`, `exception_message`, `traceback`, `node_id` |
| `execution_interrupted` | 执行被中断 | `prompt_id` |

### 二进制帧（预览图像）

| 类型码 | 含义 |
|---------|------|
| `0x00000001` | `PREVIEW_IMAGE` — `[type:4][image_type:4][data]`（其中 image_type 1=JPEG，2=PNG） |
| `0x00000003` | `TEXT` — `[type:4][nid_len:4][nid][text]`（文本为UTF-8编码） |
| `0x00000004` | `PREVIEW_IMAGE_WITH_METADATA` — `[type:4][meta_len:4][json][image_data]` |

可使用命令 `scripts/ws_monitor.py --previews <dir>` 将预览帧保存到磁盘。

## 文件上传

```bash
# Image
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# Returns: {"name": "photo.png", "subfolder": "", "type": "input"}

# Mask (linked to a previously uploaded image)
curl -X POST "http://127.0.0.1:8188/upload/mask" \
  -F "image=@mask.png" -F "type=input" \
  -F 'original_ref={"filename":"photo.png","subfolder":"","type":"input"}'
```

云端对应方案：在请求地址前添加 `https://cloud.comfy.org/api`，并同时加入 `-H "X-API-Key: $COMFY_CLOUD_API_KEY"`。

## 节点与模型检索

```bash
# All node types and their input specs
curl -s "http://127.0.0.1:8188/object_info" | python3 -m json.tool

# Specific node
curl -s "http://127.0.0.1:8188/object_info/KSampler"

# Models per folder (local)
curl -s "http://127.0.0.1:8188/models/checkpoints"
curl -s "http://127.0.0.1:8188/models/loras"

# Models per folder (cloud — note the experimental prefix)
curl -s "https://cloud.comfy.org/api/experiment/models/checkpoints" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY"
```

## 队列管理

```bash
# View queue
curl -s "http://127.0.0.1:8188/queue"

# Clear all pending
curl -X POST "http://127.0.0.1:8188/queue" \
  -H "Content-Type: application/json" \
  -d '{"clear": true}'

# Delete specific items
curl -X POST "http://127.0.0.1:8188/queue" \
  -H "Content-Type: application/json" \
  -d '{"delete": ["prompt_id_1", "prompt_id_2"]}'

# Cancel currently-running job
curl -X POST "http://127.0.0.1:8188/interrupt"
```

## 系统管理

```bash
# Stats (VRAM, RAM, GPU, ComfyUI version)
curl -s "http://127.0.0.1:8188/system_stats"

# Free GPU memory
curl -X POST "http://127.0.0.1:8188/free" \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'
```

## ComfyUI-Manager 接口（可选）

使用这些接口前需先安装 ComfyUI-Manager。它们便于通过 API 而非 `comfy-cli` 来安装节点或模型。

```bash
# Install a custom node from a git URL
curl -X POST "http://127.0.0.1:8188/manager/queue/install" \
  -H "Content-Type: application/json" \
  -d '{"git_url": "https://github.com/user/comfyui-node.git"}'

# Check install queue status
curl -s "http://127.0.0.1:8188/manager/queue/status"

# Install model
curl -X POST "http://127.0.0.1:8188/manager/queue/install_model" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://...", "path": "models/checkpoints", "filename": "model.safetensors"}'
```

## POST /prompt 请求载荷格式

```json
{
  "prompt": {
    "3": {
      "class_type": "KSampler",
      "inputs": {
        "seed": 42,
        "steps": 20,
        "cfg": 7.5,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1.0,
        "model": ["4", 0],
        "positive": ["6", 0],
        "negative": ["7", 0],
        "latent_image": ["5", 0]
      }
    }
  },
  "client_id": "unique-uuid-for-ws-filtering",
  "extra_data": {
    "api_key_comfy_org": "optional-PARTNER-NODE-key (NOT the cloud auth key)"
  }
}
```

- `prompt`：API 格式的流程图  
- `client_id`：UUID —— 本地服务器会用它来筛选 WebSocket 事件；云端服务则忽略该字段。  
- `extra_data.api_key_comfy_org`：仅当流程中使用合作伙伴节点（如 Flux Pro、Ideogram 等）时才需要。请勿与 `X-API-Key` 混淆。  

## 错误类型（云端：`execution_error` `exception_type`）

| 类型 | 含义 |
|------|------|
| `ValidationError` | 流程或输入有误（通常通过 `node_errors` 更清晰地显示错误信息） |
| `ModelDownloadError` | 所需模型不可用 |
| `ImageDownloadError` | 无法从 URL 获取输入图像 |
| `OOMError` | GPU 内存不足 |
| `InsufficientFundsError` | 账户余额过低（适用于合作伙伴节点） |
| `InactiveSubscriptionError` | 订阅未处于有效状态 |
