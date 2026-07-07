---
sidebar_position: 11
title: "Image Generation Provider Plugins"
description: "How to build an image-generation backend plugin for Hermes Agent"
---

# 构建图像生成提供者插件

图像生成提供者插件用于注册后端服务，以处理所有的 `image_generate` 工具调用——无论是 DALL·E、gpt-image、Grok、Flux、Imagen、Stable Diffusion、fal、Replicate，还是本地的 ComfyUI 工作流，乃至其他任何图像生成工具。所有内置提供者（OpenAI、OpenAI-Codex、xAI）均以插件形式提供。您可以通过将相关目录放入 `plugins/image_gen/<名称>/` 中来添加新插件，或覆盖已有的内置插件。

:::提示
图像生成插件是 Hermes 支持的多种**后端插件**之一。其他具有更专门功能的插件还包括[内存提供者插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)以及[模型提供者插件](/developer-guide/model-provider-plugin)。而常规的工具/钩子/CLI 插件则位于[构建 Hermes 插件](/developer-guide/plugins)相关文档中。
:::

## 发现机制

Hermes 会在三个位置扫描图像生成后端：

1. **内置版本** — `<项目目录>/plugins/image_gen/<名称>/`（带有 `kind: backend` 标识，会自动加载且始终可用）
2. **用户自定义版本** — `~/.hermes/plugins/image_gen/<名称>/`（需通过 `plugins.enabled` 参数启用）
3. **Pip 安装版本** — 包含 `hermes_agent.plugins` 入口点的软件包

每个插件中的 `register(ctx)` 函数都会调用 `ctx.register_image_gen_provider(...)`，从而将其注册到 `agent/image_gen_registry.py` 中的注册表中。活跃的提供者由 `config.yaml` 文件中的 `image_gen.provider` 参数指定；`hermes tools` 会指导用户完成选择过程。

`image_generate` 工具会在运行时向注册表查询当前的活跃提供者，并将请求转发至该提供者处处理。如果未找到任何已注册的提供者，该工具会显示一条包含操作指引的错误信息，提示用户使用 `hermes tools` 进行设置。

## 目录结构

```
plugins/image_gen/my-backend/
├── __init__.py      # ImageGenProvider subclass + register()
└── plugin.yaml      # Manifest with kind: backend
```

至此，一个打包好的插件便已生成完成。位于 `~/.hermes/plugins/image_gen/<name>/` 目录下的用户自定义插件需要被添加到 `config.yaml` 文件中的 `plugins.enabled` 列表中（或执行命令 `hermes plugins enable <name>`）。

## ImageGenProvider ABC 接口

该插件需继承自 `agent.image_gen_provider.ImageGenProvider` 类。其中仅要求必须定义 `name` 属性和 `generate()` 方法——其余所有字段均具有合理的默认值：

```python
# plugins/image_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    normalize_reference_images,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)


class MyBackendImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        # Stable id used in image_gen.provider config. Lowercase, no spaces.
        return "my-backend"

    @property
    def display_name(self) -> str:
        # Human label shown in `hermes tools`. Defaults to name.title() if omitted.
        return "My Backend"

    def is_available(self) -> bool:
        # Return False if credentials or deps are missing.
        # The tool's availability gate calls this before dispatch.
        if not os.environ.get("MY_BACKEND_API_KEY"):
            return False
        try:
            import my_backend_sdk  # noqa: F401
        except ImportError:
            return False
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        # Catalog shown in `hermes tools` model picker.
        return [
            {
                "id": "my-model-fast",
                "display": "My Model (Fast)",
                "speed": "~5s",
                "strengths": "Quick iteration",
                "price": "$0.01/image",
            },
            {
                "id": "my-model-hq",
                "display": "My Model (HQ)",
                "speed": "~30s",
                "strengths": "Highest fidelity",
                "price": "$0.04/image",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "my-model-fast"

    def get_setup_schema(self) -> Dict[str, Any]:
        # Metadata for the `hermes tools` picker — keys to prompt for at setup.
        return {
            "name": "My Backend",
            "badge": "paid",        # optional; shown as a short tag in the picker
            "tag": "One-line description shown under the name",
            "env_vars": [
                {
                    "key": "MY_BACKEND_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://my-backend.example.com/api-keys",
                },
            ],
        }

    def capabilities(self) -> Dict[str, Any]:
        # Declare whether this backend supports image-to-image / editing.
        # The tool layer surfaces this in the dynamic schema so the model
        # knows when `image_url` is honored. Default (if you omit this) is
        # text-only: {"modalities": ["text"], "max_reference_images": 0}.
        return {"modalities": ["text", "image"], "max_reference_images": 4}

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        *,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect_ratio = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="Prompt is required",
                error_type="invalid_input",
                provider=self.name,
                prompt="",
                aspect_ratio=aspect_ratio,
            )

        # Routing: if image_url (or reference_image_urls) is set, the call is
        # an image-to-image / edit request; otherwise text-to-image. Report
        # which path you took via the `modality` field of success_response.
        sources = []
        if image_url:
            sources.append(image_url)
        sources.extend(normalize_reference_images(reference_image_urls) or [])
        modality = "image" if sources else "text"

        # Model selection precedence: env var → config → default. The helper
        # _resolve_model() in the built-in openai plugin is a good reference.
        model_id = kwargs.get("model") or self.default_model() or "my-model-fast"

        try:
            import my_backend_sdk
            client = my_backend_sdk.Client(api_key=os.environ["MY_BACKEND_API_KEY"])
            if modality == "image":
                result = client.edit(
                    prompt=prompt,
                    model=model_id,
                    image_urls=sources,
                )
            else:
                result = client.generate(
                    prompt=prompt,
                    model=model_id,
                    aspect_ratio=aspect_ratio,
                )

            # Two shapes supported:
            #   - URL string: return it as `image`
            #   - base64 data: save under $HERMES_HOME/cache/images/ via save_b64_image()
            if result.get("image_b64"):
                path = save_b64_image(
                    result["image_b64"],
                    prefix=self.name,
                    extension="png",
                )
                image = str(path)
            else:
                image = result["image_url"]

            return success_response(
                image=image,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                provider=self.name,
                modality=modality,
            )
        except Exception as exc:
            return error_response(
                error=str(exc),
                error_type=type(exc).__name__,
                provider=self.name,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
            )


def register(ctx) -> None:
    """Plugin entry point — called once at load time."""
    ctx.register_image_gen_provider(MyBackendImageGenProvider())
```

## plugin.yaml 配置文件

```yaml
name: my-backend
version: 1.0.0
description: My image backend — text-to-image via My Backend SDK
author: Your Name
kind: backend
requires_env:
  - MY_BACKEND_API_KEY
```

`kind: backend` 用于将插件路由至 image-gen 注册路径。`requires_env` 参数会在执行 `hermes plugins install` 时被询问。

## ABC 参考

完整契约定义在 `agent/image_gen_provider.py` 中。通常需要重写的方法如下：

| 成员 | 是否必填 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 用于 `image_gen.provider` 配置中的稳定标识符 |
| `display_name` | — | `name.title()` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | — | `True` | 用于检测缺失的凭证或依赖项 |
| `list_models()` | — | `[]` | 供 `hermes tools` 模型选择器使用的目录 |
| `default_model()` | — | `list_models()` 中的第一个元素 | 当未配置模型时的默认选项 |
| `get_setup_schema()` | — | 最简结构 | 用于提供选择器元数据及环境变量提示 |
| `generate(prompt, aspect_ratio, **kwargs)` | ✅ | — | 实际执行生成操作的函数 |

## 响应格式

`generate()` 方法必须通过 `success_response()` 或 `error_response()` 返回字典格式的结果。这两个函数均位于 `agent/image_gen_provider.py` 中。

**成功情况：**
```python
success_response(
    image=<url-or-absolute-path>,
    model=<model-id>,
    prompt=<echoed-prompt>,
    aspect_ratio="landscape" | "square" | "portrait",
    provider=<your-provider-name>,
    extra={...},  # optional backend-specific fields
)
```

**错误：**
```python
error_response(
    error="human-readable message",
    error_type="provider_error" | "invalid_input" | "<exception class name>",
    provider=<your-provider-name>,
    model=<model-id>,
    prompt=<prompt>,
    aspect_ratio=<resolved aspect>,
)
```

该工具封装层会将字典进行 JSON 序列化后传递给大语言模型。任何错误都会作为工具的返回结果呈现，由大语言模型自行决定如何向用户解释这些错误。

## 处理 base64 格式与 URL 格式的输出

部分后端会返回图像的 URL（如 fal、Replicate），而其他后端则返回 base64 编码的图像数据（如 OpenAI 的 gpt-image-2）。对于 base64 格式的输出，可使用 `save_b64_image()` 函数——该函数会将图像保存至 `$HERMES_HOME/cache/images/<前缀>_<时间戳>_<唯一标识符>.<扩展名>` 路径下，并返回该路径的绝对地址。随后可在 `success_response()` 函数中以 `image=` 参数的形式传入该路径（作为字符串类型）。无论是 Telegram 的图片消息还是 Discord 的附件，都能识别这两种格式的地址及绝对路径。

## 用户自定义插件

用户可将自己的插件放在 `~/.hermes/plugins/image_gen/<名称>/` 目录下，该插件需具有与内置插件相同的 `name` 属性，随后通过 `hermes plugins enable <名称>` 命令启用它。由于插件注册机制遵循“最后写入者胜出”的原则，用户自定义的版本将会替换掉内置版本。此方法非常适合将 `openai` 插件指向私有代理服务器，或更换为自定义的模型目录。

## 测试

```bash
export HERMES_HOME=/tmp/hermes-imggen-test
mkdir -p $HERMES_HOME/plugins/image_gen/my-backend
# …copy __init__.py + plugin.yaml into that dir…

export MY_BACKEND_API_KEY=your-test-key
hermes plugins enable my-backend

# Pick it as the active provider
echo "image_gen:" >> $HERMES_HOME/config.yaml
echo "  provider: my-backend" >> $HERMES_HOME/config.yaml

# Exercise it
hermes -z "Generate an image of a corgi in a spacesuit"
```

或者通过交互方式操作：执行 `hermes tools` → 选择“图像生成” → 选中 `my-backend` → 如有提示则输入 API 密钥。

## 参考实现

- **`plugins/image_gen/openai/__init__.py`** — 提供低/中/高三个级别的 gpt-image-2 模型，它们实际上共享同一个 API 模型，仅通过不同的 `quality` 参数来区分级别。这是单后端架构下结合 config.yaml 配置优先级链实现分级模型的典型示例。
- **`plugins/image_gen/xai/__init__.py`** — 通过 xAI 技术实现 Grok Imagine 功能。其接口形式有所不同（以 URL 形式返回结果，且目录结构更为简单）。
- **`plugins/image_gen/openai-codex/__init__.py`** — 基于 OpenAI SDK 并采用不同路由基础 URL 的 Codex 风格响应 API 变体。

## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-imggen = "my_backend_imggen_package"
```

`my_backend_imggen_package` 必须提供一个顶层 `register` 函数。有关完整的设置流程，请参阅通用插件指南中的[通过 pip 分发](/developer-guide/plugins#distribute-via-pip)部分。

## 相关页面

- [图像生成](/user-guide/features/image-generation) — 面向用户的功能文档
- [插件概览](/user-guide/features/plugins) — 所有插件类型的概要介绍
- [构建 Hermes 插件](/developer-guide/plugins) — 工具、钩子及斜杠命令的通用指南
