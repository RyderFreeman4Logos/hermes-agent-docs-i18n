---
sidebar_position: 9
title: "Optional Skills Catalog"
description: "Official optional skills shipped with hermes-agent — install via hermes skills install official/<category>/<skill>"
---

# 可选技能目录

Hermes Agent 自带位于 `optional-skills/` 目录下的可选技能，但这些技能**默认处于关闭状态**。如需使用，需手动进行安装：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

以下列出的每项技能均对应一个专门页面，其中详细介绍了其定义、配置方法及使用方式。

如需卸载：

```bash
hermes skills uninstall <skill-name>
```

## autonomous-ai-agents

| 技能 | 描述 |
|-------|-------------|
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | 操作 Antigravity CLI（agy）：插件、认证与沙箱功能。 |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编程任务委托给 Blackbox AI CLI 智能体。该多模型智能体内置评估器，可让多个大语言模型处理任务并选出最佳结果。需要使用 blackbox CLI 以及 Blackbox AI API 密钥。 |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | 将编程任务委托给 xAI Grok Build CLI（用于功能开发与代码提交）。 |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 配置并使用 Hermes 的 Honcho 内存功能——实现跨会话用户建模、多配置文件隔离、观察配置、辩证推理、会话总结以及上下文预算管控。在设置 Honcho 或进行故障排查时使用。 |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | 将编程任务委托给 OpenHands CLI（支持多种模型，基于 LiteLLM）。 |

## blockchain

| 技能 | 描述 |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | 仅读型 EVM 客户端：可查询 8 条区块链上的钱包信息、代币数据及燃气费用。 |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | 提供 Hyperliquid 市场数据、账户历史记录及交易审核功能。 |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | 可查询 Solana 区块链数据，并以美元标价显示——包括钱包余额、带价值标签的代币组合、交易详情、NFT 信息、大额交易检测以及实时网络统计数据。该功能基于 Solana RPC 与 CoinGecko 数据源，无需 API 密钥。 |

## communication

| 技能 | 描述 |
|-------|-------------|
| [**one-three-one-rule**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | 一种用于技术方案制定与权衡分析的结构化决策框架。当用户需要在多种方案（架构决策、工具选择、重构策略、迁移路径等）之间做出抉择时，该技能可帮助... |

## creative

| 技能 | 描述 |
|-------|-------------|
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | 用于文章插图制作：确保类型、风格与色彩方案的一致性。 |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | 制作知识漫画：适用于教育、传记及教程类内容。 |
| [**blender-mcp**](/docs/user-guide/skills/optional/creative/creative-blender-mcp) | 通过连接到 blender-mcp 插件，可直接从 Hermes 控制 Blender。可创建 3D 对象、材质与动画，还能运行任意的 Blender Python（bpy）代码。适用于需要在 Blender 中创建或修改内容的用户。 |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | 能生成扁平化、极简风格的 SVG 图表，支持明暗模式，以独立 HTML 文件形式输出。该工具采用统一的教育可视化语言，包含 9 种语义色彩渐变、标题大小写一致的排版以及自动暗色模式功能，非常适合用于教育类内容... |
| [**creative-ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | 通过基于创意实践的特定方法来生成创意点子。 |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | 可使用 HyperFrames 创建基于 HTML 的视频合成内容，包括动画标题卡、社交平台用叠加画面、带字幕的出镜视频、随音频变化的视觉效果以及着色器过渡效果。视频的所有内容都以 HTML 为基准格式，适用于需要创建此类视频的用户。 |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | 基于 Hermes Kanban 平台，可规划、搭建并监控多智能体视频制作流程。适用于需要制作各类视频的用户——无论是叙事电影、产品/营销视频、音乐视频、解说视频，还是 ASCII/终端艺术、抽象/生成式内容... |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | 可通过选择模板并使用 Pillow 工具添加文字，从而生成真实的迷因图片，最终输出 .png 格式的迷因文件。 |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | 支持使用不同时代风格的色彩方案（如 NES、Game Boy、PICO-8 风格）制作像素艺术。 |

## devops

| 技能 | 描述 |
|-------|-------------|
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-cli) | 可通过 inference.sh CLI（infsh）运行 150 多种 AI 应用——包括图像生成、视频制作、大语言模型应用、搜索功能、3D 处理以及社交自动化任务。该工具基于终端界面，相关触发词包括：inference.sh、infsh、AI 应用、flux、veo、图像生成、视频生成、seedrea... |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | 可对 Docker 容器、镜像、卷、网络以及 Compose 配置文件进行管理——包括生命周期操作、故障排查、清理工作以及 Dockerfile 优化。 |
| [**hermes-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-hermes-s6-container-supervision) | 可修改、调试或扩展 Hermes Agent Docker 镜像中的 s6-overlay 监控结构——可添加新服务、调试配置文件网关，同时深入理解 Architecture B 主程序架构模式。 |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | 可通过 Pinggy 工具在本地实现无需安装的 SSH 隧道连接。 |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | 可轮询 RSS、JSON API 以及 GitHub 数据，并自动去除重复内容。 |

## dogfood

| 技能 | 描述 |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 模拟最难缠、对技术最不熟悉的用户来测试产品。以该类用户的视角浏览应用，找出所有用户体验痛点，再通过实用主义层面对反馈进行筛选，从而区分真正的问题与无意义的声音。最终可生成可操作的改进清单... |

## email

| 技能 | 描述 |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | 可通过 AgentMail 为智能体配置专属的电子邮件收件箱。智能体可使用自己拥有的邮箱地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理邮件。 |

## finance

| 技能 | 描述 |
|-------|-------------|
| [**3-statement-model**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | 可在 Excel 中构建功能完备的三表模型（损益表、资产负债表、现金流量表），并包含营运资金计划、折旧摊销递推计算、债务还款计划，以及连接现金与留存收益的各项公式。该技能可与 excel-author 工具搭配使用。 |
| [**comps-analysis**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | 可在 Excel 中构建可比公司分析模型——包括运营指标、估值倍数，以及针对同行群体的统计对比分析。该技能同样可与 excel-author 工具配合使用，适用于上市公司估值、首次公开募股定价、行业基准分析或异常值检测等场景。 |
| [**dcf-model**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | 可在 Excel 中构建专业级的现金流折现估值模型——包括收入预测、自由现金流计算、加权平均资本成本估算、终值计算，以及熊市/基准/牛市情景分析、5×5 敏感性分析表等。该技能可与 excel-author 工具搭配使用，适用于股票内在价值分析。 |
| [**excel-author**](/docs/user-guide/skills/optional/finance/finance-excel-author) | 可使用 openpyxl 在无界面模式下构建可审计的 Excel 工作簿——支持蓝/黑/绿三种颜色标识单元格、用公式替代硬编码值、定义名称范围、进行余额校验以及生成敏感性分析表。该工具适用于财务模型、审计输出文件及对账工作。 |
| [**lbo-model**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | 可在 Excel 中构建杠杆收购模型——包括资金来源与用途分析、债务还款计划、现金流转分析、退出倍数计算，以及内部收益率/投资回收期敏感性分析。该技能可与 excel-author 工具搭配使用，适用于私募股权项目筛选、投资方案例估值，或演示用杠杆收购分析模型。 |
| [**merger-model**](/docs/user-guide/skills/optional/finance/finance-merger-model) | 可在 Excel 中构建并购带来的价值增值/稀释分析模型——包括合并后的损益表预测、协同效应分析、融资结构设计以及每股收益影响分析。该技能可与 excel-author 工具搭配使用，适用于并购项目演示、董事会汇报材料或交易估值分析。 |
| [**pptx-author**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | 可使用 python-pptx 在无界面模式下创建 PowerPoint 演示文稿。该工具可与 excel-author 工具结合使用，确保演示文稿中的所有数据都能追溯到对应的 Excel 单元格，适用于项目演示、投资委员会备忘录及业绩通报等场景。 |
| [**stocks**](/docs/user-guide/skills/optional/finance/finance-stocks) | 可通过 Yahoo 提供的功能获取股票行情、历史数据、搜索功能、对比分析以及加密货币相关信息。 |

## gaming

| 技能 | 描述 |
|-------|-------------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | 可托管经过修改的 Minecraft 服务器（支持 CurseForge、Modrinth 平台）。 |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | 可通过无界面模拟器结合内存读取功能来游玩《宝可梦》游戏。 |

## health

| 技能 | 描述 |
|-------|-------------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | 提供健身计划制定与营养追踪功能。可通过 wger 工具按肌肉群、训练设备或类别搜索 690 多种锻炼动作；还可通过 USDA FoodData Central 数据库查询 38 万多种食物的营养成分与热量信息。该工具可帮助计算 BMI、每日总能量消耗、一次最大力量值、营养素分配比例以及身体各项指标... |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | 可连接正在运行的 NeuroSkill 实例，将用户的实时认知与情绪状态（包括专注度、放松程度、情绪状态、认知负荷、困倦程度、心率、心率变异性、睡眠阶段以及 40 多种基于肌电信号的衍生指标）融入智能体的响应中... |

## mcp

| 技能 | 描述 |
|-------|-------------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | 可使用 Python 的 FastMCP 工具来构建、测试、检查、安装及部署 MCP 服务器。适用于需要创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示词，或是为 Claude Code、Cur... 等平台准备 FastMCP 服务器的场景。 |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | 可使用 mcporter CLI 直接列出、配置、认证并调用 MCP 服务器/工具（支持 HTTP 或标准输入方式），包括临时搭建的服务器、配置文件编辑以及 CLI/类型生成功能。 |

## migration

| 技能 | 描述 |
|-------|-------------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | 可将用户的 OpenClaw 定制配置迁移至 Hermes Agent 中。该功能可从 ~/.openclaw 文件中导入与 Hermes 兼容的记忆数据、SOUL.md 配置文件、命令允许列表、用户技能以及选定的工作区资产，随后会详细列出所有无法迁移的内容... |

## mlops| 技能 | 描述 |
|-------|-------------|
| [**huggingface-accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | 最简单的分布式训练API。仅需4行代码即可为任何PyTorch脚本添加分布式支持，同时兼容DeepSpeed/FSDP/Megatron/DDP等多种框架。具备自动设备分配、混合精度计算（FP16/BF16/FP8）功能，支持交互式配置，可通过单次启动完成训练…… |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl：基于YAML的LLM微调工具，支持LoRA、DPO、GRPO等微调方法。 |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | 专为AI应用设计的开源嵌入数据库，可用于存储嵌入向量及元数据，支持向量搜索与全文检索，并能根据元数据进行过滤。拥有简洁的4功能API，可从笔记本环境扩展至生产级集群，适用于语义搜索、RAG等场景…… |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | OpenAI开发的连接视觉与语言的模型，可实现零样本图像分类、图像文本匹配以及跨模态检索功能，已基于4亿组图像文本对进行训练。可用于图像搜索、内容审核或视觉语言相关任务…… |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy：声明式LLM编程工具，可自动优化提示词，并支持RAG功能。 |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Facebook开发的用于高效处理密集向量相似性搜索与聚类的库，可支持数十亿级向量处理，具备GPU加速能力，还提供Flat、IVF、HNSW等多种索引类型。适用于快速k-NN搜索、大规模向量检索等场景…… |
| [**optimizing-attention-flash**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | 通过Flash Attention技术优化Transformer模型的注意力机制，可使训练速度提升2-4倍，同时内存占用降低10-20倍。适用于处理长度超过512个token的序列、遇到注意力机制相关的GPU内存问题，或需要更快推理速度的场景…… |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | 基于Microsoft Research开发的约束生成框架Guidance，可通过正则表达式与语法控制LLM的输出，确保生成的JSON/XML/代码格式正确，强制要求结构化输出，还能用于构建多步骤工作流…… |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | 为研究与生产环境优化的快速分词器，基于Rust实现，可在20秒内完成1GB文本的分词处理。支持BPE、WordPiece、Unigram等多种分词算法，可用于训练自定义词汇表、跟踪文本对齐情况，以及处理填充与截断操作，具备良好的集成性…… |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | 基于经过实战检验的结构化输出库Instructor，可通过Pydantic验证从LLM响应中提取结构化数据，自动重试失败的提取操作，以类型安全的方式解析复杂JSON，还能按需流式返回部分处理结果…… |
| [**lambda-labs-gpu-cloud**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | 专为机器学习训练与推理提供的预留型及按需型GPU云实例，适用于需要具备简单SSH访问权限的专用GPU实例、持久化文件系统，或用于大规模训练的高性能多节点集群场景…… |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | 大语言与视觉助手模型，支持基于视觉的指令微调以及图像驱动的对话功能。它将CLIP视觉编码器与Vicuna/LLaMA语言模型相结合，可支持多轮图像聊天、视觉问答以及指令遵循等任务…… |
| [**modal-serverless-gpu**](/docs/user-guide/skills/optional/mlops/mlops-modal) | 用于运行机器学习工作负载的无服务器GPU云平台，适用于无需自行管理基础设施即可按需使用GPU的场景，也可用于将机器学习模型部署为API，或运行具备自动扩展功能的批处理作业…… |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | 专为LLM训练设计的GPU加速数据筛选工具，支持文本、图像、视频、音频等多种数据类型。具备模糊去重功能（速度提升16倍）、质量过滤功能（基于30多种规则）、语义去重功能、个人身份信息遮蔽功能以及不适宜内容检测功能，可跨多台GPU扩展使用…… |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS：通过差分均值技术消除LLM的拒绝回应现象。 |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines：支持生成结构化的JSON/正则表达式/Pydantic格式的LLM输出内容。 |
| [**peft-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-peft) | 基于LoRA、QLoRA以及25种以上方法实现的参数高效型LLM微调技术，适用于在GPU内存有限的条件下微调70亿参数量级的大型模型，可在几乎不损失准确率的前提下仅训练不到1%的模型参数，也支持多适配器微调场景…… |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | 专为生产级AI应用设计的托管型向量数据库，具备完全托管、自动扩展功能，支持密集向量与稀疏向量的混合搜索、元数据过滤以及命名空间管理功能，查询延迟低于100毫秒（p95值）。适用于生产环境中的RAG系统、推荐系统等场景…… |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | 提供针对PyTorch FSDP全分片数据并行训练的专业指导，涵盖参数分片、混合精度计算、CPU卸载以及FSDP2等相关技术内容。 |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | 基于PyTorch开发的高级框架，拥有Trainer类、自动分布式训练功能（支持DDP/FSDP/DeepSpeed）、回调系统，且代码实现极为简洁。使用同一份代码即可在从笔记本电脑到超级计算机的不同硬件环境中进行训练，适用于需要简洁训练逻辑的场景…… |
| [**qdrant-vector-search**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | 高性能向量相似性搜索引擎，专为RAG与语义搜索场景设计。适用于构建需要快速最近邻搜索、支持带过滤条件的混合搜索功能，或需要具备可扩展向量存储能力的生产级系统，该引擎基于Rust语言实现…… |
| [**sparse-autoencoder-training**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | 提供基于SAELens工具的稀疏自编码器（SAE）训练与分析指导，该工具可将神经网络激活值分解为可解释的特征。适用于发现可解释的特征、分析特征叠加效应，或开展相关研究工作…… |
| [**simpo-training**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | 一种简单的LLM对齐偏好优化方法，是无需参考模型的DPO替代方案，性能更优（在AlpacaEval 2.0测试中得分高出6.4分）。无需参考模型，效率也高于DPO，适用于需要简化对齐流程的场景…… |
| [**slime-rl-training**](/docs/user-guide/skills/optional/mlops/mlops-slime) | 基于Megatron+SGLang框架slime为LLM训练后的强化学习阶段提供指导，适用于训练GLM模型、实现自定义数据生成工作流，或需要深度整合Megatron-LM框架以实现强化学习性能提升的场景…… |
| [**stable-diffusion-image-generation**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | 基于HuggingFace Diffusers库的先进文本到图像生成技术，可通过文本提示词生成图像，实现图像到图像的转换、图像修复功能，也可用于构建自定义的扩散模型工作流…… |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | 利用NVIDIA TensorRT优化LLM推理流程，可实现最高吞吐量与最低延迟。适用于在NVIDIA GPU（A100/H100）上开展生产环境部署，当需要比使用PyTorch快10-100倍的推理速度，或需要对模型进行量化处理以实现高效服务时，该工具非常适用…… |
| [**distributed-llm-pretraining-torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | 提供基于PyTorch的原生分布式LLM预训练功能，采用torchtitan框架以及4D并行技术（包括FSDP2、TP、PP、CP），可在8到512台及以上GPU上，使用Float8精度、torch.compile优化技术以及分布式训练功能，大规模预训练Llama 3.1、DeepSeek V3或自定义模型…… |
| [**fine-tuning-with-trl**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL系列方法：包括SFT、DPO、PPO、GRPO以及用于LLM强化学习对齐的奖励建模技术。 |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth：可让LoRA/QLoRA微调速度提升2-5倍，同时减少所需的VRAM内存用量。 |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI开发的通用语音识别模型，支持99种语言的识别功能，可完成文本转写、英语翻译以及语言识别任务。提供从小型模型（3900万参数）到大型模型（15.5亿参数）共六种版本，适用于语音转文本、播客处理等场景…… |

## 支付相关

| 技能 | 描述 |
|-------|-------------|
| [**mpp-agent**](/docs/user-guide/skills/optional/payments/payments-mpp-agent) | 通过机器支付协议（MPP）调用返回HTTP 402状态码的API接口完成支付操作。 |
| [**stripe-link-cli**](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli) | 通过Stripe Link实现代理支付功能，支持信用卡、SPT支付方式以及支付审批流程。 |
| [**stripe-projects**](/docs/user-guide/skills/optional/payments/payments-stripe-projects) | 通过Stripe Projects功能配置SaaS服务，并同步相关认证信息。 |

## 生产力提升工具

| 技能 | 描述 |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | Canvas学习管理系统集成工具，可通过API令牌认证获取已注册的课程与作业信息。 |
| [**here.now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | 可将静态网站发布到&#123;slug&#125;.here.now地址，同时可将私有文件存储在云盘服务中，便于不同代理之间传递文件。 |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 基于间隔重复算法的闪卡系统，用户可从事实或文本中创建闪卡，可通过自由文本形式与闪卡进行互动，系统会由代理对回答进行评分，还能从YouTube视频字幕中生成测验题，具备自适应排程功能可提醒用户复习到期的闪卡，同时支持闪卡的导出与导入操作…… |
| [**shop**](/docs/user-guide/skills/optional/productivity/productivity-shop) | 提供商品目录搜索、结账、订单追踪以及退货处理等功能。 |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | 通过curl命令调用Shopify的管理后台与前端店铺GraphQL API，可获取产品、订单、客户、库存以及元字段等相关数据。 |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | SiYuan笔记API，支持通过curl命令对自托管知识库中的块状内容与文档进行搜索、阅读、创建及管理操作。 |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | 无需修改核心工具即可为Hermes添加电话功能，可配置并保留Twilio号码，支持发送和接收短信/MMS消息，可进行直接通话，还能通过Bland.ai或Vapi平台发起基于人工智能的呼出电话…… |

## 研究领域相关工具| 技能 | 描述 |
|-------|-------------|
| [**生物信息学**](/docs/user-guide/skills/optional/research/research-bioinformatics) | 提供来自 bioSkills 与 ClawBio 的 400 多种生物信息学技能的访问入口。涵盖基因组学、转录组学、单细胞分析、变异检测、药物基因组学、宏基因组学、结构生物学等领域，还能获取相关领域的专用参考资料…… |
| [**达尔文进化器**](/docs/user-guide/skills/optional/research/research-darwinian-evolver) | 利用 Imbue 的进化循环功能，对提示词、正则表达式、SQL 代码等进行优化演化。 |
| [**领域情报收集**](/docs/user-guide/skills/optional/research/research-domain-intel) | 基于 Python 标准库实现被动式的领域侦察功能，可执行子域名发现、SSL 证书检测、WHOIS 查询、DNS 记录查看、域名可用性检查以及批量多域名分析，无需 API 密钥。 |
| [**药物发现**](/docs/user-guide/skills/optional/research/research-drug-discovery) | 专为药物发现工作流程设计的辅助工具，可在 ChEMBL 中搜索生物活性化合物，计算药物的相似度（如 Lipinski Ro5、QED、TPSA、合成可及性），通过 OpenFDA 查询药物相互作用信息，还能解读 ADMET 参数…… |
| [**DuckDuckGo 搜索**](/docs/user-guide/skills/optional/research/research-duckduckgo-search) | 通过 DuckDuckGo 进行免费网络搜索——支持文本、新闻、图片和视频内容检索，无需 API 密钥。建议在安装了 `ddgs` CLI 后优先使用该工具；只有在确认当前运行环境中可用时，才可使用 Python 版的 DDGS 库。 |
| [**GitNexus 浏览器**](/docs/user-guide/skills/optional/research/research-gitnexus-explorer) | 利用 GitNexus 对代码库进行索引，并通过网页界面及 Cloudflare 隧道提供交互式知识图谱服务。 |
| [**开源情报调查**](/docs/user-guide/skills/optional/research/research-osint-investigation) | 用于公开记录类开源情报调查的框架，可查询 SEC EDGAR 提交信息、USAspending 合同数据、参议院游说活动、OFAC 制裁信息、ICIJ 海外泄密数据、纽约市房产记录（ACRIS）、OpenCorporates 公司注册信息、CourtListener 法院记录以及网页历史版本…… |
| [**Parallel CLI**](/docs/user-guide/skills/optional/research/research-parallel-cli) | Parallel CLI 提供的可选供应商技能，具备原生代理式网络搜索、数据提取、深度研究、信息丰富化、FindAll 搜索及监控功能，推荐使用 JSON 格式输出以及非交互式操作流程。 |
| [**qmd**](/docs/user-guide/skills/optional/research/research-qmd) | 使用 qmd 在本地搜索个人知识库、笔记、文档以及会议记录——这是一种融合了 BM25、向量搜索和大型语言模型重排技术的混合检索引擎，同时支持 CLI 与 MCP 集成。 |
| [**网络爬虫**](/docs/user-guide/skills/optional/research/research-scraping) | 利用 Scrapling 工具进行网络爬取，可通过 CLI 或 Python 实现 HTTP 请求、隐蔽浏览器自动化操作、Cloudflare 反爬绕过以及蜘蛛爬行等功能。 |
| [**SearXNG 搜索**](/docs/user-guide/skills/optional/research/research-searxng-search) | 通过 SearXNG 实现免费元搜索，可聚合来自 70 多个搜索引擎的结果。支持自行托管或使用公共实例，无需 API 密钥；当常规网络搜索工具不可用时，会自动切换到该方案。 |

## 安全领域

| 技能 | 描述 |
|-------|-------------|
| [**1Password**](/docs/user-guide/skills/optional/security/security-1password) | 设置并使用 1Password CLI（可选功能）。可在安装 CLI、启用桌面应用集成、登录操作，以及为命令读取/注入机密信息时使用该工具。 |
| [**神模式**](/docs/user-guide/skills/optional/security/security-godmode) | 用于破解大型语言模型的限制功能，包括 Parseltongue、GODMODE、ULTRAPLINIAN 等。 |
| [**OSS 取证分析**](/docs/user-guide/skills/optional/security/security-oss-forensics) | 针对 GitHub 代码库的供应链调查、证据恢复及取证分析功能，可恢复已删除的提交记录、检测强制推送行为、提取威胁指标、收集多源证据、形成/验证假设，还可执行其他相关操作…… |
| [**Sherlock**](/docs/user-guide/skills/optional/security/security-sherlock) | 能在 400 多个社交网络中搜索用户名，可根据用户名定位社交媒体账号。 |
| [**网页渗透测试**](/docs/user-guide/skills/optional/security/security-web-pentest) | 提供授权范围内的网页应用渗透测试服务，包括侦察、漏洞分析、基于证据的利用测试以及专业报告生成。该服务采用了 Shannon 的“无利用则无报告”方法论，并设置了严格的范围控制与授权机制…… |

## 软件开发领域

| 技能 | 描述 |
|-------|-------------|
| [**代码维基**](/docs/user-guide/skills/optional/software-development/software-development-code-wiki) | 为任意代码库自动生成维基文档及 Mermaid 图表。 |
| [**REST/GraphQL 调试**](/docs/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) | 用于调试 REST/GraphQL API，可查看状态码、认证机制、架构信息以及问题复现步骤。 |
| [**子代理驱动开发**](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) | 通过 delegate_task 子代理来执行计划，支持两阶段审核流程。 |

## 网页开发领域

| 技能 | 描述 |
|-------|-------------|
| [**Page Agent**](/docs/user-guide/skills/optional/web-development/web-development-page-agent) | 可将 alibaba/page-Agent 集成到自定义网页应用中——这是一种纯 JavaScript 实现的页面内 GUI 代理，以单个 `<script>` 标签或 npm 包的形式提供，允许网站最终用户使用自然语言控制界面（例如“点击登录按钮，填写用户名……”）。 |

---

## 贡献可选技能

若要向该仓库添加新的可选技能，请按以下步骤操作：

1. 在 `optional-skills/<类别>/<技能名称>/` 下创建一个目录。
2. 添加一份包含标准前端信息的 `SKILL.md` 文件，需注明技能名称、描述、版本信息及作者。
3. 将相关辅助文件放入 `references/`、`templates/` 或 `scripts/` 子目录中。
4. 提交 Pull Request——该技能一旦被合并，就会出现在此技能列表中，并拥有独立的文档页面。
