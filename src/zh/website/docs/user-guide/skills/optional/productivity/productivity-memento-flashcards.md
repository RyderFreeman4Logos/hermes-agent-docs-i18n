---
title: "Memento Flashcards — Spaced-repetition flashcards: create, review, quiz, export"
sidebar_label: "Memento Flashcards"
description: "Spaced-repetition flashcards: create, review, quiz, export"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Memento 记忆卡片

间隔重复记忆卡片功能：支持创建、复习、测试及导出。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过命令 `hermes skills install official/productivity/memento-flashcards` 安装 |
| 路径 | `optional-skills/productivity\memento-flashcards` |
| 版本 | `1.0.0` |
| 开发者 | Memento AI |
| 许可协议 | MIT |
| 支持平台 | macos、linux |
| 标签 | `教育`, `记忆卡片`, `间隔重复`, `学习`, `测试`, `YouTube` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行相应操作。
:::

# Memento 记忆卡片 — 间隔重复记忆卡片技能

## 概述

Memento 提供了一套基于本地文件的记忆卡片系统，并具备间隔重复复习功能。
用户可以通过自由文本形式回答问题与卡片进行互动，智能体会先对答案进行评分，然后再安排下一次复习时间。
以下场景非常适合使用该功能：
- **记住某个事实** — 将任何陈述转化为问答式记忆卡片
- **通过间隔重复法学习** — 根据自适应间隔安排复习，并查看智能体评分后的自由文本答案
- **根据 YouTube 视频生成测试题** — 自动提取视频字幕并生成包含5道题的测试卷
- **管理卡片组** — 将卡片分类整理，支持 CSV 格式导入/导出
所有卡片数据均存储在同一个 JSON 文件中。无需任何外部 API 密钥——您（即智能体）可直接生成抽认卡内容与测验题目。

Memento 抽认卡的面向用户回复格式：
- 仅使用纯文本，不得在回复用户时使用 Markdown 格式。
- 回复中的复习与测验反馈应简短且客观，避免过多的表扬、激励性话语或冗长的解释。

## 适用场景

当用户希望实现以下功能时，可使用此技能：
- 将知识点保存为抽认卡以便日后复习
- 通过间隔重复法复习到期的卡片
- 根据 YouTube 视频的字幕生成测验
- 导入、导出、查看或删除抽认卡数据

请勿将此技能用于常规问答、编程帮助或与记忆无关的任务。

## 快速参考

| 用户意图 | 操作 |
|---|---|
| “记住X” / “将此内容保存为抽认卡” | 生成问答卡片，并调用 `memento_cards.py add` |
| 发送事实信息但未提及抽认卡 | 询问“需要我将此内容保存为Memento抽认卡吗？”——仅在得到确认后才创建 |
| “创建抽认卡” | 请求问题、答案及分类名称，然后调用 `memento_cards.py add` |
| “查看我的抽认卡” | 调用 `memento_cards.py due`，逐一展示卡片 |
| “根据[YouTube链接]对我进行测试” | 调用 `youtube_quiz.py fetch VIDEO_ID`，生成5道题目，随后调用 `memento_cards.py add-quiz` |
| “导出我的抽认卡” | 调用 `memento_cards.py export --output PATH` |
| “从CSV文件导入抽认卡” | 调用 `memento_cards.py import --file PATH --collection NAME` |
| “查看我的统计数据” | 调用 `memento_cards.py stats` |
| “删除一张卡片” | 调用 `memento_cards.py delete --id ID` |
| “删除一个分类” | 调用 `memento_cards.py delete-collection --collection NAME` |

## 卡片存储方式

卡片存储在以下位置的JSON文件中：

```
~/.hermes/skills/productivity/memento-flashcards/data/cards.json
```

**切勿直接编辑此文件。** 应始终使用 `memento_cards.py` 的子命令。该脚本通过原子化写入方式（先写入临时文件，再重命名）来避免数据损坏。

该文件会在首次使用时自动创建。

## 操作步骤

### 从事实信息创建闪卡

### 激活规则

并非所有事实陈述都应转化为闪卡。请遵循以下三级判断标准：

1. **明确意图** — 用户提到“memento”、“flashcard”、“记住这个”、“保存这张卡片”、“添加一张卡片”或类似明确要求创建闪卡的表述 → **直接创建闪卡**，无需确认。
2. **隐含意图** — 用户仅陈述事实，未提及闪卡（例如：“光速为299,792公里/秒”） → **先进行询问**：“需要我将此内容保存为Memento闪卡吗？”只有得到用户确认后才能创建闪卡。
3. **无意图** — 消息属于编程任务、问题、指令、普通对话，或明显不属于需记忆的事实内容 → **完全不要激活此功能**。让其他功能或默认处理方式来处理该内容。

在确认激活后（一级直接激活，二级需经确认），即可生成闪卡：

**第一步：** 将陈述内容转换为问答对。内部请使用以下格式：

```
Turn the factual statement into a front-back pair.
Return exactly two lines:
Q: <question text>
A: <answer text>

Statement: "{statement}"
```

规则：  
- 问题需用于测试对关键事实的回忆能力；  
- 答案应简洁明了。  

**步骤2：** 调用脚本以保存该卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add \
  --question "What year did World War 2 end?" \
  --answer "1945" \
  --collection "History"
```

如果用户未指定分类，则默认使用“General”作为分类名称。

脚本会输出 JSON 文件以确认卡片已创建。

### 手动创建卡片

当用户明确要求创建抽认卡时，需向用户收集以下信息：
1. 问题（卡片正面内容）
2. 答案（卡片背面内容）
3. 分类名称（可选——默认为“General”）

之后即可按照前述方式调用 `memento_cards.py add` 函数。

### 查看到期卡片

当用户想要查看卡片时，需获取所有已到期的卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

该方法会返回一个 JSON 数组，其中包含所有满足 `next_review_at <= now` 条件的卡片。如需应用集合筛选条件：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due --collection "History"
```

**评分流程（自由文本评分）：**

以下是您必须遵循的标准化交互模式示例。用户回答问题后，您需先给出评分，告知正确答案，然后再对卡片进行评分。

**示例交互：**

> **智能体：** 柏林墙是在哪一年倒塌的？
>
> **用户：** 1991年
>
> **智能体：** 不对。柏林墙实际上是在1989年倒塌的。下次评估时间为明天。
> *(智能体调用命令：memento_cards.py rate --id ABC --rating hard --user-answer "1991")*
>
> 下一题：谁是第一个登上月球的人？

**评分规则：**

1. 仅显示问题，等待用户作答。
2. 收到答案后，将其与标准答案对比并给出评分：
   - **正确** → 用户答对了关键事实（即便表述方式不同）；
   - **部分正确** → 思路正确，但遗漏了核心细节；
   - **错误** → 答案有误或偏离主题。
3. **您必须告知用户正确答案以及他们的答题情况。** 说明要简短，且使用纯文本格式，格式如下：
   - correct: “答对了。正确答案：&#123;answer&#125;。7天后进行下一次评估。”
   - partial: “接近正确。正确答案：&#123;answer&#125;。遗漏了&#123;what they missed&#125;。3天后进行下一次评估。”
   - incorrect: “不对。正确答案：&#123;answer&#125;。明天进行下一次评估。”
4. 随后调用评分命令：正确→easy，部分正确→good，错误→hard。
5. 最后展示下一道题目。

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```

**切勿跳过第3步。** 在继续之前，必须始终让用户看到正确的答案及反馈。

如果当前没有需要审核的卡片，请告知用户：“目前没有需要审核的卡片，请稍后再查看！”

**永久移除功能：** 用户随时可以输入“retire this card”来将该卡片永久从审核列表中移除。此时可使用 `--rating retire` 命令。

### 间隔重复算法

评分将决定下一次的复习间隔：

| 评分 | 间隔时间 | 连续简单次数 | 状态变化 |
|---|---|---|---|
| **困难** | +1天 | 重置为0 | 继续学习 |
| **良好** | +3天 | 重置为0 | 继续学习 |
| **简单** | +7天 | +1 | 若连续简单次数≥3 → 归档 |
| **已归档** | 永久 | 重置为0 | → 归档 |

- **学习中**：该卡片仍在循环复习中
- **已归档**：该卡片不会再出现在复习列表中（用户已掌握该内容或手动将其归档）
- 连续三次获得“简单”评分，该卡片将自动归档

### YouTube测验生成

当用户提供YouTube视频链接并希望生成测验时：

**第1步：** 从链接中提取视频ID（例如，从 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 中提取出 `dQw4w9WgXcQ`）。

**第2步：** 获取视频字幕：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/youtube_quiz.py fetch VIDEO_ID
```

该操作会返回 `{"title": "...", "transcript": "..."}` 的结果，或抛出错误信息。

如果脚本提示“缺少依赖项”，请告知用户需先安装该依赖：
```bash
pip install youtube-transcript-api
```

**步骤 3：** 根据转录内容生成 5 道测验题。需遵循以下规则：

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

该脚本会通过`video_id`进行去重处理——如果该视频对应的卡片已存在，它将跳过创建步骤，并直接显示现有的卡片。

**第6步：** 按照相同的自由文本评分流程逐一提出问题：
1. 显示“问题1/5：……”，等待用户回答。严禁透露答案或任何相关提示。
2. 等待用户用自己的话作答。
3. 使用评分提示对用户的答案进行评分（参见“检查到期卡片”部分）。
4. **重要提示：在采取其他任何操作之前，您必须先向用户反馈意见。** 需显示评分结果、正确答案以及下一次检查的时间。切勿直接跳过到下一个问题。回复内容应简短且为纯文本格式。示例：“不太对。正确答案是&#123;answer&#125;。下次检查时间为明天。”
5. **在给出反馈后**，调用rate命令，然后在同一条消息中展示下一个问题。
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```
6. 重复操作。每个答案在进入下一个问题之前，都必须收到明确的反馈。

### CSV导出/导入

**导出：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py export \
  --output ~/flashcards.csv
```

生成一个包含三列的 CSV 文件：`question,answer,collection`（不包含表头行）。

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

返回包含以下信息的 JSON 数据：
- `total`：卡片总数
- `learning`：正在轮换学习的卡片数量
- `retired`：已掌握的卡片数量
- `due_now`：当前需要复习的卡片数量
- `collections`：按收藏集名称分类的统计信息

## 常见问题

- **切勿直接编辑 `cards.json` 文件**——务必使用脚本中的子命令操作，以避免数据损坏
- **字幕获取失败**——部分 YouTube 视频没有英文字幕或字幕功能被关闭；此时应告知用户并推荐其他视频
- **可选依赖项**——`youtube_quiz.py` 需要 `youtube-transcript-api` 库；若该库缺失，需提示用户执行 `pip install youtube-transcript-api` 命令进行安装
- **大量数据导入**——包含数千行的 CSV 文件可以正常导入，但生成的 JSON 输出可能较为冗长；建议为用户总结关键结果
- **视频 ID 提取**——支持 `youtube.com/watch?v=ID` 和 `youtu.be/ID` 两种 URL 格式

## 验证方法

可直接运行辅助脚本进行验证：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add --question "Capital of France?" --answer "Paris" --collection "General"
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

如果您是从代码仓库检出版本后进行测试，请运行：

```bash
pytest tests/skills/test_memento_cards.py tests/skills/test_youtube_quiz.py -q
```

代理级验证：
- 启动评估流程，确认反馈为纯文本形式、简短精炼，且每张新卡片出现前均会附带正确答案；
- 运行YouTube测验流程，确保在进入下一道题目之前，用户能看到针对每一道题目的反馈。
