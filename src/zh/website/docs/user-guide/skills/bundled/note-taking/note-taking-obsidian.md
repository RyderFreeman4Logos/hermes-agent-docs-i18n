---
title: "Obsidian — Read, search, create, and edit notes in the Obsidian vault"
sidebar_label: "Obsidian"
description: "Read, search, create, and edit notes in the Obsidian vault"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Obsidian

在 Obsidian 数据库中读取、搜索、创建及编辑笔记。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/note-taking/obsidian` |
| 支持平台 | linux、macos、windows |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体所看到的指令即为此内容。
:::

# Obsidian 数据库

使用此技能处理以文件系统为基础的 Obsidian 数据库操作：读取笔记、列出笔记、搜索笔记文件、创建笔记、追加内容以及添加维基链接。

## 数据库路径

在调用文件相关工具之前，需使用已知或已解析的数据库路径。

文档中规定的数据库路径格式为 `OBSIDIAN_VAULT_PATH` 环境变量，例如可从 `${HERMES_HOME:-~/.hermes}/.env` 中获取该值。如果未设置该变量，则可使用 `~/Documents/Obsidian Vault`。

文件工具不会自动展开shell变量。请勿将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files` 函数；应先解析出具体的绝对路径后再使用。数据库路径中可能包含空格，这也是为何相比shell命令更推荐使用文件工具的原因之一。

如果不知道数据库路径，可使用 `terminal` 工具来解析 `OBSIDIAN_VAULT_PATH` 或检查备用路径是否存在。一旦确定路径，再切换回文件工具使用。

## 读取笔记

使用已解析的笔记绝对路径配合 `read_file` 函数来读取笔记。相比 `cat`，此方法能显示行号并支持分页查看，更为便捷。

## 列出笔记

使用 `search_files` 函数，设置 `target: "files"` 参数并传入已解析的数据库路径。相比 `find` 或 `ls`，此方法更为高效。

- 要列出所有 Markdown 格式的笔记，可在数据库路径后添加 `pattern: "*.md"`。
- 要列出某个子文件夹中的笔记，则需在该子文件夹的绝对路径下进行搜索。

## 搜索

无论是搜索文件名还是内容，均可使用 `search_files` 函数。相比 `grep`、`find` 或 `ls`，此方法更为适用。

- 搜索文件名时，可使用 `search_files`，设置 `target: "files"` 参数及文件名匹配模式 `pattern`。
- 搜索笔记内容时，可使用 `search_files`，设置 `target: "content"` 参数、内容正则表达式作为 `pattern`；若希望仅搜索 Markdown 格式的笔记，还可添加 `file_glob: "*.md"` 参数。

## 创建笔记

使用已解析的绝对路径及完整的 Markdown 内容，配合 `write_file` 函数来创建笔记。相比使用shell heredoc或 `echo` 命令，此方法能避免shell引号相关问题，并返回结构化的处理结果。

## 向笔记追加内容

在操作不会造成困扰的情况下，建议优先使用内置的文件工具流程：

- 先使用 `read_file` 读取目标笔记。
- 若有稳定的上下文背景（例如可在现有标题后添加新章节，或在已知的内容块前追加内容），可使用 `patch` 函数进行定位追加。
- 若直接重写整个笔记更为清晰，而非通过复杂的补丁方式操作，则可使用 `write_file` 函数。

对于使用 `patch` 进行定位追加的操作，需将原锚点替换为“锚点+新内容”的格式。

对于没有稳定上下文背景的简单追加操作，若 `terminal` 工具是最佳且安全的选择，也可使用该工具。

## 定向编辑

当当前笔记内容能提供稳定的上下文背景时，可使用 `patch` 函数对笔记进行精准修改。相比使用shell命令重写文本，此方法更为高效。

## 维基链接

Obsidian 使用 `[[笔记名称]]` 语法来关联不同笔记。在创建笔记时，可利用该语法关联相关内容。
