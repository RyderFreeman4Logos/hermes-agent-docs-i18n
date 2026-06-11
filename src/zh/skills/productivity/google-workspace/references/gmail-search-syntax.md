# Gmail 搜索语法

标准的 Gmail 搜索运算符可用于 `query` 参数中。

## 常用运算符

| 运算符 | 示例 | 说明 |
|--------|------|------|
| `is:unread` | `is:unread` | 未读邮件 |
| `is:starred` | `is:starred` | 被星标标记的邮件 |
| `is:important` | `is:important` | 重要邮件 |
| `in:inbox` | `in:inbox` | 仅限收件箱内的邮件 |
| `in:sent` | `in:sent` | 已发送文件夹中的邮件 |
| `in:drafts` | `in:drafts` | 草稿箱中的邮件 |
| `in:trash` | `in:trash` | 垃圾箱中的邮件 |
| `in:anywhere` | `in:anywhere` | 包含垃圾邮件/垃圾箱在内的所有邮件 |
| `from:` | `from:alice@example.com` | 发件人 |
| `to:` | `to:bob@example.com` | 收件人 |
| `cc:` | `cc:team@example.com` | 抄送收件人 |
| `subject:` | `subject:invoice` | 主题包含该字词 |
| `label:` | `label:work` | 带有特定标签的邮件 |
| `has:attachment` | `has:attachment` | 包含附件的邮件 |
| `filename:` | `filename:pdf` | 附件的文件名或类型 |
| `larger:` | `larger:5M` | 大于指定大小的邮件 |
| `smaller:` | `smaller:1M` | 小于指定大小的邮件 |

## 日期运算符

| 运算符 | 示例 | 说明 |
|--------|------|------|
| `newer_than:` | `newer_than:7d` | 最近 N 天（d）、月（m）或年（y）内的邮件 |
| `older_than:` | `older_than:30d` | 老于 N 天/月/年的邮件 |
| `after:` | `after:2026/02/01` | 发送日期在之后的邮件（格式：YYYY/MM/DD） |
| `before:` | `before:2026/03/01` | 发送日期之前的邮件 |

## 运算符组合方式

| 语法 | 示例 | 说明 |
|------|------|------|
| 空格 | `from:alice subject:meeting` | 表示“且”关系（隐含） |
| `OR` | `from:alice OR from:bob` | 表示“或”关系 |
| `-` | `-from:noreply@` | 表示“非”关系（排除） |
| `()` | `(from:alice OR from:bob) subject:meeting` | 用于对条件进行分组 |
| `""` | `"exact phrase"` | 表示精确匹配整个短语 |

## 常见搜索模式

```
# Unread emails from the last day
is:unread newer_than:1d

# Emails with PDF attachments from a specific sender
from:accounting@company.com has:attachment filename:pdf

# Important unread emails (not promotions/social)
is:unread -category:promotions -category:social

# Emails in a thread about a topic
subject:"Q4 budget" newer_than:30d

# Large attachments to clean up
has:attachment larger:10M older_than:90d
```
