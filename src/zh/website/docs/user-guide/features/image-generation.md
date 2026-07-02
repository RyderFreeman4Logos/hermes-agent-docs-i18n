---
title: Image Generation
description: Generate images via FAL.ai — 11 models including FLUX 2, GPT Image (1.5 & 2), Nano Banana Pro, Ideogram, Recraft V4 Pro, Krea 2, and more, selectable via `hermes tools`.
sidebar_label: Image Generation
sidebar_position: 6
---

# 图像生成

Hermes Agent 能够通过 FAL.ai 根据文本提示词生成图像。系统预置了 11 种模型，每种模型在速度、质量与成本之间各有侧重。用户可通过 `hermes tools` 自行配置当前使用的模型，相关设置会保存在 `config.yaml` 文件中。

## 支持的模型

| 模型 | 生成速度 | 优势特点 | 费用 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `<1秒` | 速度快，文本渲染清晰 | $0.006/百万像素 |
| `fal-ai/flux-2-pro` | 约6秒 | 具有工作室级真实感 | $0.03/百万像素 |
| `fal-ai/z-image/turbo` | 约2秒 | 支持中英文双语，参数量为60亿 | $0.005/百万像素 |
| `fal-ai/nano-banana-pro` | 约8秒 | 基于 Gemini 3 Pro，具备较强的推理能力与文本渲染功能 | $0.15/张（1K分辨率） |
| `fal-ai/gpt-image-1.5` | 约15秒 | 能较好地遵循提示词要求 | $0.034/张 |
| `fal-ai/gpt-image-2` | 约20秒 | 拥有当前最先进的文本渲染技术，支持中文等CJK语言，具备世界级真实感 | $0.04–0.06/张 |
| `fal-ai/ideogram/v3` | 约5秒 | 文字排版效果最佳 | $0.03–0.09/张 |
| `fal-ai/recraft/v4/pro/text-to-image` | 约8秒 | 适用于设计、品牌系统制作，输出结果可直接用于实际应用 | $0.25/张 |
| `fal-ai/qwen-image` | 约12秒 | 基于大语言模型，擅长处理复杂文本 | $0.02/百万像素 |
| `fal-ai/krea/v2/medium/text-to-image` | 约15–25秒 | 适用于插画、动漫、绘画等富有表现力或艺术风格的图像生成 | $0.030–0.035/张 |
| `fal-ai/krea/v2/large/text-to-image` | 约25–60秒 | 能生成具有真实感、原始纹理效果的图像（如运动模糊、颗粒感、电影质感） | $0.060–0.065/张 |

以上费用为撰写本文时 FAL 的定价标准，最新价格请访问 [fal.ai](https://fal.ai/) 查阅。

## 设置流程

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅账户，无需 FAL API 密钥即可通过 **[Tool Gateway](tool-gateway.md)** 功能进行图像生成。无论通过哪种方式，您选择的模型设置都会被保留。新安装的用户可运行 `hermes setup --portal` 进行登录并一次性启用所有网关工具；已有安装的用户则可通过 `hermes tools` 选择 **Nous Subscription** 作为图像生成的后端服务。

如果管理型网关针对某个特定模型返回 `HTTP 4xx` 错误，说明该模型尚未在门户端配置代理——Agent 会告知您问题所在，并提供解决方案（如设置 `FAL_KEY` 实现直接访问，或选择其他模型）。
:::

### 获取 FAL API 密钥

1. 在 [fal.ai](https://fal.ai/) 注册账号
2. 在控制面板中生成 API 密钥

### 配置并选择模型

运行相应的工具命令：

```bash
hermes tools
```

进入**🎨 图像生成**页面，选择您的后端服务（Nous Subscription或FAL.ai），随后界面会以列对齐的表格形式展示所有支持的模型——可使用方向键进行浏览，按回车键进行选择。

```
  Model                          Speed    Strengths                    Price
  fal-ai/flux-2/klein/9b         <1s      Fast, crisp text             $0.006/MP   ← currently in use
  fal-ai/flux-2-pro              ~6s      Studio photorealism          $0.03/MP
  fal-ai/z-image/turbo           ~2s      Bilingual EN/CN, 6B          $0.005/MP
  ...
```

您所做的选择已保存至 `config.yaml` 文件中：

```yaml
image_gen:
  model: fal-ai/flux-2/klein/9b
  use_gateway: false            # true if using Nous Subscription
```

### GPT-图像质量

`fal-ai/gpt-image-1.5`与`fal-ai/gpt-image-2`的默认质量等级为“中等”（在1024×1024分辨率下，每张图片的费用约为0.034美元至0.06美元）。我们并未将“低”/“高”质量等级作为面向用户的可选选项，这是为了确保Nous Portal的计费方式对所有用户而言都具有可预测性——不同质量等级之间的费用差异可达3到22倍。如果您希望选择更便宜的选项，可使用Klein 9B或Z-Image Turbo；若需要更高品质，则可选择Nano Banana Pro或Recraft V4 Pro。

## 使用方法

面向智能体的接口结构被刻意设计得极为简洁——模型会自动采用您所配置的所有设置：

```
Generate an image of a serene mountain landscape with cherry blossoms
```

```
Create a square portrait of a wise old owl — use the typography model
```

```
Make me a futuristic cityscape, landscape orientation
```

## 图像到图像/图像编辑

当当前激活的模型支持时，同一个 `image_generate` 工具也可用于**编辑现有图像**——只需提供源图像，后端便会自动将其路由至相应的编辑接口（其工作方式与 `video_generate` 处理图像到视频的流程类似）。若不提供源图像，则该工具将执行纯文本到图像的生成功能。

```
Take this photo and make it a rainy Tokyo street at night → <image>
```

```
Blend these two product shots into one hero image → <image1> <image2>
```

编辑功能由两个输入参数驱动：

- **`image_url`** — 需要编辑/转换的原始图片（公共网址或本地路径）。
- **`reference_image_urls`** — 额外的风格/构图参考图片（每个模型有上限）。

### 哪些后端支持编辑功能

| 后端 | 图像转图像功能 | 参考图片数量上限 | 实现方式 |
|---|---|---|---|
| **FAL.ai**（以下支持编辑的模型） | ✓ | 最多9张 | 路由至模型的 `/edit` 接口 |
| **OpenAI** (`gpt-image-2`) | ✓ | 最多16张 | 使用 `images.edit()` 方法 |
| **xAI** (Grok Imagine) | ✓ | 1张 | 通过 `/v1/images/edits` 接口及 `grok-imagine-image-quality` 参数 |
| **Krea** (`Krea 2`) | ✓ | 最多10张 | 基于参考图片的生成功能（`image_style_references` 参数） |
| **OpenAI (Codex认证)** | ✓ | 最多16张 | 使用 Codex Responses 的 `image_generation` 工具及 `input_image` 内容参数 |

支持编辑功能的 FAL 模型包括：`flux-2/klein/9b`、`flux-2-pro`、`nano-banana-pro`、`gpt-image-1.5`、`gpt-image-2`、`ideogram/v3` 以及 `qwen-image`。而纯文本转图像的 FAL 模型（如 `z-image/turbo`、`recraft`、`krea/*`）会拒绝接收图片输入，并给出明确错误提示，建议使用支持编辑功能的模型。

运行时，工具描述中会显示当前激活模型的编辑功能支持情况，这样智能体在调用工具之前就能知道是否可以处理 `image_url` 参数。

## 宽高比

从智能体的角度来看，所有模型都接受相同的三种宽高比。实际上，每个模型的原生尺寸规格会自动填充：

| 智能体输入 | flux/z-image/qwen/recraft/ideogram 系列的图像尺寸 | nano-banana-pro 的宽高比 | gpt-image-1.5 的图像尺寸 | gpt-image-2 的图像尺寸 |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3`（1024×768） |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd`（1024×1024） |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3`（768×1024） |

GPT Image 2 因其最小像素数为 655,360，无法使用 `landscape_16_9` 格式（1024×576 = 589,824 像素），因此只能使用 4:3 的预设比例。

这一转换是在 `_build_fal_payload()` 函数中完成的——智能体代码无需了解不同模型之间的格式差异。

## 自动放大处理

是否通过 FAL 的 **Clarity Upscaler** 进行放大处理需根据模型而定：

| 模型 | 是否放大？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 兼容旧版本需求（曾是默认选项） |
| 其他所有模型 | ✗ | 快速生成模型无需放大即可保持秒级响应速度；高分辨率模型也不需要此功能 |

放大处理时会使用以下参数设置：

| 参数 | 值 |
|---|---|
| 放大倍数 | 2倍 |
| 创意程度 | 0.35 |
| 相似度保留 | 0.6 |
| 指导强度 | 4 |
| 推理步数 | 18 |

如果放大处理失败（如网络问题或速率限制），系统会自动返回原始图片。

## 内部工作原理

1. **模型分辨率确定** — `_resolve_fal_model()` 函数会先从 `config.yaml` 文件中读取 `image_gen.model` 的配置，若未找到则使用 `FAL_IMAGE_MODEL` 环境变量指定的值，最终默认为 `fal-ai/flux-2/klein/9b`。
2. **负载数据构建** — `_build_fal_payload()` 函数会将用户指定的 `aspect_ratio` 转换为模型支持的格式（预设枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用调用方自定义的参数设置，最后通过模型的 `supports` 白名单进行过滤，确保不会发送不支持的参数。
3. **请求提交** — `_submit_fal_request()` 函数会通过直接的 FAL 认证信息或托管的 Nous 网关来提交请求。
4. **放大处理** — 仅当模型的元数据中包含 `upscale: True` 时才会执行放大操作。
5. **结果返回** — 最终的图片网址会被返回给智能体，智能体会输出 `MEDIA:<url>` 标签，平台适配器会将此标签转换为相应的媒体格式。

## 调试方法

启用调试日志记录：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会保存在 `./logs/image_tools_debug_<session_id>.json` 文件中，其中包含每次调用的详细信息（模型类型、参数、耗时及错误信息）。

## 输出方式

| 平台 | 输出形式 |
|---|---|
| **CLI** | 以 Markdown 格式输出图片链接 `![](url)`——点击即可打开 |
| **Telegram** | 附带提示语的图片消息 |
| **Discord** | 嵌入在消息中 |
| **Slack** | 由 Slack 自动展开链接 |
| **WhatsApp** | 媒体消息形式 |
| **其他平台** | 纯文本形式的链接 |

## 局限性

- **需要有效后端凭证**（FAL 的 `FAL_KEY` / Nous 订阅账号、`OPENAI_API_KEY`、xAI OAuth、`KREA_API_KEY`）
- **编辑功能取决于模型类型**——仅支持图像间编辑的模型才能实现该功能（参见上表）；仅支持文本生成模型的则会直接拒绝图片输入并给出明确错误提示
- **临时链接**——后端返回的链接会在数小时或数天后失效；Hermes 会将其缓存到本地，以确保链接过期后仍能正常使用
- **模型特定限制**——部分模型不支持 `seed`、`num_inference_steps` 等参数。`supports` / `edit_supports` 过滤机制会自动忽略不受支持的参数，这是正常现象 |
