---
title: "Gif Search — Search/download GIFs from Tenor via curl + jq"
sidebar_label: "Gif Search"
description: "Search/download GIFs from Tenor via curl + jq"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# GIF 搜索

通过 curl + jq 工具从 Tenor 平台搜索/下载 GIF 图片。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/media/gif-search` |
| 版本 | `1.1.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `GIF`、`媒体`、`搜索`、`Tenor`、`API` |

## 参考：完整 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# GIF 搜索（Tenor API）

使用 curl 直接通过 Tenor API 搜索并下载 GIF 图片，无需额外工具。

## 适用场景

适用于查找表情 GIF、创建视觉内容，以及在聊天中发送 GIF 图片。

## 设置方法

在您的环境变量中设置 Tenor API 密钥（可添加到 `${HERMES_HOME:-~/.hermes}/.env` 文件中）：

```bash
TENOR_API_KEY=your_key_here
```

您可以在 https://developers.google.com/tenor/guides/quickstart 获取免费的 API 密钥——Google Cloud Console 提供的 Tenor API 密钥完全免费，且拥有较为宽松的调用频率限制。

## 先决条件

- `curl` 和 `jq`（在 macOS/Linux 系统中均为标准工具）
- `TENOR_API_KEY` 环境变量

## 搜索 GIF 图片

```bash
# Search and get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Get smaller/preview versions
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## 下载 GIF 图片

```bash
# Search and download the top result
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## 获取完整元数据

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

## API 参数

| 参数 | 描述 |
|------|------|
| `q` | 搜索查询（空格需用 `+` 进行 URL 编码） |
| `limit` | 最大返回结果数（1-50，默认为 20） |
| `key` | API 密钥（来自 `$TENOR_API_KEY` 环境变量） |
| `media_filter` | 格式筛选：`gif`、`tinygif`、`mp4`、`tinymp4`、`webm` |
| `contentfilter` | 安全级别：`off`、`low`、`medium`、`high` |
| `locale` | 语言：`en_US`、`es`、`fr` 等 |

## 支持的媒体格式

每个搜索结果在 `.media_formats` 字段下会包含多种格式：

| 格式 | 用途 |
|------|------|
| `gif` | 全质量 GIF 图片 |
| `tinygif` | 小尺寸预览 GIF 图片 |
| `mp4` | 视频版本（文件体积更小） |
| `tinymp4` | 小尺寸预览视频 |
| `webm` | WebM 视频格式 |
| `nanogif` | 极小尺寸缩略图 |

## 注意事项

- 需对查询内容进行 URL 编码：空格替换为 `+`，特殊字符替换为 `%XX` 格式。
- 若在聊天中发送，`tinygif` 格式的链接体积更小，更利于传输。
- GIF 链接可直接在 Markdown 中使用，格式如下：`![标题](https://github.com/NousResearch/hermes-agent/blob/main/skills/media/gif-search/url)`
