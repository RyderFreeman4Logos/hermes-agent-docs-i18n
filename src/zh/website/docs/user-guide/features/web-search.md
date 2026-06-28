---
title: Web Search & Extract
description: Search the web and extract page content with multiple backend providers — including free self-hosted SearXNG.
sidebar_label: Web Search
sidebar_position: 6
---

# 网页搜索与内容提取

Hermes Agent 提供了两款可通过模型调用的网页工具，这些工具由多种后端服务提供支持：

- **`web_search`** — 在网络上进行搜索并返回排序后的结果  
- **`web_extract`** — 从一个或多个网址中获取并提取可读内容  

这两项功能均可通过选择同一个后端来配置。后端服务可通过 `hermes tools` 命令选择，也可直接在 `config.yaml` 文件中指定。

## 后端服务

| 后端服务 | 环境变量 | 搜索功能 | 提取功能 | 免费额度 |
|----------|---------|--------|---------|-----------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | 每月 500 个积分 |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | ✔ 免费（需自行托管） |
| **Brave Search（免费版）** | `BRAVE_SEARCH_API_KEY` | ✔ | — | 每月 2,000 次查询 |
| **DDGS（DuckDuckGo）** | —（无需密钥） | ✔ | — | ✔ 免费 |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | 每月 1,000 次搜索 |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | 每月 1,000 次搜索 |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | 需付费 |
| **xAI（Grok）** | `XAI_API_KEY` 或 `hermes auth login xai-oauth` | ✔ | — | 需付费（SuperGrok 或按令牌计费） |

Brave Search、DDGS 和 xAI 仅支持搜索功能——若需要内容提取功能，需将它们与 Firecrawl/Tavily/Exa/Parallel 结合使用。DDGS 在底层使用了 [`ddgs` Python 包](https://pypi.org/project/ddgs/)；如果尚未安装，可运行 `pip install ddgs`（或让 Hermes 在首次使用时自动安装）。xAI 则通过 Responses API 运行 Grok 的服务器端 `web_search` 工具——其结果由大语言模型生成而非基于索引，因此标题、描述和网址选择均为模型输出（详见下文的 [关于模型可信度的说明](#xai-grok)）。

**按功能独立配置**：您可以为搜索和提取分别使用不同的后端服务——例如，搜索使用免费的 SearXNG，而提取则使用 Firecrawl。详情请参阅下文 [按功能独立配置](#per-capability-configuration)。

:::提示 Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅账号，即可通过 **[Tool Gateway](tool-gateway.md)** 使用由 Firecrawl 提供的托管服务来执行网页搜索和内容提取——无需 API 密钥。新安装的用户可运行 `hermes setup --portal` 登录并一次性启用所有网关工具；现有用户则可通过 `hermes tools` 仅启用网页搜索功能。
:::

---

## `web_extract` 如何处理长页面

后端服务会返回原始的页面 Markdown 格式内容，这类内容可能非常庞大（如论坛帖子、文档网站、包含嵌入评论的新闻文章等）。为保持上下文窗口的有效性并降低成本，`web_extract` 会在将内容传递给智能体之前，先通过 **`web_extract` 辅助模型** 对其进行处理。该功能的处理方式完全取决于页面大小：

| 页面大小（字符数） | 处理方式 |
|------------------|----------|
| 5,000 字符以下 | 按原样返回——无需调用大语言模型，完整的 Markdown 内容会直接传递给智能体 |
| 5,000 – 500,000 字符 | 通过 `web_extract` 辅助模型进行单次摘要处理，输出结果长度限制在约 5,000 字符 |
| 500,000 – 2,000,000 字符 | 拆分处理：将页面内容分割为 100,000 字符大小的块，对每个块并行进行摘要处理，最后综合生成一份最终摘要（约 5,000 字符） |
| 超过 2,000,000 字符 | 拒绝处理，并提示用户使用内容更精简的网址 |

该摘要功能会保留引文、代码块及关键事实的原始格式——它属于内容压缩工具，而非改写工具。如果摘要生成失败或超时，Hermes 会回退到前约 5,000 字符的原始内容，而不会返回无用的错误信息。

### 哪个模型负责生成摘要？

是 `web_extract` 辅助任务。默认情况下（`auxiliary.web_extract.provider: "auto"`），使用的是您的 **主聊天模型**——即与 `hermes model` 相同的提供者和模型。对于大多数场景而言这已足够，但在那些计算成本较高的推理模型（如 Opus、MiniMax M2.7 等）上，每次处理长页面都会产生额外费用。

无论您使用的主模型是什么，都可以将提取后的内容摘要路由到某个廉价且快速的模型上进行进一步处理：

```yaml
# ~/.hermes/config.yaml
auxiliary:
  web_extract:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 360       # seconds; raise if you hit summarization timeouts
```

或者通过交互方式选择：`hermes model` → **配置辅助模型** → `web_extract`。

如需完整参考信息及针对不同任务的覆盖规则，请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。

### 当摘要功能造成干扰时

如果您需要原始的、未经摘要处理的页面内容——例如在抓取结构化页面时，LLM生成的摘要会遗漏重要字段——建议改用`browser_navigate` + `browser_snapshot`。该浏览器工具能够返回实时的可访问性树结构，且不会经过辅助模型的重新处理（不过对于内容过长的页面，仍受其8,000字符的快照长度限制）。

---

## 设置

### 通过 `hermes tools` 快速设置

运行 `hermes tools`，进入**网页搜索与提取**选项，然后选择相应的服务提供商。向导会提示输入所需的URL或API密钥，并将其保存到您的配置文件中。

```bash
hermes tools
```

### Firecrawl（默认选项）

具备全面的搜索与提取功能，非常适合大多数用户使用。

```bash
# ~/.hermes/.env
FIRECRAWL_API_KEY=fc-your-key-here
```

请在 [firecrawl.dev](https://firecrawl.dev) 获取密钥。免费套餐每月提供 500 个积分。

**自托管版 Firecrawl：** 直接指向您自己的实例，而非云端 API：

```bash
# ~/.hermes/.env
FIRECRAWL_API_URL=http://localhost:3002
```

当设置了 `FIRECRAWL_API_URL` 后，API 密钥即为可选项（可通过设置 `USE_DB_AUTHENTICATION=false` 关闭服务器身份验证）。

---

### SearXNG（免费，自托管）

SearXNG 是一款注重隐私保护的开源元搜索引擎，能够聚合来自 70 多个搜索引擎的搜索结果。**无需 API 密钥**——只需将 Hermes 指向正在运行的 SearXNG 实例即可。

SearXNG 仅支持搜索功能——`web_extract` 功能需要单独的提取服务提供商。

#### 方案 A — 使用 Docker 自托管（推荐）

此方案可让您拥有无速率限制的私有实例。

**1. 创建工作目录：**

```bash
mkdir -p ~/searxng/searxng
cd ~/searxng
```

**2. 编写 `docker-compose.yml` 文件：**

```yaml
# ~/searxng/docker-compose.yml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8888:8080"
    volumes:
      - ./searxng:/etc/searxng:rw
    environment:
      - SEARXNG_BASE_URL=http://localhost:8888/
    restart: unless-stopped
```

**3. 启动容器：**

```bash
docker compose up -d
```

**4. 启用 JSON API 格式：**

SearXNG 默认处于禁用 JSON 输出的状态。请复制生成的配置文件并将其启用：

```bash
# Copy the auto-generated config out of the container
docker cp searxng:/etc/searxng/settings.yml ~/searxng/searxng/settings.yml
```

打开 `~/searxng/searxng/settings.yml` 文件。如果其中存在 `use_default_settings: true` 这一选项，那么该文件将仅包含您自定义的设置，其余所有设置都会沿用内置的默认值。若希望为 Hermes 启用 JSON 格式的响应，需添加以下自定义设置：

```yaml
search:
  formats:
    - html
    - json
```

您的 `settings.yml` 文件应类似于以下结构：

```yaml
# Read the documentation before extending the defaults:
# https://docs.searxng.org/admin/settings/

use_default_settings: true

server:
  secret_key: "abcdef12345678"
  image_proxy: true

search:
  formats:
    - html
    - json
```

**5. 重启以应用更改：**

```bash
docker cp ~/searxng/searxng/settings.yml searxng:/etc/searxng/settings.yml
docker restart searxng
```

**6. 验证其功能是否正常：**

```bash
curl -s "http://localhost:8888/search?q=test&format=json" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"results\"])} results')"
```

您应该会看到类似“10个结果”的提示。如果出现“403 禁止访问”的错误，说明 JSON 格式仍未启用——请重新检查第4步。

**7. 配置 Hermes：**

```bash
# ~/.hermes/.env
SEARXNG_URL=http://localhost:8888
```

接着在 `~/.hermes/config.yaml` 文件中选择 SearXNG 作为搜索后端：

```yaml
web:
  search_backend: "searxng"
```

或者通过 `hermes tools` → Web Search & Extract → SearXNG 来进行设置。

---

#### 方案 B — 使用公共实例

公共 SearXNG 实例的列表可在 [searx.space](https://searx.space/) 查看。请筛选出已开启 **JSON 格式** 的实例（会在表格中显示）。

```bash
# ~/.hermes/.env
SEARXNG_URL=https://searx.example.com
```

:::警告 公共实例
公共实例存在速率限制，运行时间不稳定，且可能随时停止支持 JSON 格式。如需用于生产环境，强烈建议自行托管。
:::

---

#### 将 SearXNG 与提取提供程序配对

SearXNG 负责搜索功能，而 `web_extract` 功能则需要单独的提供程序。请使用对应功能的密钥：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"   # or tavily, exa, parallel
```

通过此配置，Hermes 会使用 SearXNG 处理所有搜索查询，并借助 Firecrawl 进行网址提取——从而将免费搜索与高质量数据提取功能完美结合。

---

### Tavily

提供经过 AI 优化的搜索与提取功能，同时还拥有充足的免费使用额度。

```bash
# ~/.hermes/.env
TAVILY_API_KEY=tvly-your-key-here
```

请在 [app.tavily.com](https://app.tavily.com/home) 获取密钥。免费套餐每月提供 1,000 次搜索额度。

---

### Exa

具备语义理解能力的神经网络搜索工具，非常适合用于研究及查找概念上相关的内容。

```bash
# ~/.hermes/.env
EXA_API_KEY=your-exa-key-here
```

请在 [exa.ai](https://exa.ai) 获取密钥。免费套餐每月提供 1,000 次搜索额度。

---

### Parallel

具备深度研究能力的原生 AI 搜索与提取工具。

```bash
# ~/.hermes/.env
PARALLEL_API_KEY=your-parallel-key-here
```

可通过 [parallel.ai](https://parallel.ai) 获取访问权限。

---

### xAI (Grok) {#xai-grok}

在 Responses API 中，该功能会将 `web_search` 请求路由至 Grok 服务器端的 [web_search 工具](https://docs.x.ai/developers/tools/web-search)。Grok 负责执行实际搜索，并以结构化的 JSON 格式返回最佳结果。

支持两种凭证配置方式——无需新增环境变量，也无需额外的设置向导：

```bash
# ~/.hermes/.env (env-var path)
XAI_API_KEY=sk-xai-your-key-here
```

或针对 SuperGrok 订阅用户：

```bash
hermes auth login xai-oauth
```

接着选择 xAI 作为搜索后端：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "xai"
```

**可选参数：**

```yaml
web:
  backend: "xai"
  xai:
    model: grok-build-0.1        # reasoning model required by web_search (default)
    allowed_domains:             # optional, max 5 — mutex with excluded_domains
      - arxiv.org
    excluded_domains:            # optional, max 5
      - example-spam.com
    timeout: 90                  # seconds (default)
```

**仅搜索模式**——如果您同时需要`web_extract`功能，则需将其与Firecrawl / Tavily / Exa / Parallel搭配使用。当遇到401错误时，该服务提供商会强制刷新一次OAuth令牌并尝试重试（可处理窗口期内的令牌撤销以及主动过期检查无法解析的加密令牌）；而通过环境变量传递的凭证则无需进行重试。

:::警示 信任模型
与Brave、Tavily、Exa等基于索引的服务提供商会原封不动地返回搜索引擎的结果不同，xAI属于大型语言模型，它自行决定展示哪些网址，并负责生成这些网址的标题和描述。查询的*内容*会直接影响输出结果，因此，若查询内容是经恶意构造的（例如通过代理工具获取的不可信上游输入注入的），理论上就有可能引导Grok展示攻击者指定的网址。对待返回的网址应与处理任何模型生成的链接保持一致——在获取数据之前务必进行验证，尤其是当查询来自不可信来源时。
:::

---

## 配置

### 单一后端

为所有网页相关功能设置一个服务提供商：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "searxng"   # firecrawl | searxng | brave-free | ddgs | tavily | exa | parallel | xai
```

### 按功能配置

为搜索与数据提取分别使用不同的服务提供商。这样一来，您既可以将免费的搜索服务（SearXNG）与付费的数据提取服务结合使用，也可以反之：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"     # used by web_search
  extract_backend: "firecrawl"  # used by web_extract
```

当各功能对应的配置键为空时，系统会回退至 `web.backend`。若 `web.backend` 也为空，则会根据现有的 API 密钥或 URL 自动检测后端。

**各功能的优先级顺序：**
1. `web.search_backend` / `web.extract_backend`（针对特定功能明确指定）
2. `web.backend`（通用回退选项）
3. 根据环境变量自动检测

### 自动检测机制

如果未明确配置后端，Hermes 会根据已设置的凭据选择第一个可用的后端：

| 已设置的凭据 | 自动选定的后端 |
|--------------|----------------|
| `FIRECRAWL_API_KEY` 或 `FIRECRAWL_API_URL` | firecrawl |
| `PARALLEL_API_KEY` | parallel |
| `TAVILY_API_KEY` | tavily |
| `EXA_API_KEY` | exa |
| `SEARXNG_URL` | searxng |

xAI Web Search 不在自动检测范围内——即使设置了 `XAI_API_KEY` 或通过 xAI Grok OAuth 登录，也不会自动将网页请求路由至 xAI，因为这些凭据同样用于推理、文本转语音及图像生成功能，用户可能希望为网页搜索使用不同的后端。如需手动指定，可使用 `web.backend: "xai"`。

---

## 验证您的设置

运行 `hermes setup` 可查看系统检测到的网页后端类型：

```
✅ Web Search & Extract (searxng)
```

或者通过 CLI 进行查看：

```bash
# Activate the venv and run the web tools module directly
source ~/.hermes/hermes-agent/.venv/bin/activate
python -m tools.web_tools
```

这将输出当前正在使用的后端及其状态：

```
✅ Web backend: searxng
   Using SearXNG (search only): http://localhost:8888
```

## 故障排除

### `web_search` 返回 `{"success": false}`

- 检查 `SEARXNG_URL` 是否可访问：执行 `curl -s "http://localhost:8888/search?q=test&format=json"` 
- 如果出现 HTTP 403 错误，说明 JSON 格式已被禁用——请在 `settings.yml` 中的 `formats` 列表中添加 `json` 并重启服务
- 如果出现连接错误，可能是容器未运行：执行 `docker ps | grep searxng`

### `web_extract` 显示“仅支持搜索的后端”

SearXNG 无法提取 URL 内容。请将 `web.extract_backend` 设置为支持内容提取的提供方：

```yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"  # or tavily / exa / parallel
```

### SearXNG 返回 0 条结果

某些公共实例会禁用特定的搜索引擎或搜索类别。可以尝试：
- 使用不同的查询词
- 切换到 [searx.space](https://searx.space/) 上的其他公共实例
- 自行托管实例以获得更可靠的结果

### 在公共实例上遇到速率限制

请切换到自托管实例（参见上文[选项 A](#option-a--self-host-with-docker-recommended)）。使用 Docker 托管的实例不存在速率限制问题。

### `web_extract` 返回被截断的内容，并附带“摘要生成超时”的提示

辅助模型未能在设定的超时时间内完成摘要生成。可以采取以下措施：
- 在 `config.yaml` 中增加 `auxiliary.web_extract.timeout` 的值（新安装时的默认值为 360 秒，若该键不存在则默认为 30 秒）
- 将 `web_extract` 辅助任务更换为速度更快的模型（例如 `google/gemini-3-flash-preview`）——详见[How `web_extract` handles long pages](#how-web_extract-handles-long-pages)
- 对于不适合使用摘要生成功能的页面，改用 `browser_navigate` 工具

---

## 可选技能：`searxng-search`

对于需要通过 `curl` 直接使用 SearXNG 的智能体（例如在网页工具集不可用时的备用方案），可安装 `searxng-search` 这一可选技能：

```bash
hermes skills install official/research/searxng-search
```

该功能会新增一项技能，用于指导智能体掌握以下操作方法：
- 通过 `curl` 或 Python 调用 SearXNG JSON API；
- 按类别（如“综合”、“新闻”、“科学”等）进行筛选；
- 处理分页及错误情况；
- 在无法连接 SearXNG 时实现平滑的降级处理。
