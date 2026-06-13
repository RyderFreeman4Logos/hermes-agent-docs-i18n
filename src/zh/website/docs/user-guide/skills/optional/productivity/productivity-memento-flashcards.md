---
title: "Memento Flashcards — Spaced-repetition flashcard system"
sidebar_label: "Memento Flashcards"
description: "Spaced-repetition flashcard system"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请修改源文件 SKILL.md，而非此页面。 */}

# Memento 记忆卡片

一种基于间隔重复法的记忆卡片系统。您可以将事实或文本转换为卡片，通过自由文本回答与卡片进行互动，由智能体对回答进行评分后再安排下一次复习；还能从 YouTube 视频字幕中生成测验题，借助自适应调度功能复习到期的卡片，并以 CSV 格式导出/导入卡片组。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/productivity/memento-flashcards` 安装 |
| 路径 | `optional-skills/productivity/memento-flashcards` |
| 版本 | `1.0.0` |
| 开发者 | Memento AI |
| 许可协议 | MIT |
| 支持平台 | macos、linux |
| 标签 | `教育`, `记忆卡片`, `间隔重复法`, `学习`, `测验`, `YouTube` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为内容。
:::

# Memento 记忆卡片 — 基于间隔重复法的记忆卡片技能

## 概述

Memento 提供了一个基于本地文件、支持间隔重复调度的记忆卡片系统。
用户可以通过自由文本回答与卡片互动，智能体会先对回答进行评分，之后再安排下一次复习。
以下情况适合使用该功能：
- **记住某个事实** — 将任何陈述转换为问答式记忆卡片
- **通过间隔重复法学习** — 利用自适应间隔和智能体评分的自由文本回答来复习到期的卡片
- **根据 YouTube 视频生成测验** — 获取视频字幕并生成 5 道试题
- **管理卡片组** — 将卡片分类整理，以 CSV 格式导出/导入数据

所有卡片数据都存储在同一个 JSON 文件中。无需任何外部 API 密钥——您（即智能体）可直接生成卡片内容及测验题目。

Memento 记忆卡片面向用户的回复风格：
- 仅使用纯文本，不要在回复用户时使用 Markdown 格式
- 复习和测验的反馈需简短且中立，避免过多的表扬、激励或冗长解释

## 适用场景

当用户希望：
- 将事实保存为记忆卡片以便日后复习
- 通过间隔重复法复习到期的卡片
- 根据 YouTube 视频字幕生成测验
- 导入、导出、查看或删除记忆卡片数据

时，可使用此技能。
请勿将此技能用于常规问答、编程帮助或与记忆无关的任务。

## 快速参考

| 用户意图 | 操作 |
|---|---|
| “记住 X” / “把这条内容保存为记忆卡片” | 生成问答式卡片，调用 `memento_cards.py add` |
| 发送事实内容但未提及记忆卡片 | 询问“需要我将此内容保存为 Memento 记忆卡片吗？”——仅在得到确认后才创建卡片 |
| “创建一张记忆卡片” | 询问问题、答案及分类名称，然后调用 `memento_cards.py add` |
| “复习我的卡片” | 调用 `memento_cards.py due`，逐张展示卡片 |
| “根据 [YouTube URL] 给我出题测验” | 调用 `youtube_quiz.py fetch VIDEO_ID` 获取视频 ID，生成 5 道试题，再调用 `memento_cards.py add-quiz` |
| “导出我的卡片” | 调用 `memento_cards.py export --output PATH` |
| “从 CSV 文件导入卡片” | 调用 `memento_cards.py import --file PATH --collection NAME` |
| “查看我的使用数据统计” | 调用 `memento_cards.py stats` |
| “删除一张卡片” | 调用 `memento_cards.py delete --id ID` |
| “删除一个卡片分类” | 调用 `memento_cards.py delete-collection --collection NAME` |

## 卡片存储方式

卡片存储在以下位置的 JSON 文件中：

```
~/.hermes/skills/productivity/memento-flashcards/data/cards.json
```

**请勿直接编辑此文件。** 应始终使用 `memento_cards.py` 的子命令。该脚本通过原子化写入方式（先写入临时文件，再重命名）来避免数据损坏。

该文件会在首次使用时自动创建。

## 操作步骤

### 从事实信息创建抽认卡

### 激活规则

并非所有事实陈述都应转化为抽认卡。请遵循以下三级判断标准：

1. **明确意图** — 用户提及“memento”、“flashcard”、“记住这个”、“保存这张卡片”、“添加一张卡片”或类似明确要求创建抽认卡的表述 → **直接创建卡片**，无需确认。
2. **隐含意图** — 用户仅提供事实陈述，未提及抽认卡（例如：“光速为299,792公里/秒”） → **先进行询问**：“需要我将此内容保存为Memento抽认卡吗？”仅在用户确认后创建卡片。
3. **无意图** — 消息为编程任务、问题、指令、普通对话，或明显不属于需记忆的事实内容 → **完全不要激活此功能**。让其他功能或默认行为来处理。

一旦确认要激活该功能（第一级直接激活，第二级需经确认后激活），即生成抽认卡：

**第一步：** 将陈述内容转换为问答对。内部请使用以下格式：

```
Turn the factual statement into a front-back pair.
Return exactly two lines:
Q: <question text>
A: <answer text>

Statement: "{statement}"
```

规则：  
- 问题需用于考察对关键事实的回忆能力；  
- 答案应简洁明了。  

**步骤2：** 调用脚本以保存该卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add \
  --question "What year did World War 2 end?" \
  --answer "1945" \
  --collection "History"
```

如果用户未指定集合，则默认使用“General”作为集合名称。

脚本会输出 JSON 文件以确认卡片已创建。

### 手动创建卡片

当用户明确要求创建抽认卡时，需向用户收集以下信息：
1. 问题（卡片正面内容）
2. 答案（卡片背面内容）
3. 集合名称（可选——默认为“General”）

之后即可按照前述方式调用 `memento_cards.py add` 函数。

### 查看到期卡片

当用户想要查看需要复习的卡片时，需获取所有即将到期的卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

该方法会返回一个 JSON 数组，其中包含所有满足 `next_review_at <= now` 条件的卡片。如果需要应用集合筛选条件：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due --collection "History"
```

**评分流程（自由文本评分）：**

以下是您必须遵循的标准交互模式示例。用户回答问题后，您需对其进行评分，告知正确答案，随后为该题卡打分。

**示例交互：**

> **智能体：** 柏林墙是在哪一年倒塌的？
>
> **用户：** 1991年
>
> **智能体：** 不对。柏林墙实际上是在1989年倒塌的。下次测评时间为明天。
> *(智能体调用命令：memento_cards.py rate --id ABC --rating hard --user-answer "1991")*
>
> 下一题：谁是第一个登上月球的人？

**规则如下：**

1. 仅显示问题，等待用户回答。
2. 收到答案后，将其与标准答案对比并给出评分：
   - **correct** → 用户答对了关键事实（即便表述不同）；
   - **partial** → 方向正确，但遗漏了核心细节；
   - **incorrect** → 答案错误或偏离主题。
3. **您必须告知用户正确答案以及他们的答题情况。** 语言需简洁，且为纯文本格式，格式如下：
   - correct: “答对了。正确答案：&#123;answer&#125;。7天后进行下次测评。”
   - partial: “接近正确。正确答案：&#123;answer&#125;。遗漏了&#123;what they missed&#125;。3天后进行下次测评。”
   - incorrect: “不对。正确答案：&#123;answer&#125;。明天进行下次测评。”
4. 随后调用评分命令：答对则标记为easy，部分正确标记为good，答错则标记为hard。
5. 最后展示下一道题目。

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```

**切勿跳过第3步。** 在继续之前，必须始终让用户看到正确的答案及反馈。

如果当前没有需要复习的卡片，请告知用户：“目前没有需要查看的卡片。稍后再来试试！”

**永久移除功能：** 用户随时可以输入“retire this card”以将其从复习列表中永久删除。可使用 `--rating retire` 命令实现此操作。

### 间隔重复算法

评分决定了下一次复习的时间间隔：

| 评分 | 间隔时间 | 连续轻松次数 | 状态变化 |
|---|---|---|---|
| **困难** | +1天 | 重置为0 | 继续学习 |
| **良好** | +3天 | 重置为0 | 继续学习 |
| **简单** | +7天 | +1 | 若连续轻松次数≥3 → 永久移除 |
| **已移除** | 永久 | 重置为0 | → 已永久移除 |

- **学习中**：该卡片仍在循环复习中
- **已移除**：该卡片不会出现在复习列表中（用户已掌握该内容或手动将其移除）
- 连续三次获得“简单”评分，该卡片将自动被永久移除

### YouTube测验生成

当用户提供YouTube视频链接并希望生成测验时：

**第1步：** 从链接中提取视频ID（例如，从 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 中提取出 `dQw4w9WgXcQ`）。

**第2步：** 获取视频字幕：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/youtube_quiz.py fetch VIDEO_ID
```

该操作会返回 `{"title": "...", "transcript": "..."}` 的结果，或报错信息。

如果脚本提示“缺少依赖项”，请告知用户需先安装该依赖：
```bash
pip install youtube-transcript-api
```

**第3步：** 根据转录内容生成5道测验题。请遵循以下规则：

```
You are creating a 5-question quiz for a podcast episode.
Return ONLY a JSON array with exactly 5 objects.
Each object must contain keys 'question' and 'answer'.

Selection criteria:
- Prioritize important, surprising, or foundational facts.
- Skip filler, obvious details, and facts that require heavy context.
- Never return true/false questions.
- Never ask only for a date.

Question rules:
- Each question must test exactly one discrete fact.
- Use clear, unambiguous wording.
- Prefer What, Who, How many, Which.
- Avoid open-ended Describe or Explain prompts.

Answer rules:
- Each answer must be under 240 characters.
- Lead with the answer itself, not preamble.
- Add only minimal clarifying detail if needed.
```

以转录内容的前15,000个字符作为上下文。由你自行生成问题（即由你扮演LLM）。

**第4步：** 验证输出是否为有效的JSON格式，且必须包含恰好5个条目，每个条目的`question`和`answer`字段均不能为空字符串。如果验证失败，则重新尝试一次。

**第5步：** 存储测验题卡：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add-quiz \
  --video-id "VIDEO_ID" \
  --questions '[{"question":"...","answer":"..."},...]' \
  --collection "Quiz - Episode Title"
```

该脚本会通过 `video_id` 进行去重处理——如果该视频对应的卡片已存在，它将跳过创建步骤，并直接显示现有的卡片。

**第6步：** 按照相同的自由文本评分流程逐一提出问题：
1. 显示“问题 1/5：……”，等待用户回答。切勿透露答案或任何提示。
2. 等待用户用自己的话进行回答。
3. 使用评分提示对用户的回答进行评分（参见“检查到期卡片”部分）。
4. **重要提示：在采取任何其他操作之前，您必须先向用户反馈意见。** 需显示评分结果、正确答案以及下一次检查的时间。切勿直接跳过到下一个问题。回复内容应简短且为纯文本格式。例如：“不太对。正确答案是 &#123;answer&#125;。下次检查时间为明天。”
5. **在给出反馈后**，调用 rate 命令，然后在同一条消息中显示下一个问题：
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```
6. 重复操作。在提出下一个问题之前，每个答案都必须获得明确的反馈。

### CSV导出/导入

**导出：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py export \
  --output ~/flashcards.csv
```

生成一个包含三列的 CSV 文件：`question,answer,collection`（不含表头行）。

**导入：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py import \
  --file ~/flashcards.csv \
  --collection "Imported"
```

可读取包含“问题”、“答案”以及可选的“集合”（第3列）字段的CSV文件。若该集合字段缺失，则会使用`--collection`参数来指定。 

### 统计数据

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
```

返回包含以下内容的 JSON 数据：
- `total`：卡片总数
- `learning`：正在学习的卡片数量
- `retired`：已掌握的卡片数量
- `due_now`：当前需要复习的卡片数量
- `collections`：按收藏集名称分类的统计信息

## 常见问题

- **切勿直接编辑 `cards.json` 文件** —— 始终通过脚本子命令进行操作，以避免数据损坏
- **字幕获取失败** —— 部分 YouTube 视频没有英文字幕或字幕功能已关闭；此时应告知用户并推荐其他视频
- **可选依赖项** —— `youtube_quiz.py` 需要 `youtube-transcript-api` 库；若该库缺失，需提示用户执行 `pip install youtube-transcript-api`
- **大量数据导入** —— 包含数千行的 CSV 文件可以正常导入，但生成的 JSON 输出可能较为冗长；建议为用户汇总处理结果
- **视频 ID 提取** —— 支持 `youtube.com/watch?v=ID` 和 `youtu.be/ID` 两种 URL 格式

## 验证方法

可直接运行辅助脚本进行验证：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add --question "Capital of France?" --answer "Paris" --collection "General"
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

如果您是通过代码库检出版本进行测试，请运行：

```bash
pytest tests/skills/test_memento_cards.py tests/skills/test_youtube_quiz.py -q
```

智能体级验证：
- 启动评估流程，确认反馈为纯文本格式、内容简短，并且在每张新卡片出现之前都会附带正确答案；
- 运行YouTube测验流程，确保在进入下一道题目之前，用户能够看到针对每道题目的反馈。
