---
title: "Duckduckgo Search — Free keyless web, news, and image search via ddgs"
sidebar_label: "Duckduckgo Search"
description: "Free keyless web, news, and image search via ddgs"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Duckduckgo 搜索

通过 ddgs 实现免费的无需密钥的网络、新闻及图片搜索功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/research/duckduckgo-search` 安装 |
| 路径 | `optional-skills/research/duckduckgo-search` |
| 版本 | `1.3.0` |
| 创建者 | gamedevCloudy |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `搜索`、`duckduckgo`、`网络搜索`、`免费`、`备用方案` |
| 相关技能 | [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# DuckDuckGo 搜索

使用 DuckDuckGo 进行免费的网络搜索。**无需 API 密钥。**

在 `web_search` 功能不可用或不适用时（例如未设置 `FIRECRAWL_API_KEY` 时），优先选择此功能。若需要直接获取 DuckDuckGo 的搜索结果，也可将其作为独立的搜索路径使用。

## 检测流程

在选择具体方案之前，先确认实际可用的资源情况：

```bash
# Check CLI availability
command -v ddgs >/dev/null && echo "DDGS_CLI=installed" || echo "DDGS_CLI=missing"
```

决策流程：
1. 若已安装 `ddgs` CLI，则优先使用 `terminal` + `ddgs`；
2. 若未安装 `ddgs` CLI，切勿直接假设 `execute_code` 能够导入该工具；
3. 若用户明确需要 DuckDuckGo 搜索功能，则需先在对应环境中安装 `ddgs`；
4. 其他情况则可使用内置的网页/浏览器工具。

重要运行时注意事项：
- `terminal` 与 `execute_code` 属于不同的运行时环境；
- 即使在终端环境中成功安装了 `ddgs`，也不代表 `execute_code` 就能导入它；
- 绝不可假设 `execute_code` 内已预装了各类第三方 Python 包。

## 安装说明

仅当确实需要使用 DuckDuckGo 搜索功能，且当前运行时环境未提供该功能时，才需安装 `ddgs`。

```bash
# Python package + CLI entrypoint
pip install ddgs

# Verify CLI
ddgs --help
```

如果某个工作流依赖于 Python 导入功能，在使用 `from ddgs import DDGS` 之前，请先确认相同的运行环境能够成功导入 `ddgs` 库。  

## 方法一：通过 CLI 搜索（推荐）

若系统中存在终端功能，可直接使用 `ddgs` 命令。这是较为推荐的方案，因为它无需假设 `execute_code` 沙箱环境中已安装 `ddgs` Python 包。

```bash
# Text search
ddgs text -q "python async programming" -m 5

# News search
ddgs news -q "artificial intelligence" -m 5

# Image search
ddgs images -q "landscape photography" -m 10

# Video search
ddgs videos -q "python tutorial" -m 5

# With region filter
ddgs text -q "best restaurants" -m 5 -r us-en

# Recent results only (d=day, w=week, m=month, y=year)
ddgs text -q "latest AI news" -m 5 -t w

# JSON output for parsing
ddgs text -q "fastapi tutorial" -m 5 -o json
```

### CLI 参数

| 参数 | 说明 | 示例 |
|------|------|---------|
| `-q` | 查询内容 — **必填** | `-q "搜索关键词"` |
| `-m` | 最大结果数 | `-m 5` |
| `-r` | 地区 | `-r us-en` |
| `-t` | 时间限制 | `-t w`（周） |
| `-s` | 安全搜索 | `-s off` |
| `-o` | 输出格式 | `-o json` |

## 方法 2：Python API（仅验证通过后使用）

仅在确认目标环境中已安装 `ddgs` 包后，方可在 `execute_code` 或其他 Python 运行时中使用 `DDGS` 类。请勿默认认为 `execute_code` 已内置第三方包。

建议表述：
- “如需使用，可在安装或验证该包后，结合 `ddgs` 使用 `execute_code`”

避免使用以下表述：
- “`execute_code` 已包含 `ddgs`”
- “在 `execute_code` 中默认支持 DuckDuckGo 搜索”

**重要提示：** `max_results` 参数必须始终以**关键字参数**的形式传递——所有方法中若以位置参数方式传入都会导致错误。

### 文本搜索

最适合用于：常规信息检索、企业相关查询及文档查找。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.text("python async programming", max_results=5):
        print(r["title"])
        print(r["href"])
        print(r.get("body", "")[:200])
        print()
```

返回值：`title`、`href`、`body`

### 新闻搜索

适用场景：时事动态、突发新闻及最新资讯。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.news("AI regulation 2026", max_results=5):
        print(r["date"], "-", r["title"])
        print(r.get("source", ""), "|", r["url"])
        print(r.get("body", "")[:200])
        print()
```

返回值：`date`、`title`、`body`、`url`、`image`、`source`

### 图片搜索

最适合用于：视觉参考资料、产品图片及图表。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.images("semiconductor chip", max_results=5):
        print(r["title"])
        print(r["image"])
        print(r.get("thumbnail", ""))
        print(r.get("source", ""))
        print()
```

返回值：`title`、`image`、`thumbnail`、`url`、`height`、`width`、`source`

### 视频搜索

最适合用于：教程、演示及说明视频。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.videos("FastAPI tutorial", max_results=5):
        print(r["title"])
        print(r.get("content", ""))
        print(r.get("duration", ""))
        print(r.get("provider", ""))
        print(r.get("published", ""))
        print()
```

返回字段：`title`、`content`、`description`、`duration`、`provider`、`published`、`statistics`、`uploader`

### 快速参考

| 方法 | 适用场景 | 主要字段 |
|------|----------|----------|
| `text()` | 一般性检索、企业信息查询 | title、href、body |
| `news()` | 最新新闻、动态更新 | date、title、source、body、url |
| `images()` | 图片、图表检索 | title、image、thumbnail、url |
| `videos()` | 教程、演示视频检索 | title、content、duration、provider |

## 工作流程：先搜索再提取

DuckDuckGo仅返回标题、URL及内容片段，而非整页内容。若需获取完整页面内容，需先进行搜索，再使用 `web_extract`、浏览器工具或 curl 提取最相关的 URL。

CLI示例：

```bash
ddgs text -q "fastapi deployment guide" -m 3 -o json
```

Python 示例：仅在该运行时环境中确认已安装 `ddgs` 后方可使用。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("fastapi deployment guide", max_results=3))
    for r in results:
        print(r["title"], "->", r["href"])
```

接着，使用 `web_extract` 或其他内容获取工具来提取最优的 URL。

## 局限性

- **速率限制**：在频繁发起请求后，DuckDuckGo 可能会限制访问速度。如有需要，可在每次搜索之间稍作延迟。
- **无法提取完整内容**：`ddgs` 仅返回内容片段，而非整页内容。如需获取完整的文章或页面内容，应使用 `web_extract`、浏览器工具或 curl。
- **结果质量**：整体表现良好，但其可配置性低于 Firecrawl 的搜索功能。
- **可用性**：DuckDuckGo 可能会屏蔽来自某些云服务器 IP 的请求。如果搜索无结果，可尝试更换关键词或稍等几秒。
- **字段差异**：不同搜索结果或不同版本的 `ddgs` 所返回的字段可能有所不同。为避免出现 `KeyError` 错误，建议对可选字段使用 `.get()` 方法进行获取。
- **独立的运行环境**：在终端中成功安装 `ddgs` 并不意味着 `execute_code` 能自动导入该模块。

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `ddgs: command not found` | shell 环境中未安装 CLI 工具 | 安装 `ddgs`，或改用内置的网页/浏览器工具 |
| `ModuleNotFoundError: No module named 'ddgs'` | Python 运行环境中未安装该包 | 在准备好相应运行环境之前，不要在该环境中使用 Python 版本的 DDGS |
| 搜索无结果 | 暂时的速率限制或查询语句不当 | 稍等几秒后重试，或调整查询语句 |
| CLI 能正常使用，但 `execute_code` 导入失败 | 终端与 `execute_code` 所处的运行环境不同 | 继续使用 CLI，或单独准备 Python 运行环境 |

## 常见误区

- **`max_results` 仅适用于关键词参数**：直接使用 `ddgs.text("query", 5)` 会引发错误。应使用 `ddgs.text("query", max_results=5)` 的格式。
- **不要默认 CLI 已存在**：在使用之前，请先通过 `command -v ddgs` 检查该工具是否已安装。
- **不要认为 `execute_code` 能直接导入 `ddgs`**：除非已单独准备好相应的运行环境，否则使用 `from ddgs import DDGS` 可能会因 `ModuleNotFoundError` 而失败。
- **包名说明**：该包的名称为 `ddgs`（旧名为 `duckduckgo-search`），可通过 `pip install ddgs` 进行安装。
- **区分 CLI 参数 `-q` 和 `-m`**：`-q` 用于指定查询语句，而 `-m` 用于设置最大返回结果数量。
- **出现空结果的情况**：如果 `ddgs` 没有返回任何内容，很可能是受到了速率限制。请稍等几秒后重试。

## 验证情况

相关示例已基于 `ddgs==9.11.2` 的功能规范进行验证。目前的技能指导将 CLI 的可用性与 Python 的导入可用性视为两个独立的问题，因此文档中描述的操作流程与实际运行环境的行为更为匹配。
