---
title: "Youtube Content — YouTube transcripts to summaries, threads, blogs"
sidebar_label: "Youtube Content"
description: "YouTube transcripts to summaries, threads, blogs"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# YouTube 内容处理

将 YouTube 视频的字幕转换为摘要、主题帖或博客文章。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/media\youtube-content` |
| 版本 | `1.0.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `YouTube`、`视频`、`字幕`、`媒体` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# YouTube 内容处理工具

## 适用场景

当用户分享 YouTube 链接或视频地址、要求对视频进行总结、获取字幕，或希望从任意 YouTube 视频中提取并重新格式化内容时，可使用此工具。它能将字幕转换为结构化内容（如章节、摘要、主题帖或博客文章）。

可从 YouTube 视频中提取字幕，并将其转换为实用格式。

## 设置方法

请使用 `uv` 命令将相关依赖项安装到与运行辅助脚本相同的 Hermes 管理环境中：

```bash
uv pip install youtube-transcript-api
```

## 辅助脚本

`SKILL_DIR` 是包含该 `SKILL.md` 文件的目录。该脚本可识别任何标准的 YouTube 链接格式、短链接（youtu.be）、短视频链接、嵌入代码、直播链接，或是长度为 11 位的原始视频编号。

```bash
# JSON output with metadata
uv run python SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
uv run python SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## 输出格式

获取转录内容后，根据用户需求进行格式化处理：

- **章节划分**：按主题变化进行分组，输出标注时间戳的章节列表  
- **摘要**：用5至10句话简要概括整个视频的内容  
- **章节概要**：为每个章节提供简短的段落总结  
- **推文格式**：采用Twitter/X的推文形式——按序号排列的帖子，每条不超过280个字符  
- **博客文章**：包含标题、分节及核心要点的全文  
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

1. 通过 `uv run python` 运行辅助脚本，使用 `--text-only --timestamps` 参数获取文字记录。
2. **验证**：确认输出内容非空且为预期语言。若为空，则不指定 `--language` 参数重新尝试，以获取任何可用的文字记录。如果仍然为空，则告知用户该视频可能已禁用字幕功能。
3. **必要时分块处理**：如果文字记录长度超过约5万字符，将其拆分为重叠的片段（每个片段约4万字符，重叠部分为2千字符），并对每个片段进行总结后再合并。
4. **转换为指定格式**：根据用户要求将内容转换为目标输出格式。若用户未指定格式，则默认生成摘要。
5. **最终校验**：在展示结果之前，重新阅读转换后的内容，检查其逻辑连贯性、时间戳是否正确以及内容是否完整。

## 错误处理

- **字幕功能已禁用**：告知用户，并建议其查看视频页面上是否有字幕选项。
- **视频为私密或无法访问**：转达错误信息，并请用户确认网址是否正确。
- **未找到匹配的语言**：不指定 `--language` 参数重新尝试获取任何可用的文字记录，随后向用户说明实际使用的语言。
- **缺少依赖项**：运行 `uv pip install youtube-transcript-api` 后再次尝试。
