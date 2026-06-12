---
sidebar_position: 12
title: "Video Generation Provider Plugins"
description: "How to build a video-generation backend plugin for Hermes Agent"
---

# 构建视频生成提供者插件

视频生成提供者插件用于注册后端，以处理所有的 `video_generate` 工具调用。内置提供者（如 xAI、FAL）均以插件形式提供。若需添加新插件或覆盖现有插件，只需将相关目录放入 `plugins/video_gen/<名称>/` 中即可。

:::提示
视频生成插件的实现方式与[图像生成提供者插件](/developer-guide/image-gen-provider-plugin)几乎完全一致——如果您曾构建过图像生成后端，便已熟悉其结构。主要区别在于：需要一个用于声明支持的模式/宽高比/时长等的 `capabilities()` 方法，以及一种路由规则（传入 `image_url` 即表示图像转视频，省略该参数则表示文本转视频——由提供者内部选择合适的接口）。
:::

## 统一接口（一个工具，两种模式）

`video_generate` 工具通过一个参数支持两种不同的输入模式：

- **文本转视频**：仅传入 `prompt` 即可。提供者会将其路由至文本转视频接口。
- **图像转视频**：需同时传入 `prompt` 和 `image_url`。提供者则会将其路由至图像转视频接口。

此处不涉及编辑和扩展功能，因为大多数后端并不支持这些功能，而且若实现这些功能，将不得不在每个后端的描述中重复说明，导致内容不一致。

## 发现机制

Hermes 会在三个位置查找视频生成后端：

1. **内置插件** — `<repo>/plugins/video_gen/<名称>/`（带有 `kind: backend` 标签，会自动加载）。
2. **用户自定义插件** — `~/.hermes/plugins/video_gen/<名称>/`（需通过 `plugins.enabled` 开启）。
3. **Pip 安装的插件** — 包含 `hermes_agent.plugins` 入口点的软件包。

每个插件中的 `register(ctx)` 函数都会调用 `ctx.register_video_gen_provider()`。实际使用的提供者由 `config.yaml` 中的 `video_gen.provider` 参数指定；通过 `hermes tools` → Video Generation 可以帮助用户进行选择。与图像生成不同，视频生成没有内置的传统后端——所有的提供者均为插件形式。

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

## 插件清单文件

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

## `video_generate` 架构

该工具在所有后端中均提供相同的架构。各提供商会忽略其不支持的参数。

| 参数 | 功能说明 |
|---|---|
| `prompt` | 文本指令（必填） |
| `image_url` | 设置时用于图像转视频；未设置时用于文本转视频 |
| `reference_image_urls` | 风格/角色参考（取决于具体提供商） |
| `duration` | 秒数——由提供商进行限制 |
| `aspect_ratio` | `"16:9"`, `"9:16"`, `"1:1"` 等——由提供商进行限制 |
| `resolution` | `"480p"` / `"540p"` / `"720p"` / `"1080p"` ——由提供商进行限制 |
| `negative_prompt` | 需避免的内容（仅 Pixverse/Kling 支持） |
| `audio` | 原生音频（适用于 Veo3 / Pixverse 的特定定价套餐） |
| `seed` | 确保结果可复现 |
| `model` | 覆盖当前激活的模型/系列 |

各提供商的 `capabilities()` 方法会说明哪些参数会被支持。智能体可通过工具描述查看当前后端支持的参数，而当用户通过 `hermes tools` 更改后端时，该描述会动态更新。

## 模型系列与端点路由（FAL 模式）

如果您的后端每个“模型”都包含多个端点——例如 FAL 模式下，每个系列（Veo 3.1、Pixverse v6、Kling O3）都同时拥有 `/text-to-video` 和 `/image-to-video` 接口——则应将每个**系列**视为一个目录条目。您的 `generate()` 函数会根据是否传入了 `image_url` 来选择相应的端点。

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

用户在 `hermes tools` 中选择一次 `veo3.1` 即可。该智能体无需考虑端点信息，只需传递（或不传递）`image_url` 即可。

## 选择优先级

对于针对单个实例的模型配置选项（参见 `plugins/video_gen/fal/__init__.py`）：

1. 工具调用中的 `model=` 关键字
2. 环境变量 `<PROVIDER>_VIDEO_MODEL`
3. `config.yaml` 中的 `video_gen.<provider>.model`
4. `config.yaml` 中的 `video_gen.model`（当其为预设的模型标识之一时）
5. 提供商自定的 `default_model()` 函数

## 响应格式

`success_response()` 和 `error_response()` 会生成所有后端统一返回的字典结构。建议直接使用这些函数，而非自行构造字典。

成功响应包含的键值：`success`、`video`（URL 或绝对路径）、`model`、`prompt`、`modality`（值为 `"text"` 或 `"image"`）、`aspect_ratio`、`duration`、`provider`，以及 `extra` 键。

错误响应包含的键值：`success`、`video`（值为 `None`）、`error`、`error_type`、`model`、`prompt`、`aspect_ratio`、`provider`。

## 存储输出文件的位置

如果后端返回的是 base64 编码的数据，可使用 `save_b64_video()` 函数将其保存到 `$HERMES_HOME/cache/videos/` 目录下。若是通过后续 HTTP 请求获取的原始字节数据，则使用 `save_bytes_video()` 函数。其余情况下可直接返回上游提供的 URL，由网关在数据传输时自动解析该远程地址。

## 测试方法

可在 `tests/plugins/video_gen/test_<name>_plugin.py` 文件中编写简单测试用例。xAI 和 FAL 相关的测试案例已展示了标准流程：注册智能体、验证模型目录、在有/无 `image_url` 的情况下测试路由功能，同时检查在缺少授权时是否能返回规范的错误响应。
