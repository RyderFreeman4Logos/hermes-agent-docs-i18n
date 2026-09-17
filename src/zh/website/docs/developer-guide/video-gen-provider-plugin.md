---
sidebar_position: 12
title: "Video Generation Provider Plugins"
description: "How to build a video-generation backend plugin for Hermes Agent"
---

# 构建视频生成提供者插件

视频生成提供者插件用于注册后端，为每一次 `video_generate` 工具调用提供服务。内置提供者（xAI、FAL、DeepInfra）均以插件形式提供。如需添加新插件或覆盖现有插件，只需将对应目录放入 `plugins/video_gen/<名称>/` 中即可。

:::提示
视频生成插件的实现方式与[图像生成提供者插件](/developer-guide/image-gen-provider-plugin)几乎完全一致——如果您曾构建过图像生成后端，便已熟悉其结构。主要区别在于：需要一个用于声明支持的模式/分辨率/时长等的 `capabilities()` 方法，以及一种路由规则（传入 `image_url` 即表示使用图像转视频功能，省略该参数则表示使用文本转视频功能——由提供者内部选择合适的接口）。
:::

## 统一接口（一个工具，两种模式）

`video_generate` 工具通过一个参数支持两种模式：

- **文本转视频** — 仅传入 `prompt` 即可。提供者会将请求路由至其文本转视频接口。
- **图像转视频** — 需同时传入 `prompt` 和 `image_url`。提供者会将请求路由至其图像转视频接口。

编辑和扩展功能有意不在当前讨论范围内。大多数后端并不支持这些功能，若加入此类功能，将不得不在智能体的工具描述中为每个后端单独编写说明，从而导致内容混乱。

## 发现机制

Hermes 会在三个位置扫描视频生成后端：

1. **内置型** — `<repo>/plugins/video_gen/<name>/`（通过 `kind: backend` 自动加载）  
2. **用户自定义型** — `~/.hermes/plugins/video_gen/<name>/`（需通过 `plugins.enabled` 手动启用）  
3. **Pip 安装型** — 包含 `hermes_agent.plugins` 入口点的软件包  

每个插件都会调用其 `register(ctx)` 函数来执行 `ctx.register_video_gen_provider(...)` 操作。具体的可用提供者由 `config.yaml` 中的 `video_gen.provider` 参数决定；`hermes tools` → Video Generation 功能会引导用户完成选择流程。与 `image_generate` 不同，此处不存在内置的旧版后端——所有的提供者均为插件形式。  

## 目录结构

```
plugins/video_gen/my-backend/
├── __init__.py      # VideoGenProvider subclass + register()
└── plugin.yaml      # Manifest with kind: backend
```

## VideoGenProvider 接口规范

需继承自 `agent.video_gen_provider.VideoGenProvider` 类。必须包含 `name` 属性以及 `generate()` 方法。

```python
# plugins/video_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.video_gen_provider import (
    VideoGenProvider,
    error_response,
    success_response,
)


class MyVideoGenProvider(VideoGenProvider):
    @property
    def name(self) -> str:
        return "my-backend"

    @property
    def display_name(self) -> str:
        return "My Backend"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self) -> List[Dict[str, Any]]:
        # Each entry is a model FAMILY — a name the user picks once.
        # Your provider's generate() routes within the family based on
        # whether image_url was passed.
        return [
            {
                "id": "fast",
                "display": "Fast",
                "speed": "~30s",
                "strengths": "Cheapest tier",
                "price": "$0.05/s",
                "modalities": ["text", "image"],  # advisory
            },
        ]

    def default_model(self) -> Optional[str]:
        return "fast"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "modalities": ["text", "image"],
            "aspect_ratios": ["16:9", "9:16"],
            "resolutions": ["720p", "1080p"],
            "min_duration": 1,
            "max_duration": 10,
            "supports_audio": False,
            "supports_negative_prompt": True,
            "max_reference_images": 0,
        }

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "My Backend",
            "badge": "paid",
            "tag": "Short description shown in `hermes tools`",
            "env_vars": [
                {
                    "key": "MY_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://mybackend.example.com/keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        duration: Optional[int] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        negative_prompt: Optional[str] = None,
        audio: Optional[bool] = None,
        seed: Optional[int] = None,
        **kwargs: Any,  # always ignore unknown kwargs for forward-compat
    ) -> Dict[str, Any]:
        # ROUTE: image_url presence picks the endpoint.
        if image_url:
            endpoint = "my-backend/image-to-video"
            modality_used = "image"
        else:
            endpoint = "my-backend/text-to-video"
            modality_used = "text"

        # ... call your API ...

        return success_response(
            video="https://your-cdn/output.mp4",
            model=model or "fast",
            prompt=prompt,
            modality=modality_used,
            aspect_ratio=aspect_ratio,
            duration=duration or 5,
            provider=self.name,
        )


def register(ctx) -> None:
    ctx.register_video_gen_provider(MyVideoGenProvider())
```

## 插件清单

```yaml
# plugins/video_gen/my-backend/plugin.yaml
name: my-backend
version: 1.0.0
description: "My video generation backend"
author: Your Name
kind: backend
requires_env:
  - MY_API_KEY
```

## `video_generate` 结构体

该工具在所有后端中均提供相同的结构体。各服务提供商会忽略其不支持的参数。

| 参数 | 功能说明 |
|---|---|
| `prompt` | 文本指令（必填） |
| `image_url` | 设置时用于图像转视频；未设置时用于文本转视频 |
| `reference_image_urls` | 风格/角色参考资料（具体支持情况因服务提供商而异） |
| `duration` | 时长，单位为秒——由服务提供商进行限制 |
| `aspect_ratio` | 比例值，如 `"16:9"`、`"9:16"`、`"1:1"` 等——由服务提供商进行限制 |
| `resolution` | 分辨率，如 `"480p"`、`"540p"`、`"720p"`、`"1080p"` 等——由服务提供商进行限制 |
| `negative_prompt` | 需避免的内容（仅 Pixverse/Kling 支持） |
| `audio` | 原生音频（适用于 Veo3 / Pixverse 的特定定价套餐） |
| `seed` | 用于确保结果可重复生成 |
| `model` | 覆盖当前使用的模型/系列 |

服务提供商的 `capabilities()` 方法会说明哪些参数会被支持。智能体可通过工具描述查看当前后端支持的功能，当用户通过 `hermes tools` 更换后端时，这些信息会动态更新。

## 模型系列与端点路由（FAL 模式）

如果您的后端每个“模型”都包含多个端点——例如 FAL 模式下，每个模型系列（Veo 3.1、Pixverse v6、Kling O3）都同时拥有 `/text-to-video` 和 `/image-to-video` 两个端点——则应将每个**模型系列**视为一个独立的目录条目。您的 `generate()` 函数会根据是否传入了 `image_url` 来选择合适的端点。

```python
FAMILIES = {
    "veo3.1": {
        "text_endpoint": "fal-ai/veo3.1",
        "image_endpoint": "fal-ai/veo3.1/image-to-video",
        # ... family-specific capability flags ...
    },
}

def generate(self, prompt, *, image_url=None, model=None, **kwargs):
    family_id, family = _resolve_family(model)
    endpoint = family["image_endpoint"] if image_url else family["text_endpoint"]
    # ... build payload from family's declared capability flags, call endpoint ...
```

用户在 `hermes tools` 中选择一次 `veo3.1` 即可。Agent 不需要考虑端点信息，只需传递（或不传递）`image_url` 即可。

## 选择优先级

对于针对单个实例的模型配置选项（参见 `plugins/video_gen/fal/__init__.py`）：

1. 工具调用中的 `model=` 关键字
2. 环境变量 `<PROVIDER>_VIDEO_MODEL`
3. `config.yaml` 中的 `video_gen.<provider>.model`
4. `config.yaml` 中的 `video_gen.model`（当其为预设的模型标识之一时）
5. 提供商实现的 `default_model()` 函数

## 响应格式

`success_response()` 和 `error_response()` 会生成所有后端返回的相同字典结构。建议直接使用这些函数，而非自行构造字典。

成功响应包含的键值：`success`、`video`（URL 或绝对路径）、`model`、`prompt`、`modality`（值为 `"text"` 或 `"image"`）、`aspect_ratio`、`duration`、`provider`，以及 `extra`。

错误响应包含的键值：`success`、`video`（值为 `None`）、`error`、`error_type`、`model`、`prompt`、`aspect_ratio`、`provider`。

## 如何保存生成内容

如果后端返回的是 base64 编码格式，可使用 `save_b64_video()` 函数将其保存到 `$HERMES_HOME/cache/videos/` 目录下。若是通过后续 HTTP 请求获取的原始字节数据，则使用 `save_bytes_video()` 函数。否则可直接返回上游提供的 URL，由网关在内容传输时自动解析该远程地址。

## 测试方法

可在 `tests/plugins/video_gen/test_<name>_plugin.py` 文件中编写简单的功能测试用例。xAI 和 FAL 相关的测试案例已展示了标准流程：注册服务、验证模型目录、测试有无 `image_url` 参数时的路由逻辑，同时还需确保在缺少授权时能返回规范的错误响应。
