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

这两项功能均可通过选择同一个后端来配置。后端服务既可通过 `hermes tools` 命令选择，也可直接在 `config.yaml` 文件中指定。

## 后端服务列表

| 后端服务 | 环境变量 | 搜索功能 | 提取功能 | 免费额度 |
|----------|---------|--------|---------|-----------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY`（可选——选择该服务时可无需密钥） | ✔ | ✔ | 每月 500 个查询次数；选择“无密钥云服务”模式则无需密钥 |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | ✔ 免费（需自行托管） |
| **Brave Search（免费版）** | `BRAVE_SEARCH_API_KEY` | ✔ | — | 每月 2,000 次查询次数 |
| **DDGS（DuckDuckGo）** | —（无需密钥） | ✔ | — | ✔ 免费 |
| **Exa** | `EXA_API_KEY`（可选） | ✔ | ✔ | ✔ 属于“无密钥会员”；使用密钥时每月可进行 1,000 次搜索 |
| **Parallel** | `PARALLEL_API_KEY`（可选） | ✔ | ✔ | ✔ 属于“无密钥会员”；使用密钥则需付费 |
| **Tavily** | `TAVILY_API_KEY`（可选） | ✔ | ✔ | ✔ 选择该服务时可启用无密钥模式 |
| **Perplexity** | `PERPLEXITY_API_KEY` | ✔ | ✔（可获取与查询相关的片段） | 需付费（按每次请求收取 Search API 费用） |
| **Keenable** | `KEENABLE_API_KEY`（可选） | ✔ | ✔ | ✔ 属于“无密钥会员”；使用密钥则需付费 |
| **xAI（Grok）** | `XAI_API_KEY` 或 `hermes auth add xai-oauth` | ✔ | — | 需付费（按 SuperGrok 计费或按令牌数量计费） |
Brave Search、DDGS 和 xAI 仅具备**搜索功能**——若您同时需要 `web_extract` 功能，可将它们与 Firecrawl/Tavily/Perplexity/Keenable/Exa/Parallel 结合使用。DDGS 在底层使用了 [`ddgs` Python 包](https://pypi.org/project/ddgs/)；如果该包尚未安装，请运行 `pip install ddgs`（或让 Hermes 在首次使用时自动安装）。xAI 则通过 Responses API 调用 Grok 的服务器端 `web_search` 工具——其返回结果由大语言模型生成，而非基于索引，因此标题、描述及 URL 的选择均为模型输出（详见下文的[关于模型可信度的说明](#xai-grok)）。

**按功能分离配置**：您可以为搜索和数据提取分别使用不同的服务提供商——例如用免费的 SearXNG 进行搜索，再用 Firecrawl 进行数据提取。详情请参阅下文的[按功能配置](#per-capability-configuration)。

:::info 开箱即用——无需密钥的免费层级服务  
全新安装后，**完全无需任何网站凭证**即可立即使用 `web_search` 和 `web_extract` 功能：请求会按轮询方式在环内各供应商的公共免费服务端之间切换——包括 **Exa、Parallel、Firecrawl 和 Keenable**——从而实现负载均衡。遇到速率限制时，请求会自动尝试向环中的下一个供应商发送（多跳机制，直至有服务端响应或所有服务端均被限流）。无需注册，也无需密钥。此免费层级仅作为最后手段使用——任何已配置的后端或有效的 API 密钥都将优先生效——且请求不包含任何用户标识信息（仅有一个随机生成的进程级会话 ID，重启时会重新生成）。如需获得稳定、无限流的体验，请配置带密钥的供应商。可通过设置 `web.keyless_fallback: false` 完全禁用无需密钥的免费层级。  

:::  
**明确选择免费或付费版本：** 在 `hermes tools` 中，Exa、Parallel 和 Keenable 各自会显示为两行——**免费（无需密钥）**和**付费（需 API 密钥）**。选择免费版本时，系统会使用该供应商的匿名端点（即便后续您添加了密钥也是如此）；而选择付费版本则必须使用带密钥的路径，若缺少密钥，则会直接报错，而不会自动降级为免费版本。此选择会被保存为 `web.provider_tier.<名称>: free|paid` 的格式；如不进行设置，则系统将自动判断（有密钥则使用付费版本，否则使用无需密钥的环式服务）。

:::提示 Nous订阅用户
如果您拥有付费的[Nous Portal](https://portal.nousresearch.com)订阅权限，即可通过**[Tool Gateway](tool-gateway.md)**借助托管的Firecrawl功能进行网页搜索与内容提取，且无需API密钥。新安装的用户可运行`hermes setup --portal`登录并一次性启用所有网关工具；已有安装的用户则可通过`hermes tools`仅启用网页相关功能。
:::

---

## `web_extract`如何处理长页面

后端会返回原始的页面Markdown格式内容，这类内容可能体积巨大（如论坛帖子、文档网站、包含嵌入评论的新闻文章）。为确保上下文窗口的有效性，`web_extract`会采用**固定字符配额机制**——不会借助大语言模型进行总结：

| 页面大小（字符数） | 处理方式 |
|------------------|----------|
| 未超过配额（默认为15,000） | 完整返回——所有Markdown内容都会传递给智能体 |
| 超过配额 | 仅返回页面开头和结尾部分（开头约占75%，结尾约占25%，切割点以Markdown行分隔符为准），并添加明确的`[TRUNCATED]`页脚说明。完整的纯文本会被存储到磁盘，页脚会告知智能体文件路径以及用于读取被省略中间内容的精确`read_file`调用方式 |
| 超过2,000,000字符 | 存储的文本上限为2MB |

每页的字符配额可通过`config.yaml`中的`web.extract_char_limit`参数进行配置（默认值为15,000，实际范围限制在2,000至500,000之间），智能体也可通过该工具的`char_limit`参数在每次调用时提升这一数值。

### 当截断功能造成影响时

如果您确实需要实时的 DOM 内容而非提取后的 Markdown 格式——例如那些包含大量 JavaScript 代码的页面，用提取方式往往无法获取到足够的内容——那么可以改用 `browser_navigate` + `browser_snapshot` 方法。该浏览器工具会返回实时的无障碍访问树结构（不过对于内容极为庞大的页面，仍会受到其自身的快照限制）。

---

## 结果缓存

在短时间内重复发起的网页请求会直接从缓存中获取响应，而无需调用付费的后端服务——这能在那些容易出现重复请求的场景下节省积分并降低延迟，这类场景包括子代理并行处理（多个委托代理同时研究同一主题）以及代理重新查询其几分钟前已读取过的页面。

| 请求类型 | 缓存位置 | 作用范围 |
|----------|----------|----------|
| `web_search` —— 相同的查询条件（不区分大小写和空格），相同的提供方 | 内存中的缓存机制 | 每个进程独立缓存 |
| `web_extract` —— 相同的 URL、相同的格式、相同的提供方 | 完整文本存储在 `~/.hermes/cache/web/` 目录下 | 在 CLI、网关、定时任务以及子代理进程之间共享 |

同时发起的完全相同的搜索请求（即多个并行子代理同时执行相同查询）会被**合并为一次后端请求**——仅第一个发起请求的代理需要付费，其余代理可共享该响应。搜索请求的限制值被分为 10/20/50/100 不同等级，因此几乎相同的请求（如 `limit=5` 和 `limit=8`）会共享同一个缓存条目，每个请求方仍能获得其指定的结果数量。

仅成功的响应会被缓存。出现故障时系统会自动重试向后端请求；通过“一次性无密钥救援”功能获取的响应绝不会被缓存（下一次调用时会再次尝试使用您指定的后端），同时符合 `security.website_blocklist` 规则的网址也永远不会从缓存中读取。经过缓存的抓取结果会重新经过常规的截断处理流程，因此即使第二次调用时设置了不同的 `char_limit`，所使用的仍会是之前存储的抓取内容。

**本地开发网址绝不会被缓存。** 任何位于 `localhost`、`127.0.0.1`、`*.local`、单标签局域网主机名，或是私有/链路本地 IP 范围（如 `192.168.*`、`10.*`、`172.16-31.*`）内的网址，都会完全绕过抓取缓存——开发服务器、热重载构建的版本以及聊天 GUI 的预览内容每次保存后都会发生变化，若使用缓存版本则会导致您看到过时的内容。每次获取本地页面的内容都是实时最新的。（只有在启用了 `security.allow_private_urls` 时，这些网址才能被访问。）

**需要在公共互联网上进行测试吗？** 测试环境部署地址及隧道地址都属于公共 DNS，因此本地开发规则无法覆盖它们——只需将这类地址添加到 `web.cache_exempt_hosts` 中，它们也会始终以实时方式被获取。匹配规则既可以是完全一致的内容，也可以使用 `*.` 通配符，或是作为域名后缀（例如 `mysite.dev` 也能同时匹配 `preview.mysite.dev`）：

```yaml
# ~/.hermes/config.yaml
web:
  cache_exempt_hosts:
    - mysite.vercel.app
    - "*.ngrok-free.app"
```

```yaml
# ~/.hermes/config.yaml
web:
  cache_enabled: true      # default; set false to disable both caches
  cache_ttl_minutes: 20    # freshness window, clamped 1–1440
```

如果您需要查询真正实时的数据（如比分、价格、突发新闻），并且要求每次调用的数据都是最新的，建议降低TTL值或设置 `web.cache_enabled: false`。

---

## 设置

### 通过 `hermes tools` 快速设置

运行 `hermes tools`，进入 **Web Search & Extract** 页面，然后选择相应的数据提供方。向导会提示您输入所需的URL或API密钥，并将其保存到您的配置文件中。

```bash
hermes tools
```

### Firecrawl（默认）

具备完整的搜索与提取功能，非常适合大多数用户使用。

```bash
# ~/.hermes/.env
FIRECRAWL_API_KEY=fc-your-key-here
```

在 [firecrawl.dev](https://firecrawl.dev) 获取密钥。免费套餐每月提供 500 个积分。

**自托管版 Firecrawl**：直接指向您自己的实例，而非云端 API：

```bash
# ~/.hermes/.env
FIRECRAWL_API_URL=http://localhost:3002
```

当设置了 `FIRECRAWL_API_URL` 后，API 密钥即为可选项（可通过设置 `USE_DB_AUTHENTICATION=false` 关闭服务器身份验证）。

---

### SearXNG（免费、自托管版）

SearXNG 是一款注重用户隐私的开源元搜索引擎，能够聚合来自 70 多种搜索引擎的搜索结果。**无需 API 密钥**——只需将 Hermes 指向正在运行的 SearXNG 实例即可。

SearXNG 仅支持搜索功能——若需执行 `web_extract` 操作，则需要额外的数据提取服务提供商。

#### 方案 A — 使用 Docker 自托管（推荐）

此方案可帮助您搭建无速率限制的私有实例。

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

SearXNG 在默认情况下会禁用 JSON 输出功能。请复制生成的配置文件并将其启用：

```bash
# Copy the auto-generated config out of the container
docker cp searxng:/etc/searxng/settings.yml ~/searxng/searxng/settings.yml
```

打开 `~/searxng/searxng/settings.yml` 文件。如果其中存在 `use_default_settings: true` 选项，该文件将仅包含您自定义的设置；其余所有设置则会沿用内置的默认值。若希望为 Hermes 启用 JSON 格式的响应，需添加以下自定义设置：

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

**6. 验证功能是否正常：**

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
  extract_backend: "firecrawl"   # or tavily, perplexity, keenable, exa, parallel
```

通过该配置，Hermes 会使用 SearXNG 处理所有搜索查询，并借助 Firecrawl 进行网址提取——从而将免费搜索与高质量数据提取功能完美结合。

---

### Tavily

专为人工智能优化的搜索与提取工具。在 `hermes tools` 中选择 Tavily（或设置 `web.backend: tavily`），即可在无需账户的情况下直接使用该服务（但会受到速率限制）。如需提升使用频率，可自行配置 API 密钥。

```bash
# optional — skip this for keyless access after selecting Tavily
# ~/.hermes/.env
TAVILY_API_KEY=tvly-your-key-here
```

请在 [app.tavily.com](https://app.tavily.com/home) 获取密钥。更多详情请参阅 [Tavily 无密钥模式](https://docs.tavily.com/documentation/keyless)。

---

### Perplexity

[Perplexity 的搜索 API](https://docs.perplexity.ai/docs/search/quickstart) 会从 Perplexity 自建的索引（`web_search`）中返回经过排序并标注日期的结果。对于 `web_extract` 功能，它采用与官方 `pplx` CLI 相同的基于查询相关性的*片段*提取方式：您将获得每页中重要的内容片段，省略部分会用 `…` 标示，而不会输出整页的完整文本——如需获取整页内容，请将 `web.extract_backend` 设置为 Firecrawl / Exa / Parallel。该服务仅提供带密钥的版本，没有匿名使用选项。

```bash
# ~/.hermes/.env
PERPLEXITY_API_KEY=pplx-your-key-here
```

请在 [perplexity.ai/account/api](https://www.perplexity.ai/account/api) 获取密钥。如需通过代理服务器访问，可设置 `PERPLEXITY_BASE_URL` 参数。  

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

在 Responses API 中，通过 Grok 的服务器端 [web_search 工具](https://docs.x.ai/developers/tools/web-search) 来处理 `web_search` 请求。Grok 负责执行实际搜索，并以结构化的 JSON 格式返回最相关的结果。

支持两种凭证配置方式——无需新增环境变量，也无需新的设置向导：

```bash
# ~/.hermes/.env (env-var path)
XAI_API_KEY=sk-xai-your-key-here
```

或者，对于 SuperGrok 的订阅用户：

```bash
hermes auth add xai-oauth
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

**仅搜索模式**——如果您同时需要`web_extract`功能，可将其与Firecrawl / Tavily / Keenable / Exa / Parallel搭配使用。当遇到401错误时，该服务提供商会强制刷新一次OAuth令牌并尝试重试（可处理窗口期中途令牌失效以及主动过期检查无法解析的加密令牌）；而通过环境变量传入的凭证则无需进行重试。

:::警示 信任模型
与Brave、Tavily、Exa等基于索引的服务提供商会原样返回搜索引擎的结果不同，xAI是一种大型语言模型，它自行决定要展示哪些网址，并负责生成这些网址的标题和描述。查询内容会直接影响输出结果，因此，若存在恶意构造的查询（例如通过代理接收到的不可信上游输入注入），理论上就可能引导Grok展示攻击者指定的网址。对待返回的网址应与处理任何模型生成的链接保持一致——在获取数据之前务必进行验证，尤其是当查询来自不可信来源时。
:::

---

## 配置

### 单一后端

为所有网页相关功能设置一个服务提供商：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "searxng"   # firecrawl | searxng | brave-free | ddgs | tavily | perplexity | keenable | exa | parallel | xai
```

### 按功能配置

为搜索和数据提取分别使用不同的服务提供商。这样一来，您既可以将免费的搜索服务（SearXNG）与付费的数据提取服务结合使用，反之亦然：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"     # used by web_search
  extract_backend: "firecrawl"  # used by web_extract
```

当各功能对应的配置键为空时，系统会统一回退到 `web.backend`。只有从未进行过网页端选择的情况下，系统才会根据现有的 API 密钥或 URL 自动检测后端——一旦有了明确的选择，运行时将始终使用该后端，且在 `.env` 文件中添加新密钥也不会改变网页请求的路由路径。

**各功能的优先级顺序：**
1. `web.search_backend` / `web.extract_backend`（针对特定功能明确指定的后端）
2. `web.backend`（通用回退选项；`nous` 表示托管式 Tool Gateway）
3. 根据环境变量自动检测（仅适用于未进行过任何配置的场景）

### 自动检测机制

如果从未选择过后端（既没有手动设置 `web.backend` 或各功能对应的配置键，也没有通过 `hermes tools` 进行配置），Hermes 会根据已设置的凭证自动选择第一个可用的后端：

| 已设置的凭证 | 自动选择的后端 |
|--------------|----------------|
| `TAVILY_API_KEY` | tavily |
| `PERPLEXITY_API_KEY` | perplexity |
| `EXA_API_KEY` | exa |
| `PARALLEL_API_KEY` | parallel |
| `FIRECRAWL_API_KEY` 或 `FIRECRAWL_API_URL`（或 Nous Tool Gateway 已准备就绪） | firecrawl |
| `SEARXNG_URL` | searxng |
| `BRAVE_SEARCH_API_KEY` | brave-free |
| 可导入的 `ddgs` 包 | ddgs |
| *未设置任何凭证* | 无密钥轮询机制：exa / parallel / firecrawl / keenable（循环选择） |
**无密钥免费层级机制：** 当上述任何凭据均不存在时，请求会自动在环中的各供应商公共免费层级（Exa、Parallel、Firecrawl、Keenable）之间轮询，从而让网页工具在无需任何配置的情况下即可在新环境中正常运行。若遇到速率限制导致的请求失败，系统会自动切换到环中的下一个供应商。若要在 `hermes tools` 中固定使用某家供应商，可停止此轮询机制（此时该环仅用于在出现限流时进行故障转移）。所有免费层级在面临突发负载时都会受到供应商端的速率限制，但正常的持续使用则不受影响。如需关闭此功能，可设置 `web.keyless_fallback: false`；在关闭该选项且没有配置任何凭据的情况下，网页工具将无法使用，直到用户配置好相应的供应商。

**针对已配置密钥后端的一次性无密钥救援机制：** 当您选择的已配置密钥的后端出现调用失败（如密钥错误、服务中断或上游返回5xx错误）时，该次请求会自动在无密钥免费层级环中重试，而不会直接报错。结果会显示是由哪家供应商处理了请求以及原因（`rescued_from` / `backend_error`）。此故障转移机制绝不会保持固定，下一次发起 `web_search`/`web_extract` 请求时仍会尝试使用您最初选择的后端。如需禁用此功能，可设置 `web.keyless_rescue: false`（当 `keyless_fallback` 为关闭状态时，该选项也会自动关闭）。

xAI Web Search 并不包含在自动检测流程中——即使设置了 `XAI_API_KEY` 或通过 xAI Grok OAuth 登录，也不会自动将网页流量路由到 xAI，因为这些凭据同样用于推理、文本转语音及图像生成等功能，用户可能希望为网页请求使用不同的后端。如需明确启用该功能，需设置 `web.backend: "xai"`。

## 验证您的设置

运行 `hermes setup` 命令，即可查看系统检测到了哪种 Web 后端：

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
- 如果返回 HTTP 403 错误，说明已禁用 JSON 格式——请在 `settings.yml` 中的 `formats` 列表中添加 `json`，然后重启服务
- 如果出现连接错误，可能是容器未运行：执行 `docker ps | grep searxng`

### `web_extract` 显示“仅支持搜索的后端”

SearXNG 无法提取 URL 内容。请将 `web.extract_backend` 设置为支持内容提取的提供方：

```yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"  # or tavily / perplexity / keenable / exa / parallel
```

### SearXNG 返回 0 条结果

某些公共实例会禁用特定的搜索引擎或搜索类别。可尝试以下方法：
- 使用不同的查询语句
- 切换到 [searx.space](https://searx.space/) 上的其他公共实例
- 自行托管实例以获得更可靠的结果

### 在公共实例上遇到速率限制

请切换到自托管实例（参见上文[选项 A](#option-a--self-host-with-docker-recommended)）。使用 Docker 托管的实例不存在速率限制问题。

### `web_extract` 返回被截断的内容，并带有 `[TRUNCATED]` 标签

对于字符数超过限制的页面，出现这种情况是正常的。该标签会注明存储完整文本内容的磁盘文件名称，以及用于读取被省略部分内容的具体 `read_file` 调用方式。若希望显示更多内容，可在 `config.yaml` 中提高 `web.extract_char_limit` 的值，或在调用时设置更大的 `char_limit` 参数。

---

## 可选技能：`searxng-search`

对于需要通过 `curl` 直接使用 SearXNG 的智能体（例如在无法使用网络工具集时的备用方案），可安装 `searxng-search` 这一可选技能：

```bash
hermes skills install official/research/searxng-search
```

该功能会新增一项技能，用于指导智能体掌握以下操作方法：
- 通过 `curl` 或 Python 调用 SearXNG JSON API；
- 按类别（如“综合”、“新闻”、“科学”等）进行筛选；
- 处理分页及错误情况；
- 在无法连接到 SearXNG 时实现平滑的降级处理。
