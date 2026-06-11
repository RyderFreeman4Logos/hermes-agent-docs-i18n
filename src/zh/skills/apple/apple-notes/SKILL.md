---
name: apple-notes
description: "Manage Apple Notes via memo CLI: create, search, edit."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Notes, Apple, macOS, note-taking]
    related_skills: [obsidian]
prerequisites:
  commands: [memo]
---

# Apple Notes

您可以使用 `memo` 命令直接在终端中管理 Apple Notes。这些笔记会通过 iCloud 在所有 Apple 设备之间实现同步。

## 先决条件

- 安装了 Notes.app 的 **macOS** 系统
- 执行以下命令进行安装：`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- 当系统提示时，需为 Notes.app 授权自动化访问权限（路径：系统设置 → 隐私 → 自动化）

## 适用场景

- 用户需要创建、查看或搜索 Apple Notes
- 将信息保存到 Notes.app 以实现跨设备访问
- 将笔记整理到不同文件夹中
- 将笔记导出为 Markdown/HTML 格式

## 不适用场景

- Obsidian 笔记库管理 → 请使用 `obsidian` 技能
- Bear Notes → 该应用为独立程序，此处不支持
- 仅用于快速记录的笔记 → 请改用 `memory` 工具

## 快速参考

### 查看笔记

```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
```

### 创建笔记

```bash
memo notes -a                     # Interactive editor
memo notes -a "Note Title"        # Quick add with title
```

### 编辑说明

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
- 交互式提示需要终端访问权限（如需则使用 pty=true 参数）
- 仅支持 macOS 系统——必须使用 Apple Notes.app 应用

## 规则

1. 当用户需要跨设备同步（iPhone/iPad/Mac）时，优先推荐使用 Apple Notes
2. 对于无需同步的智能体内部笔记，可使用 `memory` 工具
3. 对于基于 Markdown 的知识管理需求，建议使用 `obsidian` 技能
