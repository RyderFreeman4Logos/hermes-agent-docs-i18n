---
title: Deliverable Mode (Artifacts in Chat)
sidebar_label: Deliverable Mode
description: How the agent ships generated charts, PDFs, spreadsheets, and other files as native attachments in messaging platforms.
---

# 文件交付模式

当 Hermes Agent 在消息网关（如 Slack、Discord、Telegram、WhatsApp、Signal 等）中运行时，它可以直接将生成的文件发送到聊天界面——并非以用户需手动复制的路径形式，而是作为原生附件呈现。

图表会以内嵌图片的形式显示，PDF 报告则会以文件下载的方式呈现，电子表格则会被上传为 `.xlsx` 格式。Agent 无需编写 `MEDIA:` 标签或执行任何特殊操作——它只需生成文件，并在响应中注明其绝对路径即可。网关会从文本中提取该路径，将其从可见消息中移除，然后以原生方式上传文件。

## 工作原理

这一过程由三个部分协同完成：

1. **Agent 拥有用于生成文件的工具。** 例如，可通过 `matplotlib` 的 `execute_code` 功能生成图表，使用 `docx` 技能处理 Word 文档，`xlsx` 技能处理电子表格，`pdf` 和 `latex-pdf-report` 技能生成 PDF 文件，`powerpoint` 技能处理演示文稿，`image_generate` 功能生成图片，`text_to_speech` 功能生成音频文件，等等。

2. **网关会扫描 Agent 的响应内容以查找文件路径。** 任何以支持的文件扩展名结尾的绝对路径（如 `/tmp/...`）或基于用户主目录的相对路径（如 `~/...`）都会被提取出来。代码块及内联代码中的路径会被忽略，从而确保代码示例不会被破坏。

3. **网关会根据文件类型进行相应处理。** 图片会在平台支持的情况下以内嵌形式显示；视频同样以内嵌方式呈现；音频文件则会被转为语音/音频附件；其余类型的文件则作为普通附件上传。

## 支持的文件扩展名

| 类别 | 支持的文件扩展名 | 传输方式 |
|---|---|---|
| 图片 | `.png .jpg .jpeg .gif .webp .bmp .tiff .svg` | 内嵌显示 |
| 视频 | `.mp4 .mov .avi .mkv .webm .3gp` | 在支持的情况下内嵌显示 |
| 音频 | `.mp3 .m2a .wav .ogg .opus .m4a .flac` | 以语音/音频附件形式发送 |
| 文档 | `.pdf .docx .doc .odt .rtf .txt .md .epub` | 文件上传 |
| 数据文件 | `.xlsx .xls .ods .csv .tsv .json .xml .yaml .yml` | 文件上传 |
| 地理空间数据 | `.kmz .kml .geojson .gpx` | 文件上传 |
| 演示文稿 | `.pptx .ppt .odp .key` | 文件上传 |
| 压缩文件 | `.zip .tar .gz .tgz .bz2 .xz .7z .rar .apk .ipa` | 文件上传 |
| 网页文件 | `.html .htm` | 文件上传 |

`.py`、`.log` 以及其他源代码文件扩展名被刻意排除在外，以避免智能体自动传输任意源文件；若需向用户发送代码，请使用代码块格式。

## 指导智能体生成输出结果

默认情况下，智能体不会主动生成输出结果——它需要明确指示才能如此操作。有两种方法可以引导它：

**会话级引导：** 明确提出要求（如“以图表形式将对比结果发送给我”，“以 CSV 格式返回数据”），或编写自定义指令/个性设定，在消息平台中促使智能体倾向于生成结构化的输出。

**项目级引导：** 在智能体工作的项目中的 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件中添加相应设定，或在 `~/.hermes/SOUL.md` 中设置全局个性设定，又或者是在 `~/.hermes/config.yaml` 的 `agent.personalities` 下创建命名预设（可通过 `/personality` 选项在每次会话中切换）。

该智能体所需使用的机制非常简单：将文件渲染为绝对路径（例如 `/tmp/q3-revenue.png`），并在回复中以纯文本形式注明该路径，其余工作则由网关处理。位于代码块或反引号内的路径会被忽略，因此代码示例不会被篡改。

## 看板模式：交付物随完成通知一同发送

如果您使用 Hermes 的看板多智能体工作流，工作节点可以将交付文件附加到其 `kanban_complete` 调用中：

```python
kanban_complete(
    summary="rendered Q3 revenue chart and report",
    artifacts=[
        "/tmp/q3-revenue.png",
        "/tmp/q3-report.pdf",
    ],
)
```

当网关通知器向在 Slack、Telegram 等平台中订阅该任务的用户发送“任务已完成”消息时，它还会将每个交付物作为原生附件上传到 해당聊天窗口中。这样，用户便能在一个地方获取交付成果与任务摘要。

如果在通知器运行时对应文件并不存在于磁盘上，系统会自动跳过这些文件。

## 通过 MCP 连接更多服务

除了文件交付功能外，该智能体还能通过 MCP（模型上下文协议）接入其他服务。MCP 生态系统提供了大多数常用工具的社区服务器——只需安装您需要的即可：

| 服务 | 能实现的功能 |
|---|---|
| **Notion** | 读取/写入 Notion 页面、数据库，查询工作空间内容 |
| **GitHub** | 查看问题、拉取请求、评论，以及进行超出 gh CLI 范围的仓库搜索 |
| **Linear** | 管理工单、项目与周期 |
| **Slack** | 在整个工作空间内搜索，查看其他频道的内容 |
| **Gmail** | 对收件箱进行分类处理、发送邮件、管理标签 |
| **Salesforce** | 查看潜在客户、销售机会及账户数据 |
| **Snowflake / BigQuery** | 对数据仓库执行 SQL 查询 |
| **Google Drive** | 搜索文件、查看内容、管理共享设置 |

可通过 `~/.hermes/config.yaml` 文件中的 `mcp_servers` 部分来安装 MCP 服务器。完整的设置指南请参阅 [MCP 集成文档](./mcp.md)。

## 与 Slack 中的 Perplexity Computer 的对比

Perplexity Computer的Slack集成也基于相同的理念：智能体先生成相应的输出内容（如图表、PDF文件或幻灯片集），再将其作为原生附件回传至对应聊天线程中。Hermes Agent的输出功能在本地同样采用了类似的用户体验模式：

- 内容生成会在用户的虚拟环境/沙箱中进行，无需依赖远程租户环境。
- 文件通过Slack的`files.uploadV2` API上传至聊天界面。
- 集成功能的丰富度是通过MCP机制实现的，而非依赖预先整理好的400种托管集成列表——用户只需安装自己实际使用的集成即可。

OAuth令牌会存储在用户设备上的`auth.json`或`.env`文件中，不存在托管式的令牌存储方案，也不采用多租户微虚拟机架构。最终效果却是一致的。
