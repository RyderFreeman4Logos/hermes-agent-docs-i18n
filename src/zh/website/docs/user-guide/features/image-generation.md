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

## 宽高比设置

从智能体的视角来看，所有模型都支持相同的三种宽高比。在内部处理时，每个模型的原生尺寸规格会自动填充：

| 智能体输入 | flux/z-image/qwen/recraft/ideogram 的 image_size | nano-banana-pro 的 aspect_ratio | gpt-image-1.5 的 image_size | gpt-image-2 的 image_size |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3`（1024×768） |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd`（1024×1024） |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3`（768×1024） |

GPT Image 2 因其最小像素数为 655,360，无法使用 `landscape_16_9` 预设（1024×576 = 589,824），因此只能使用 4:3 比例的预设。

这一转换工作在 `_build_fal_payload()` 函数中完成——智能体代码无需了解不同模型之间的格式差异。

## 自动放大功能

通过 FAL 的 **Clarity Upscaler** 进行放大功能需根据模型类型来决定是否启用：

| 模型 | 是否放大？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 兼容旧版本需求（曾是默认选择） |
| 其他所有模型 | ✗ | 快速生成模型会失去秒级响应的优势；高分辨率模型则无需此功能 |

放大处理时会使用以下参数：

| 参数 | 值 |
|---|---|
| 放大倍数 | 2倍 |
| 创意程度 | 0.35 |
| 相似度保持 | 0.6 |
| 指导强度 | 4 |
| 推理步数 | 18 |

如果放大失败（如网络问题或速率限制），系统会自动返回原始图像。

## 内部工作流程

1. **模型分辨率确定** — `_resolve_fal_model()` 函数会先从 `config.yaml` 中读取 `image_gen.model` 的配置，若未找到则使用 `FAL_IMAGE_MODEL` 环境变量，最后默认使用 `fal-ai/flux-2/klein/9b` 模型。
2. **负载构建** — `_build_fal_payload()` 函数会将用户指定的 `aspect_ratio` 转换为模型所支持的格式（预设枚举值、宽高比枚举值或 GPT 的直接数值），合并模型的默认参数，应用调用方设置的自定义参数，最后通过模型的 `supports` 白名单进行过滤，确保不会发送不支持的参数。
3. **请求提交** — `_submit_fal_request()` 函数会通过直接的 FAL 认证信息或托管的 Nous 网关来提交请求。
4. **放大处理** — 仅当模型的元数据中标记 `upscale: True` 时才会执行放大操作。
5. **结果返回** — 最终的图像 URL 会被返回给智能体，智能体会输出 `MEDIA:<url>` 标签，平台适配器会将该标签转换为对应的原生媒体格式。

## 调试方法

启用调试日志记录：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会保存在 `./logs/image_tools_debug_<session_id>.json` 文件中，其中包含每次调用的详细信息（模型、参数、耗时及错误情况）。

## 推送方式

| 平台 | 推送形式 |
|---|---|
| **CLI** | 以 Markdown 格式输出图片链接 `![](url)` — 点击即可打开 |
| **Telegram** | 附带提示语的图片消息 |
| **Discord** | 嵌入在消息中 |
| **Slack** | 由 Slack 自动展开链接 |
| **WhatsApp** | 媒体消息形式 |
| **其他平台** | 纯文本形式的链接 |

## 局限性

- **需要 FAL 凭证**（直接使用 `FAL_KEY` 或 Nous 订阅账号）
- **仅支持文本转图片** — 无法通过该工具进行修复绘图、图像间转换或编辑操作
- **临时链接** — FAL 返回的链接会在数小时或数天后失效；如需长期保存，请自行下载到本地
- **模型相关限制** — 部分模型不支持 `seed`、`num_inference_steps` 等参数。系统会自动忽略不受支持的参数，这是正常现象 |
