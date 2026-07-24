---
title: "Inference Sh Cli — Run 150+ AI apps (image, video, LLM) via inference"
sidebar_label: "Inference Sh Cli"
description: "Run 150+ AI apps (image, video, LLM) via inference"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# inference.sh CLI

通过 inference.sh CLI 运行 150 多种 AI 应用（图像、视频、大语言模型）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/devops/cli` 安装 |
| 路径 | `optional-skills/devops/cli` |
| 版本 | `1.0.0` |
| 创建者 | okaris |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `AI`、`图像生成`、`视频`、`LLM`、`搜索`、`推理`、`FLUX`、`Veo`、`Claude` |

## 参考：完整 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体将看到这些指令作为操作指南。
:::

# inference.sh CLI

通过简洁的 CLI 在云端运行 150 多种 AI 应用，无需 GPU。

所有命令均通过 **终端工具** 来执行 `infsh` 命令。

## 适用场景

- 用户请求生成图像（FLUX、Reve、Seedream、Grok、Gemini 图像）
- 用户请求生成视频（Veo、Wan、Seedance、OmniHuman）
- 用户询问关于 inference.sh 或 infsh 的相关问题
- 用户希望运行 AI 应用而无需管理各个服务提供商的 API
- 用户需要基于 AI 的搜索功能（Tavily、Exa）
- 用户需要生成头像或同步嘴唇动作

## 先决条件

必须已安装并完成身份验证 `infsh` CLI。可通过以下方式进行检查：

```bash
infsh me
```

如果尚未安装：

```bash
curl -fsSL https://cli.inference.sh | sh
infsh login
```

有关完整的设置详细信息，请参阅 `references/authentication.md` 文件。

## 工作流程

### 1. 始终先进行搜索

切勿凭猜测确定应用名称——务必通过搜索来找到正确的应用 ID：

```bash
infsh app list --search flux
infsh app list --search video
infsh app list --search image
```

### 2. 运行应用

请使用搜索结果中显示的准确应用编号。为获得机器可读取的输出格式，务必使用 `--json` 参数：

```bash
infsh app run <app-id> --input '{"prompt": "your prompt here"}' --json
```

### 3. 解析输出结果

JSON格式的输出中包含已生成媒体的网址。可通过`MEDIA:<url>`的格式将这些网址呈现给用户，以便在界面中直接显示。

## 常用命令

### 图像生成

```bash
# Search for image apps
infsh app list --search image

# FLUX Dev with LoRA
infsh app run falai/flux-dev-lora --input '{"prompt": "sunset over mountains", "num_images": 1}' --json

# Gemini image generation
infsh app run google/gemini-2-5-flash-image --input '{"prompt": "futuristic city", "num_images": 1}' --json

# Seedream (ByteDance)
infsh app run bytedance/seedream-5-lite --input '{"prompt": "nature scene"}' --json

# Grok Imagine (xAI)
infsh app run xai/grok-imagine-image --input '{"prompt": "abstract art"}' --json
```

### 视频生成

```bash
# Search for video apps
infsh app list --search video

# Veo 3.1 (Google)
infsh app run google/veo-3-1-fast --input '{"prompt": "drone shot of coastline"}' --json

# Seedance (ByteDance)
infsh app run bytedance/seedance-1-5-pro --input '{"prompt": "dancing figure", "resolution": "1080p"}' --json

# Wan 2.5
infsh app run falai/wan-2-5 --input '{"prompt": "person walking through city"}' --json
```

### 本地文件上传

当您提供文件路径时，CLI会自动上传该本地文件：

```bash
# Upscale a local image
infsh app run falai/topaz-image-upscaler --input '{"image": "/path/to/photo.jpg", "upscale_factor": 2}' --json

# Image-to-video from local file
infsh app run falai/wan-2-5-i2v --input '{"image": "/path/to/image.png", "prompt": "make it move"}' --json

# Avatar with audio
infsh app run bytedance/omnihuman-1-5 --input '{"audio": "/path/to/audio.mp3", "image": "/path/to/face.jpg"}' --json
```

### 搜索与调研

```bash
infsh app list --search search
infsh app run tavily/tavily-search --input '{"query": "latest AI news"}' --json
infsh app run exa/exa-search --input '{"query": "machine learning papers"}' --json
```

### 其他类别

```bash
# 3D generation
infsh app list --search 3d

# Audio / TTS
infsh app list --search tts

# Twitter/X automation
infsh app list --search twitter
```

## 常见问题

1. **切勿猜测应用 ID**——务必先运行 `infsh app list --search <term>`。应用 ID 随时会发生变化，同时也会不断有新应用添加。
2. **始终使用 `--json` 参数**——原始输出格式难以解析。使用 `--json` 参数即可获得包含 URL 的结构化输出。
3. **检查认证状态**——如果命令因认证错误而失败，请运行 `infsh login`，或确认 `INFSH_API_KEY` 已正确设置。
4. **长时间运行的应用**——视频生成过程可能需要 30 到 120 秒。终端工具的超时时间应足够长，但仍建议告知用户该过程可能需要一些时间。
5. **输入格式**——`--input` 参数要求输入 JSON 字符串，请确保正确转义引号。

## 参考文档

- `references/authentication.md` —— 认证设置、登录及 API 密钥相关说明
- `references/app-discovery.md` —— 搜索与浏览应用目录的方法
- `references/running-apps.md` —— 运行应用、输入格式及输出处理方式
- `references/cli-reference.md` —— 完整的 CLI 命令参考手册
