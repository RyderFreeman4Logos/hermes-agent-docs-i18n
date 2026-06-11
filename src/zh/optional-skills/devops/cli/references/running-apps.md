# 运行应用

## 基本运行方式

```bash
infsh app run user/app-name --input input.json
```

## 内联 JSON

```bash
infsh app run falai/flux-dev-lora --input '{"prompt": "a sunset over mountains"}'
```

## 版本锁定机制

```bash
infsh app run user/app-name@1.0.0 --input input.json
```

## 本地文件上传

当您提供文件路径而非 URL 时，CLI 会自动上传该本地文件。所有支持 URL 的字段也同样支持本地路径：

```bash
# Upscale a local image
infsh app run falai/topaz-image-upscaler --input '{"image": "/path/to/photo.jpg", "upscale_factor": 2}'

# Image-to-video from local file
infsh app run falai/wan-2-5-i2v --input '{"image": "./my-image.png", "prompt": "make it move"}'

# Avatar with local audio and image
infsh app run bytedance/omnihuman-1-5 --input '{"audio": "/path/to/speech.mp3", "image": "/path/to/face.jpg"}'

# Post tweet with local media
infsh app run x/post-create --input '{"text": "Check this out!", "media": "./screenshot.png"}'
```

支持的路径类型：
- 绝对路径：`/home/user/images/photo.jpg`
- 相对路径：`./image.png`、`../data/video.mp4`
- 主目录路径：`~/Pictures/photo.jpg`

## 生成示例输入文件

在运行之前，先生成一个示例输入文件：

```bash
infsh app sample falai/flux-dev-lora
```

保存到文件：

```bash
infsh app sample falai/flux-dev-lora --save input.json
```

接着编辑 `input.json` 并运行：

```bash
infsh app run falai/flux-dev-lora --input input.json
```

## 工作流示例

### 使用 FLUX 进行图像生成

```bash
# 1. Get app details
infsh app get falai/flux-dev-lora

# 2. Generate sample input
infsh app sample falai/flux-dev-lora --save input.json

# 3. Edit input.json
# {
#   "prompt": "a cat astronaut floating in space",
#   "num_images": 1,
#   "image_size": "landscape_16_9"
# }

# 4. Run
infsh app run falai/flux-dev-lora --input input.json
```

### 使用 Veo 进行视频生成

```bash
# 1. Generate sample
infsh app sample google/veo-3-1-fast --save input.json

# 2. Edit prompt
# {
#   "prompt": "A drone shot flying over a forest at sunset"
# }

# 3. Run
infsh app run google/veo-3-1-fast --input input.json
```

### 文本转语音

```bash
# Quick inline run
infsh app run falai/kokoro-tts --input '{"text": "Hello, this is a test."}'
```

## 任务跟踪

运行应用时，命令行界面会显示任务编号：

```
Running falai/flux-dev-lora
Task ID: abc123def456
```

对于需要长时间运行的任务，您可以随时查看其运行状态：

```bash
# Check task status
infsh task get abc123def456

# Get result as JSON
infsh task get abc123def456 --json

# Save result to file
infsh task get abc123def456 --save result.json
```

### 无需等待即可运行

对于耗时较长的任务，可在后台运行：

```bash
# Submit and return immediately
infsh app run google/veo-3 --input input.json --no-wait

# Check later
infsh task get <task-id>
```

## 输出结果

CLI会直接返回应用程序的输出内容。对于文件类型的输出（图片、视频、音频），系统会提供对应的下载链接。

示例输出：

```json
{
  "images": [
    {
      "url": "https://cloud.inference.sh/...",
      "content_type": "image/png"
    }
  ]
}
```

## 错误处理

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| “无效输入” | 数据结构不匹配 | 使用 `infsh app get` 查看所需字段 |
| “应用未找到” | 应用名称错误 | 使用 `infsh app list --search` 进行查询 |
| “配额已用尽” | 信用额度耗尽 | 检查账户余额 |

## 文档参考

- [运行应用](https://inference.sh/docs/apps/running) - 完整的应用运行指南
- [流式结果输出](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新功能
- [配置参数](https://inference.sh/docs/apps/setup-parameters) - 应用输入参数设置方法
