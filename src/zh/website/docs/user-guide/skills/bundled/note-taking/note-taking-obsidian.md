---
title: "Obsidian — Read, search, create, and edit notes in the Obsidian vault"
sidebar_label: "Obsidian"
description: "Read, search, create, and edit notes in the Obsidian vault"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Obsidian

在 Obsidian 文档库中读取、搜索、创建及编辑笔记。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/note-taking/obsidian` |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# Obsidian 文档库

使用此技能处理以文件系统为基础的 Obsidian 文档库操作：读取笔记、列出笔记、搜索笔记文件、创建笔记、追加内容以及添加维基链接。

## 文档库路径

在调用文件相关工具之前，需使用已知或已解析的文档库路径。

官方推荐的文档库路径约定是 `OBSIDIAN_VAULT_PATH` 环境变量，通常位于 `~/.hermes/.env` 文件中。若该变量未设置，则可使用 `~/Documents/Obsidian Vault` 作为默认路径。

文件工具不会自动展开 shell 变量。请勿将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files` 函数；应先解析出具体的绝对路径再传入。文档库路径中可能包含空格，这也是为何相比 shell 命令更推荐使用文件工具的原因之一。

如果不确定文档库路径，可使用 `terminal` 工具来解析 `OBSIDIAN_VAULT_PATH` 或检查默认路径是否存在。确定路径后，再切换回文件工具使用。

## 读取笔记

使用已解析的笔记绝对路径配合 `read_file` 函数进行读取。相比 `cat` 命令，此方法能显示行号并支持分页查看，更为便捷。

## 列出笔记

使用 `search_files` 函数，设置 `target: "files"` 参数并传入已解析的文档库路径。相比 `find` 或 `ls` 命令，此方法更为高效。

- 若要列出所有 Markdown 格式的笔记，可在文档库路径后添加 `pattern: "*.md"` 参数。
- 若要列出某个子文件夹中的笔记，则需在该子文件夹的绝对路径下进行搜索。

## 搜索

无论是搜索文件名还是内容，均可使用 `search_files` 函数。相比 `grep`、`find` 或 `ls` 命令，此方法更为适用。

- 搜索文件名时，设置 `target: "files"` 参数，并指定文件名匹配模式 `pattern`。
- 搜索笔记内容时，设置 `target: "content"` 参数，将内容正则表达式作为 `pattern` 参数；若希望仅搜索 Markdown 格式的笔记，还可添加 `file_glob: "*.md"` 参数。

## 创建笔记

使用已解析的绝对路径以及完整的 Markdown 内容，通过 `write_file` 函数创建笔记。相比 shell 的 heredoc 或 `echo` 命令，此方法能避免 shell 引号相关的问题，并返回结构化的操作结果。

## 向笔记追加内容

在操作方式较为简便的情况下，建议优先使用内置的文件工具流程：

- 先使用 `read_file` 函数读取目标笔记。
- 若存在稳定的上下文参考（例如可在现有标题后添加新章节，或在已知的内容块前追加内容），可使用 `patch` 函数实现精准追加。
- 若直接重写整个笔记更为清晰，而非通过临时拼接内容，可使用 `write_file` 函数。

对于使用 `patch` 进行精准追加的场景，需将原有内容作为锚点，再附加新内容。

若没有稳定的上下文参考，且 `terminal` 工具是唯一安全且清晰的解决方案，也可选择此方式简单追加内容。

## 定向编辑

当当前笔记内容能提供足够的上下文参考时，可使用 `patch` 函数对笔记进行针对性修改。相比手动重写文本，此方法更为高效。

## 维基链接

Obsidian 使用 `[[笔记名称]]` 语法来关联不同笔记。在创建笔记时，可利用该语法链接相关内容。
