---
sidebar_position: 5
title: "Bundled Skills Catalog"
description: "Catalog of bundled skills that ship with Hermes Agent"
---

# 内置技能目录

Hermes 在安装时会将庞大的内置技能库复制到 `~/.hermes/skills/` 目录中。下表中的每项技能都对应一个专门页面，详细介绍其定义、配置方法及使用方式。

通过执行 `hermes update` 命令，Hermes 也会同步这些内置技能，但同步时会尊重用户本地的删除操作及自定义修改。如果此处列出的某个技能并未出现在您个人目录的 `~/.hermes/skills/` 中，它依然属于 Hermes 的内置功能；您可以通过 `hermes skills reset <name> --restore` 命令将其恢复。

若某个技能未出现在此列表中，但实际存在于代码仓库中，系统会通过 `website/scripts/generate-skill-docs.py` 脚本重新生成相应的文档。

## apple

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`apple-notes`](/docs/user-guide/skills/bundled/apple/apple-apple-notes) | 通过 memo CLI 管理 Apple Notes：创建、搜索、编辑。 | `apple\apple-notes` |
| [`apple-reminders`](/docs/user-guide/skills/bundled/apple/apple-apple-reminders) | 通过 remindctl 管理 Apple Reminders：添加、查看、标记完成。 | `apple\apple-reminders` |
| [`findmy`](/docs/user-guide/skills/bundled/apple/apple-findmy) | 通过 macOS 上的 FindMy.app 追踪 Apple 设备及 AirTags。 | `apple\findmy` |
| [`imessage`](/docs/user-guide/skills/bundled/apple/apple-imessage) | 通过 macOS 上的 imsg CLI 发送和接收 iMessages/SMS 消息。 | `apple\imessage` |

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | 将编码任务委托给 Claude Code CLI（用于处理功能开发及 Pull Request）。 | `autonomous-ai-agents\claude-code` |
| [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | 将编码任务委托给 OpenAI Codex CLI（用于处理功能开发及 Pull Request）。 | `autonomous-ai-agents\codex` |
| [`computer-use`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-computer-use) | 优先控制桌面背景，接收到信号后再执行其他操作。 | `autonomous-ai-agents\computer-use` |
| [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | 对 Hermes Agent 进行使用、配置、主题设置、扩展及调度管理。 | `autonomous-ai-agents\hermes-agent` |
| [`merge-reconciler`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-merge-reconciler) | 由中立的第三方来解决智能体之间的合并冲突问题。 | `autonomous-ai-agents\merge-reconciler` |
| [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | 将编码任务委托给 OpenCode CLI（用于处理功能开发及 Pull Request 审核）。 | `autonomous-ai-agents\opencode` |

## 创意领域

| Skill | Description | Path |
|-------|-------------|------|
| [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) | Dark-themed SVG architecture/cloud/infra diagrams as HTML. | `creative\architecture-diagram` |
| [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video) | ASCII video: convert video/audio to colored ASCII MP4/GIF. | `creative\ascii-video` |
| [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic) | Infographics: 21 layouts x 21 styles (信息图, 可视化). | `creative\baoyu-infographic` |
| [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design) | Design one-off HTML artifacts (landing, deck, prototype). | `creative\claude-design` |
| [`design-md`](/docs/user-guide/skills/bundled/creative/creative-design-md) | Author/validate/export Google's DESIGN.md token spec files. | `creative\design-md` |
| [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer) | Humanize text: strip AI-isms and add real voice. | `creative\humanizer` |
| [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video) | Manim CE animations: 3Blue1Brown math/algo videos. | `creative\manim-video` |
| [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js) | p5.js sketches: gen art, shaders, interactive, 3D. | `creative\p5js` |
| [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs) | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. | `creative\popular-web-designs` |
| [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | Songwriting craft and Suno AI music prompts. | `creative\songwriting-and-ai-music` |

## DevOps

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`sdlc-review`](/docs/user-guide/skills/bundled/devops/devops-sdlc-review) | 审核看板任务交接流程，并对处理结果进行确认。 | `devops\sdlc-review` |

## 邮件处理

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`email-inbox-triage`](/docs/user-guide/skills/bundled/email/email-email-inbox-triage) | 对收件箱中的邮件进行分类处理：为不同邮件线程设定优先级，并安全地起草回复。 | `email\email-inbox-triage` |
| [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) | Himalaya CLI：通过终端操作IMAP/SMTP邮件。 | `email\himalaya` |

## 媒体处理

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search) | 使用curl和jq工具从Tenor平台搜索并下载GIF文件。 | `media\gif-search` |
| [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee) | 通过CLI命令获取音频的频谱图及特征数据（如梅尔频谱、色度图、MFCC参数等）。 | `media\songsee` |
| [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content) | 将YouTube视频的字幕转换为摘要、讨论帖或博客内容。 | `media\youtube-content` |

## 笔记管理

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) | 在Obsidian笔记库中读取、搜索、创建及编辑笔记。 | `note-taking\obsidian` |

## 效率提升工具

| Skill | Description | Path |
|-------|-------------|------|
| [`airtable`](/docs/user-guide/skills/bundled/productivity/productivity-airtable) | Airtable REST API via curl. Records CRUD, filters, upserts. | `productivity\airtable` |
| [`box`](/docs/user-guide/skills/bundled/productivity/productivity-box) | Box manages cloud files, sharing, search, and metadata. | `productivity\box` |
| [`document-to-action-items`](/docs/user-guide/skills/bundled/productivity/productivity-document-to-action-items) | Extract cited obligations, deadlines, tasks from documents. | `productivity\document-to-action-items` |
| [`docx`](/docs/user-guide/skills/bundled/productivity/productivity-docx) | Create, read, edit, template, and review Word .docx files. | `productivity\docx` |
| [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. | `productivity\google-workspace` |
| [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps) | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. | `productivity\maps` |
| [`meeting-action-items`](/docs/user-guide/skills/bundled/productivity/productivity-meeting-action-items) | Turn meeting notes into cited decisions, owners, tickets. | `productivity\meeting-action-items` |
| [`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) | Notion API + ntn CLI: pages, databases, markdown, Workers. | `productivity\notion` |
| [`pdf`](/docs/user-guide/skills/bundled/productivity/productivity-pdf) | PDF files: create, read, merge, fill, OCR, edit text. | `productivity\pdf` |
| [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) | Create, read, edit .pptx decks with python-pptx. | `productivity\powerpoint` |
| [`product-price-monitor`](/docs/user-guide/skills/bundled/productivity/productivity-product-price-monitor) | Watch product, flight, or listing prices; alert on target. | `productivity\product-price-monitor` |
| [`teams-meeting-pipeline`](/docs/user-guide/skills/bundled/productivity/productivity-teams-meeting-pipeline) | Teams meeting summaries, job replay, Graph subscriptions. | `productivity\teams-meeting-pipeline` |
| [`weekly-review-planning`](/docs/user-guide/skills/bundled/productivity/productivity-weekly-review-planning) | Weekly reset: commitments, stalled work, next-week plan. | `productivity\weekly-review-planning` |
| [`xlsx`](/docs/user-guide/skills/bundled/productivity/productivity-xlsx) | Create, read, edit Excel .xlsx workbooks and CSVs. | `productivity\xlsx` |

## 研究

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) | 按关键词、作者、类别或编号搜索 arXiv 论文。 | `research\arxiv` |
| [`competitor-news-monitor`](/docs/user-guide/skills/bundled/research/research-competitor-news-monitor) | 监控指定公司的重要新闻及相关摘要信息。 | `research\competitor-news-monitor` |
| [`grounded-citations`](/docs/user-guide/skills/bundled/research/research-grounded-citations) | 将答案与文档依据至可验证的引用来源。 | `research\grounded-citations` |
| [`llm-wiki`](/docs/user-guide/skills/bundled/research/research-llm-wiki) | Karpathy 的 LLM 维基：构建/查询相互关联的 Markdown 知识库。 | `research\llm-wiki` |

## 社交媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) | 通过 xurl CLI 操作 X/Twitter：原始帖子搜索、发布、私信发送及媒体处理。 | `social-media\xurl` |

## 软件开发

| Skill | Description | Path |
|-------|-------------|------|
| [`codebase-inspection`](/docs/user-guide/skills/bundled/software-development/software-development-codebase-inspection) | Inspect codebases w/ pygount: LOC, languages, ratios. | `software-development\codebase-inspection` |
| [`dogfood`](/docs/user-guide/skills/bundled/software-development/software-development-dogfood) | Exploratory QA of web apps: find bugs, evidence, reports. | `software-development\dogfood` |
| [`github`](/docs/user-guide/skills/bundled/software-development/software-development-github) | GitHub via gh CLI: PRs, issues, reviews, repos, auth. | `software-development\github` |
| [`hermes-agent-skill-authoring`](/docs/user-guide/skills/bundled/software-development/software-development-hermes-agent-skill-authoring) | Author in-repo SKILL.md files: frontmatter and structure. | `software-development\hermes-agent-skill-authoring` |
| [`inspecting-hermes-desktop-dom`](/docs/user-guide/skills/bundled/software-development/software-development-inspecting-hermes-desktop-dom) | Read the live Hermes desktop DOM/CSS over CDP. | `software-development\inspecting-hermes-desktop-dom` |
| [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger) | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. | `software-development\node-inspect-debugger` |
| [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy) | Debug Python: pdb REPL + debugpy remote (DAP). | `software-development\python-debugpy` |
| [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | Pre-commit review: security scan, quality gates, auto-fix. | `software-development\requesting-code-review` |
| [`simplify-code`](/docs/user-guide/skills/bundled/software-development/software-development-simplify-code) | Parallel 4-agent cleanup of recent code changes. | `software-development\simplify-code` |
| [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike) | Throwaway experiments to validate an idea before build. | `software-development\spike` |
| [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 4-phase root cause debugging: understand bugs before fixing. | `software-development\systematic-debugging` |
| [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) | TDD: enforce RED-GREEN-REFACTOR, tests before code. | `software-development\test-driven-development` |

## Web 模块

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`blocked-page-recovery`](/docs/user-guide/skills/bundled/web/web-blocked-page-recovery) | 当请求失败时使用：如 403/429 错误、付费墙、WAF 防护或机器人拦截。 | `web\blocked-page-recovery` |
