---
title: "Openhue — Control Philips Hue lights, scenes, rooms via OpenHue CLI"
sidebar_label: "Openhue"
description: "Control Philips Hue lights, scenes, rooms via OpenHue CLI"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Openhue

通过 OpenHue CLI 控制 Philips Hue 灯具、场景及房间。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/smart-home/openhue` |
| 版本 | `1.0.0` |
| 创建者 | 社区用户 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Smart-Home`、`Hue`、`Lights`、`IoT`、`Automation` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# OpenHue CLI

通过 Hue Bridge 从终端控制 Philips Hue 灯具及场景。

## 先决条件

```bash
# Linux (pre-built binary)
curl -sL https://github.com/openhue/openhue-cli/releases/latest/download/openhue-linux-amd64 -o ~/.local/bin/openhue && chmod +x ~/.local/bin/openhue

# macOS
brew install openhue/cli/openhue-cli
```

首次使用时，需按下 Hue Bridge 上的按钮进行配对。该桥接设备必须处于同一局域网内。

## 适用场景

- “打开/关闭灯光”
- “调节客厅灯光的亮度”
- “设置场景”或“电影模式”
- 控制特定的 Hue 房间、区域或单个灯泡
- 调整亮度、颜色或色温

## 常用命令

### 列出资源

```bash
openhue get light       # List all lights
openhue get room        # List all rooms
openhue get scene       # List all scenes
```

### 控制灯光

```bash
# Turn on/off
openhue set light "Bedroom Lamp" --on
openhue set light "Bedroom Lamp" --off

# Brightness (0-100)
openhue set light "Bedroom Lamp" --on --brightness 50

# Color temperature (warm to cool: 153-500 mirek)
openhue set light "Bedroom Lamp" --on --temperature 300

# Color (by name or hex)
openhue set light "Bedroom Lamp" --on --color red
openhue set light "Bedroom Lamp" --on --rgb "#FF5500"
```

### 控制室

```bash
# Turn off entire room
openhue set room "Bedroom" --off

# Set room brightness
openhue set room "Bedroom" --on --brightness 30
```

### 场景

```bash
openhue set scene "Relax" --room "Bedroom"
openhue set scene "Concentrate" --room "Office"
```

## 快速预设

```bash
# Bedtime (dim warm)
openhue set room "Bedroom" --on --brightness 20 --temperature 450

# Work mode (bright cool)
openhue set room "Office" --on --brightness 100 --temperature 250

# Movie mode (dim)
openhue set room "Living Room" --on --brightness 10

# Everything off
openhue set room "Bedroom" --off
openhue set room "Office" --off
openhue set room "Living Room" --off
```

## 备注

- Bridge设备必须与运行Hermes的机器处于同一局域网内。
- 首次使用时，需手动按下Hue Bridge上的按钮进行授权。
- 颜色功能仅适用于支持色彩显示的灯泡（不支持纯白光型号）。
- 灯光名称及房间名称对大小写敏感——可使用`openhue get light`命令查看确切名称。
- 该功能可与cron作业结合使用，实现定时控制灯光亮度（例如睡前调暗灯光，醒来时调亮）。
