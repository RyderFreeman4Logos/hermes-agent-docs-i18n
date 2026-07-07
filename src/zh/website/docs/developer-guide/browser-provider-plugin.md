---
sidebar_position: 13
title: "Browser Provider Plugins"
description: "How to build a cloud browser backend plugin for Hermes Agent"
---

# 构建浏览器提供程序插件

浏览器提供程序插件用于注册**云浏览器后端**，该后端可处理云端模式下的 `browser_*` 工具调用（如导航、点击、截图等）。内置的提供程序——Browserbase、Browser Use 和 Firecrawl——均以插件形式存在于 `plugins/browser/<name>/` 目录下。你可以通过在该目录旁创建新文件夹来添加自定义插件，或覆盖现有的内置插件。

:::提示
浏览器后端是 Hermes 支持的多种**后端插件**之一。其他类型的后端插件及其对应的 ABC 接口包括：[Web 搜索提供程序插件](/developer-guide/web-search-provider-plugin)（其 ABC 接口与此处刻意保持一致）、[图像生成插件](/developer-guide/image-gen-provider-plugin)、[视频生成插件](/developer-guide/video-gen-provider-plugin)、[内存提供程序插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)、[机密信息源插件](/developer-guide/secret-source-plugin)以及[模型提供程序插件](/developer-guide/model-provider-plugin)。常规的工具/钩子/CLI 插件则位于 [构建 Hermes 插件](/developer-guide/plugins) 文档中。
:::

## 各组件的协同工作方式

浏览器提供程序本身并不负责实际的浏览操作，而是负责管理**会话生命周期**：创建远程浏览器会话、返回 CDP WebSocket 地址，以及最终终止该会话。Hermes 自带的浏览器栈（`agent-browser` + `tools/browser_tool.py`）会连接到你返回的任何 CDP 地址，并从那里控制页面操作——因此所有提供程序都能免费使用完整的 `browser_*` 工具集。

活跃的提供程序由 `config.yaml` 文件中的 `browser.cloud_provider` 参数指定；而 `tools/browser_tool.py` 中的调度器仅通过注册表进行查找，不会针对不同提供程序设置任何条件判断。

## 插件发现机制

Hermes 会在三个位置扫描浏览器后端插件：

1. **内置插件**——位于 `<repo>/plugins/browser/<name>/` 目录下，带有 `kind: backend` 标记，会自动加载。
2. **用户自定义插件**——位于 `~/.hermes/plugins/browser/<name>/` 目录下，需通过 `plugins.enabled` 或 `hermes plugins enable <name>` 参数启用。
3. **Pip 安装的插件**——即那些声明了 `hermes_agent.plugins` 入口点的包。

每个插件都会在其 `register(ctx)` 方法中调用 `ctx.register_browser_provider()`，该方法会将该插件实例添加到 `agent/browser_registry.py` 中的注册表中。

## 目录结构

```
plugins/browser/my-backend/
├── __init__.py     # register() entry point
├── provider.py     # BrowserProvider subclass
└── plugin.yaml     # Manifest with kind: backend and provides_browser_providers
```

`plugin.yaml`：  
插件配置文件

```yaml
name: browser-my-backend
version: 1.0.0
description: "My cloud browser backend. Requires MY_BACKEND_API_KEY."
author: you
kind: backend
provides_browser_providers:
  - my-backend
```

`__init__.py`：

```python
from plugins.browser.my_backend.provider import MyBackendProvider


def register(ctx) -> None:
    ctx.register_browser_provider(MyBackendProvider())
```

## BrowserProvider 接口规范

需实现 `agent.browser_provider.BrowserProvider` 接口，该接口包含三个生命周期方法以及身份识别相关功能：

```python
from agent.browser_provider import BrowserProvider


class MyBackendProvider(BrowserProvider):
    @property
    def name(self) -> str:
        return "my-backend"          # the browser.cloud_provider config value

    @property
    def display_name(self) -> str:
        return "My Backend"          # shown in `hermes tools`

    def is_available(self) -> bool:
        """Cheap check only — env var present, dep importable.
        NO network calls: runs at tool-registration time and on every
        `hermes tools` paint."""
        return bool(os.environ.get("MY_BACKEND_API_KEY"))

    def create_session(self, task_id: str) -> dict:
        """Create a remote browser session; return the session-metadata contract."""
        session = my_api.create_browser(...)
        return {
            "session_name": f"my-backend-{task_id}",  # unique agent-browser session name
            "bb_session_id": session.id,              # provider session ID (for cleanup)
            "cdp_url": session.cdp_ws_url,            # CDP websocket URL
            "features": {"stealth": True},            # feature flags you enabled
        }

    def close_session(self, session_id: str) -> bool:
        """Terminate by provider session ID. Log-and-return-False on error —
        never raise, so the dispatcher's cleanup loop keeps moving."""
        ...

    def emergency_cleanup(self, session_id: str) -> None:
        """Best-effort teardown from atexit/signal handlers. Must not raise."""
        ...
```

### 会话元数据契约

`create_session()` 函数至少需要返回 `session_name`、`bb_session_id`、`cdp_url` 和 `features` 这些参数。有两个需要注意的特殊点：

- **`bb_session_id` 是一个旧版键名**，为保持与 `tools/browser_tool.py` 的向后兼容性而原封不动保留——它无论来自哪个供应商，都存储着*您所使用提供商的*会话 ID，因此请勿重命名。
- `create_session()` **可能会抛出异常**：若缺少凭证则会引发 `ValueError`，若出现网络或 API 错误则会引发 `RuntimeError`。调度器会将这些异常展示给用户。这与 `close_session`/`emergency_cleanup` 不同，后两者绝不能抛出任何异常。

可选的 `external_call_id` 键可用于支持托管网关计费功能。

### `get_setup_schema()` —— “Hermes Tools”选择项行

通过重写此函数，可在浏览器自动化选择器中将其设为首选选项，并显示 API 密钥输入界面及安装钩子：

```python
def get_setup_schema(self) -> dict:
    return {
        "name": "My Backend",
        "badge": "paid",
        "tag": "Cloud browser with stealth and proxies",
        "env_vars": [
            {"key": "MY_BACKEND_API_KEY",
             "prompt": "My Backend API key",
             "url": "https://mybackend.example"},
        ],
        "post_setup": "agent_browser",   # auto-installs the agent-browser npm dep
    }
```

根据项目关于工具后端的规范：如果无法通过 `hermes tools` 选择并配置后端，则该任务尚未完成——“手动设置此环境变量”并不算是一种真正的集成方式。

## 由用户自行配置

```yaml
browser:
  cloud_provider: my-backend
```

## 参考实现

`plugins/browser/` 目录下预置的三个提供程序分别是按复杂度由低到高排列的标准示例：`firecrawl`（最简单）、`browser_use` 以及 `browserbase`（具备隐身模式、代理支持及保持连接功能；在付费功能不可用时还能实现平滑降级处理）。请选择与自身需求最接近的实现方案进行复制。

## 检查清单

- [ ] `name` 属性需为小写且保持不变（该值由用户直接写入配置中）
- [ ] `is_available()` 方法不得发起任何网络请求
- [ ] `create_session()` 方法需返回完整的元数据结构（且 `bb_session_id` 键名必须保持不变）
- [ ] `close_session()` / `emergency_cleanup()` 方法绝不能抛出异常
- [ ] `get_setup_schema()` 方法需暴露相关环境变量，以便 `hermes tools` 能够配置后端服务
- [ ] `plugin.yaml` 文件中需明确标注 `kind: backend` 以及 `provides_browser_providers` 属性
