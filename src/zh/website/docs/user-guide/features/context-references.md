---
sidebar_position: 9
sidebar_label: "Context References"
title: "Context References"
description: "Inline @-syntax for attaching files, folders, git diffs, and URLs directly into your messages"
---

# 上下文引用

输入 `@` 后跟对应的引用，即可将内容直接插入消息中。Hermes 会在线展开该引用，并在 `--- 已附加上下文 ---` 标签下显示相关内容。

## 支持的引用类型

| 语法 | 描述 |
|------|------|
| `@file:path/to/file.py` | 插入文件内容 |
| `@file:path/to/file.py:10-25` | 插入特定行范围的内容（从1开始计数，包含首尾行） |
| `@folder:path/to/dir` | 插入包含文件元数据的目录树列表 |
| `@diff` | 插入 `git diff` 输出（未暂存的工作区更改内容） |
| `@staged` | 插入 `git diff --staged` 输出（已暂存的更改内容） |
| `@git:5` | 插入最近N次提交的内容及对应的补丁（最多10次） |
| `@url:https://example.com` | 获取并插入网页内容 |

## 使用示例

```text
Review @file:src/main.py and suggest improvements

What changed? @diff

Compare @file:old_config.yaml and @file:new_config.yaml

What's in @folder:src/components?

Summarize this article @url:https://arxiv.org/abs/2301.00001
```

在单条消息中可支持多次引用：

```text
Check @file:main.py, and also @file:test.py.
```

引用值中的尾部标点符号（`,`、`.`、`;`、`!`、`?`）会自动被移除。

## CLI 列表自动补全

在交互式 CLI 中，输入 `@` 即可触发自动补全功能：

- `@` 会显示所有引用类型（`@diff`、`@staged`、`@file:`、`@folder:`、`@git:`、`@url:`）
- `@file:` 和 `@folder:` 可用于补全文件系统路径，并同时显示文件大小等元数据
- 仅输入 `@` 后跟部分文本，则可查找当前目录中匹配的文件和文件夹

## 行号范围

`@file:` 引用类型支持行号范围指定，从而实现更精确的内容插入：

```text
@file:src/main.py:42        # Single line 42
@file:src/main.py:10-25     # Lines 10 through 25 (inclusive)
```

行号采用从1开始计数的方式。无效的范围会被静默忽略（此时会返回整个文件内容）。

## 大小限制

为防止超出模型的上下文窗口容量，对上下文引用设置了限制：

| 阈值 | 值 | 行为表现 |
|------|-----|----------|
| 柔性限制 | 上下文长度的25% | 会附加警告提示，但仍允许继续扩展 |
| 硬性限制 | 上下文长度的50% | 拒绝进一步扩展，原消息将保持不变地返回 |
| 文件夹内的条目 | 最多200个文件 | 超出数量的条目将被替换为“- ...” |
| Git提交记录 | 最多10条 | `@git:N` 的值会被限制在[1, 10]范围内 |

## 安全性

### 敏感路径屏蔽

为防止凭证信息泄露，以下路径始终会被禁止通过`@file:`引用：

- SSH密钥及配置文件：`~/.ssh/id_rsa`、`~/.ssh/id_ed25519`、`~/.ssh/authorized_keys`、`~/.ssh/config`
- Shell配置文件：`~/.bashrc`、`~/.zshrc`、`~/.profile`、`~/.bash_profile`、`~/.zprofile`
- 凭证文件：`~/.netrc`、`~/.pgpass`、`~/.npmrc`、`~/.pypirc`
- Hermes环境变量文件：`$

```text
# Code review workflow
Review @diff and check for security issues

# Debug with context
This test is failing. Here's the test @file:tests/test_auth.py
and the implementation @file:src/auth.py:50-80

# Project exploration
What does this project do? @folder:src @file:README.md

# Research
Compare the approaches in @url:https://arxiv.org/abs/2301.00001
and @url:https://arxiv.org/abs/2301.00002
```

## 错误处理

无效的引用只会触发内联警告，而不会导致任务失败：

| 情况 | 行为表现 |
|-----------|----------|
| 文件不存在 | 警告信息：“文件未找到” |
| 二进制文件 | 警告信息：“不支持二进制文件” |
| 目录不存在 | 警告信息：“目录未找到” |
| Git命令执行失败 | 显示包含Git标准错误信息的警告 |
| URL返回无内容 | 警告信息：“未提取到任何内容” |
| 路径包含敏感信息 | 警告信息：“该路径为敏感凭证文件” |
| 路径位于工作区之外 | 警告信息：“该路径不在允许的工作区范围内” |
