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
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | 操作 Antigravity CLI (agy)：插件、认证与沙箱功能。 |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编程任务委托给 Blackbox AI CLI 智能体。该多模型智能体内置评估器，可让多个大语言模型处理任务并选出最佳结果。需要使用 blackbox CLI 以及 Blackbox AI API 密钥。 |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | 将编程任务委托给 xAI Grok Build CLI（用于功能开发与代码提交）。 |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 配置并使用 Hermes 的 Honcho 记忆系统——实现跨会话用户建模、多配置文件隔离、观察配置、辩证推理、会话总结以及上下文预算管控。在设置 Honcho 或进行故障排查时使用。 |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | 将编程任务委托给 OpenHands CLI（支持多种模型，兼容 LiteLLM）。 |

## blockchain

| 技能 | 描述 |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | 仅读型 EVM 客户端：可查询 8 条区块链上的钱包信息、代币数据及 Gas 费用。 |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | 提供 Hyperliquid 市场数据、账户历史记录及交易分析功能。 |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | 可查询 Solana 区块链数据，并以美元为单位显示数值——包括钱包余额、带价值标签的代币组合、交易详情、NFT 信息、大额交易检测以及实时网络状态。基于 Solana RPC 与 CoinGecko 数据源，无需 API 密钥。 |

## communication

| 技能 | 描述 |
|-------|-------------|
| [**one-three-one-rule**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | 一种用于技术方案制定与权衡分析的结构化决策框架。当用户需要在多种方案（架构选择、工具挑选、重构策略、迁移路径等）之间做决策时，该技能可帮助... |

## creative

| 技能 | 描述 |
|-------|-------------|
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | 用于文章插图制作：确保类型、风格与色彩方案的一致性。 |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | 制作知识漫画：可用于教育、人物传记或教程类内容。 |
| [**blender-mcp**](/docs/user-guide/skills/optional/creative/creative-blender-mcp) | 通过连接到 blender-mcp 插件，可直接从 Hermes 控制 Blender。可创建 3D 对象、材质与动画，还能运行任意的 Blender Python (bpy) 代码。适用于需要在 Blender 中创建或修改内容的场景。 |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | 能生成简洁的、支持明暗效果的 SVG 图表，并以独立 HTML 文件形式输出。采用统一的教育类视觉语言，包含 9 种语义化颜色渐变、规范的大小写排版以及自动暗色模式。非常适合用于教育场景... |
| [**ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | 根据特定创意约束条件生成项目创意。 |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | 使用 HyperFrames 创建基于 HTML 的视频合成内容，包括动画标题卡、社交平台用叠加元素、带字幕的出镜视频、音频响应式视觉效果以及着色器过渡动画。视频的所有内容都以 HTML 为基准。适用于需要创建此类视频的用户... |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | 基于 Hermes Kanban 系统规划、搭建并监控多智能体视频制作流程。无论是要制作叙事电影、产品/营销视频、音乐视频、说明视频，还是 ASCII/终端艺术、抽象/生成式内容，均可使用该工具。 |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | 通过选择模板并使用 Pillow 工具叠加文字，即可生成真实的迷因图片。可输出真正的 .png 格式迷因文件。 |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | 支持使用不同时代风格的色彩方案（NES、Game Boy、PICO-8）制作像素艺术。 |

## devops

| 技能 | 描述 |
|-------|-------------|
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-cli) | 通过 inference.sh CLI (infsh) 运行 150 多种 AI 应用——包括图像生成、视频制作、大语言模型应用、搜索功能、3D 处理以及社交自动化任务。基于终端工具实现，相关触发词包括：inference.sh、infsh、AI 应用、flux、veo、图像生成、视频生成、seedrea 等。 |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | 可对 Docker 容器、镜像、卷、网络以及 Compose 配置文件进行管理——包括生命周期操作、故障排查、清理工作以及 Dockerfile 优化。 |
| [**hermes-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-hermes-s6-container-supervision) | 能够修改、调试或扩展 Hermes Agent Docker 镜像内的 s6-overlay 监控结构——可添加新服务、调试配置文件网关，进而深入理解 Architecture B 主程序架构模式。 |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | 通过 Pinggy 工具实现无需安装即可在本地通过 SSH 建立隧道。 |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | 可轮询 RSS、JSON API 以及 GitHub 数据，并自动去除重复内容。 |

## dogfood

| 技能 | 描述 |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 模拟最难缠、对技术最不熟悉的用户来测试产品。以该类用户的视角浏览应用，找出所有用户体验痛点，再通过务实性分析筛选出真正的问题，剔除无关噪音。可生成可执行的改进清单... |

## email

| 技能 | 描述 |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | 通过 AgentMail 为智能体配置专属的电子邮件收件箱。智能体可使用自己的邮箱地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理邮件。 |

## finance

| 技能 | 描述 |
|-------|-------------|
| [**3-statement-model**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | 可在 Excel 中构建功能完备的三表模型（损益表、资产负债表、现金流量表），包含营运资金计划、折旧摊销递推计算、债务偿还计划，以及实现现金与留存收益关联的公式。需与 excel-author 工具配合使用。 |
| [**comps-analysis**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | 能在 Excel 中完成可比公司分析——包括运营指标、估值倍数以及针对同行群体的统计基准对比。需与 excel-author 工具配合使用，适用于上市公司估值、首次公开募股定价、行业基准分析或异常值检测等场景。 |
| [**dcf-model**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | 可在 Excel 中构建专业级的现金流折现估值模型——包括收入预测、自由现金流计算、加权平均资本成本、终值估算，以及熊市/基准/牛市情景分析、5x5 敏感性分析表。需与 excel-author 工具配合使用，用于股票内在价值分析。 |
| [**excel-author**](/docs/user-guide/skills/optional/finance/finance-excel-author) | 能够使用 openpyxl 在无界面模式下构建可审计的 Excel 工作簿——支持蓝色/黑色/绿色单元格规范、公式替代硬编码值、命名范围设置、余额校验以及敏感性分析表等功能。适用于财务模型、审计输出文件及对账工作。 |
| [**lbo-model**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | 可在 Excel 中构建杠杆收购模型——包括资金来源与用途、债务偿还计划、现金流转分析、退出倍数计算，以及 IRR/MOIC 敏感性分析。需与 excel-author 工具配合使用，适用于私募股权项目筛选、投资方案例估值或演示用杠杆收购分析。 |
| [**merger-model**](/docs/user-guide/skills/optional/finance/finance-merger-model) | 可在 Excel 中构建并购带来的价值增值/稀释模型——包括合并后的损益表、协同效应分析、融资结构以及每股收益影响测算。需与 excel-author 工具配合使用，适用于并购项目演示、董事会材料准备或交易估值分析。 |
| [**pptx-author**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | 可使用 python-pptx 在无界面模式下创建 PowerPoint 演示文稿。可与 excel-author 工具结合使用，打造每一项数据都能追溯到对应工作表单元格的模型驱动型演示文稿，适用于项目推介、投资委员会备忘录及业绩公告等场景。 |
| [**stocks**](/docs/user-guide/skills/optional/finance/finance-stocks) | 可通过 Yahoo 提供的股票服务获取行情数据、历史记录、搜索功能、对比分析以及加密货币相关信息。 |

## gaming

| 技能 | 描述 |
|-------|-------------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | 可托管经过修改的 Minecraft 服务器（支持 CurseForge、Modrinth 平台）。 |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | 通过无界面模拟器结合内存读取功能来游玩《宝可梦》游戏。 |

## health

| 技能 | 描述 |
|-------|-------------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | 提供健身计划制定与营养追踪功能。可通过 wger 工具按肌肉群、训练设备或类别搜索 690 多种锻炼动作；还能通过 USDA FoodData Central 数据库查询 38 万多种食物的营养成分与热量信息。可计算 BMI、每日总能量消耗、一次最大力量值、营养素分配比例以及身体相关指标... |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | 能连接正在运行的 NeuroSkill 实例，将用户的实时认知与情绪状态（专注度、放松程度、情绪状态、认知负荷、困倦程度、心率、心率变异性、睡眠阶段以及 40 多种基于肌电信号的衍生评分）纳入智能体的响应逻辑中... |

## mcp

| 技能 | 描述 |
|-------|-------------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | 可使用 Python 的 FastMCP 工具构建、测试、检查、安装及部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示词，或是为 Claude Code、Cur 等平台准备 FastMCP 服务器。 |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | 可通过 mcporter CLI 直接列出、配置、认证并调用 MCP 服务器/工具（支持 HTTP 或标准输入输出方式），包括临时搭建的服务器、配置文件编辑以及 CLI/类型生成功能。 |

## migration

| 技能 | 描述 |
|-------|-------------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | 可将用户的 OpenClaw 定制配置迁移至 Hermes Agent 中。该工具能够从 ~/.openclaw 文件中导入与 Hermes 兼容的记忆数据、SOUL.md 配置文件、命令允许列表、用户技能以及选定的工作区资产，随后会明确列出所有无法迁移的内容... |

## mlops| 技能 | 描述 |
|-------|-------------|
| [**huggingface-accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | 最简单的分布式训练API。仅需4行代码即可为任何PyTorch脚本添加分布式支持，同时兼容DeepSpeed/FSDP/Megatron/DDP等多种框架。具备自动设备分配、混合精度计算（FP16/BF16/FP8）功能，支持交互式配置，可通过单次启动完成训练…… |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl：基于YAML的LLM微调工具，支持LoRA、DPO、GRPO等多种微调方法。 |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | 专为AI应用设计的开源嵌入数据库。可存储嵌入向量及元数据，支持向量和全文搜索，还能根据元数据进行过滤。拥有简洁的4功能API，可从笔记本环境扩展到生产级集群，适用于语义搜索、RAG等场景…… |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | OpenAI开发的连接视觉与语言的模型，可实现零样本图像分类、图像文本匹配以及跨模态检索功能。该模型基于4亿对图像文本数据训练而成，可用于图像搜索、内容审核或视觉语言相关任务…… |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy：声明式LM编程工具，可自动优化提示词，并支持RAG功能。 |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Facebook开发的用于高效处理密集向量相似性搜索与聚类的库，可支持数十亿级向量数据，具备GPU加速功能，还提供Flat、IVF、HNSW等多种索引类型。适用于快速k-NN搜索、大规模向量检索等场景…… |
| [**optimizing-attention-flash**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | 通过Flash Attention技术优化Transformer模型的注意力机制，可实现2-4倍的加速效果，同时降低10-20倍的内存占用。适用于训练/运行包含长序列（>512个标记）的Transformer模型、遇到注意力机制相关的GPU内存问题，或需要更快推理速度的场景…… |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | 基于Microsoft Research开发的约束生成框架Guidance，可通过正则表达式和语法控制LLM的输出，确保生成的JSON/XML/代码格式合法，强制遵循结构化格式，还可构建多步骤工作流…… |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | 专为研究和生产环境优化的快速分词器，基于Rust实现，可在20秒内完成1GB文本的分词任务。支持BPE、WordPiece和Unigram等多种分词算法，可训练自定义词汇表，跟踪序列对齐情况，处理填充与截断操作，还具备集成功能…… |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | 经过实战检验的结构化输出库Instructor，可通过Pydantic验证从LLM响应中提取结构化数据，自动重试失败的提取操作，以类型安全的方式解析复杂的JSON数据，还能按需流式返回部分结果…… |
| [**lambda-labs-gpu-cloud**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | 专为机器学习训练和推理提供的预留型及按需型GPU云实例，当您需要具备简单SSH访问功能的专用GPU实例、持久化文件系统，或用于大规模训练的高性能多节点集群时，可选用此服务…… |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | 大语言与视觉助手，支持视觉指令微调及基于图像的对话功能。该模型将CLIP视觉编码器与Vicuna/LLaMA语言模型相结合，可支持多轮图像聊天、视觉问答以及指令遵循等任务…… |
| [**modal-serverless-gpu**](/docs/user-guide/skills/optional/mlops/mlops-modal) | 用于运行机器学习工作负载的无服务器GPU云平台，当您需要无需管理基础设施即可按需使用GPU资源、将机器学习模型作为API部署，或运行具备自动扩展功能的批处理作业时，可选用此服务…… |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | 专为LLM训练设计的GPU加速数据筛选工具，支持处理文本、图像、视频、音频等多种类型的数据。具备模糊去重功能（速度提升16倍）、质量过滤功能（基于30多种规则）、语义去重功能、个人信息掩蔽功能以及不适宜内容检测功能，可跨多台GPU扩展使用…… |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS：通过差分均值技术消除LLM的拒绝响应问题。 |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines：支持生成结构化的JSON/正则表达式/Pydantic格式的LLM输出内容。 |
| [**peft-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-peft) | 基于LoRA、QLoRA及25种以上方法实现的参数高效型LLM微调技术，适用于在GPU内存有限的条件下微调7B-70B规模的大型模型，可在几乎不损失精度的前提下仅训练不到1%的模型参数，也支持多适配器微调场景…… |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | 专为生产级AI应用设计的托管型向量数据库，具备完全托管、自动扩展功能，支持密集向量与稀疏向量的混合搜索、元数据过滤以及命名空间管理功能，查询延迟低于100ms（p95值）。适用于生产环境中的RAG系统、推荐系统等场景…… |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | 提供关于使用PyTorch FSDP进行全分片数据并行训练的专家级指导，涵盖参数分片、混合精度计算、CPU卸载以及FSDP2等相关技术内容。 |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | 基于PyTorch开发的高级框架，拥有Trainer类，可自动实现DDP/FSDP/DeepSpeed等分布式训练功能，还具备回调系统以及极简的代码结构。使用相同代码即可在从笔记本电脑到超级计算机的不同硬件上实现模型训练，适用于需要简洁训练循环的场景…… |
| [**qdrant-vector-search**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | 高性能向量相似性搜索引擎，专为RAG和语义搜索场景设计。当您需要构建要求快速最近邻搜索、支持带过滤功能的混合搜索，或需要具备可扩展性的向量存储方案时，可选用此工具，其底层基于Rust语言实现…… |
| [**sparse-autoencoder-training**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | 提供基于SAELens工具的稀疏自编码器（SAE）训练与分析指导，该工具可通过分解神经网络激活值来获取可解释的特征。适用于发现可解释的特征、分析特征叠加效应，或开展相关研究场景…… |
| [**simpo-training**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | 用于LLM对齐的简单偏好优化方法，是无需参考模型的DPO替代方案，性能更优（在AlpacaEval 2.0测试中得分高出6.4分），无需参考模型，效率也高于DPO，适用于需要简化对齐流程的场景…… |
| [**slime-rl-training**](/docs/user-guide/skills/optional/mlops/mlops-slime) | 基于Megatron+SGLang框架的slime工具，为LLM训练后的强化学习阶段提供指导。适用于训练GLM模型、实现自定义数据生成工作流，或需要深度集成Megatron-LM以实现强化学习任务高效扩展的场景…… |
| [**stable-diffusion-image-generation**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | 通过HuggingFace Diffusers库实现的先进文本到图像生成技术，基于Stable Diffusion模型。适用于根据文本提示生成图像、实现图像到图像的转换、图像修复，或构建自定义的扩散模型流程…… |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | 利用NVIDIA TensorRT优化LLM推理过程，可实现最高的处理吞吐量与最低的延迟。适用于在NVIDIA GPU（A100/H100）上开展生产环境部署，当您需要比使用PyTorch快10-100倍的推理速度，或需要对模型进行量化处理以实现高效服务时，可选用此工具…… |
| [**distributed-llm-pretraining-torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | 提供基于PyTorch的原生分布式LLM预训练功能，可通过torchtitan实现4D并行训练（包括FSDP2、TP、PP、CP四种并行模式），适用于大规模预训练Llama 3.1、DeepSeek V3或自定义模型，支持使用Float8精度、torch.compile优化技术以及dist函数实现分布式训练…… |
| [**fine-tuning-with-trl**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL：为LLM的强化学习对齐任务提供SFT、DPO、PPO、GRPO以及奖励建模等相关功能。 |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth：可让LoRA/QLoRA微调速度提升2-5倍，同时降低VRAM占用量。 |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI开发的通用语音识别模型，支持99种语言的语音识别、转录功能，可将识别结果翻译为英文，同时还具备语言识别能力。该模型提供从小型（3900万参数）到大型（15.5亿参数）共六种不同规模版本，适用于语音转文本、播客处理等场景…… |

## 生产力提升

| 技能 | 描述 |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | Canvas学习管理系统集成功能——可通过API令牌认证获取已注册的课程及作业信息。 |
| [**here.now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | 可将静态网站发布到&#123;slug&#125;.here.now平台，同时可将私有文件存储在云盘服务中，便于不同代理之间传递数据。 |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 基于间隔重复算法的闪卡系统，允许用户从事实或文本中创建闪卡，可通过自由文本回答与闪卡进行互动，系统会由代理对回答进行评分，还能从YouTube视频字幕中生成测验题，具备自适应调度功能的到期卡片提醒功能，同时支持闪卡的导入与导出…… |
| [**shop-app**](/docs/user-guide/skills/optional/productivity/productivity-shop-app) | Shop.app：提供产品搜索、订单追踪、退货处理以及重新下单等功能。 |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | 通过curl命令调用Shopify的管理后台及前端店铺的GraphQL API，可获取产品、订单、客户、库存以及元字段等相关数据。 |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | SiYuan Note API，允许用户通过curl命令搜索、阅读、创建及管理自托管知识库中的块状内容与文档。 |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | 无需对核心工具进行修改即可为Hermes添加电话功能，可配置并保留Twilio号码，支持发送和接收短信/MMS消息，能够直接拨打电话，还可通过Bland.ai或Vapi平台发起由人工智能驱动的呼出电话…… |

## 研究领域| 技能 | 描述 |
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
