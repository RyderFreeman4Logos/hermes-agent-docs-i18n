---
title: "Petdex — Install and select animated petdex mascots for Hermes"
sidebar_label: "Petdex"
description: "Install and select animated petdex mascots for Hermes"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Petdex

为 Hermes 安装并选择动画宠物吉祥物。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/petdex` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `petdex`、`mascot`、`display`、`cli`、`tui`、`desktop` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令。
:::

# Petdex 技能

从公共 [petdex](https://github.com/crafter-station/petdex) 图库中浏览、安装并选择动画“宠物”吉祥物。已安装的宠物会响应 Hermes CLI、TUI 以及桌面应用中的各种操作状态（空闲、运行工具、查看内容、出错、完成）。该技能负责驱动 `hermes pets` CLI 命令以及 `display.pet` 配置项——它不会生成精灵图。

## 适用场景

- 用户希望使用桌面/终端吉祥物，或询问有关“宠物”/petdex 的信息。
- 用户想要更改、预览或禁用当前激活的宠物。
- 排查为何宠物未显示的问题（终端图形支持情况、配置问题）。

## 先决条件

- 能够访问 `petdex.dev` 以获取图库和清单内容（仅读权限，无需认证）。
- 需要 Pillow（Hermes 的核心依赖项）用于精灵图解码——该组件通常已预装。
- 如需在终端中实现高保真渲染：需要使用具备图形处理功能的终端（如 kitty、Ghostty、WezTerm、iTerm2 或 sixel）。否则系统会自动回退到真彩色 Unicode 半块字符显示方式。

## 运行方法

使用 `terminal` 工具来运行 `hermes pets <subcommand>` 命令。

## 快速参考

| 目标 | 命令 |
| --- | --- |
| 浏览图库 | `hermes pets list`（可添加子字符串进行筛选：`hermes pets list cat`） |
| 列出已安装的宠物 | `hermes pets list --installed` |
| 安装宠物 | `hermes pets install <slug>`（添加 `--select` 可使其立即激活） |
| 设置激活的宠物 | `hermes pets select <slug>`（省略 slug 参数则会出现选择器） |
| 调整所有界面上的宠物大小 | `hermes pets scale <factor>`（例如 `0.5`，范围限制在 0.1–3.0 之间） |
| 在终端中预览/播放动画 | `hermes pets show [slug] [--cycle] [--state run]` |
| 禁用宠物 | `hermes pets off` |
| 移除宠物 | `hermes pets remove <slug>` |
| 检查设置是否正常 | `hermes pets doctor` |

## 操作步骤

1. 查找宠物：输入 `hermes pets list <query>` 并记下其 `slug` 值。
2. 安装并激活：执行 `hermes pets install <slug> --select`。
3. 预览效果：运行 `hermes pets show`（按 Ctrl+C 可停止预览）。
4. 确认设置：使用 `hermes pets doctor` 命令，即可查看最终选定的宠物、配置的渲染模式、检测到的终端图形协议以及当前实际生效的模式。

宠物会被安装到 `<HERMES_HOME>/pets/<slug>/` 目录下（支持根据用户配置文件选择不同路径）。选中某个宠物后，系统会将 `display.pet.slug` 和 `display.pet.enabled` 的值写入 `config.yaml` 文件中。

## 配置选项

在 `config.yaml` 文件的 `display.pet` 部分可进行以下配置：

- `enabled`（布尔值）——整体开关控制。
- `slug`（字符串）——当前激活的宠物；留空则表示使用第一个已安装的宠物。
- `render_mode` —— `auto`（自动检测）| `kitty` | `iterm` | `sixel` | `unicode` | `off`。
- `scale`（浮点数）——原生 192×208 像素图帧在屏幕上的显示尺寸（默认值为 0.33，范围限制在 0.1–3.0 之间）。调整此值可同步改变所有界面上的宠物大小；可通过 `hermes pets scale <factor>` 命令、`/pet scale` 分隔符命令或桌面端的“外观”滑块进行设置。
- `unicode_cols`（整数）——Unicode 回退显示时的列数。

## 常见问题

- 只有在同时完成安装并选中宠物（即 `enabled: true`）后，它才会显示出来。
- 在管道或重定向操作中（即没有 TTY 的情况下），出于设计考虑，终端渲染功能会被禁用。
- petdex 的 npm CLI 会将文件安装到 `~/.codex/pets` 目录；而 Hermes 则使用自身基于用户配置文件的 `<HERMES_HOME>/pets/` 目录——请通过 `hermes pets` 命令进行安装。

## 验证方法

- 当宠物已正确安装、被选中、处于启用状态且 Pillow 可正常导入时，执行 `hermes pets doctor` 命令后会显示 `✓ ready` 的提示。
