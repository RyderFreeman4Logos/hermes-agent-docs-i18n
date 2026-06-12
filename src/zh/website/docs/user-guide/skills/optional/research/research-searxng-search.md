---
title: "Searxng Search — Free meta-search via SearXNG — aggregates results from 70+ search engines"
sidebar_label: "Searxng Search"
description: "Free meta-search via SearXNG — aggregates results from 70+ search engines"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# SearXNG 搜索

通过 SearXNG 实现免费的全文检索功能——该工具可聚合 70 多个搜索引擎的结果。支持自行托管或使用公共实例，无需 API 密钥。当常规网络搜索工具不可用时，会自动切换为备用方案。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——可通过 `hermes skills install official/research/searxng-search` 安装 |
| 路径 | `optional-skills/research/searxng-search` |
| 版本 | `1.0.0` |
| 开发者 | hermes-agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos |
| 标签 | `搜索`、`searxng`、`全文检索`、`自行托管`、`免费`、`备用方案` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search)、[`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel) |

## 参考：完整 SKILL.md 内容

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# SearXNG 搜索

基于 [SearXNG](https://searxng.org/) 提供的免费全文检索服务——这是一款注重用户隐私的自行托管型搜索聚合工具，能够同时查询 70 多个搜索引擎。

使用公共实例时**无需 API 密钥**。如需更强的控制权，也可选择自行托管。当未配置主要网络搜索工具集（`FIRECRAWL_API_KEY`）时，该技能会自动作为备用方案启用。

## 配置说明

SearXNG 需要一个名为 `SEARXNG_URL` 的环境变量，用于指定您的 SearXNG 实例地址：

```bash
# Public instances (no setup required)
SEARXNG_URL=https://searxng.example.com

# Self-hosted SearXNG
SEARXNG_URL=http://localhost:8888
```

如果未配置任何实例，则该技能将不可用，代理程序会转而使用其他搜索选项。

## 检测流程

在选择相应方法之前，请先确认实际可用的资源情况：

```bash
# Check if SEARXNG_URL is set and the instance is reachable
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

决策流程：
1. 若已设置 `SEARXNG_URL` 且实例能够响应，则使用 SearXNG。
2. 若未设置 `SEARXNG_URL` 或无法连接该地址，则转而使用其他可用的搜索工具。
3. 若用户明确要求使用 SearXNG，则协助其搭建实例或寻找公共可用实例。

## 方法 1：通过 curl 调用 CLI（推荐方式）

通过“终端”使用 `curl` 命令来调用 SearXNG 的 JSON API。这种方式无需假设系统中已安装特定的 Python 包。

```bash
# Text search (JSON output)
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=python+async+programming&format=json&engines=google,bing&limit=10"

# With Safesearch off
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=example&format=json&safesearch=0"

# Specific categories (general, news, science, etc.)
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=AI+news&format=json&categories=news"
```

### 常用 CLI 参数

| 参数 | 描述 | 示例 |
|------|-------------|---------|
| `q` | 查询字符串（已进行 URL 编码） | `q=python+async` |
| `format` | 输出格式：`json`、`csv`、`rss` | `format=json` |
| `engines` | 以逗号分隔的引擎名称 | `engines=google,bing,ddg` |
| `limit` | 每个引擎的最大返回结果数（默认为 10） | `limit=5` |
| `categories` | 按类别筛选 | `categories=news,science` |
| `safesearch` | 0=无限制，1=适度限制，2=严格限制 | `safesearch=0` |
| `time_range` | 筛选时间范围：`day`、`week`、`month`、`year` | `time_range=week` |

### 解析 JSON 结果

```bash
# Extract titles and URLs from JSON
curl -s --max-time 10 "${SEARXNG_URL}/search?q=fastapi&format=json&limit=5" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(r.get('title',''))
    print(r.get('url',''))
    print(r.get('content','')[:200])
    print()
"
```

每个搜索结果返回的字段包括：`title`、`url`、`content`（摘要）、`engine`、`parsed_url`、`img_src`、`thumbnail`、`author`以及`published_date`。

## 方法 2：通过 `requests` 调用 Python API

可使用 `requests` 库直接从 Python 程序调用 SearXNG 的 REST API：

```python
import os, requests, urllib.parse

base_url = os.environ.get("SEARXNG_URL", "")
if not base_url:
    raise RuntimeError("SEARXNG_URL is not set")

query = "fastapi deployment guide"
params = {
    "q": query,
    "format": "json",
    "limit": 5,
    "engines": "google,bing",
}

resp = requests.get(f"{base_url}/search", params=params, timeout=10)
resp.raise_for_status()
data = resp.json()

for r in data.get("results", []):
    print(r["title"])
    print(r["url"])
    print(r.get("content", "")[:200])
    print()
```

## 方法 3：searxng-data Python 包

如需更结构化的访问方式，请安装 `searxng-data` 包：

```bash
pip install searxng-data
```

```python
from searxng_data import engines

# List available engines
print(engines.list_engines())
```

注意：该软件包仅提供引擎元数据，而非搜索 API 本身。

## 自主托管 SearXNG

如需运行自己的 SearXNG 实例：

```bash
# Using Docker
docker run -d -p 8888:8080 \
  -v $(pwd)/searxng:/etc/searxng \
  searxng/searxng:latest

# Then set
SEARXNG_URL=http://localhost:8888
```

或者通过 pip 安装：
```bash
pip install searxng
# Edit /etc/searxng/settings.yml
searxng-run
```

公开的 SearXNG 实例地址如下：
- `https://searxng.example.com`（可替换为任意其他公开实例）

## 工作流程：先搜索再提取

SearXNG 返回的是标题、URL 以及内容片段，而非整页内容。若需获取完整页面内容，应先进行搜索，然后使用 `web_extract`、浏览器工具或 `curl` 来提取最相关的 URL。

```bash
# Search for relevant pages
curl -s "${SEARXNG_URL}/search?q=fastapi+deployment&format=json&limit=3"
# Output: list of results with titles and URLs

# Then extract the best URL with web_extract
```

## 局限性

- **实例可用性**：如果 SearXNG 实例处于关闭状态或无法访问，搜索将失败。请务必确认已设置 `SEARXNG_URL` 且该实例可正常访问。
- **无内容提取功能**：SearXNG 只能返回摘要信息，而非完整页面内容。如需获取全文，请使用 `web_extract`、浏览器工具或 `curl`。
- **请求频率限制**：部分公共实例会对请求次数进行限制，而自托管则可避免此问题。
- **搜索引擎支持情况**：可用的搜索引擎取决于 SearXNG 实例的配置，某些搜索引擎可能被禁用。
- **结果更新频率**：元搜索服务会聚合多个外部搜索引擎的结果，因此其更新速度取决于这些引擎的表现。

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 未设置 `SEARXNG_URL` | 未配置任何实例 | 使用公共 SearXNG 实例或自行搭建实例 |
| 连接被拒绝 | 实例未运行或 URL 错误 | 检查 URL 是否正确以及实例是否正在运行 |
| 返回空结果 | 实例阻止了查询请求 | 尝试使用其他实例或选择自托管方案 |
| 响应速度缓慢 | 公共实例负载过重 | 选择自托管方式或使用负载较低的公共实例 |
| 不支持 `json` 格式 | SearXNG 版本过旧 | 尝试使用 `format=rss` 格式或升级 SearXNG |

## 常见误区

- **务必设置 `SEARXNG_URL`**：若未设置该参数，相关功能将无法正常工作。
- **需对查询语句进行 URL 编码**：在使用 `curl` 时，空格和特殊字符必须进行 URL 编码；在 Python 中则可使用 `urllib.parse.quote()` 函数。
- **建议使用 `format=json`**：默认输出格式可能无法被机器直接读取，建议始终明确请求 JSON 格式的数据。
- **需设置超时时间**：务必使用 `--max-time` 或 `timeout=` 参数，以避免在无法访问的实例上无限等待。
- **自托管是最优选择**：公共实例可能会关闭、受到频率限制或被屏蔽，而自托管的实例则更为可靠。

## 实例查找

如果未设置 `SEARXNG_URL` 且用户询问相关问题，可协助他们：
1. 查找公共 SearXNG 实例（可通过搜索“public searxng instance”找到）；
2. 使用 Docker 或 pip 自行搭建实例。

公共实例列表地址：https://searxng.org/
