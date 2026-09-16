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
| 路径 | `skills/note-taking\obsidian` |
| 版本 | `1.0.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Obsidian`、`笔记`、`Markdown`、`文档库` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会依据这些指令来执行操作。
:::

# Obsidian 文档库

使用此技能可进行以文件系统为基础的 Obsidian 文档库操作：读取笔记、列出笔记、搜索笔记文件、创建新笔记、追加内容以及添加维基链接。

## 文档库路径

在调用文件相关工具之前，需先确定或解析出正确的文档库路径。

官方规定的文档库路径格式为 `OBSIDIAN_VAULT_PATH` 环境变量，该变量的值通常来自 `${HERMES_HOME:-~/.hermes}/.env` 文件。如果该变量未被设置，则可使用 `~/Documents/Obsidian Vault` 作为默认路径。

文件工具不会自动展开shell变量。请勿将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files` 等函数，应先解析出具体的绝对路径后再使用。由于文档库路径中可能包含空格，这也是为何相较于shell命令，更建议使用文件工具的原因之一。

如果不知道保险库路径，可以使用 `terminal` 来确定 `OBSIDIAN_VAULT_PATH` 的值或检查备用路径是否存在。一旦确定了路径，就应转而使用文件操作工具。

## 读取笔记

使用已确定的笔记绝对路径配合 `read_file` 命令进行读取。相比 `cat`，该方式能显示行号并支持分页查看，更为实用。

## 列出笔记

使用 `search_files` 命令，设置 `target: "files"` 参数并传入已确定的保险库路径。相比 `find` 或 `ls`，此方法更为高效。

- 若要列出所有 Markdown 格式的笔记，可在保险库路径后指定 `pattern: "*.md"`。
- 若要列出某个子文件夹中的笔记，则需在该子文件夹的绝对路径下进行搜索。

## 搜索

无论是按文件名还是内容搜索，均可使用 `search_files` 命令。相比 `grep`、`find` 或 `ls`，它更为合适。

- 对于按文件名搜索，可使用 `search_files`，设置 `target: "files"` 参数并指定文件名匹配模式。
- 对于搜索笔记内容，可使用 `search_files`，设置 `target: "content"` 参数，将内容正则表达式作为匹配模式；若希望仅搜索 Markdown 格式的笔记，还可添加 `file_glob: "*.md"` 参数。

## 创建笔记

使用已确定的绝对路径及完整的 Markdown 内容，通过 `write_file` 命令创建笔记。相比使用 Shell 的 heredoc 或 `echo` 命令，此方法能避免引号相关的问题，并返回结构化的结果。

## 向笔记追加内容

在操作起来不会过于繁琐的情况下，建议优先使用内置的文件操作工具来完成该操作。

- 使用 `read_file` 命令读取目标笔记。  
- 当存在稳定的上下文环境时（例如在现有标题后添加章节，或在已知的结尾块之前追加内容），可使用 `patch` 命令进行基于锚点的追加操作。  
- 若直接重写整个笔记更为清晰，而非通过复杂的修补方式，可使用 `write_file` 命令。  

对于使用 `patch` 进行的基于锚点的追加操作，需将原锚点替换为“锚点+新内容”的组合形式。  
而对于没有稳定上下文的简单追加操作，若 `terminal` 方式是最清晰且安全的选项，则也可选用该方式。  

## 定向编辑  

当当前笔记内容能够提供稳定的上下文时，可使用 `patch` 命令对笔记进行精准修改，这种方式优于通过 Shell 命令重写文本。  

## 维基链接  

Obsidian 使用 `[[笔记名称]]` 语法来关联不同笔记。在创建笔记时，可利用此语法来链接相关内容。
