---
title: "Watchers — Poll RSS, JSON APIs, and GitHub with watermark dedup"
sidebar_label: "Watchers"
description: "Poll RSS, JSON APIs, and GitHub with watermark dedup"
---

# 监视器

定期轮询 RSS、JSON API 以及 GitHub 数据，并通过水印机制实现去重处理。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/devops/watchers` 安装 |
| 路径 | `optional-skills/devops\watchers` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos |
| 标签 | `cron`、`polling`、`rss`、`github`、`http`、`automation`、`monitoring` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当该技能被触发时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 会将此内容视为操作指令。
:::

# 监视器

定期轮询外部数据源，仅对新增内容作出响应。该功能提供三个现成脚本以及一个通用的水印辅助工具；可将它们集成到 cron 作业中运行，或直接从终端手动执行。

## 适用场景

- 用户希望监控 RSS/Atom 订阅源，并在有新文章发布时收到通知
- 用户希望监控 GitHub 仓库中的问题、拉取请求、版本发布及代码提交记录
- 用户希望轮询任意 JSON 接口，并在新数据出现时获得通知
- 用户要求“为 X 创建一个监视器”或“在 X 发生变化时通知我”

## 工作原理

监视器本质上只是一个脚本，其功能包括：

1. 从外部数据源获取数据
2. 将获取到的 ID 与之前记录的水印文件进行比对
3. 将更新后的水印文件写回原处
4. 将新增内容输出到标准输出（若无变化则不输出任何内容）
以下脚本可同时处理这三种监控任务。Agent会通过终端工具执行这些脚本——无论是通过定时任务、Webhook还是交互式聊天方式——并反馈最新变化。

## 现成脚本

技能安装完成后，这三个脚本均位于 `$HERMES_HOME/skills/devops/watchers/scripts/` 目录下。每个脚本都会根据 `--name` 参数指定的键值，从 `WATCHER_STATE_DIR`（默认为 `$HERMES_HOME/watcher-state/`）中读取状态文件。

| 脚本名称 | 监控内容 | 去重键 |
|---|---|---|
| `watch_rss.py` | RSS 2.0或Atom订阅源URL | `<guid>` / `<id>` |
| `watch_http_json.py` | 任何返回对象列表的JSON接口 | 可配置的ID字段 |
| `watch_github.py` | 指定仓库的GitHub问题、拉取请求、版本发布及代码提交记录 | `id` / `sha` |

这三个脚本的共同特点如下：

- 首次运行时会记录基准数据，不会重复处理已有的订阅源内容
- 为限制内存占用，去重键采用有限集合形式（最多500个）
- 输出格式：每个监控项以 `## <标题>\n<url>\n\n<可选内容>` 的形式呈现
- 若没有新内容，则标准输出为空，调用方可将其视为无变化状态
- 在获取数据时出现错误时，脚本会以非零状态码退出

## 使用方法

可直接通过终端工具运行相应的监控脚本：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_rss.py \
  --name hn --url https://news.ycombinator.com/rss --max 5
```

观看 GitHub 仓库内容（为避免每小时 60 次的匿名访问限制，请在 `${HERMES_HOME:-~/.hermes}/.env` 中设置 `GITHUB_TOKEN`）：

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

可以通过如下提示语让代理安排 cron 任务：

> 每 15 分钟运行一次 `watch_rss.py --name hn --url https://news.ycombinator.com/rss`。如果该脚本输出了内容，则汇总相关标题并发送出去；如果没有输出，则保持静默。

代理会在 cron 任务的代理循环中通过终端工具来调用该脚本，无需对 cron 内置的 `--script` 参数进行任何修改。

## 状态文件

每个监控器都会生成 `$HERMES_HOME/watcher-state/<name>.json` 文件。可对此文件进行检查：

```bash
cat $HERMES_HOME/watcher-state/hn.json
```

强制重新执行（将下一次运行视为首次轮询）：

```bash
rm $HERMES_HOME/watcher-state/hn.json
```

## 自定义脚本编写

这三份脚本均采用相同的结构模板：加载水印、获取数据、进行差异对比、保存结果以及输出信息。`scripts/_watermark.py` 是通用的辅助脚本，导入该文件即可免费获得原子级写入功能、受限的 ID 集以及首次运行时的基准数据。只需查看这三份参考脚本，就能了解其所需的样板代码量其实非常少。

## 常见误区

1. **在每次循环时都打印“无新内容”提示。** 调用方通常认为标准输出为空即表示没有变化。如果在空的数据差异上仍打印内容，就会造成通道信息过载。官方提供的脚本已解决了此问题，自定义脚本同样需要做到这一点。
2. **误以为首次运行时会输出数据。** 实际并非如此——首次运行仅用于记录基准数据。如果需要初始摘要，可在首次运行后删除状态文件，或在自己的脚本中添加 `--prime-with-latest N` 参数。
3. **水印数量无限制增长。** 通用辅助脚本将 ID 数量上限设定为 500 个。对于数据更新频繁的源数据，可提高此上限；在磁盘空间有限的系统中，则应适当降低该值。
4. **将状态目录设置在代理程序的沙箱环境无法写入的位置。** `$HERMES_HOME/watcher-state/` 目录始终是可写的。而 Docker/Modal 后端可能无法访问主机上的任意路径。
