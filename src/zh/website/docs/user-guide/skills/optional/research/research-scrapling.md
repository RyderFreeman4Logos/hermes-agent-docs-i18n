---
title: "Scrapling — Scrape sites with stealth browsing and Cloudflare bypass"
sidebar_label: "Scrapling"
description: "Scrape sites with stealth browsing and Cloudflare bypass"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 网站抓取

通过隐身浏览及 Cloudflare 绕过功能实现网站抓取。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/scraping` 安装 |
| 路径 | `optional-skills/research\scraping` |
| 版本 | `1.0.0` |
| 开发者 | FEUAZUR |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Web Scraping`、`浏览器`、`Cloudflare`、`隐身模式`、`爬取`、`蜘蛛爬虫` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search)、[`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体将依据此内容执行操作。
:::

# 网站抓取

[Scraping](https://github.com/D4Vinci/Scraping) 是一个具备反机器人绕过功能、隐身浏览器自动化能力以及蜘蛛爬虫框架的网页抓取工具。它提供了三种数据获取策略（HTTP、动态 JS、隐身/Cloudflare 模式），并配有完整的命令行界面。

**本技能仅用于教育与研究目的。** 用户必须遵守当地及国际上的数据抓取法规，并尊重目标网站的条款和服务协议。

## 适用场景

- 抓取静态 HTML 页面（速度优于浏览器工具）  
- 抓取需要真实浏览器才能渲染的 JS 页面  
- 规避 Cloudflare Turnstile 及机器人检测机制  
- 使用爬虫程序批量抓取多个页面  
- 当内置的 `web_extract` 工具无法获取所需数据时  

## 安装指南

```bash
pip install "scrapling[all]"
scrapling install
```

最小化安装版本（仅支持 HTTP，无需浏览器）：
```bash
pip install scrapling
```

仅支持浏览器自动化功能：
```bash
pip install "scrapling[fetchers]"
scrapling install
```

## 快速参考

| 方式 | 类别 | 适用场景 |
|------|------|----------|
| HTTP | `Fetcher` / `FetcherSession` | 静态页面、API 以及大量数据的快速请求 |
| 动态渲染 | `DynamicFetcher` / `DynamicSession` | 通过 JavaScript 渲染的内容及单页应用 |
| 隐秘模式 | `StealthyFetcher` / `StealthySession` | 面临 Cloudflare 保护或反爬虫机制的网站 |
| 爬虫模式 | `Spider` | 基于链接追踪进行多页面爬取 |

## CLI 使用方法

### 提取静态页面

```bash
scrapling extract get 'https://example.com' output.md
```

支持使用 CSS 选择器及浏览器模拟功能：

```bash
scrapling extract get 'https://example.com' output.md \
  --css-selector '.content' \
  --impersonate 'chrome'
```

### 提取 JavaScript 渲染的页面内容

```bash
scrapling extract fetch 'https://example.com' output.md \
  --css-selector '.dynamic-content' \
  --disable-resources \
  --network-idle
```

### 提取受 Cloudflare 保护的页面

```bash
scrapling extract stealthy-fetch 'https://protected-site.com' output.html \
  --solve-cloudflare \
  --block-webrtc \
  --hide-canvas
```

### POST 请求

```bash
scrapling extract post 'https://example.com/api' output.json \
  --json '{"query": "search term"}'
```

### 输出格式

输出格式由文件扩展名决定：
- `.html` -- 原始 HTML 格式
- `.md` -- 转换为 Markdown 格式
- `.txt` -- 纯文本格式
- `.json` / `.jsonl` -- JSON 格式

## Python：HTTP 爬虫

### 单次请求

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
for q in quotes:
    print(q)
```

### 会话（持久性 Cookie）

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
    for link in links[:5]:
        sub = session.get(link)
        print(sub.css('h1::text').get())
```

### POST / PUT / DELETE 请求

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

### 使用代理时

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

## Python：动态页面（JS渲染）

适用于需要执行JavaScript的页面（单页应用、延迟加载内容）：

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True)
data = page.css('.js-loaded-content::text').getall()
```

### 等待特定元素出现

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

### 禁用冗余资源以提升速度

关闭字体、图片、媒体文件及样式表的功能（可提升约25%的速度）：

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
    items = page.css('.item::text').getall()
```

### 自定义页面自动化

```python
from playwright.sync_api import Page
from scrapling.fetchers import DynamicFetcher

def scroll_and_click(page: Page):
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(1000)
    page.click('button.load-more')
    page.wait_for_selector('.extra-results')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_and_click)
results = page.css('.extra-results .item::text').getall()
```

## Python：隐身模式（防止机器人绕过检测）

适用于受 Cloudflare 保护或存在严重指纹识别特征的网站：

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
    hide_canvas=True,
)
content = page.css('.protected-content::text').getall()
```

### 隐秘会话模式

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```

## 元素选择

所有数据获取器都会返回一个包含以下方法的 `Selector` 对象：

### CSS 选择器

```python
page.css('h1::text').get()              # First h1 text
page.css('a::attr(href)').getall()      # All link hrefs
page.css('.quote .text::text').getall() # Nested selection
```

### XPath路径查询

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

### 查找方法

```python
page.find_all('div', class_='quote')       # By tag + attribute
page.find_by_text('Read more', tag='a')    # By text content
page.find_by_regex(r'\$\d+\.\d{2}')       # By regex pattern
```

### 类似元素

查找结构相似的元素（适用于产品列表等场景）：

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

### 导航

```python
el = page.css('.target')[0]
el.parent                # Parent element
el.children              # Child elements
el.next_sibling          # Next sibling
el.prev_sibling          # Previous sibling
```

## Python：Spider Framework

用于通过链接追踪实现多页面爬取：

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    download_delay = 1

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
                "tags": quote.css('.tag::text').getall(),
            }

        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

### 多会话爬虫

将请求路由至不同的数据获取器类型：

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class SmartSpider(Spider):
    name = "smart"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)
```

### 暂停/恢复爬取

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # Ctrl+C to pause, re-run to resume from checkpoint
```

## 常见问题与注意事项

- **需安装浏览器**：在运行 `pip install` 之后必须执行 `scraping install`——若未完成此步骤，`DynamicFetcher` 和 `StealthyFetcher` 将无法正常工作。
- **超时设置**：`DynamicFetcher`/`StealthyFetcher` 的超时时间以**毫秒**为单位（默认值为 30000），而普通 `Fetcher` 的超时时间则以**秒**为单位。
- **Cloudflare 反爬绕过**：设置 `solve_cloudflare=True` 会使数据获取时间增加 5 至 15 秒——请仅在确实需要时启用该选项。
- **资源占用**：`StealthyFetcher` 会启动真实的浏览器，因此需控制其并发使用数量。
- **法律合规**：在抓取数据前，请务必查阅目标网站的 robots.txt 文件及服务条款。本库仅用于教学与研究目的。
- **Python 版本要求**：需使用 Python 3.10 及更高版本。
