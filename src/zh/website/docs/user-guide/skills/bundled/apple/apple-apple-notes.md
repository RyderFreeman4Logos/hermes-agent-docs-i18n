---
title: "Apple Notes — Manage Apple Notes via memo CLI: create, search, edit"
sidebar_label: "Apple Notes"
description: "Manage Apple Notes via memo CLI: create, search, edit"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Apple Notes

通过 memo CLI 管理 Apple Notes：创建、搜索、编辑。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/apple\apple-notes` |
| 版本 | `1.0.1` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | macos |
| 标签 | `Notes`, `Apple`, `macOS`, `note-taking` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，Agent 就会依据这些内容执行操作。
:::

# Apple Notes

可直接在终端中使用 `memo` 命令管理 Apple Notes。笔记会通过 iCloud 在所有 Apple 设备间同步。

## 先决条件

- 安装了 Notes.app 的 **macOS** 系统
- 安装对应工具：`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- 根据系统提示授予 Notes.app 自动化访问权限（系统设置 → 隐私 → 自动化）

## 适用场景

- 用户需要创建、查看或搜索 Apple Notes
- 将信息保存到 Notes.app 以实现跨设备访问
- 将笔记整理到不同文件夹中
- 将笔记导出为 Markdown/HTML 格式

## 不适用场景

- Obsidian 笔记库管理 → 请使用 `obsidian` 技能
- Bear Notes → 为独立应用（本技能不支持）
- 仅需 Agent 内部存储的临时笔记 → 请使用 `memory` 工具

## 快速参考

### 查看笔记

```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
```

### 创建笔记

```bash
memo notes -a                     # Add a note (opens your $EDITOR)
memo notes -a -f "Folder Name"    # Add a note into a specific folder
```

`-a`/`--add` 是一个基础标志——它会打开您的 `$EDITOR` 程序以便编辑笔记，且不接受标题参数。若需指定文件夹，请使用 `-f/--folder`。请先设置 `$EDITOR`（例如：`export EDITOR=vim`）。

### 编辑笔记

```bash
memo notes -e                     # Interactive selection to edit
```

### 删除笔记

```bash
memo notes -d                     # Interactive selection to delete
```

### 移动说明

```bash
memo notes -m                     # Move note to folder (interactive)
```

### 导出说明

```bash
memo notes -ex                    # Export to HTML/Markdown
```

## 局限性

- 无法编辑包含图片或附件的笔记
- 交互式提示需要终端访问权限（如需使用，请设置 pty=true）
- 仅支持 macOS 系统——必须使用 Apple Notes.app 应用

## 规则

1. 当用户需要跨设备同步（iPhone/iPad/Mac）时，优先推荐使用 Apple Notes
2. 对于无需同步的代理内部笔记，可使用 `memory` 工具
3. 对于基于 Markdown 的知识管理需求，建议使用 `obsidian` 技能
