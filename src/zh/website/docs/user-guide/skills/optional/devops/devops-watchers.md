---
title: "Watchers — Poll RSS, JSON APIs, and GitHub with watermark dedup"
sidebar_label: "Watchers"
description: "Poll RSS, JSON APIs, and GitHub with watermark dedup"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请修改源文件 SKILL.md，而非此页面。 */}

# 监视器

定期轮询 RSS、JSON API 和 GitHub 并通过水印机制去重。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/devops/watchers` 安装 |
| 路径 | `optional-skills/devops/watchers` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux, macos |
| 标签 | `cron`, `polling`, `rss`, `github`, `http`, `automation`, `monitoring` |

## 参考：完整 SKILL.md

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令作为操作指南。
:::

# 监视器

定期轮询外部数据源，并仅对新增内容作出响应。提供三个现成脚本以及一个通用的水印辅助工具；可将它们集成到 cron 作业中（或直接从终端运行）。

## 适用场景

- 用户希望监控 RSS/Atom 订阅源，并在有新内容时收到通知
- 用户希望监控 GitHub 仓库中的问题、拉取请求、版本发布和代码提交
- 用户希望轮询任意 JSON 接口，并在有新数据时获得通知
- 用户要求“为 X 创建一个监视器”或“在 X 发生变化时通知我”

## 工作原理

监视器本质上只是一个脚本，其功能包括：

1. 从外部数据源获取数据
2. 将其与之前记录的水印文件中的 ID 进行比对
3. 将新的水印信息写回文件
4. 将新内容输出到标准输出（若无变化则不输出任何内容）

下面的三个脚本均实现了上述功能。Agent 可通过终端工具、cron 作业、Webhook 或交互式聊天来运行这些脚本，并反馈最新变化。

## 现成脚本

安装该技能后，这三个脚本都会位于 `$HERMES_HOME/skills/devops/watchers/scripts/` 目录下。每个脚本都会读取 `WATCHER_STATE_DIR`（默认为 `$HERMES_HOME/watcher-state/`）中的状态文件，状态文件的键由 `--name` 参数指定。

| 脚本 | 监控内容 | 去重键 |
|---|---|---|
| `watch_rss.py` | RSS 2.0 或 Atom 订阅源地址 | `<guid>` / `<id>` |
| `watch_http_json.py` | 任何返回对象列表的 JSON 接口 | 可配置的 ID 字段 |
| `watch_github.py` | 指定 GitHub 仓库的问题、拉取请求、版本发布和代码提交 | `id` / `sha` |

这三个脚本的共同特点包括：

- 首次运行时会记录基准数据，不会重复处理已有的内容
- 采用有限范围的 ID 集合（最多 500 个）以控制内存占用
- 每条内容的输出格式为：`## <标题>\n<url>\n\n<可选内容>`
- 若无新内容则标准输出为空，调用方可将其视为无变化
- 获取数据时出错则会返回非零退出码

## 使用方法

直接通过终端工具运行监视器：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_rss.py \
  --name hn --url https://news.ycombinator.com/rss --max 5
```

监控 GitHub 仓库（请在 `${HERMES_HOME:-~/.hermes}/.env` 中设置 `GITHUB_TOKEN`，以避免每小时 60 次的匿名请求限制）：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_github.py \
  --name hermes-issues --repo NousResearch/hermes-agent --scope issues
```

轮询任意 JSON API：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_http_json.py \
  --name api --url https://api.example.com/events \
  --id-field event_id --items-path data.events
```

## 与 cron 的集成

可通过如下提示语让智能体安排 cron 任务：

> 每 15 分钟运行一次 `watch_rss.py --name hn --url https://news.ycombinator.com/rss`。如果该脚本输出了内容，则汇总相关标题并发送出去；若无输出，则保持沉默。

智能体会在 cron 任务的智能体循环中通过终端工具来调用该脚本，无需对 cron 内置的 `--script` 参数进行任何修改。

## 状态文件

每个监控器都会生成 `$HERMES_HOME/watcher-state/<名称>.json` 文件。可对此文件进行检查：

```bash
cat $HERMES_HOME/watcher-state/hn.json
```

强制重新执行（将下一次运行视为首次查询）：

```bash
rm $HERMES_HOME/watcher-state/hn.json
```

## 自定义脚本编写

这三种脚本均采用相同的结构模板：加载水印、获取数据、进行差异对比、保存结果以及输出信息。`scripts/_watermark.py` 是一个通用的辅助工具，导入该文件即可免费获得原子化写入功能、受限的 ID 集以及首次运行时的基准数据。只需查看任意一个参考脚本，就能了解其所需的样板代码量其实非常少。

## 常见问题

1. **在每次循环时都打印“无新项目”的提示信息**。调用方通常认为空的标准输出即代表没有变化。如果在为空的差异数据上仍打印内容，就会造成通道信息过载。现有脚本已解决了此问题，自定义脚本同样需要做到这一点。
2. **误以为首次运行时会输出项目数据**。实际上并不会——首次运行仅用于记录基准数据。如果需要初始摘要，可在首次运行后删除状态文件，或在自己的脚本中添加 `--prime-with-latest N` 参数。
3. **水印数量无限制增长**。通用辅助工具将 ID 数量上限设定为 500 个。对于数据更新频繁的源数据，可提高此上限；在磁盘空间有限的系统中，则应适当降低该数值。
4. **将状态目录设置在代理程序的沙箱环境无法写入的位置**。`$
