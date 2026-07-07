---
sidebar_position: 12
title: "Web Search Provider Plugins"
description: "How to build a web-search/extract/crawl backend plugin for Hermes Agent"
---

# 构建网页搜索提供者插件

网页搜索提供者插件用于注册能够处理 `web_search`、`web_extract` 以及（可选的）深度爬取任务的后端服务。所有内置提供者——Firecrawl、SearXNG、Tavily、Exa、Parallel、Brave Search（免费版）、xAI 和 DDGS——均以 `plugins/web/<名称>/` 目录的形式作为插件提供。您可以通过在该目录旁创建新文件夹来添加自定义插件，或覆盖现有的内置插件。

:::提示
网页搜索是 Hermes 支持的多种**后端插件**之一。其他类型的插件及其对应的缩写包括：[图像生成提供者插件](/developer-guide/image-gen-provider-plugin)、[视频生成提供者插件](/developer-guide/video-gen-provider-plugin)、[内存提供者插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)以及[模型提供者插件](/developer-guide/model-provider-plugin)。而常规的工具/钩子/CLI 插件则位于 [构建 Hermes 插件](/developer-guide/plugins) 文档中。
:::

## 发现机制的工作原理

Hermes 会在三个位置查找网页搜索后端：

1. **内置插件** — `<仓库路径>/plugins/web/<名称>/`（带有 `kind: backend` 标签，始终会被加载）
2. **用户自定义插件** — `~/.hermes/plugins/web/<名称>/`（需通过 `plugins.enabled` 或 `hermes plugins enable <名称>` 手动启用）
3. **Pip 安装的插件** — 包含 `hermes_agent.plugins` 入口点的包

每个插件中的 `register(ctx)` 函数都会调用 `ctx.register_web_search_provider(...)`，从而将该插件的实例注册到 `agent/web_search_registry.py` 中的注册表中。针对各项功能的默认后端将通过配置来确定：

| 功能 | 配置键 | 默认回退值 |
|---|---|---|
| `web_search` | `web.search_backend` | `web.backend` |
| `web_extract` | `web.extract_backend` | `web.backend` |
| `web_extract` 中的深度爬取模式 | `web.extract_backend` | `web.backend` |

如果上述配置键均未设置，Hermes 会自动从环境变量中存在的 API 密钥或 URL 中检测合适的后端。`hermes tools` 工具可指导用户完成后端的选定过程。

## 目录结构

```
plugins/web/my-backend/
├── __init__.py     # register() entry point
├── provider.py     # WebSearchProvider subclass
└── plugin.yaml     # Manifest with kind: backend and provides_web_providers
```

`brave_free/` 和 `ddgs/` 是树结构中最小的引用项——`brave_free` 对应需通过 API 密钥才能使用的仅支持搜索的提供者，而 `ddgs` 则是无需密钥、会延迟加载其 SDK 的提供者。

## WebSearchProvider 抽象基类

该类继承自 `agent.web_search_provider.WebSearchProvider`。必须实现的成员仅有 `name`、`is_available()`，以及您选择的 `search()` 或 `extract()` 方法之一。（深度爬取并非独立的函数，而是 `extract()` 方法的一种模式。）

```python
# plugins/web/my-backend/provider.py
from __future__ import annotations

import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider


class MyBackendWebSearchProvider(WebSearchProvider):
    """Minimal search-only provider against the My Backend HTTP API."""

    @property
    def name(self) -> str:
        # Stable id used in web.search_backend / web.extract_backend / web.backend
        # config keys. Lowercase, no spaces; hyphens permitted.
        return "my-backend"

    @property
    def display_name(self) -> str:
        # Human label shown in `hermes tools`. Defaults to `name`.
        return "My Backend"

    def is_available(self) -> bool:
        # Cheap check — env var present, optional dep importable, etc.
        # MUST NOT make network calls (runs on every `hermes tools` paint).
        return bool(os.getenv("MY_BACKEND_API_KEY", "").strip())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        import httpx

        api_key = os.environ["MY_BACKEND_API_KEY"]
        try:
            resp = httpx.get(
                "https://api.example.com/search",
                params={"q": query, "count": max(1, min(int(limit), 20))},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            return {"success": False, "error": str(exc)}

        # Response shape is fixed — see "Response shape" below.
        return {
            "success": True,
            "data": {
                "web": [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("snippet", ""),
                        "position": idx + 1,
                    }
                    for idx, item in enumerate(data.get("results", []))
                ],
            },
        }
```

```python
# plugins/web/my-backend/__init__.py
from plugins.web.my_backend.provider import MyBackendWebSearchProvider


def register(ctx) -> None:
    """Plugin entry point — called once at load time."""
    ctx.register_web_search_provider(MyBackendWebSearchProvider())
```

## plugin.yaml 配置文件

```yaml
name: web-my-backend
version: 1.0.0
description: "My Backend web search — Bearer-auth REST API"
author: Your Name
kind: backend
provides_web_providers:
  - my-backend
requires_env:
  - MY_BACKEND_API_KEY
```

| 键值 | 用途 |
|---|---|
| `kind: backend` | 将插件通过后端加载路径进行路由处理 |
| `provides_web_providers` | 该插件注册的提供者名称列表——加载器会在执行 `register()` 方法之前，利用此列表在 `hermes tools` 中展示该插件 |
| `requires_env` | 在执行 `hermes plugins install` 时触发交互式凭据输入（有关详细格式，请参阅[构建 Hermes 插件](/developer-guide/plugins#gate-on-environment-variables)） |

## ABC 参考

完整接口定义位于 `agent/web_search_provider.py` 文件中。您可以重写的 方法如下：

| 成员 | 是否必选 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 用于 `web.*_backend` 配置中的稳定标识符 |
| `display_name` | — | `name` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | ✅ | — | 可用性检测机制——基于环境变量及可选依赖项判断 |
| `supports_search()` | — | `True` | 用于 `web_search` 路由的能力标志 |
| `supports_extract()` | — | `False` | 用于 `web_extract` 路由的能力标志 |
| `search(query, limit)` | 条件性 | 抛出异常 | 当 `supports_search()` 返回 `True` 时必须实现 |
| `extract(urls, **kwargs)` | 条件性 | 抛出异常 | 当 `supports_extract()` 返回 `True` 时必须实现 |

单个类即可支持多种功能——Firecrawl、Tavily、Exa 和 Parallel 均同时具备搜索和提取功能。Brave Search 和 DDGS 仅支持搜索功能；SearXNG 也仅支持搜索功能，但文档中提供了“与我搭配提取提供者”的使用方案。

## 响应格式

工具封装层期望统一的响应结构，从而无需在不同后端之间进行转换。

**搜索成功时：**

```python
{
    "success": True,
    "data": {
        "web": [
            {"title": str, "url": str, "description": str, "position": int},
            ...
        ],
    },
}
```

**提取成功：**

```python
{
    "success": True,
    "data": [
        {
            "url": str,
            "title": str,
            "content": str,
            "raw_content": str,
            "metadata": dict,    # optional
            "error": str,        # optional, only on per-URL failure
        },
        ...
    ],
}
```

**任一功能在发生故障时：**

```python
{"success": False, "error": "human-readable message"}
```

`search()` 和 `extract()` 都可以定义为 `async def` 函数——调度器会通过 `inspect.iscoroutinefunction` 来识别协程函数，并据此进行等待处理。对于小型后端系统，那些执行阻塞式 I/O 操作（如 HTTP 请求、SDK 调用）的同步实现也是完全可以的，因为调度器会负责线程管理。

## 功能标志

Hermes 会根据 `supports_*` 标志将请求路由到合适的提供方。常见的多提供方配置方式如下：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "brave-free"     # search-only, fast, free 2k/mo
  extract_backend: "firecrawl"     # extract + crawl, paid quota
```

当未设置 `web.search_backend` 或 `web.extract_backend` 时，系统会自动回退到 `web.backend`。如果该选项也未配置，Hermes 会根据环境变量的存在情况，选择第一个支持所需功能的可用提供者。

如果您的提供者仅支持一种功能，请将其他标志保持默认值（`False`），这样注册表就会跳过该工具——这样当用户仅使用该工具进行搜索却要求智能体执行提取操作时，就不会出现“提供者 X 失败”这类误导性错误。

## Hermes 如何将其集成到工具中

`web_search` 和 `web_extract` 工具位于 `tools/web_tools.py` 文件中。在调用时，它们会执行以下步骤：

1. 读取相关的配置键（`web_search` 使用 `web.search_backend`，`web_extract` 使用 `web.extract_backend`）；
2. 向注册表请求具有该 `name` 的提供者；
3. 检查 `is_available()` 方法以及对应的 `supports_*()` 标志；
4. 调用 `search()` / `extract()` 方法（深度爬取功能作为 `extract()` 内部的模式运行），如果是协程则等待其执行完成；
5. 将响应结果序列化为 JSON 后传回给大语言模型。

错误会以工具结果的形式呈现，由大语言模型决定如何解释这些错误。如果未注册任何提供者（或所有可用提供者均不满足功能要求），该工具会返回指向 `hermes tools` 的有用错误信息。

## 懒加载可选依赖项

如果您的提供者封装了第三方 SDK（例如 DDGS 所使用的 `ddgs` 包），请勿在模块顶层进行 `import` 操作。应在 `is_available()` 或 `search()` 方法中使用 `tools.lazy_deps.ensure(...)` —— Hermes 会在首次使用时根据 `security.allow_lazy_installs` 的设置来安装该包。有关安全机制的详细信息，请参阅 [构建 Hermes 插件 → 懒加载](/developer-guide/plugins#lazy-install-optional-python-dependencies)。

## 参考实现示例

- **`plugins/web/brave_free/`** —— 一个小型、需 API 密钥且仅支持搜索的 HTTP 提供者，是不错的入门模板。
- **`plugins/web/ddgs/`** —— 无需密钥且会懒加载 SDK 的提供者，适用于封装了 Python 包的后端实现。
- **`plugins/web/firecrawl/`** —— 具备多种功能（搜索、提取、爬取）的完整提供者，支持多种格式处理模式。
- **`plugins/web/searxng/`** —— 自托管、通过 URL 配置且无需身份验证的后端。
- **`plugins/web/xai/`** —— 基于 Grok 服务器端 `web_search` 工具的大语言模型驱动搜索方案。该示例展示了如何在不新增环境变量的情况下，复用现有的 OAuth/环境变量认证机制（`tools/xai_http.py`），以及如何编写符合“无网络环境”要求的简单 `is_available()` 方法。

## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-web = "my_backend_web_package"
```

`my_backend_web_package` 必须提供一个顶层 `register` 函数。有关完整的设置步骤，请参阅通用插件指南中的[通过 pip 分发](/developer-guide/plugins#distribute-via-pip)部分。

## 相关页面

- [网络搜索](/user-guide/features/web-search) — 面向用户的功能文档及各后端配置说明
- [插件概览](/user-guide/features/plugins) — 所有插件类型的简要介绍
- [构建 Hermes 插件](/developer-guide/plugins) — 通用工具、钩子函数及斜杠命令指南
