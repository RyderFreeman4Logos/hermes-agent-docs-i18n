---
title: Deliverable Mode (Artifacts in Chat)
sidebar_label: Deliverable Mode
description: How the agent ships generated charts, PDFs, spreadsheets, and other files as native attachments in messaging platforms.
---

# 输出文件模式

当 Hermes Agent 在消息网关（如 Slack、Discord、Telegram、WhatsApp、Signal 等）中运行时，它可以直接将生成的文件发送到聊天窗口——并非以用户需手动复制的路径形式，而是作为原生附件呈现。

图表会以内嵌图片的形式显示，PDF 报告则会以文件下载的形式呈现，电子表格则作为 `.xlsx` 格式上传。Agent 无需编写 `MEDIA:` 标签或执行任何特殊操作——只需生成文件，并在回复中注明其绝对路径即可。网关会从文本中提取该路径，将其从可见消息中移除，然后以原生方式上传文件。

## 工作原理

这一流程由三个部分协同完成：

1. **Agent 拥有生成文件的工具**。例如，可通过 `matplotlib` 的 `execute_code` 功能生成图表，使用 `latex-pdf-report` 技能生成 PDF，借助 `powerpoint` 技能创建演示文稿，通过 `image_generate` 生成图片，利用 `text_to_speech` 生成音频等等。

2. **网关会扫描 Agent 的回复以查找文件路径**。凡是带有支持格式扩展名的绝对路径（如 `/tmp/...`）或基于用户主目录的相对路径（如 `~/...`）都会被提取出来。代码块及内联代码中的路径会被忽略，从而确保代码示例不会被破坏。

3. **网关会根据文件类型进行相应处理**。在平台支持的情况下，图片会以内嵌形式显示；视频同样以内嵌方式呈现；音频则会作为语音/音频附件发送；其余类型的文件则全部作为文件附件上传。

## 支持的文件扩展名

| 类别 | 扩展名 | 传输方式 |
|---|---|---|
| 图片 | `.png .jpg .jpeg .gif .webp .bmp .tiff .svg` | 内嵌显示 |
| 视频 | `.mp4 .mov .avi .mkv .webm` | 在支持的平台内内嵌显示 |
| 音频 | `.mp3 .wav .ogg .m4a .flac` | 作为语音/音频附件发送 |
| 文档 | `.pdf .docx .doc .odt .rtf .txt .md` | 文件上传 |
| 数据文件 | `.xlsx .xls .csv .tsv .json .xml .yaml .yml` | 文件上传 |
| 演示文稿 | `.pptx .ppt .odp` | 文件上传 |
| 压缩文件 | `.zip .tar .gz .tgz .bz2 .7z` | 文件上传 |
| 网页文件 | `.html .htm` | 文件上传 |

`.py`、`.log` 以及其他源代码文件扩展名被刻意排除在外，以避免 Agent 自动发送任意源文件；如果需要向用户发送代码，请使用代码块。

## 激励 Agent 生成输出文件

默认情况下，Agent 并不会主动生成输出文件——它需要明确得到指示才行。有两种方式可以引导它：

**会话级**：直接提出要求（如“以图表形式将对比结果发给我”，“以 CSV 格式返回数据”），或编写自定义指令/个性设定，促使 Agent 在消息平台中倾向于回复输出文件。

**项目级**：在 Agent 所使用的项目的 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件中添加相关设置，或在 `~/.hermes/SOUL.md` 中设置全局个性设定，又或者是在 `~/.hermes/config.yaml` 的 `agent.personalities` 下创建命名预设（可通过 `/personality` 选项在每次会话中切换）。

Agent 需要使用的机制很简单：将文件渲染为绝对路径（例如 `/tmp/q3-revenue.png`），并在回复中以纯文本形式注明该路径，其余工作则由网关处理。代码块或反引号内的路径会被忽略，从而确保代码示例不会被破坏。

## Kanban 工作流：输出文件随完成通知一同发送

如果您使用 Hermes 的 Kanban 多 Agent 工作流，工作节点可以将输出文件附加到他们的 `kanban_complete` 请求中：

```python
kanban_complete(
    summary="rendered Q3 revenue chart and report",
    artifacts=[
        "/tmp/q3-revenue.png",
        "/tmp/q3-report.pdf",
    ],
)
```

当网关通知器向在 Slack、Telegram 等平台订阅该任务的用户发送“任务已完成”消息时，它还会将每个输出文件作为原生附件上传到对应聊天窗口中。这样，用户便能在一个地方获取任务成果与总结信息。

若在通知器运行时文件并不存在于磁盘上，则会直接跳过处理。

## 利用 MCP 连接更多服务

除了文件传输功能外，该智能体还可通过 MCP（模型上下文协议）接入其他服务。MCP 生态系统为大多数常用工具提供了社区开发的服务器——只需安装您需要的即可：

| 服务 | 能实现的功能 |
|---|---|
| **Notion** | 读写 Notion 页面、数据库及查询工作空间内容 |
| **GitHub** | 查看问题、 pull request、评论，以及执行超出 gh CLI 范围的仓库搜索功能 |
| **Linear** | 管理工单、项目与周期 |
| **Slack** | 在整个工作空间内进行搜索，查看其他频道的内容 |
| **Gmail** | 对收件箱内容进行分类处理、发送邮件及管理标签 |
| **Salesforce** | 查看潜在客户、销售机会及账户数据 |
| **Snowflake / BigQuery** | 对数据仓库执行 SQL 查询 |
| **Google Drive** | 搜索文件、查看文件内容及管理共享设置 |

可通过 `~/.hermes/config.yaml` 文件中的 `mcp_servers` 部分来安装 MCP 服务器。完整的设置指南请参阅 [MCP 集成文档](./mcp.md)。

## 与 Perplexity Computer 在 Slack 中的对比

Perplexity Computer 在 Slack 中的集成也基于相同原理：智能体会生成图表、PDF、幻灯片等成果，并将其作为原生附件发布回聊天线程中。Hermes Agent 的成果生成模式在本地也能实现类似的用户体验：

- 生成过程在用户的虚拟环境/沙箱中完成（无需远程租户）；
- 文件通过相同的 Slack `files.uploadV2` API 上传至聊天窗口；
- 连接功能的丰富度依赖于 MCP，而非预先预设的 400 种集成选项——用户只需安装自己实际使用的功能即可。

OAuth 令牌会保存在用户机器上的 `auth.json` 或 `.env` 文件中，不存在托管式的令牌存储机制，也没有多租户微虚拟机架构。最终效果却十分相似。
