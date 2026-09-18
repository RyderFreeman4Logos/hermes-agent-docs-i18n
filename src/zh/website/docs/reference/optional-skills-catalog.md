---
sidebar_position: 9
title: "Optional Skills Catalog"
description: "Official optional skills shipped with hermes-agent — install via hermes skills install official/<category>/<skill>"
---

# 可选技能目录

Hermes Agent 默认会随附位于 `optional-skills/` 目录下的可选技能，但这些技能**默认处于关闭状态**。如需使用，需手动进行安装：

```bash
hermes skills install official/<category>/<skill>
```

例如：


需将整个输入内容完整翻译，不得提前终止。

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

以下列出的每项技能均对应一个专门页面，其中详细介绍了其定义、配置方法及使用方式。

如需卸载：

```bash
hermes skills uninstall <skill-name>
```

## 自主 AI 智能体

| 技能 | 描述 |
|-------|-------------|
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | 操作 Antigravity CLI (agy)：插件管理、身份认证及沙箱环境功能。 |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编程任务委托给 Blackbox AI 多模型 CLI 处理。 |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | 将编程任务交由 xAI Grok Build CLI 执行（支持功能开发与 Pull Request 提交）。 |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 配置并排查 Hermes 所使用的 Honcho 内存相关问题。 |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | 将编程任务委托给 OpenHands CLI 处理（支持模型无关操作及 LiteLLM 功能）。 |

## 区块链

| 技能 | 描述 |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | 仅读型 EVM 客户端：可查询 8 条区块链上的钱包信息、代币数据及 Gas 费用。 |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | 提供 Hyperliquid 市场数据、账户历史记录及交易审核功能。 |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | 以美元为单位查询 Solana 网络上的钱包、代币、交易记录及 NFT 信息。 |

## 通信功能

| 技能 | 描述 |
|-------|-------------|
| [**1-3-1规则**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | 1-3-1决策简报：明确问题、列出三种方案，并选定一个最终选项。 |

## 创意类

| Skill | Description |
|-------|-------------|
| [**ascii-art**](/docs/user-guide/skills/optional/creative/creative-ascii-art) | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| [**audiocraft-audio-generation**](/docs/user-guide/skills/optional/creative/creative-audiocraft-audio-generation) | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound. |
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | Article illustrations: type × style × palette consistency. |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | Knowledge comics (知识漫画): educational, biography, tutorial. |
| [**comfyui**](/docs/user-guide/skills/optional/creative/creative-comfyui) | Generate images, video, and audio via diffusion workflows. |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | Generate flat, minimal educational SVG visuals as HTML. |
| [**creative-ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | Generate ideas via named methods from creative practice. |
| [**draw-your-font**](/docs/user-guide/skills/optional/creative/creative-draw-your-font) | Turn a handwriting photo into an installable TTF font. |
| [**excalidraw**](/docs/user-guide/skills/optional/creative/creative-excalidraw) | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| [**heartmula**](/docs/user-guide/skills/optional/creative/creative-heartmula) | HeartMuLa: Suno-like song generation from lyrics + tags. |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | Render MP4/WebM videos from HTML compositions. |
| [**impeccable**](/docs/user-guide/skills/optional/creative/creative-impeccable) | Frontend design guidance, upstream-maintained (impeccable). |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | Plan and run multi-agent video production pipelines. |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | Create meme PNGs from templates with Pillow text overlay. |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| [**pretext**](/docs/user-guide/skills/optional/creative/creative-pretext) | Build creative browser demos with DOM-free text layout. |
| [**simple-english**](/docs/user-guide/skills/optional/creative/creative-simple-english) | Rewrite text to ASD-STE100 Simplified Technical English. |
| [**sketch**](/docs/user-guide/skills/optional/creative/creative-sketch) | Throwaway HTML mockups: 2-3 design variants to compare. |
| [**social-media-content-calendar**](/docs/user-guide/skills/optional/creative/creative-social-media-content-calendar) | Plan multi-platform social campaigns: briefs to posting. |
| [**tldraw-offline**](/docs/user-guide/skills/optional/creative/creative-tldraw-offline) | Drive and script tldraw offline canvases with an agent. |
| [**touchdesigner-mcp**](/docs/user-guide/skills/optional/creative/creative-touchdesigner-mcp) | Control TouchDesigner via twozero MCP. |
| [**unreal-mcp**](/docs/user-guide/skills/optional/creative/creative-unreal-mcp) | Automate Unreal Engine editor scenes, actors, and renders. |

## 数据科学

| 技能 | 描述 |
|-------|-------------|
| [**jupyter-notebook**](/docs/user-guide/skills/optional/data-science/data-science-jupyter-notebook) | 通过实时 Jupyter 内核（hamelnb）实现 Python 迭代开发。 |

## DevOps

| 技能 | 描述 |
|-------|-------------|
| [**actual-setup**](/docs/user-guide/skills/optional/devops/devops-actual-setup) | 在 Hermes 环境中配置 Actual Computer (actual.inc) 推理功能。 |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | 管理 Docker 容器、镜像、卷以及 Compose 配置。 |
| [**hermes-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-hermes-s6-container-supervision) | 修改或调试 Hermes Docker 镜像中的 s6 服务。 |
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-inference-sh-cli) | 通过 inference.sh CLI 运行 150 多种 AI 应用（图像、视频、大语言模型）。 |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | 利用 Pinggy 实现无需安装的 SSH 本地主机隧道功能。 |
| [**setup-wizard-generator**](/docs/user-guide/skills/optional/devops/devops-setup-wizard-generator) | 生成用于指导用户完成手动配置的 Bash 向导。 |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | 支持轮询 RSS、JSON API 以及 GitHub 数据，并具备水印去重功能。 |

## 内部测试工具

| 技能 | 描述 |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 扮演恶意用户，以发现并分类用户体验方面的问题。 |

## 邮件

| 技能 | 描述 |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | 当智能体需要使用 AgentMail CLI 邮箱收件箱时使用。 |

## 金融领域

| 技能 | 描述 |
|-------|-------------|
| [**三表模型**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | 在 Excel 中构建整合了资产负债表、利润表和现金流量表的财务工作表。 |
| [**可比公司分析**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | 在 Excel 中构建用于可比公司估值的工作表。 |
| [**DCF模型**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | 在 Excel 中构建折现现金流估值工作表。 |
| [**Excel文档生成**](/docs/user-guide/skills/optional/finance/finance-excel-author) | 使用 openpyxl 以无界面方式生成可审计的财务工作表。 |
| [**杠杆收购模型**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | 在 Excel 中构建包含内部收益率及投资回收期等指标的杠杆收购分析工作表。 |
| [**并购模型**](/docs/user-guide/skills/optional/finance/finance-merger-model) | 在 Excel 中构建用于分析并购带来的价值增值或稀释效应的工作表。 |
| [**Polymarket接口**](/docs/user-guide/skills/optional/finance/finance-polymarket) | 查询 Polymarket 的市场信息、价格数据、订单簿及历史记录。 |
| [**PowerPoint文档生成**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | 使用 python-pptx 以无界面方式生成 PowerPoint 演示文稿。 |
| [**股票信息**](/docs/user-guide/skills/optional/finance/finance-stocks) | 通过 Yahoo 提供股票行情、历史数据、搜索功能、对比分析以及加密货币相关信息。 |

## 游戏领域

## 技能

| 技能 | 描述 |
|------|------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | 托管经过修改的 Minecraft 服务器（CurseForge、Modrinth）。 |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | 通过无头模拟器结合内存读取功能来游玩《宝可梦》。 |

## 健康管理

| 技能 | 描述 |
|------|------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | 基于 wger/USDA 数据提供锻炼计划、营养摄入规划以及身体指标分析。 |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | 利用 NeuroSkill 提供的实时脑机接口数据来监测认知状态与情绪变化。 |

## MCP

| 技能 | 描述 |
|------|------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | 开发、测试并部署 Python 版 MCP 服务器。 |
| [**mcp-oauth-remote-gateway**](/docs/user-guide/skills/optional/mcp/mcp-mcp-oauth-remote-gateway) | 为运行在无头网关上的远程 MCP 服务器手动配置 OAuth 认证。 |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | 通过终端查看、认证并调用各类 MCP 服务器及工具。 |

## 迁移

| 技能 | 描述 |
|------|------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | 将 OpenClaw 环境中的配置（包括记忆数据与技能）导入 Hermes 系统。 |

## MLOps

| Skill | Description |
|-------|-------------|
| [**accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | Run PyTorch training across GPUs with minimal changes. |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO). |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | Embedding database for RAG and semantic search. |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | Zero-shot image classification and image-text search. |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy: declarative LM programs, auto-optimize prompts, RAG. |
| [**evaluating-llms-harness**](/docs/user-guide/skills/optional/mlops/mlops-evaluation-evaluating-llms-harness) | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Fast vector similarity search at billion scale. |
| [**flash-attention**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | Speed up long-sequence transformer training and inference. |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | Constrain LLM output with grammars; guarantee valid JSON. |
| [**huggingface-hub**](/docs/user-guide/skills/optional/mlops/mlops-models-huggingface-hub) | HuggingFace hf CLI: search/download/upload models, datasets. |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | Fast BPE/WordPiece tokenization and custom vocab training. |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | Structured LLM outputs validated with Pydantic. |
| [**lambda-labs**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | On-demand GPU cloud instances for ML training. |
| [**llama-cpp**](/docs/user-guide/skills/optional/mlops/mlops-inference-llama-cpp) | llama.cpp local GGUF inference + HF Hub model discovery. |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | Vision-language chat: VQA, captioning, image dialogue. |
| [**modal**](/docs/user-guide/skills/optional/mlops/mlops-modal) | Serverless GPU cloud for ML jobs and model APIs. |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | Curate LLM training data: dedupe, filter, PII redaction. |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS: abliterate LLM refusals (diff-in-means). |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines: structured JSON/regex/Pydantic LLM generation. |
| [**peft**](/docs/user-guide/skills/optional/mlops/mlops-peft) | Fine-tune large LLMs with LoRA on limited GPU memory. |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | Managed vector DB for production RAG and search. |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | Fully sharded data-parallel training for large models. |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | Clean training loops with built-in distributed support. |
| [**qdrant**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | Vector search engine for production RAG systems. |
| [**saelens**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | Train sparse autoencoders to interpret model features. |
| [**segment-anything-model**](/docs/user-guide/skills/optional/mlops/mlops-models-segment-anything-model) | SAM: zero-shot image segmentation via points, boxes, masks. |
| [**serving-llms-vllm**](/docs/user-guide/skills/optional/mlops/mlops-inference-serving-llms-vllm) | vLLM: high-throughput LLM serving, OpenAI API, quantization. |
| [**simpo**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | Reference-free preference alignment, simpler than DPO. |
| [**slime**](/docs/user-guide/skills/optional/mlops/mlops-slime) | RL post-training for LLMs with Megatron and SGLang. |
| [**stable-diffusion**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | Text-to-image generation, inpainting, and img2img. |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | High-throughput LLM inference on NVIDIA GPUs. |
| [**torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | Pretrain LLMs at scale with PyTorch 4D parallelism. |
| [**trl-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL: SFT, DPO, GRPO, RLOO reward modeling for LLM RLHF. |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM. |
| [**weights-and-biases**](/docs/user-guide/skills/optional/mlops/mlops-evaluation-weights-and-biases) | W&B: log ML experiments, sweeps, model registry, dashboards. |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | Transcribe and translate speech in 99 languages. |

## 支付功能

| 技能 | 描述 |
|-------|-------------|
| [**mpp-agent**](/docs/user-guide/skills/optional/payments/payments-mpp-agent) | 通过机器支付协议（MPP）调用返回 HTTP 402 状态的 API 进行支付。 |
| [**stripe-link-cli**](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli) | 利用 Stripe Link 实现支付功能——支持卡片支付、SPT 支付以及审批流程。 |
| [**stripe-projects**](/docs/user-guide/skills/optional/payments/payments-stripe-projects) | 通过 Stripe Projects 部署 SaaS 服务并同步相关凭证。 |

## 生产力工具

| 功能 | 描述 |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | 通过 API 令牌获取 Canvas LMS 的课程与作业信息。 |
| [**decision-questionnaire**](/docs/user-guide/skills/optional/productivity/productivity-decision-questionnaire) | 将难以决策的问题转化为问卷文档。 |
| [**here-now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | 将网站发布到 &#123;slug&#125;.here.now 并将文件存储在 Drives 中。 |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 基于间隔重复法的抽认卡功能：可创建、复习、测试及导出卡片。 |
| [**property-listings**](/docs/user-guide/skills/optional/productivity/productivity-property-listings) | 以桌面卡片形式展示房产及租赁信息。 |
| [**shop**](/docs/user-guide/skills/optional/productivity/productivity-shop) | 支持商品目录搜索、结账、订单追踪及退货处理。 |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | 通过 curl 工具调用 Shopify 管理后台/店铺的 GraphQL API。 |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | 通过其 API 查询并编辑 SiYuan 知识库内容。 |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | 提供 Twilio 号码、短信/MMS 服务以及人工智能外呼功能。 |

## 研究

| Skill | Description |
|-------|-------------|
| [**bioinformatics**](/docs/user-guide/skills/optional/research/research-bioinformatics) | Gateway to 400+ genomics and computational biology skills. |
| [**blogwatcher**](/docs/user-guide/skills/optional/research/research-blogwatcher) | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| [**darwinian-evolver**](/docs/user-guide/skills/optional/research/research-darwinian-evolver) | Evolve prompts/regex/SQL/code with Imbue's evolution loop. |
| [**domain-intel**](/docs/user-guide/skills/optional/research/research-domain-intel) | Passive recon of subdomains, SSL certs, WHOIS, and DNS. |
| [**drug-discovery**](/docs/user-guide/skills/optional/research/research-drug-discovery) | Drug discovery: ChEMBL search, drug-likeness, interactions. |
| [**duckduckgo-search**](/docs/user-guide/skills/optional/research/research-duckduckgo-search) | Free keyless web, news, and image search via ddgs. |
| [**gitnexus-explorer**](/docs/user-guide/skills/optional/research/research-gitnexus-explorer) | Serve an interactive codebase knowledge graph web UI. |
| [**osint-investigation**](/docs/user-guide/skills/optional/research/research-osint-investigation) | Follow the money via public records and sanctions data. |
| [**parallel-cli**](/docs/user-guide/skills/optional/research/research-parallel-cli) | Agent-native web search, deep research, and enrichment. |
| [**pinecone-research**](/docs/user-guide/skills/optional/research/research-pinecone-research) | Agent RAG and long-term memory with Pinecone. |
| [**qmd**](/docs/user-guide/skills/optional/research/research-qmd) | Hybrid local search over notes, docs, and transcripts. |
| [**research-paper-writing**](/docs/user-guide/skills/optional/research/research-research-paper-writing) | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| [**rss-feeds**](/docs/user-guide/skills/optional/research/research-rss-feeds) | Read RSS, Atom, JSON feeds; discover feeds behind a page. |
| [**scrapling**](/docs/user-guide/skills/optional/research/research-scrapling) | Scrape sites with stealth browsing and Cloudflare bypass. |
| [**searxng-search**](/docs/user-guide/skills/optional/research/research-searxng-search) | Free keyless meta-search aggregating 70+ engines. |

## 安全防护

| 技能 | 描述 |
|-------|-------------|
| [**1password**](/docs/user-guide/skills/optional/security/security-1password) | 配置 op CLI，登录并读取或注入机密信息。 |
| [**godmode**](/docs/user-guide/skills/optional/security/security-godmode) | 解锁各类大型语言模型：Parseltongue、GODMODE、ULTRAPLINIAN。 |
| [**oss-forensics**](/docs/user-guide/skills/optional/security/security-oss-forensics) | GitHub 供应链分析：数据恢复、威胁指标识别及报告生成。 |
| [**sherlock**](/docs/user-guide/skills/optional/security/security-sherlock) | 在 400 多个平台上查找指定用户名对应的账户信息。 |
| [**unbroker**](/docs/user-guide/skills/optional/security/security-unbroker) | 自动将您的个人信息从数据交易网站上移除。 |
| [**web-pentest**](/docs/user-guide/skills/optional/security/security-web-pentest) | 经授权的网页安全测试：环境侦察、基于原理的漏洞利用及测试报告生成。 |

## 智能家居

| 技能 | 描述 |
|-------|-------------|
| [**openhue**](/docs/user-guide/skills/optional/smart-home/smart-home-openhue) | 通过 OpenHue CLI 控制 Philips Hue 灯具、场景及房间。 |

## 社交媒体

| 技能 | 描述 |
|-------|-------------|
| [**reddit-reading**](/docs/user-guide/skills/optional/social-media/social-media-reddit-reading) | 无需浏览器即可阅读 Reddit 内容，包括子版块、搜索结果、帖子及用户信息。 |

## 软件开发

| 技能 | 描述 |
|-------|-------------|
| [**ast-grep**](/docs/user-guide/skills/optional/software-development/software-development-ast-grep) | 利用 AST 功能实现基于结构化的代码搜索与重写。 |
| [**code-wiki**](/docs/user-guide/skills/optional/software-development/software-development-code-wiki) 为任意代码库生成维基文档及 Mermaid 图表。 |
| [**grill-me**](/docs/user-guide/skills/optional/software-development/software-development-grill-me) 在实现代码前进行对抗式方案面试。 |
| [**rest-graphql-debug**](/docs/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) 调试 REST/GraphQL API：状态码、身份认证、架构设计及问题复现。 |
| [**subagent-driven-development**](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) 通过 delegate_task 子代理执行方案（两阶段审核机制）。 |

## Web 开发

| 技能 | 描述 |
|-------|-------------|
| [**cloudflare-temporary-deploy**](/docs/user-guide/skills/optional/web-development/web-development-cloudflare-temporary-deploy) | 无需账号，即可通过 wrangler --temporary 功能实时部署 Worker。 |
| [**har-derived-api-client**](/docs/user-guide/skills/optional/web-development/web-development-har-derived-api-client) | 将网站的 XHR 请求记录为 HAR 文件，进而生成 HTTP 客户端。 |
| [**page-agent**](/docs/user-guide/skills/optional/web-development/web-development-page-agent) | 在网页应用中嵌入内置的自然语言 GUI 助手。 |
| [**publish-site**](/docs/user-guide/skills/optional/web-development/web-development-publish-site) | 将分版本管理的网站部署到 GitHub/Cloudflare/Netlify Pages 上。 |

## yuanbao

| 技能 | 描述 |
|-------|-------------|
| [**yuanbao**](/docs/user-guide/skills/optional/yuanbao/yuanbao-yuanbao) | Yuanbao（元宝）相关功能：@提及用户，查询信息或成员列表。 |

---

## 贡献可选技能

若要向该仓库添加新的可选技能：

1. 在 `optional-skills/<类别>/<技能名称>/` 下创建目录；
2. 添加包含标准 frontmatter 信息的 `SKILL.md` 文件（包括名称、描述、版本及作者信息）；
3. 将相关辅助文件放入 `references/`、`templates/` 或 `scripts/` 子目录中；
4. 提交 Pull Request——该技能将在合并后被收录至此目录，并拥有独立的文档页面。
