---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube内容处理工具

## 适用场景

当用户分享YouTube网址或视频链接、请求对视频进行总结、要求获取字幕，或是希望从任意YouTube视频中提取并重新整理内容时，均可使用该工具。它能将字幕转换为结构化内容（如章节、摘要、讨论串、博客文章等），并可将YouTube视频中的字幕提取出来并转换为实用的格式。

## 设置方法

```bash
pip install youtube-transcript-api
```

## 辅助脚本

`SKILL_DIR` 即包含该 `SKILL.md` 文件的目录。该脚本可识别任何标准的 YouTube 链接格式、短链接（youtu.be）、短视频链接、嵌入代码、直播链接，或是长度为 11 位的原始视频 ID。

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## 输出格式

获取转录内容后，根据用户需求对其进行格式化处理：

- **章节划分**：按主题变化进行分组，输出带时间戳的章节列表
- **摘要**：用5到10句话简要概括整个视频的内容
- **章节概要**：为每个章节提供简短的段落总结
- **推文格式**：采用Twitter/X的推文形式——按序号排列的帖子，每条不超过280个字符
- **博客文章**：包含标题、分章节以及核心要点的全文
- **名句摘录**：附带时间戳的重要语录

### 示例——章节划分输出格式

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## 工作流程

1. 使用辅助脚本，通过 `--text-only --timestamps` 参数**获取**文字记录。
2. **验证**：确认输出内容非空且为预期语言。若为空，则不指定 `--language` 参数重新尝试，以获取任何可用的文字记录。如果仍为空，则告知用户该视频可能已禁用字幕功能。
3. **按需分块**：如果文字记录长度超过约50K字符，将其拆分为重叠的片段（每个片段约40K字符，片段间重叠2K字符），并对每个片段进行摘要处理后再合并。
4. **转换**为用户要求的输出格式。若用户未指定格式，则默认生成摘要。
5. **校验**：在展示结果之前，重新阅读转换后的内容，检查其连贯性、时间戳是否正确以及内容是否完整。

## 错误处理

- **字幕功能已禁用**：告知用户，并建议其查看视频页面上是否有字幕选项。
- **视频为私密/无法访问**：转达该错误信息，并请用户核实URL地址。
- **未找到匹配的语言**：不指定 `--language` 参数重新尝试获取任何可用的文字记录，然后向用户说明实际使用的语言。
- **缺少依赖项**：运行 `pip install youtube-transcript-api` 后再试。
