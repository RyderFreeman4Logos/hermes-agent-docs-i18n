---
title: "Apple Reminders — Apple Reminders via remindctl: add, list, complete"
sidebar_label: "Apple Reminders"
description: "Apple Reminders via remindctl: add, list, complete"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Apple Reminders

通过 remindctl 管理 Apple Reminders：添加、列出、完成任务。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/apple\apple-reminders` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | macos |
| 标签 | `Reminders`, `tasks`, `todo`, `macOS`, `Apple` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# Apple Reminders

通过终端使用 `remindctl` 直接管理 Apple Reminders。任务会通过 iCloud 在所有 Apple 设备间同步。

## 先决条件

- 安装了 Reminders.app 的 **macOS** 系统
- 安装命令：`brew install steipete/tap/remindctl`
- 按提示授予 Reminders 应用相应权限
- 检查状态：`remindctl status` / 授权操作：`remindctl authorize`

## 适用场景

- 用户提及“提醒”或“Reminders 应用”
- 创建带有截止日期的个人待办事项，并同步至 iOS 设备
- 管理 Apple Reminders 中的列表
- 用户希望任务在 iPhone/iPad 上显示

## 不适用场景

- 安排智能体警报 → 请使用 cronjob 工具
- 日历事件管理 → 请使用 Apple Calendar 或 Google Calendar
- 项目任务管理 → 请使用 GitHub Issues、Notion 等工具
- 若用户说“提醒我”但实际指的是智能体警报 → 需先明确需求

## 快速参考

### 查看提醒事项

```bash
remindctl                    # Today's reminders
remindctl today              # Today
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # Everything
remindctl 2026-01-04         # Specific date
```

### 管理列表

```bash
remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list
```

### 创建提醒事项

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### 截止时间与提醒/提前通知

`--due` 和 `--alarm` 是两个不同的参数：

- `--due` 用于设置提醒的截止日期或时间。
- `--alarm` 用于设置 EventKit 的提醒/通知触发机制。对于定时截止的提醒，系统通常会在截止时间触发警报；但若用户希望提前收到通知，则需明确指定 `--alarm` 参数。

例如，设定在下午2:00到期的提醒，并在30分钟前发送通知：

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

要编辑现有的提醒事项：

```bash
remindctl edit 87354 --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

“提醒”界面可能会根据闹钟时间来显示或对相关事项进行分组，因为通知正是在该时间触发的。建议通过 JSON 数据进行核实，而非直接假设截止时间发生了变化。

```bash
remindctl today --json
```

预期数据结构如下：

- `dueDate`：实际截止时间  
- `alarmDate`：通知或提前提醒时间  

Apple官方的`EKReminder`文档仅列出了与提醒功能相关的属性。而报警功能则通过remindctl工具的`--alarm`参数所调用的、继承自`EKCalendarItem`的相应功能来实现。

### 完成/删除操作

```bash
remindctl complete 1 2 3          # Complete by ID
remindctl delete 4A83 --force     # Delete by ID
```

### 输出格式

```bash
remindctl today --json       # JSON for scripting
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

## 日期格式

`--due` 参数及日期筛选器所支持的格式包括：
- `today`、`tomorrow`、`yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 格式（`2026-01-04T12:34:56Z`）

## 规则

1. 当用户输入“提醒我”时，需明确说明是使用 Apple Reminders（同步至手机）还是通过代理的定时任务进行提醒。
2. 在创建提醒之前，务必确认提醒内容和截止日期。
3. 如需通过程序进行解析，请使用 `--json` 参数。
