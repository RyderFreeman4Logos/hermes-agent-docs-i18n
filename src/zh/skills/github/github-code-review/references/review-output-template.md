# 输出模板说明

请使用此模板作为拉取请求评审总结评论的结构，复制后填写相应内容即可。

## 用于拉取请求总结评论

```markdown
## Code Review Summary

**Verdict: [Approved ✅ | Changes Requested 🔴 | Reviewed 💬]** ([N] issues, [N] suggestions)

**PR:** #[number] — [title]
**Author:** @[username]
**Files changed:** [N] (+[additions] -[deletions])

### 🔴 Critical
<!-- Issues that MUST be fixed before merge -->
- **file.py:line** — [description]. Suggestion: [fix].

### ⚠️ Warnings
<!-- Issues that SHOULD be fixed, but not strictly blocking -->
- **file.py:line** — [description].

### 💡 Suggestions
<!-- Non-blocking improvements, style preferences, future considerations -->
- **file.py:line** — [description].

### ✅ Looks Good
<!-- Call out things done well — positive reinforcement -->
- [aspect that was done well]

---
*Reviewed by Hermes Agent*
```

## 严重性等级指南

| 等级 | 图标 | 适用场景 | 是否阻止合并？ |
|-------|------|-----------|--------------|
| 严重 | 🔴 | 安全漏洞、数据丢失风险、程序崩溃、核心功能故障 | 是 |
| 警告 | ⚠️ | 非关键路径中的错误、缺失的错误处理机制、新代码缺乏测试 | 通常会阻止 |
| 建议 | 💡 | 代码风格优化建议、重构方案、性能提升提示、文档缺失问题 | 不会阻止 |
| 表现良好 | ✅ | 代码结构清晰、测试覆盖率充足、命名规范、设计合理 | 无 |

## 审核结果判定

- **已通过 ✅** — 不存在任何严重或警告问题，仅有建议或所有问题均已解决。
- **需要修改 🔴** — 存在任何严重或警告级别的问题。
- **正在审核 💬** — 仅包含观察意见（如草稿 PR、不确定的发现或信息性内容）。

## 内联评论的使用规范

请在内联评论前加上对应严重性等级的图标，以便于快速识别：

```
🔴 **Critical:** User input passed directly to SQL query — use parameterized queries to prevent injection.
```

```
⚠️ **Warning:** This error is silently swallowed. At minimum, log it.
```

```
💡 **Suggestion:** This could be simplified with a dict comprehension:
`{k: v for k, v in items if v is not None}`
```

```
✅ **Nice:** Good use of context manager here — ensures cleanup on exceptions.
```

## 用于本地（推送前）审查

在推送之前进行本地审查时，可采用相同的结构，但需以消息形式呈现给用户，而非作为 PR 评论。无需包含 PR 元数据标题，直接从严重程度相关部分开始即可。
