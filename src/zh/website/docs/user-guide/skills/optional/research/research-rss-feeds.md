---
title: "Rss Feeds — Read RSS, Atom, JSON feeds; discover feeds behind a page"
sidebar_label: "Rss Feeds"
description: "Read RSS, Atom, JSON feeds; discover feeds behind a page"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# RSS 订阅源

读取 RSS、Atom、JSON 格式的订阅源；发现页面背后隐藏的订阅源。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/rss-feeds` 命令安装 |
| 路径 | `optional-skills/research/rss-feeds` |
| 版本 | `1.0.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `RSS`、`Atom`、`订阅源`、`监控`、`研究`、`博客`、`版本发布` |
| 相关技能 | [`reddit-reading`](/docs/user-guide/skills/optional/social-media/social-media-reddit-reading)、[`competitor-news-monitor`](/docs/user-guide/skills/bundled/research/research-competitor-news-monitor)、[`grounded-citations`](/docs/user-guide/skills/bundled/research/research-grounded-citations)、[`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content)、[`blogwatcher`](/docs/user-guide/skills/optional/research/research-blogwatcher) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# RSS 订阅源技能

能够将任何 RSS 2.0、RSS 1.0/RDF、Atom 或 JSON Feed 地址解析为结构清晰、按日期排序的文章列表，同时还能从普通网页地址中识别出对应的 Feed（通过 `<link rel="alternate">` 标签或常见的 `/feed`、`/rss.xml`、`/atom.xml` 路径）。该功能仅依赖标准库，无需额外安装。它不会获取文章的完整内容——如需提取全文，请将对应文章的链接传递给 `web_extract` 功能。

## 适用场景

- 查看“<blog/site> 的最新动态”、“<GitHub 仓库> 的最新发布”、“<subreddit> 的近期帖子”、“阅读此 Feed”以及“该网站是否有 RSS Feed”。
- 使用 `cronjob_manage` 功能构建定期摘要——相比每次都抓取 HTML 首页，Feed 更为经济且稳定。如需为多个 Feed 管理统一的已读/未读状态数据库，可安装可选的 `blogwatcher` 功能；该功能可实现无需安装即可进行阅读管理。
- 任何需要结构化列表（包含标题/链接/日期/作者/摘要）而非渲染后的页面的场景：如播客、变更日志、YouTube 频道、新闻编辑室以及论坛分类等。

## 先决条件

无特殊要求。只需使用 Python 3.10 及以上版本，并能访问 Feed 所在服务器的网络连接。

## 运行方法

通过终端，使用对应功能的脚本路径来运行即可：

```bash
python3 scripts/feed.py read https://hnrss.org/frontpage --limit 10
python3 scripts/feed.py read https://simonwillison.net/            # page URL → discovers the feed
python3 scripts/feed.py read URL --since 2026-09-01 --json          # only newer entries, machine-readable
python3 scripts/feed.py discover https://example.com/               # list candidate feed URLs
```

## 快速参考

| 数据来源 | 订阅源 URL 模式 |
|---|---|
| GitHub 发布/提交/标签 | `https://github.com/OWNER/REPO/releases.atom`, `…/commits/BRANCH.atom`, `…/tags.atom` |
| Subreddit / Reddit 搜索结果 | `https://www.reddit.com/r/NAME/.rss`, `https://www.reddit.com/search.rss?q=…`（匿名用户每分钟仅可请求 1 次；详情参见 `reddit-reading`） |
| YouTube 频道 | `https://www.youtube.com/feeds/videos.xml?channel_id=UC…` |
| Hacker News | `https://hnrss.org/frontpage`, `https://hnrss.org/newest?q=TERM` |
| arXiv 分类目录 | `https://rss.arxiv.org/rss/cs.CL` |
| Substack / Medium / WordPress / Ghost | `SITE/feed`, `medium.com/feed/@user`, `SITE/rss/` |
| 播客 | 在其托管页面上可找到该节目的 RSS URL（可通过 `discover` 功能定位） |

每条记录的输出字段包括：`title`、`link`、`published`（UTC 格式，符合 ISO 8601 标准）、`author`、`summary`
（已去除 HTML 格式，字符数不超过 2000）。记录将按最新优先的顺序排列。

## 操作步骤

① 如果仅知道网站 URL，可直接对其运行 `read` 命令；该脚本会自动识别出对应的订阅源，并显示所使用的 URL 地址（字段名为 `discovered_from`）。当需要在多个提供的订阅源中选择时（例如评论源与文章源，或不同分类下的订阅源），可使用 `discover` 命令。

② 对请求进行限制：使用 `--limit` 参数指定“最近 N 条记录”，使用 `--since YYYY-MM-DD` 参数指定“从上次检查之后的记录”。对于定时任务，可保存上一次查询得到的 `published` 时间值，并在下次运行时作为 `--since` 参数传入。

③ 若需要获取全文内容，可将对应记录的 `link` 地址传递给 `web_extract` 工具；而订阅源摘要通常会被截断，仅显示开头段落内容。

④ 当结果用于生成报告时，应引用 `link` 条目而非源 Feed 的 URL（即使用 `grounded-citations` 功能）。

## 常见问题

- 若返回 200 状态码且内容为 HTML，则说明该 URL 对应的是页面而非 Feed；脚本会自动进入发现阶段。但若某个网站既没有 `<link rel="alternate">` 标签，也没有常见的路径，脚本则会提示“未找到 Feed”——在判定不存在 Feed 之前，请先检查该网站的页脚或 `/sitemap.xml` 文件。
- Reddit 的 Feed 遵循 Reddit 的匿名访问限制（每个 IP 每分钟约仅可发起一次请求）。当需要多次调用 Reddit 接口时，可通过 `reddit-reading` 插件来排队等待，从而规避限制。
- 日期格式：RSS 使用 RFC 822 标准的 `pubDate`，而 Atom 使用 ISO 8601 标准；脚本会将这两种格式统一转换为 UTC 时间。未标注日期的 Feed 会排在最下方，并会被 `--since` 参数过滤掉。
- 部分 Feed 由 Cloudflare 托管，且会拒绝非浏览器客户端访问；`blocked-page-recovery` 插件可处理此类情况。

## 验证方法

执行命令 `python3 scripts/feed.py read https://github.com/NousResearch/hermes-agent/releases.atom --limit 1`，将会输出一条包含 `releases/tag/` 链接以及 `[atom]` 格式标签的条目；而执行命令 `discover https://simonwillison.net/` 则会输出一个 `/atom/` 格式的 URL。
