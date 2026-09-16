---
title: "Blogwatcher — Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool"
sidebar_label: "Blogwatcher"
description: "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Blogwatcher

通过 blogwatcher-cli 工具监控博客以及 RSS/Atom 订阅源。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/blogwatcher` 安装 |
| 路径 | `optional-skills/research/blogwatcher` |
| 版本 | `2.0.0` |
| 开发者 | JulienTant（基于 Hyaxia/blogwatcher 的分支） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `RSS`、`博客`、`订阅源阅读器`、`监控` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# Blogwatcher

利用 `blogwatcher-cli` 工具追踪博客及 RSS/Atom 订阅源的更新情况。该技能支持自动发现订阅源、HTML 抓取备用方案、OPML 导入，以及文章的已读/未读状态管理。

## Hermes 工具使用指南（请先阅读）

`blogwatcher-cli` 是订阅源数据库；Hermes 的各种工具则负责围绕它实现自动化功能：

- **周期性监控——请使用 cronjob 工具的 `monitor` 字段，而非简单的定时任务**。`monitor` 会在每个时间间隔执行一次脚本，仅当输出发生变化时才会唤醒代理：可将该字段设置为执行如下命令的脚本：`blogwatcher-cli scan >/dev/null 2>&1 && blogwatcher-cli articles`（此命令的输出是确定的；若有新文章出现，则输出会改变，代理便会随之被唤醒并获取差异内容）。若无变化，则不会触发任何 LLM 调用。可将 `deliver` 字段设置为将摘要发送到聊天窗口或频道中；同时添加 `continuity: true` 选项，以便对连续的摘要进行去重处理。
- **读取用户询问的文章**：直接使用 `blogwatcher-cli articles` 命令获取文章 URL，然后调用 `web_extract([url])` 函数即可——无需手动重新抓取内容。
- **仅需一次性监控页面变化且无需订阅源相关功能**：可跳过此技能，因为 cronjob 工具的 `monitor` 字段可直接接受 http(s) URL。
- **只需一次性读取订阅源或网站的最新文章，且无需安装任何组件**：可使用内置的 `rss-feeds` 技能（通过 `scripts/feed.py read URL` 命令实现）；只有当您需要跟踪多个订阅源并标记其已读/未读状态时，才需要安装 BlogWatcher。
- **需要对公司或竞争对手进行跟踪并分析相关信息及引用内容**：建议使用 `competitor-news-monitor` 技能；BlogWatcher 可作为其轻量级的原始数据来源层使用。

## 安装

请选择一种安装方式：

- **Go 语言版本：** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker 版本：** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **二进制文件（Linux amd64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（Linux arm64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（macOS Apple Silicon）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（macOS Intel）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

所有版本信息请访问：https://github.com/JulienTant/blogwatcher-cli/releases

### 使用 Docker 并实现数据持久化

默认情况下，数据库存储在 `~/.blogwatcher-cli/blogwatcher-cli.db` 目录中。在 Docker 环境下，容器重启后该数据将会丢失。可通过设置 `BLOGWATCHER_DB` 变量或使用卷挂载来确保数据持久保存：

```bash
# Named volume (simplest)
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# Host bind mount
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

### 从旧版 BlogWatcher 迁移

若需从 `Hyaxia/blogwatcher` 升级，请先迁移您的数据库：

```bash
mv ~/.blogwatcher/blogwatcher.db ~/.blogwatcher-cli/blogwatcher-cli.db
```

二进制文件的名称已从 `blogwatcher` 更改为 `blogwatcher-cli`。

## 常用命令

### 管理博客

- 添加博客：`blogwatcher-cli add "我的博客" https://example.com`
- 指定订阅源添加：`blogwatcher-cli add "我的博客" https://example.com --feed-url https://example.com/feed.xml`
- 通过 HTML 抓取添加：`blogwatcher-cli add "我的博客" https://example.com --scrape-selector "article h2 a"`
- 列出已跟踪的博客：`blogwatcher-cli blogs`
- 删除博客：`blogwatcher-cli remove "我的博客" --yes`
- 从 OPML 导入：`blogwatcher-cli import subscriptions.opml`

### 扫描与阅读

- 扫描所有博客：`blogwatcher-cli scan`
- 扫描单个博客：`blogwatcher-cli scan "我的博客"`
- 列出未读文章：`blogwatcher-cli articles`
- 列出所有文章：`blogwatcher-cli articles --all`
- 按博客筛选：`blogwatcher-cli articles --blog "我的博客"`
- 按分类筛选：`blogwatcher-cli articles --category "工程技术"`
- 标记文章为已读：`blogwatcher-cli read 1`
- 标记文章为未读：`blogwatcher-cli unread 1`
- 全部标记为已读：`blogwatcher-cli read-all`
- 为某个博客全部标记为已读：`blogwatcher-cli read-all --blog "我的博客" --yes`

## 环境变量

所有命令参数均可通过带有 `BLOGWATCHER_` 前缀的环境变量来设置：

| 变量 | 描述 |
|---|---|
| `BLOGWATCHER_DB` | SQLite 数据库文件的路径 |
| `BLOGWATCHER_WORKERS` | 并行扫描的工作进程数量（默认值：8） |
| `BLOGWATCHER_SILENT` | 扫描时仅输出“扫描完成”信息 |
| `BLOGWATCHER_YES` | 跳过确认提示 |
| `BLOGWATCHER_CATEGORY` | 文章分类的默认过滤条件 |

## 示例输出

```
$ blogwatcher-cli blogs
Tracked blogs (1):

  xkcd
    URL: https://xkcd.com
    Feed: https://xkcd.com/atom.xml
    Last scanned: 2026-04-03 10:30
```

```
$ blogwatcher-cli scan
Scanning 1 blog(s)...

  xkcd
    Source: RSS | Found: 4 | New: 4

Found 4 new article(s) total!
```

```
$ blogwatcher-cli articles
Unread articles (2):

  [1] [new] Barrel - Part 13
       Blog: xkcd
       URL: https://xkcd.com/3095/
       Published: 2026-04-02
       Categories: Comics, Science

  [2] [new] Volcano Fact
       Blog: xkcd
       URL: https://xkcd.com/3094/
       Published: 2026-04-01
       Categories: Comics
```

## 备注

- 若未指定 `--feed-url`，则会自动从博客主页检测 RSS/Atom 订阅源。
- 若 RSS 获取失败且已配置 `--scrape-selector`，则会转而使用 HTML 抓取功能。
- RSS/Atom 订阅源中的分类信息会被保存下来，可用于筛选文章。
- 支持批量导入来自 Feedly、Inoreader、NewsBlur 等工具导出的 OPML 文件中的博客。
- 数据库默认存储在 `~/.blogwatcher-cli/blogwatcher-cli.db` 目录下（可通过 `--db` 或 `BLOGWATCHER_DB` 参数进行修改）。
- 如需查看所有参数和选项，可使用命令 `blogwatcher-cli <command> --help`。
