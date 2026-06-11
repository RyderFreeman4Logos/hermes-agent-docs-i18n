---
title: "Blogwatcher — Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool"
sidebar_label: "Blogwatcher"
description: "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Blogwatcher

通过 blogwatcher-cli 工具监控博客及 RSS/Atom 订阅源。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/research/blogwatcher` |
| 版本 | `2.0.0` |
| 开发者 | JulienTant（基于 Hyaxia/blogwatcher 项目开发） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `RSS`、`博客`、`订阅源阅读器`、`监控` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# Blogwatcher

使用 `blogwatcher-cli` 工具追踪博客及 RSS/Atom 订阅源的更新情况。该工具支持自动发现订阅源、HTML 爬取备用方案、OPML 导入，以及文章的已读/未读状态管理。

## 安装方式

请选择以下其中一种方法：

- **Go 语言版本：** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker 版本：** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **二进制文件（Linux amd64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（Linux arm64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（macOS Apple Silicon）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制文件（macOS Intel）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

所有版本信息请见：https://github.com/JulienTant/blogwatcher-cli/releases

### 带持久化存储的 Docker 方式

默认情况下，数据库存储在 `~/.blogwatcher-cli/blogwatcher-cli.db` 目录中。在 Docker 环境下，容器重启后该数据将会丢失。如需保留数据，可使用 `BLOGWATCHER_DB` 参数或通过卷挂载来实现持久化存储：

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

该二进制文件的名称已从 `blogwatcher` 更改为 `blogwatcher-cli`。

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
- 按类别筛选：`blogwatcher-cli articles --category "工程技术"`
- 标记文章为已读：`blogwatcher-cli read 1`
- 标记文章为未读：`blogwatcher-cli unread 1`
- 全部标记为已读：`blogwatcher-cli read-all`
- 为某个博客全部标记为已读：`blogwatcher-cli read-all --blog "我的博客" --yes`

## 环境变量

所有命令参数均可通过带有 `BLOGWATCHER_` 前缀的环境变量来设置：

| 变量名 | 描述 |
|---|---|
| `BLOGWATCHER_DB` | SQLite 数据库文件的路径 |
| `BLOGWATCHER_WORKERS` | 并行扫描的工作进程数量（默认值：8） |
| `BLOGWATCHER_SILENT` | 扫描时仅输出“扫描完成”信息 |
| `BLOGWATCHER_YES` | 跳过确认提示 |
| `BLOGWATCHER_CATEGORY` | 文章的默认类别筛选条件 |

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
- 当 RSS 方式失败且已配置 `--scrape-selector` 时，将自动切换为 HTML 抓取模式。
- RSS/Atom 订阅源中的分类信息会被保存下来，可用于筛选文章。
- 支持批量导入来自 Feedly、Inoreader、NewsBlur 等工具导出的 OPML 文件中的博客。
- 数据库默认存储在 `~/.blogwatcher-cli/blogwatcher-cli.db` 目录下（可通过 `--db` 或 `BLOGWATCHER_DB` 参数进行修改）。
- 如需查看所有参数和选项，可输入 `blogwatcher-cli <command> --help`。
