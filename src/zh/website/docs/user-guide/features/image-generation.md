---
title: Image Generation
description: Generate images via FAL.ai — 11 models including FLUX 2, GPT Image (1.5 & 2), Nano Banana Pro, Ideogram, Recraft V4 Pro, Krea 2, and more, selectable via `hermes tools`.
sidebar_label: Image Generation
sidebar_position: 6
---

# 图像生成

Hermes Agent 能够通过 FAL.ai 根据文本提示词生成图像。系统预置了 11 种模型，每种模型在速度、质量与成本之间各有侧重。用户可通过 `hermes tools` 自行选择当前使用的模型，该设置会保存在 `config.yaml` 文件中。

## 支持的模型

| 模型 | 生成速度 | 优势特点 | 成本 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `<1秒` | 速度快，文本渲染清晰 | $0.006/百万像素 |
| `fal-ai/flux-2-pro` | 约 6秒 | 具有工作室级的真实感 | $0.03/百万像素 |
| `fal-ai/z-image/turbo` | 约 2秒 | 支持中英文双语，参数量为 6B | $0.005/百万像素 |
| `fal-ai/nano-banana-pro` | 约 8秒 | 基于 Gemini 3 Pro，具备较强的推理能力与文本渲染功能 | $0.15/张（1K分辨率） |
| `fal-ai/gpt-image-1.5` | 约 15秒 | 能较好地遵循提示词要求 | $0.034/张 |
| `fal-ai/gpt-image-2` | 约 20秒 | 拥有当前最先进的文本渲染技术，支持中文等复杂字符，具备对场景的深刻理解能力，真实感强 | $0.04–0.06/张 |
| `fal-ai/ideogram/v3` | 约 5秒 | 文字排版效果最佳 | $0.03–0.09/张 |
| `fal-ai/recraft/v4/pro/text-to-image` | 约 8秒 | 适用于设计、品牌视觉系统创建，输出结果可直接用于实际应用 | $0.25/张 |
| `fal-ai/qwen-image` | 约 12秒 | 基于大语言模型，擅长处理复杂文本内容 | $0.02/百万像素 |
| `fal-ai/krea/v2/medium/text-to-image` | 约 15–25秒 | 适用于插画、动漫、绘画等风格，具备强烈的艺术表现力 | $0.030–0.035/张 |
| `fal-ai/krea/v2/large/text-to-image` | 约 25–60秒 | 能生成高度逼真的图像，可呈现原始的纹理效果（如运动模糊、颗粒感、胶片质感） | $0.060–0.065/张 |

以上价格均为本文撰写时 FAL.ai 的定价标准，具体最新价格请访问 [fal.ai](https://fal.ai/) 查阅。

## 设置指南

:::提示 Nous订阅用户
如果您拥有付费的[Nous Portal](https://portal.nousresearch.com)订阅资格，无需FAL API密钥即可通过**[Tool Gateway](tool-gateway.md)**使用图像生成功能。两种路径下的模型选择设置都会被保留。新安装的用户可运行`hermes setup --portal`进行登录并一次性启用所有网关工具；已安装的用户则可通过`hermes tools`将**Nous订阅**设置为图像生成的后端。

如果某个特定模型在管理型网关处返回`HTTP 4xx`错误，说明该模型尚未在门户端实现代理——Agent会告知您问题所在并提供解决方案（可在`hermes tools`中切换到FAL.ai并使用自己的`FAL_KEY`直接访问，或选择其他模型）。
:::

### 获取FAL API密钥

1. 在[fal.ai](https://fal.ai/)注册账号
2. 从控制面板生成API密钥

### 配置并选择模型

运行tools命令：

```bash
hermes tools
```

进入**🎨 图像生成**页面，选择您的后端服务（Nous Subscription或FAL.ai），随后系统会以列对齐的表格形式展示所有支持的模型——可使用方向键进行导航，按回车键即可选中对应模型。

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
  provider: fal                 # `nous` if you picked Nous Subscription
  model: fal-ai/flux-2/klein/9b
  max_parallel_requests: 4      # concurrent images in one tool-call batch
```

`image_gen.provider` 是唯一的配置键：值为 `nous` 时，请求会通过托管的 Tool Gateway 处理；而厂商名称（如 `fal`、`openai`、`xai`、`krea` 等）则直接对应相应的专用密钥。运行时始终会遵循此已存储的配置——当 `provider: nous` 时，`.env` 文件中的 `FAL_KEY` 会被忽略；而若设置 `provider: fal` 却未指定 `FAL_KEY`，则会出现错误，提示“图像生成功能已配置为使用 fal（通过 hermes tools 设置），但未设置 FAL_KEY。请运行 ‘hermes tools’ 进行修改”，而不会默默地改变路由方式。应通过 `hermes tools` 更改提供商，而非通过添加或删除配置键来实现。（旧的 `use_gateway` 布尔值属于旧版本遗留项——当其值为 `true` 时仍会被解析为 `nous`，但已不再被写入使用。）

`max_parallel_requests` 的默认值为 `4`。Hermes 会将其限制在至少 1 个请求以及全局工具工作进程的限制范围内，从而确保图像处理服务收到的并行请求数量处于可控状态，避免图像批量处理绕过代理的并发上限。

### OpenRouter：完整的图像 API 目录

当设置 `image_gen.provider: openrouter` 时，模型选择器会列出 OpenRouter 的全部实时图像模型目录——这些专门的[Image API](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)模型（如 Seedream、FLUX.2、Recraft、Qwen Image、MAI、Krea、Riverflow、Grok Imagine 等，共计40多种模型）与聊天完成型图像模型被合并在一起。该目录会通过 `GET /images/models` 和 `GET /models` 实时获取，因此一旦 OpenRouter 提供了新模型，它们就会立即出现在选择器中，无需进行 Hermes 更新。生成系统会自动将每个模型路由到对应的处理接口（专门的 `POST /images/generations` 接口或聊天完成型接口）。而 Nous Portal 仅支持代理聊天完成型协议，因此其选择器仅提供通过聊天方式处理的模型。

针对 Image API 模型的可选请求级参数则位于作用域配置部分（或 `OPENROUTER_IMAGE_API_*` 环境变量）中：

```yaml
image_gen:
  provider: openrouter
  model: bytedance-seed/seedream-4.5
  openrouter:
    resolution: 2K        # model-dependent: 1K / 2K / 4K
    quality: high         # gpt-image models
    output_format: png
```

### GPT图像质量

`fal-ai/gpt-image-1.5`和`fal-ai/gpt-image-2`的生成质量固定为“中等”级别（在1024×1024分辨率下，每张图片的费用约为0.034美元至0.06美元）。我们未将“低”/“高”质量选项作为面向用户的可选择项，以确保所有用户的Nous Portal账单费用保持稳定——不同质量等级之间的费用差异可达3到22倍。如果您希望选择更经济的选择，可选用Klein 9B或Z-Image Turbo；若需要更高质量，则建议使用Nano Banana Pro或Recraft V4 Pro。

### 元模型API：Muse Image

当使用`image_gen.provider: meta-ai`时，图像是通过[元模型API](https://api.meta.ai)（即`https://api.meta.ai/v1`）生成的，该接口与用于支持Muse Spark聊天模型的接口相同，也兼容OpenAI标准。它是随`meta-ai`聊天服务一同提供的图像生成功能。

| 模型 | 生成速度 | 优势 | 费用 |
|---|---|---|---|
| `muse-image-1.0` *(默认)* | 约10秒 | 基于元模型API的图像生成能力 | 每张图片0.01美元 |

```yaml
image_gen:
  provider: meta-ai
  model: muse-image-1.0
```

认证功能会复用 Meta Chat 提供商所使用的相同环境变量——`MODEL_API_KEY`（即 Meta 文档中规定的名称），同时也接受 `META_API_KEY` 和 `META_MODEL_API_KEY` 作为别名。如需将请求指向代理服务器或其他主机，可设置 `META_BASE_URL`。目前仅支持文本转图像功能，生成的图片会保存在 `$HERMES_HOME/cache/images/` 目录中。

## FAL：GPT Image 2.5

在 `hermes tools` → Image Generation → FAL.ai 中选择 **GPT Image 2.5 Flare** 或 **GPT Image 2.5 Sunburst**。对应的模型编号为：

- `openai/gpt-image-2.5/flare/text-to-image`
- `openai/gpt-image-2.5/sunburst/text-to-image`

例如：

```bash
hermes config set image_gen.provider fal
hermes config set image_gen.model openai/gpt-image-2.5/flare/text-to-image
```

提供 `image_url` 或参考图片后，系统会自动选择对应的 `openai/gpt-image-2.5/flare/edit` 或 `openai/gpt-image-2.5/sunburst/edit` 接口。这两个接口均支持最多16张源图片。Hermes将图像质量固定为“中等”，这一设置与其现有的FAL GPT Image策略一致，而非采用FAL默认的更高成本“高”质量设置。为满足最小像素数要求，横屏和竖屏图像会使用4:3预设比例，而正方形图像则使用`square_hd`预设；除非用户特别要求，否则不会进行图像放大处理。

FAL按令牌数量计费，而非固定图片价格：文本输入费用为5美元/百万个令牌，缓存后的文本输入费用为1.25美元/百万个令牌，文本输出费用为10美元/百万个令牌，图片输入费用为8美元/百万个令牌，缓存后的图片输入费用为2美元/百万个令牌，图片输出费用为30美元/百万个令牌，所有费用均向上取整至每次请求0.0001美元。详情请参阅[Flare](https://fal.ai/models/openai/gpt-image-2.5/flare/text-to-image)和[Sunburst](https://fal.ai/models/openai/gpt-image-2.5/sunburst/text-to-image)页面。直接使用FAL需要具备有效的`FAL_KEY`；而托管网关的可用性则取决于该网关的接口允许列表，其可用性与FAL本身的可用性并无关联。现有的提供商和模型默认设置保持不变。

## OpenAI API：GPT Image 2.5

**OpenAI**提供商支持使用`OPENAI_API_KEY`调用GPT Image 2.5的Flare版本（适用于日常快速生成）和Sunburst版本（支持高精度生成与编辑）。用户可通过`hermes tools` → Image Generation → OpenAI来选择相应版本，或直接进行相关设置：

```bash
hermes config set image_gen.provider openai
hermes config set image_gen.openai.model gpt-image-2.5-flare
```

`gpt-image-2.5-flare`与`gpt-image-2.5-sunburst`默认采用自动质量设置。若需指定固定质量，可添加`-low`、`-medium`、`-high`、`-xhigh`或`-max`参数，例如`gpt-image-2.5-sunburst-high`。这两种模型均支持生成与编辑功能，最多可使用16张参考图片。现有的GPT Image 2选项以及默认的`gpt-image-2-medium`设置保持不变。

该服务属于付费API，需另行购买，与ChatGPT/Codex订阅服务无关。两种模型的费用分别为：每百万个文本输入令牌5美元、每百万个图像输入令牌8美元、每百万个图像输出令牌30美元（缓存输入的费率分别为1.25美元和2美元）。单张图片的费用会根据使用量有所不同；GPT Image 2计算器不包含2.5倍令牌消耗量的估算。详情请参阅官方的[Flare](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare)和[Sunburst](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)文档。

**OpenAI（Codex认证）**提供方仍为独立系统：其后台虽能接收图像模型选项，但不会实际应用该选择，因此仅上传图片并无法验证是否使用了Flare或Sunburst版本。这些选项是通过直接的OpenAI API提供方及FAL来提供的，并非经过认证的Codex认证选项。

## 使用方式

面向智能体的接口设计极为简洁——模型会自动采用您所配置的所有设置。

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

当当前激活的模型支持时，同一个 `image_generate` 工具也可用于**编辑现有图像**——只需传入源图像，后端便会自动将其路由至相应的编辑接口（其工作方式与 `video_generate` 处理图像到视频的流程类似）。若不提供源图像，则该工具将执行普通的文本到图像生成功能。

```
Take this photo and make it a rainy Tokyo street at night → <image>
```

```
Blend these two product shots into one hero image → <image1> <image2>
```

编辑功能由两个输入参数驱动：

- **`image_url`** — 需要编辑/转换的原始图像（公共网址或本地路径）。
- **`reference_image_urls`** — 其他用于参考的风格或构图元素（每个模型有上限限制）。

### 哪些后端支持编辑功能

| 后端 | 图像转图像功能 | 参考图像数量上限 | 实现方式 |
|---|---|---|---|
| **FAL.ai**（以下支持编辑的模型） | ✓ | 每个模型最多16张 | 路由至该模型的 `/edit` 接口 |
| **OpenAI**（GPT Image 2 / 2.5 Flare / Sunburst） | ✓ | 最多16张 | 使用 `images.edit()` 方法 |
| **xAI**（Grok Imagine） | ✓ | 1张 | 通过 `/v1/images/edits` 接口及 `grok-imagine-image-quality` 参数 |
| **Krea**（`Krea 2`） | ✓ | 最多10张 | 基于参考图像进行生成（通过 `image_style_references` 参数） |
| **OpenAI（Codex认证）** | ✓ | 最多16张 | 使用 Codex Responses 中的 `image_generation` 工具，并传入 `input_image` 内容参数 |
| **OpenRouter**（图像API模型） | ✓ | 每个模型最多14–16张 | 通过 `POST /images/generations` 请求中的 `input_references` 参数；聊天式服务模型则使用最多3个 `image_url` 内容参数 |

支持编辑功能的FAL模型包括：`flux-2/klein/9b`、`flux-2-pro`、`nano-banana-pro`、`gpt-image-1.5`、`gpt-image-2`、`ideogram/v3` 以及 `qwen-image`，此外还包括上述的GPT Image 2.5 Flare和Sunburst模型。而纯文本转图像功能的FAL模型（如 `z-image/turbo`、`recraft`、`krea/*`）会拒绝接收图像输入，并给出明确错误提示，指引用户使用支持编辑功能的模型。

:::note OpenAI（Codex认证）功能为尽力而为型服务。

Codex 接口（`chatgpt.com/backend-api/codex`）提供了 `image_generation` 工具，供聊天模型调用，但 Hermes 无法强制触发该调用——后端会拒绝所有针对此类托管工具的 `tool_choice` 格式请求，因此必须依靠指令来引导模型执行操作。当模型拒绝使用该工具时，调用将会以 `empty_response` 的形式失败。此外，不同账户下该托管图像工具的可用性也存在差异。若需确保图像生成功能始终稳定运行，建议配置 **OpenAI**（API 密钥）、**FAL** 或 **xAI** 后端。

:::

运行时，模型当前的编辑能力会显示在工具描述中，这样 Agent 在调用工具之前就能知道是否支持 `image_url` 参数。

## 宽高比

从 Agent 的视角来看，所有模型都支持相同的三种宽高比。实际上，每个模型的原生尺寸规格会自动填充：

| Agent 输入 | flux/z-image/qwen/recraft/ideogram 的图像尺寸 | nano-banana-pro 的宽高比 | gpt-image-1.5 的图像尺寸 | gpt-image-2 的图像尺寸 |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3`（1024×768） |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd`（1024×1024） |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3`（768×1024） |

GPT Image 2 因其最小像素数为 655,360，无法使用 `landscape_16_9` 前置设置（1024×576 = 589,824），因此只能使用 4:3 比例的预设。

该翻译操作在 `_build_fal_payload()` 函数中完成——代理代码无需知晓不同模型之间的结构差异。

## 上采样功能

### 仅可选启用

默认情况下，不会对模型图像进行上采样。现代图像模型能够直接输出最高质量的结果，而现有的上采样工具实际上属于*创意增强型*工具（基于扩散过程），可能会微妙地改变图像内容，从而导致文本、人脸及精细细节的质量下降。上采样功能仅在代理明确请求时才会启动。

### `upscale` 参数（每次调用时可选）

- `upscale: true` — 在生成结果后追加高分辨率处理步骤：

| 后端服务 | 上采样工具 |
|---|---|
| **FAL.ai** | Clarity Upscaler（2倍分辨率，每百万像素额外收费0.03美元） |
| **Krea** | Krea Enhance（2倍分辨率，最高支持8K分辨率） |
| 其他后端服务 | 不提供上采样功能；直接返回原始分辨率 |

- `upscale: false` / 省略该参数 — 使用原始分辨率（默认设置）

在 FAL 后端，`video_generate` 函数也支持设置 `upscale: true`，从而在生成视频后追加字节跳动的 **SeedVR2** 视频上采样工具（2倍分辨率，每百万像素输出视频额外收费0.001美元）。

当执行 FAL 的图像处理步骤时，会使用以下参数设置：

| 参数 | 值 |
|---|---|
| 上采样倍数 | 2倍 |
| 创意程度 | 0.35 |
| 相似度控制 | 0.6 |
| 指导强度 | 4 |
| 推理步数 | 18 |

如果上采样失败（如网络问题或速率限制），系统会自动返回原始图像。响应结果中会标注 `upscaled: true/false`，以便代理知晓最终获取的图像分辨率。

## 内部工作原理

1. **模型选择** — `_resolve_fal_model()` 首先从 `config.yaml` 中读取 `image_gen.model` 的配置，若未找到则回退至 `FAL_IMAGE_MODEL` 环境变量指定的值，最后默认使用 `fal-ai/flux-2/klein/9b` 模型。
2. **请求数据构建** — `_build_fal_payload()` 会将您输入的 `aspect_ratio` 值转换为模型支持的格式（预置枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用调用方指定的自定义参数，随后通过模型的 `supports` 白名单进行过滤，确保不会发送任何不被支持的键值。
3. **请求提交** — `_submit_fal_request()` 会根据存储的 `image_gen.provider` 配置，通过直接的 FAL 凭证或受管理的 Nous 网关来提交请求。
4. **图像放大** — 仅当代理设置 `upscale: true` 时才会执行此步骤；所有模型的默认设置均为关闭。
5. **结果返回** — 最终的图像 URL 会被返回给代理，代理会生成 `MEDIA:<url>` 标签，平台适配器会将该标签转换为对应的原生媒体格式。

## 调试

启用调试日志记录：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会保存在 `./logs/image_tools_debug_<session_id>.json` 文件中，其中包含每次调用的详细信息（模型类型、参数设置、执行时间以及错误详情）。

## 输出方式

| 平台 | 输出形式 |
|---|---|
| **CLI** | 以 Markdown 格式输出图片链接 `![](url)` — 点击即可打开 |
| **Telegram** | 以照片消息形式发送，附上提示词作为标题 |
| **Discord** | 嵌入在消息中 |
| **Slack** | 由 Slack 自动展开显示链接 |
| **WhatsApp** | 以媒体消息形式发送 |
| **其他平台** | 以纯文本形式提供链接 |

## 局限性

- **需要有效后端凭证**（FAL 的 `FAL_KEY` / Nous 订阅凭证、`OPENAI_API_KEY`、xAI OAuth 凭证、`KREA_API_KEY`）
- **编辑功能取决于模型类型** — 仅支持具备编辑功能的模型才能实现图像到图像的转换（详见上表）；仅支持文本到图像的模型会直接拒绝图像输入并给出明确错误提示
- **临时链接** — 后端返回的链接会在数小时或数天后失效；Hermes 会将这些链接缓存到本地，从而确保链接过期后仍能正常使用
- **模型特定限制** — 某些模型不支持 `seed`、`num_inference_steps` 等参数。`supports` / `edit_supports` 过滤机制会自动忽略不受支持的参数，这是正常现象 |
