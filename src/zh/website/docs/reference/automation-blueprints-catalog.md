---
sidebar_position: 7
title: "Automation Blueprints Catalog"
description: "Ready-to-run automation blueprints — set one up from the dashboard, CLI, TUI, any messenger, or the desktop app."
---

import AutomationBlueprintsCatalog from '@site/src/components/AutomationBlueprintsCatalog';

# 自动化蓝图

自动化蓝图即可直接运行的自动化任务。只需选择一个蓝图，填写少量字段，Hermes便会将其作为定时任务安排执行——无需掌握复杂的cron语法。

每个蓝图都支持通过**多种方式**进行操作：

- **控制面板/桌面应用**：打开Cron页面，切换到**Blueprints**标签页，填写表单后点击*Schedule it*即可。
- **CLI、TUI及消息工具**：输入`/blueprint <名称>`（例如`/blueprint morning-brief`），Hermes会逐个询问所需信息，随后安排任务执行。名称匹配具有容错性——前缀相同或拼写相近即可识别。高级用户可通过直接传入参数来跳过提问步骤：`/blueprint morning-brief time=08:00`。
- **桌面应用**：点击任意蓝图上的**Send to App**按钮，该蓝图即会在您的composer中预加载对应命令后打开。

自动化蓝图绝不会在后台悄悄安排任务——在任务创建前您必须进行确认。您可以随时使用`/cron`命令来管理已创建的任务。

<AutomationBlueprintsCatalog />

## 自定义编写

实际上，蓝图只不过是一种在`SKILL.md`文件的前置信息中包含`metadata.hermes.blueprint`块的技能而已。关于该字段的结构规范以及如何发布自定义蓝图，请参阅[创建技能 → 自动化蓝图](../developer-guide/creating-skills.md)。
