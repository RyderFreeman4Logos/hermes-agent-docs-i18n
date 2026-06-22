---
sidebar_position: 5
title: "Bundled Skills Catalog"
description: "Catalog of bundled skills that ship with Hermes Agent"
---

# 内置技能目录

Hermes在安装时会将大量内置技能库复制到`~/.hermes/skills/`目录中。下表中的每一项都对应着详细介绍其功能定义、设置方法及使用方式的专用页面。

通过执行`hermes update`命令，Hermes也会同步这些内置技能，但同步过程会尊重用户本地的删除操作及自定义修改。如果此处列出的某个技能未出现在您账户的`~/.hermes/skills/`目录中，它依然属于Hermes的默认配置；此时可使用`hermes skills reset <name> --restore`命令将其恢复。

若某个技能未出现在此列表中，但实际存在于代码仓库中，系统会通过`website/scripts/generate-skill-docs.py`脚本自动重新生成该技能的文档。

## apple

| 技能 | 描述 | 路径 |
|------|------|------|
| [`apple-notes`](/docs/user-guide/skills/bundled/apple/apple-apple-notes) | 通过memo CLI管理Apple Notes：创建、搜索、编辑笔记。 | `apple/apple-notes` |
| [`apple-reminders`](/docs/user-guide/skills/bundled/apple/apple-apple-reminders) | 通过remindctl管理Apple Reminders：添加、查看、标记完成任务。 | `apple/apple-reminders` |
| [`findmy`](/docs/user-guide/skills/bundled/apple/apple-findmy) | 通过macOS上的FindMy.app追踪Apple设备及AirTags。 | `apple/findmy` |
| [`imessage`](/docs/user-guide/skills/bundled/apple/apple-imessage) | 通过macOS上的imsg CLI发送和接收iMessages及短信。 | `apple/imessage` |
| [`macos-computer-use`](/docs/user-guide/skills/bundled/apple/apple-macos-computer-use) | 在后台控制macOS桌面操作——截图、鼠标操作、键盘输入、滚动、拖动等——且不会占用用户的光标、焦点或快捷键。适用于所有具备相应功能的模型。每当需要使用`computer_use`工具时，均可加载此技能。 | `apple/macos-computer-use` |

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|------|------|------|
| [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | 将编码任务委托给Claude Code CLI，支持处理功能开发及PR相关操作。 | `autonomous-ai-agents/claude-code` |
| [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | 将编码任务委托给OpenAI Codex CLI，支持处理功能开发及PR相关操作。 | `autonomous-ai-agents/codex` |
| [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | 对Hermes Agent进行配置、扩展或贡献代码。 | `autonomous-ai-agents/hermes-agent` |
| [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | 将编码任务委托给OpenCode CLI，支持处理功能开发及PR审核工作。 | `autonomous-ai-agents/opencode` |

## creative

| 技能 | 描述 | 路径 |
|------|------|------|
| [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) | 生成深色主题的SVG架构图、云架构图及基础设施图，并以HTML格式输出。 | `creative/architecture-diagram` |
| [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art) | 生成ASCII艺术内容：支持pyfiglet、cowsay、图形框以及图像转ASCII功能。 | `creative/ascii-art` |
| [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video) | 生成ASCII视频：可将视频或音频转换为带颜色的ASCII格式的MP4/GIF文件。 | `creative/ascii-video` |
| [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic) | 生成信息图：提供21种布局与21种风格可选。 | `creative/baoyu-infographic` |
| [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claudesign) | 设计一次性使用的HTML格式内容，如落地页、演示文稿或原型界面。 | `creative/claude-design` |
| [`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui) | 使用ComfyUI生成图像、视频及音频：支持安装、启动工具，管理节点与模型，还可通过参数注入方式运行工作流。该技能利用官方的comfy-cli处理生命周期相关操作，同时通过REST/WebSocket API实现实际执行功能。 | `creative/comfyui` |
| [`design-md`](/docs/user-guide/skills/bundled/creative/creative-design-md) | 编写、验证及导出Google的DESIGN.md标记规范文件。 | `creative/design-md` |
| [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) | 生成手绘风格的Excalidraw JSON格式图表，适用于架构图、流程图及序列图等场景。 | `creative/excalidraw` |
| [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer) | 对文本进行优化处理：去除AI特有的表达方式，增添真实自然的语气。 | `creative/humanizer` |
| [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video) | 生成Manim CE动画效果，类似3Blue1Brown风格的数学及算法教学视频。 | `creative/manim-video` |
| [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js) | 使用p5.js编写创意作品：可生成艺术图像、着色器效果、交互式内容及3D图形。 | `creative/p5js` |
| [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs) | 提供54套真实的网页设计系统模板，以HTML/CSS格式呈现，涵盖Stripe、Linear、Vercel等知名平台的设计风格。 | `creative/popular-web-designs` |
| [`pretext`](/docs/user-guide/skills/bundled/creative/creative-pretext) | 用于构建创意型浏览器演示项目，基于@chenglou/pretext框架实现——无需DOM即可实现ASCII艺术文本排版、围绕障碍物的排版布局、以文本为几何元素的互动游戏、动态字体效果以及基于文本的生成艺术。可生成单文件HTML格式的输出结果。 | `creative/pretext` |
| [`sketch`](/docs/user-guide/skills/bundled/creative/creative-sketch) | 快速生成用于对比的HTML风格原型，通常提供2-3种不同的设计版本。 | `creative/sketch` |
| [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | 提供歌曲创作技巧以及基于Suno AI的音乐提示词生成功能。 | `creative/songwriting-and-ai-music` |
| [`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp) | 通过twozero MCP控制正在运行的TouchDesigner实例：可创建操作符、设置参数、连接线路、执行Python代码，进而生成实时视觉效果。内置36种原生工具。 | `creative/touchdesigner-mcp` |

## data-science

| 技能 | 描述 | 路径 |
|------|------|------|
| [`jupyter-live-kernel`](/docs/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) | 通过实时运行的Jupyter内核（hamelnb）实现Python的迭代式开发。 | `data-science/jupyter-live-kernel` |

## devops

| 技能 | 描述 | 路径 |


## dogfood

| 技能 | 描述 | 路径 |
|------|------|------|
| [`dogfood`](/docs/user-guide/skills/bundled/dogfood/dogfood-dogfood) | 对网页应用进行探索性质量检测：帮助发现漏洞、收集相关证据并生成检测报告。 | `dogfood` |

## email

| 技能 | 描述 | 路径 |
|------|------|------|
| [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) | Himalaya CLI工具：允许在终端中通过IMAP/SMTP协议操作电子邮件。 | `email/himalaya` |

## github

| 技能 | 描述 | 路径 |
|------|------|------|
| [`codebase-inspection`](/docs/user-guide/skills/bundled/github/github-codebase-inspection) | 使用pygount工具分析代码库，统计行数、编程语言使用比例及各类代码占比。 | `github/codebase-inspection` |
| [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth) | 配置GitHub认证：支持HTTPS令牌、SSH密钥以及通过gh CLI登录。 | `github/github-auth` |
| [`github-code-review`](/docs/user-guide/skills/bundled/github/github-github-code-review) | 审核PR请求：可通过gh工具或REST接口查看代码差异并添加内联评论。 | `github/github-code-review` |
| [`github-issues`](/docs/user-guide/skills/bundled/github/github-github-issues) | 通过gh工具或REST接口创建、分类、标记及分配GitHub问题任务。 | `github/github-issues` |
| [`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow) | 管理GitHub PR的全生命周期：包括分支创建、代码提交、PR开启、持续集成测试以及合并操作。 | `github/github-pr-workflow` |
| [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) | 支持克隆、创建及复制仓库；同时可管理远程仓库及版本发布功能。 | `github/github-repo-management` |

## media

| 技能 | 描述 | 路径 |
|------|------|------|
| [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search) | 通过curl + jq命令从Tenor平台搜索并下载GIF图片。 | `media/gif-search` |
| [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula) | HeartMuLa：基于歌词及标签生成类似Suno风格的歌曲。 | `media/heartmula` |
| [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee) | 通过CLI命令获取音频的频谱图及各种特征参数，如梅尔频率、色度值、MFCC等。 | `media/songsee` |
| [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content) | 将YouTube视频的文字转录内容进一步整理为摘要、系列文章或博客内容。 | `media/youtube-content` |

## mlops

| 技能 | 描述 | 路径 |
|------|------|------|
| [`audiocraft-audio-generation`](/docs/user-guide/skills/bundled/mlops/mlops-models-audiocraft) | AudioCraft：支持使用MusicGen实现文本转音乐功能，以及通过AudioGen实现文本转声音功能。 | `mlops/models/audiocraft` |
| [`huggingface-hub`](/docs/user-guide/skills/bundled/mlops/mlops-huggingface-hub) | HuggingFace hf CLI工具：支持搜索、下载及上传模型及数据集。 | `mlops/huggingface-hub` |
| [`llama-cpp`](/docs/user-guide/skills/bundled/mlops/mlops-inference-llama-cpp) | llama.cpp本地GGUF格式模型推理功能，同时支持通过HF Hub查找模型。 | `mlops/inference/llama-cpp` |
| [`evaluating-llms-harness`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-lm-evaluation-harness) | lm-eval-harness：用于对大型语言模型进行性能测试，支持MMLU、GSM8K等标准测试任务。 | `mlops/evaluation/lm-evaluation-harness` |
| [`segment-anything-model`](/docs/user-guide/skills/bundled/mlops/mlops-models-segment-anything) | SAM模型：支持通过点、矩形框或掩码实现零样本图像分割功能。 | `mlops/models/segment-anything` |
| [`serving-llms-vllm`](/docs/user-guide/skills/bundled/mlops/mlops-inference-vllm) | vLLM：高效的大型语言模型服务框架，支持调用OpenAI API，并具备量化优化功能。 | `mlops/inference/vllm` |
| [`weights-and-biases`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-weights-and-biases) | W&B工具：用于记录机器学习实验过程、执行参数扫描测试，同时支持模型注册及可视化仪表板展示。 | `mlops/evaluation/weights-and-biases` |

## note-taking

| 技能 | 描述 | 路径 |
|------|------|------|
| [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) | 支持在Obsidian笔记应用中读取、搜索、创建及编辑笔记内容。 | `note-taking/obsidian` |

## productivity| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`airtable`](/docs/user-guide/skills/bundled/productivity/productivity-airtable) | 通过 curl 调用 Airtable REST API，支持记录的创建、读取、更新、删除操作，以及数据筛选与合并更新功能。 | `productivity/airtable` |
| [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) | 通过 gws CLI 或 Python 工具，实现对 Gmail、日历、云端硬盘、文档及表格等服务的操作。 | `productivity/google-workspace` |
| [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps) | 基于 OpenStreetMap/OSRM 数据，提供地址地理编码、兴趣点查询、路线规划以及时区查询功能。 | `productivity/maps` |
| [`nano-pdf`](/docs/user-guide/skills/bundled/productivity/productivity-nano-pdf) | 通过 nano-pdf CLI（支持自然语言指令），对 PDF 文件中的文本、拼写错误及标题进行编辑。 | `productivity/nano-pdf` |
| [`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) | 结合 Notion API 与 ntn CLI，可实现对页面、数据库、Markdown 内容以及 Workers 的操作。 | `productivity/notion` |
| [`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) | 使用 pymupdf、marker-pdf 等工具，从 PDF 文件或扫描图片中提取文本。 | `productivity/ocr-and-documents` |
| [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) | 支持创建、读取及编辑 .pptx 格式的演示文稿、幻灯片、备注内容以及模板。 | `productivity/powerpoint` |
| [`teams-meeting-pipeline`](/docs/user-guide/skills/bundled/productivity/productivity-teams-meeting-pipeline) | 通过 Hermes CLI 管理 Teams 会议摘要生成流程，可完成会议总结、流程状态查看、任务重放以及 Microsoft Graph 订阅管理等功能。 | `productivity/teams-meeting-pipeline` |

## 研究领域

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) | 可按关键词、作者、分类或编号等方式搜索 arXiv 上的学术论文。 | `research/arxiv` |
| [`blogwatcher`](/docs/user-guide/skills/bundled/research/research-blogwatcher) | 通过 blogwatcher-cli 工具，实现对博客以及 RSS/Atom 订阅源的内容监控。 | `research/blogwatcher` |
| [`llm-wiki`](/docs/user-guide/skills/bundled/research/research-llm-wiki) | 基于 Karpathy 编写的 LLM 维基，可用于构建和查询相互关联的 Markdown 形式知识库。 | `research/llm-wiki` |
| [`polymarket`](/docs/user-guide/skills/bundled/research/research-polymarket) | 可查询 Polymarket 平台上的市场信息、价格数据、订单簿内容以及历史交易记录。 | `research/polymarket` |
| [`research-paper-writing`](/docs/user-guide/skills/bundled/research/research-research-paper-writing) | 提供从研究设计到论文提交的完整流程，帮助用户撰写适用于 NeurIPS、ICML、ICLR 等会议的机器学习论文。 | `research/research-paper-writing` |

## 智能家居

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`openhue`](/docs/user-guide/skills/bundled/smart-home/smart-home-openhue) | 通过 OpenHue CLI 工具，可对 Philips Hue 灯具、场景模式以及房间进行控制。 | `smart-home/openhue` |

## 社交媒体

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) | 通过 xurl CLI 工具操作 X/Twitter 平台，支持发布内容、搜索信息、发送私信、上传媒体文件以及使用 v2 API。 | `social-media/xurl` |

## 软件开发

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`hermes-agent-skill-authoring`](/docs/user-guide/skills/bundled/software-development/software-development-hermes-agent-skill-authoring) | 指导用户如何在仓库中编写 SKILL.md 文件，包括设置前置信息、验证规则以及规划文件结构。 | `software-development/hermes-agent-skill-authoring` |
| [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger) | 通过 --inspect 参数结合 Chrome DevTools Protocol CLI，实现对 Node.js 程序的调试功能。 | `software-development/node-inspect-debugger` |
| [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) | 计划模式：允许用户将任务规划为结构化的 Markdown 文本并保存到 .hermes/plans/ 目录中，目前仅用于任务规划，不支持自动执行。该模式要求任务分解细致、路径明确且包含完整代码。 | `software-development/plan` |
| [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy) | 提供 Python 调试功能，包括使用 pdb REPL 以及通过 debugpy 实现远程调试（DAP）。 | `software-development/python-debugpy` |
| [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | 实现预提交代码审查功能，可自动执行安全扫描、质量检查并给出修复建议。 | `software-development/requesting-code-review` |
| [`simplify-code`](/docs/user-guide/skills/bundled/software-development/software-development-simplify-code) | 调用三个智能代理并行处理最近的代码变更，帮助简化代码结构。 | `software-development/simplify-code` |
| [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike) | 用于在正式开发之前通过快速实验来验证某个想法的可行性。 | `software-development/spike` |
| [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 提供四阶段根本原因调试方法，帮助用户在解决问题前先深入理解问题本质。 | `software-development/systematic-debugging` |
| [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) | 实现测试驱动开发模式，要求遵循 RED-GREEN-REFACTOR 原则，确保在编写代码之前先完成测试。 | `software-development/test-driven-development` |

## 元宝

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`yuanbao`](/docs/user-guide/skills/bundled/yuanbao/yuanbao-yuanbao) | 支持在元宝群组中@提及用户，以及查询群组内成员信息与相关内容。 | `yuanbao` |
