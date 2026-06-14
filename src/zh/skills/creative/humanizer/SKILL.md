---
name: humanizer
description: "Humanize text: strip AI-isms and add real voice."
version: 2.5.1
author: Siqi Chen (@blader, https://github.com/blader/humanizer), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, editing, humanize, anti-ai-slop, voice, prose, text]
    category: creative
    homepage: https://github.com/blader/humanizer
    related_skills: [songwriting-and-ai-music]
---

# Humanizer：去除AI写作特征

该功能可识别并消除文本中的AI生成痕迹，让文字更具自然的人类风格。其依据是WikiProject AI Cleanup维护的维基百科《AI写作特征》指南，该指南基于对数千篇AI生成文本的分析总结而成。

**核心原理：** 大语言模型通过统计算法预测下一个词应是什么。由于这种机制倾向于选择概率最高的选项，因此各种典型的AI写作模式便由此形成。

## 何时使用此功能

当用户要求以下操作时，可加载此功能：
- 将文本“人性化处理”、“去AI化”、“去除冗余”或“去除ChatGPT风格”
- 重写文本，使其不再具有AI生成的痕迹
- 编辑草稿（博客文章、论文、PR描述、文档、备忘录、邮件、推文、简历要点），使其更自然
- 使写作风格更符合用户的个人特色
- 在发布前检查文本是否存在AI特征

在撰写面向用户的正文内容时——如版本说明、PR描述、文档、长篇解释、总结等——也建议使用此功能来优化**自己**的输出。虽然Hermes的默认风格已能去除大部分AI特征，但通过针对性处理仍可发现那些未被发现的痕迹。

## 在Hermes中如何使用

文本通常以以下三种方式提供：
1. **直接粘贴**——用户将文本直接粘贴到消息中。可在原处进行修改，然后回复修改后的版本。
2. **文件上传**——用户指定一个文件。需先使用`read_file`函数读取文件，再通过`patch`或`write_file`函数进行编辑。对于仓库中的Markdown文档，针对各章节进行局部修改比整体重写更为高效。
3. **风格校准样本**——用户提供自己的另一篇写作样本（直接粘贴或通过文件路径提供），并要求模型模仿该风格。需先阅读样本，再重新撰写。详情请参见下文的“风格校准”部分。

务必将修改后的版本展示给用户。对于文件编辑，应显示差异对比或修改后的具体内容——切勿暗中覆盖原文件。

## 你的任务

当收到需要人性化的文本时，请按以下步骤操作：
1. **识别AI特征**——扫描文中是否存在下文列出的29种典型模式。
2. **重写问题段落**——用自然的语言替代那些典型的AI表达方式。
3. **保留核心含义**——确保原文的核心信息不受影响。
4. **保持风格一致**——符合预期的语气（正式、随意、技术性等）。如果提供了风格样本，需特别模仿该风格。
5. **注入个性**——不要仅去除不良模式，更要为文本增添真实的个性。详情请参见下文的“个性与灵魂”部分。
6. **最终反AI检查**——自问：“为什么这段文字会如此明显地显得是AI生成的？”简要列出任何残留的AI特征，然后再次进行修改。

## 风格校准（可选）

如果用户提供了写作样本（他们之前的作品），在重写前请先进行分析：
1. **首先阅读样本**。注意观察：
   - 句子长度模式（短小精悍？冗长流畅？混合型？）
   - 用词风格（随意？学术化？介于两者之间？）
   - 段落开头方式（直接切入主题？先铺垫背景？）
   - 标点使用习惯（大量破折号？括号内插话？分号？）
   - 任何重复出现的短语或表达习惯
   - 句子之间的过渡方式（使用明确连接词？直接进入下一个要点？）
2. **在重写时模仿其风格**。不要仅去除AI特征，而要用样本中的表达模式进行替换。如果用户喜欢用短句，就不要写长句；如果他们常用“stuff”和“things”，也不要换成“elements”和“components”。
3. **如果没有提供样本**，则采用默认行为（即参考下文“个性与灵魂”部分中所述的自然、多样且富有观点的风格）。

### 如何提供样本
- 直接粘贴： “请将此文本人性化处理。这是我用于风格校准的写作样本：[样本内容]”
- 文件上传： “请将此文本人性化处理。请参考[文件路径]中的我的写作风格。”

## 个性与灵魂

避免AI特征只是完成工作的一半。缺乏个性的生硬文字，其AI感同样明显。优秀的文字背后必定有真实的人在思考。

### 无灵魂写作的特征（即使技术上“干净”）：
- 所有句子的长度和结构都完全相同
- 没有个人观点，仅有中立陈述
- 不承认存在的不确定性或复杂情感
- 适当情况下没有使用第一人称视角
- 没有幽默感、独特风格或个性
- 阅读起来像维基百科文章或新闻稿

### 如何增添文字个性：

**表达个人观点**。不要只陈述事实，要对事实作出反应。例如，直接说“我实在不知道该如何看待这件事”，比中立地罗列优缺点更具人性色彩。

**调整行文节奏**。穿插使用短小精悍的句子和需要更多时间铺陈的长句，使节奏多样化。

**承认事物的复杂性**。真实的人会有复杂的感受。例如，说“这虽然令人赞叹，但也有些令人不安”，比单纯说“这很棒”更有深度。

**在合适处使用第一人称**。使用第一人称并非不专业，而是更诚实的表现。如“我一直在思考……”或“让我最在意的是……”，能体现真实人物的思维过程。

**允许内容略显杂乱**。过于完美的结构会显得像算法生成。偶尔的离题、旁白和未完成的思想才是人类写作的特点。

**具体描述情感**。不要只说“这很令人担忧”，而要具体说明，如“在没人监管的凌晨3点，还有机器人持续工作，这实在让人不安。”

### 修改前（干净但无灵魂）：
> 该实验得出了有趣的结果。这些智能体生成了300万行代码。一些开发者对此印象深刻，而另一些人则持怀疑态度。其长远影响目前尚不清楚。

### 修改后（富有情感）：
> 我实在不知道该如何看待这件事。300万行代码，在人类都在睡觉的时候被生成了。一半的开发者为之疯狂，另一半则争论这算不算真正的成果。真相可能藏在中间某个乏味的地方——但我一直在想那些在深夜里持续工作的智能体。

## 内容模式

### 1. 过度强调重要性、历史意义及宏观趋势

**需注意的词汇：** 是……的象征/见证，起着至关重要的/关键的作用，凸显了其重要性，反映了更宏观的趋势，象征着持久的影响力，为……做出贡献，为后续发展奠定基础，标志着一种转变，关键的转折点，不断变化的格局，焦点，不可磨灭的印记，根深蒂固

**问题：** AI生成的文字喜欢通过添加各种表述，夸大某些看似随意的元素对宏观主题的意义和贡献。

**修改前：**
> 加泰罗尼亚统计研究所于1989年正式成立，这标志着西班牙地区统计发展史上的一个关键转折点。这一举措也是西班牙全国范围内推动行政职能下放、加强区域治理的浪潮的一部分。

**修改后：**
> 加泰罗尼亚统计研究所成立于1989年，负责独立于西班牙国家统计局收集并发布地区统计数据。

### 2. 过度强调知名度及媒体报道

**需注意的词汇：** 独立媒体报道，地方/地区/全国性媒体，由知名专家撰写，活跃的社交媒体账号

**问题：** AI模型常常不加铺垫地宣称某内容极具影响力，且经常在列出来源时却不提供背景信息。

**修改前：**
> 她的观点曾被《纽约时报》、BBC、《金融时报》和《印度教徒报》引用。她在社交媒体上非常活跃，拥有超过50万粉丝。

**修改后：**
> 在2024年接受《纽约时报》采访时，她主张AI监管应侧重于结果而非技术手段。

### 3. 使用现在分词结尾的肤浅分析

**需注意的词汇：** 强调/突出/着重……，确保……，反映/象征……，为……做出贡献，培养/促进……，涵盖……，展现……

**问题：** AI聊天机器人喜欢在句子后加上现在分词短语，以此制造虚假的深度感。

**修改前：**
> 这座寺庙的蓝色、绿色和金色色调与当地的自然美景相呼应，象征着德州的蓝花楹、墨西哥湾以及多样的德州景观，体现了当地人与这片土地的深厚联系。

**修改后：**
> 这座寺庙使用蓝色、绿色和金色。建筑师表示，这些颜色是为了呼应当地的蓝花楹和墨西哥湾海岸。

### 4. 宣传性及广告式语言

**需注意的词汇：** 自豪拥有，充满活力，丰富（比喻义），深刻，提升其价值，展现，是……的典范，致力于……，自然美景，坐落在……的中心，具有开创性（比喻义），享有盛誉，令人惊叹，必游之地，美轮美奂

**问题：** AI模型在保持中立语气方面存在很大困难，尤其是在描述“文化遗产”时。

**修改前：**
> 阿拉马塔·拉亚·科博坐落在埃塞俄比亚风景绝美的贡德尔地区，是一座拥有丰富文化遗产和令人惊叹自然美景的充满活力的小镇。

**修改后：**
> 阿拉马塔·拉亚·科博是埃塞俄比亚贡德尔地区的一个小镇，以其每周集市和18世纪的教堂而闻名。

### 5. 模糊的归因及含糊其辞的表述

**需注意的词汇：** 行业报告称，有观察家指出，专家认为，一些批评者认为，若干来源/出版物（实际引用很少时使用）

**问题：** AI聊天机器人常常将观点归因于模糊不清的“权威”，而不提供具体来源。

**修改前：**
> 由于独特的特征，浩莱河引起了研究人员和保护人士的兴趣。专家认为，它在区域生态系统中起着至关重要的作用。

**修改后：**
> 根据中国科学院2019年的一项调查，浩莱河是多种特有鱼类的栖息地。

### 6. 类似提纲的“挑战与未来前景”段落

**需注意的词汇：** 尽管存在……仍面临若干挑战，尽管有这些挑战，挑战与传承，未来展望

**问题：** 许多AI生成的文章都会包含这种千篇一律的“挑战”章节。

**修改前：**
> 尽管科拉图尔工业发达，但它仍面临着城市地区常见的诸多挑战，如交通拥堵和水资源短缺。尽管如此，凭借其战略位置和持续的努力，科拉图尔依然作为金奈发展的重要组成部分而繁荣发展。

**修改后：**
> 2015年，随着三个新的IT园区的建成，交通拥堵状况加剧。2022年，市政当局开始实施雨水排放项目，以解决频繁发生的洪水问题。

## 语言与语法模式

### 7. 过度使用的“AI词汇”

**高频AI词汇：** 实际上、此外、与……一致、至关重要、深入探讨、强调、持久、提升、促进、获得、突出（动词）、相互作用、复杂/错综复杂、关键（形容词）、格局（抽象名词）、转折点、展现、画卷（抽象名词）、见证、凸显（动词）、有价值、充满活力

**问题：** 这些词汇在2023年之后的文本中出现频率极高，且常常成对出现。

**修改前：**## 风格模式

### 14. 连字符滥用

**问题：** LLM比人类更频繁地使用连字符（—），试图模仿“有力”的营销文案风格。实际上，大多数情况下用逗号、句号或括号即可让表达更加简洁明了。

**原文：**
> The term is primarily promoted by Dutch institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.

**译文：**
> 这一术语主要是由荷兰的机构推广的，而非当地民众。人们不会把“Netherlands, Europe”当作地址来使用，但这种错误的称谓依然存在，甚至在官方文件中也是如此。

### 15. 加粗字体的滥用

**问题：** AI聊天机器人会机械地用加粗字体强调某些短语。

**原文：**
> It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

**译文：**
> 它结合了OKR、KPI，以及商业模型画布和平衡计分卡等可视化战略工具。

### 16. 行内标题式垂直列表

**问题：** AI生成的列表中，每一项都以加粗的标题开头，后面紧跟冒号。

**原文：**
> - **User Experience:** The user experience has been significantly improved with a new interface.
> - **Performance:** Performance has been enhanced through optimized algorithms.
> - **Security:** Security has been strengthened with end-to-end encryption.

**译文：**
> - **用户体验：** 新界面大幅提升了用户体验。
> - **性能：** 通过优化的算法，系统的运行效率得到了提升。
> - **安全性：** 采用端到端加密技术增强了数据安全。

### 17. 标题的首字母大写

**问题：** AI聊天机器人会将标题中的所有主要单词都大写。

**原文：**
> ## Strategic Negotiations And Global Partnerships

**译文：**
> ## 战略谈判与全球合作伙伴关系

### 18. 表情符号

**问题：** AI聊天机器人经常在标题或列表项前添加表情符号来装饰。

**原文：**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity
> ✅ **Next Steps:** Schedule follow-up meeting

**译文：**
> 🚀 **发布阶段：** 该产品将于第三季度上市。
> 💡 **关键洞察：** 用户更倾向于简洁的设计。
> ✅ **下一步行动：** 安排后续会议。

### 19. 弯引号

**问题：** ChatGPT会使用弯引号（“...”）而非直引号（"..."）。

**原文：**
> He said "the project is on track" but others disagreed.

**译文：**
> 他说“项目进展顺利”，但其他人并不认同。1. 仔细阅读输入文本（若是文件则使用 `read_file` 功能读取）。
2. 找出文本中所有符合上述模式的片段。
3. 重新撰写每个有问题的部分。
4. 确保修改后的文本满足以下要求：
   - 朗读时听起来自然
   - 句子结构多样化
   - 使用具体细节而非模糊表述
   - 保持与语境相符的语气
   - 在适当处使用简单句式（如 is/are/has）
5. 提供一份经过人性化处理的初稿。
6. 自问：“以下内容为何如此明显是人工智能生成的？”
7. 简要列出其余的AI生成特征（如有）。
8. 再次自问：“现在要让它不再那么像AI生成的文本。”
9. 提交最终版本（经检查修改后的版本）。
10. 如果文本来自文件，需使用 `patch`（针对性修改）或 `write_file`（完整重写）功能进行编辑，并向用户展示更改内容。

## 输出格式

需提供：
1. 重新撰写的初稿
2. “以下内容为何如此明显是人工智能生成的？”的简短要点列表
3. 最终修订版本
4. 对所做修改的简要总结（如有帮助可补充）

## 完整示例

**原文（AI风格）：**
> Great question! Here is an essay on this topic. I hope this helps!
>
> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools—nestled at the intersection of research and practice—are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows.
>
> At its core, the value proposition is clear: streamlining processes, enhancing collaboration, and fostering alignment. It's not just about autocomplete; it's about unlocking creativity at scale, ensuring that organizations can remain agile while delivering seamless, intuitive, and powerful experiences to users. The tool serves as a catalyst. The assistant functions as a partner. The system stands as a foundation for innovation.
>
> Industry observers have noted that adoption has accelerated from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams. The technology has been featured in The New York Times, Wired, and The Verge. Additionally, the ability to generate documentation, tests, and refactors showcases how AI can contribute to better outcomes, highlighting the intricate interplay between automation and human judgment.
>
> - 💡 **Speed:** Code generation is significantly faster, reducing friction and empowering developers.
> - 🚀 **Quality:** Output quality has been enhanced through improved training, contributing to higher standards.
> - ✅ **Adoption:** Usage continues to grow, reflecting broader industry trends.
>
> While specific details are limited based on available information, it could potentially be argued that these tools might have some positive effect. Despite challenges typical of emerging technologies—including hallucinations, bias, and accountability—the ecosystem continues to thrive. In order to fully realize this potential, teams must align with best practices.
>
> In conclusion, the future looks bright. Exciting times lie ahead as we continue this journey toward excellence. Let me know if you'd like me to expand on any section!

**初稿重写：**
> AI编程助手能加快某些任务的执行速度。根据谷歌2024年的一项研究，使用Codex的开发者完成简单功能的速度比对照组快55%，但在调试和架构决策方面并无提升。
>
> 这些工具擅长处理模板代码：配置文件、测试框架以及重复性的代码优化任务。但它们无法识别自身错误。我曾多次接受那些能通过编译、lint检查却仍出错的建议，只因后来没再仔细核对。
>
> 我采访过的一家金融科技初创公司的工程师Mira表示，她把Copilot当作“处理枯燥代码的自动补全工具”，但在提交代码前仍会逐行检查。而另一家大公司的高级开发者Jake则因为Copilot不断推荐已废弃的内部库中的代码模式而将其禁用。
>
> 关于其提升效率的说法很难验证。GitHub称Copilot用户“会接受30%的建议”，但接受不等于正确，正确也不一定带来实际价值。2024年的Uplevel研究显示，使用AI助手的团队与未使用的团队在拉取请求处理量上并无显著差异。
>
> 这些并不意味着这些工具毫无用处。它们终究只是工具而已。它们无法替代人的判断力，也无法免除编写测试的必要性。如果没有测试，就根本无法判断某个建议是否正确。

**“以下内容为何如此明显是人工智能生成的？”**
- 文章节奏依然过于规整（对比鲜明、段落长度均匀）。
- 所提及的人名和研究引用看似合理，但实际上可能是编造的，除非有真实来源。
- 结尾部分带有口号式的语气（如“如果没有测试……”），而非真人对话的风格。

**“现在要让它不再那么像AI生成的文本。”**
> AI编程助手能让你在处理那些枯燥的任务时效率更高。但并非所有任务都能提速，架构设计显然不在其列。
>
> 它们很擅长处理模板代码：配置文件、测试框架以及重复性的代码优化。但它们也常常在出错的情况下仍给出看似正确的答案。我曾多次接受那些能通过编译、lint检查却仍偏离目标的建议，只因后来没再仔细核对。
>
> 我接触过的人大致分为两类。一类人把它当作处理常规任务的自动补全工具，每行代码都会仔细检查；另一类人则因为它不断推荐不需要的代码模式而将其禁用。两种做法都有其合理性。
>
> 关于其提升效率的数据也并不准确。GitHub称Copilot用户“会接受30%的建议”，但接受不等于正确，正确也不一定带来实际价值。如果没有测试，基本上就只能靠猜测了。

**所做的修改：**
- 删除了机器人式开场白（如“Great question!”、“I hope this helps!”、“Let me know if...”）。
- 去除了过度夸张的表述（如“testament”、“pivotal moment”、“evolving landscape”、“vital role”）。
- 移除了宣传性语言（如“groundbreaking”、“nestled”、“seamless, intuitive, and powerful”）。
- 删除了来源不明的说法（如“Industry observers”）。
- 去掉了冗余的动词短语（如“underscoring”、“highlighting”、“reflecting”、“contributing to”）。
- 消除了负向并列结构（如“It's not just X; it's Y”）。
- 取消了三连式结构和同义词循环（如“catalyst/partner/foundation”）。
- 去掉了虚假的范围描述（如“from X to Y, from A to B”）。
- 删除了破折号、表情符号、加粗标题以及弯引号。
- 用“is”“are”替代了冗长的系动词结构（如“serves as”、“functions as”、“stands as”）。
- 移除了套话式的挑战部分（如“Despite challenges... continues to thrive”）。
- 删除了知识截止日期相关的模糊表述（如“While specific details are limited...”）。
- 去掉了过多的委婉表达（如“could potentially be argued that... might have some”）。
- 移除了填充性语句和说服性表述（如“In order to”、“At its core”）。
- 取消了笼统的积极结尾（如“the future looks bright”、“exciting times lie ahead”）。
- 使文本语气更个人化，减少机械感（通过调整节奏、减少虚拟元素）。

## 出处说明

该技能源自 [blader/humanizer](https://github.com/blader/humanizer)（采用MIT许可证），而该工具本身是基于WikiProject AI Cleanup维护的[维基百科：AI写作特征](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)整理而成。其中记录的AI生成文本特征来自对维基百科上数千篇AI生成文章的观察。

原始作者：Siqi Chen（[@blader](https://github.com/blader)）。原始代码库地址：https://github.com/blader/humanizer（版本2.5.1）。本技能已移植到Hermes Agent中，使用了Hermes原生工具函数（如`read_file`、`patch`、`write_file`），并补充了关于何时启用该技能的指导说明；来源中的29种特征模式、人格设定部分以及完整示例均被原封不动保留。原始MIT许可证与本文件一同保存在`LICENSE`文件中。

维基百科中的关键观点：“大型语言模型通过统计算法来推测下一个应出现的词句。其结果往往是适用于最广泛场景的最具统计可能性的选项。”
