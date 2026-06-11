---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

此技能适用于以文件系统为基础的 Obsidian Vault 操作，包括读取笔记、列出笔记、搜索笔记文件、创建笔记、追加内容以及添加维基链接。

## Vault 路径

在调用文件工具之前，需使用已知或已解析的 Vault 路径。

文档中规定的 Vault 路径格式为 `OBSIDIAN_VAULT_PATH` 环境变量，通常可从 `${HERMES_HOME:-~/.hermes}/.env` 中获取。若该变量未设置，则可使用 `~/Documents/Obsidian Vault`。

文件工具不会自动展开 shell 变量。请勿将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files` 函数，应先解析出具体的绝对路径再使用。由于 Vault 路径中可能包含空格，这也是推荐使用文件工具而非 shell 命令的另一原因。

如果 Vault 路径未知，可使用 `terminal` 工具来解析 `OBSIDIAN_VAULT_PATH` 或检查备用路径是否存在。确定路径后，再切换回文件工具使用。

## 读取笔记

使用已解析的笔记绝对路径搭配 `read_file` 函数进行读取。相比 `cat` 命令，该方式能显示行号并支持分页查看，更为便捷。

## 列出笔记

使用 `search_files` 函数，设置 `target: "files"` 参数并传入已解析的 Vault 路径。相比 `find` 或 `ls` 命令，此方法更为高效。

- 若要列出所有 Markdown 格式的笔记，可在 Vault 路径后添加 `pattern: "*.md"` 参数。
- 若需列出某个子文件夹中的笔记，则需在该子文件夹的绝对路径下进行搜索。

## 搜索

无论是按文件名还是内容搜索，均可使用 `search_files` 函数。相比 `grep`、`find` 或 `ls` 命令，它的功能更为强大。

- 对于按文件名搜索，可使用 `search_files` 函数，设置 `target: "files"` 参数并指定文件名匹配模式。
- 对于搜索笔记内容，可使用 `search_files` 函数，设置 `target: "content"` 参数、内容正则表达式作为匹配模式；若希望仅搜索 Markdown 格式的笔记，还可添加 `file_glob: "*.md"` 参数。

## 创建笔记

使用已解析的绝对路径及完整的 Markdown 内容搭配 `write_file` 函数来创建笔记。相比 shell 的 heredoc 或 `echo` 命令，此方法能避免 shell 引号相关的问题，并返回结构化的处理结果。

## 向笔记追加内容

在操作方式不会造成困扰的情况下，建议优先使用内置的文件工具流程：

1. 先使用 `read_file` 读取目标笔记。
2. 若存在稳定的上下文环境（例如可在现有标题后添加新章节，或在已知结尾块前追加内容），可使用 `patch` 函数进行精准追加。
3. 若直接重写整个笔记更为清晰，而非通过临时拼接的方式，则可使用 `write_file` 函数。

对于使用 `patch` 进行精准追加的场景，需将原有内容作为锚点，再在其后添加新内容。

而对于没有稳定上下文的简单追加操作，若 `terminal` 工具是较为安全且清晰的解决方案，也可选用该方式。

## 定向编辑

当当前笔记内容能提供稳定的上下文时，可使用 `patch` 函数对笔记进行针对性修改。相比通过 shell 重新编写文本，此方法更为高效。

## 维基链接

Obsidian 使用 `[[Note Name]]` 语法来链接不同笔记。在创建笔记时，可利用该语法关联相关内容。
