# 磁盘清理功能

自动检测并清理 Hermes Agent 会话期间生成的临时文件——包括测试脚本、临时输出内容、cron 日志以及过期的 Chrome 配置文件。该功能仅作用于 `$HERMES_HOME` 和 `/tmp/hermes-*` 目录。

该功能最初由 [@LVT382009](https://github.com/LVT382009) 在 PR #12212 中以技能形式提交。后来被整合到插件系统中，通过 `post_tool_call` 和 `on_session_end` 回调函数实现自动清理——Agent 无需手动触发清理操作。

## 工作原理

| 回调函数 | 功能说明 |
|---|---|
| `post_tool_call` | 当 `write_file` / `terminal` / `patch` 等工具在 `HERMES_HOME` 目录下生成名为 `test_*`、`tmp_*` 或 `*.test.*` 的文件时，会将其悄悄标记为 `test`、`temp` 或 `cron-output` 类型。 |
| `on_session_end` | 若在本轮会话中有任何测试文件被自动标记，将立即执行快速清理操作（无需用户确认）。 |

删除规则与原始 PR 保持一致：

| 文件类别 | 删除阈值 | 是否需要确认 |
|---|---|---|
| `test` | 每次会话结束 | 不需要 |
| `temp` | 自标记起超过7天 | 不需要 |
| `cron-output` | 自标记起超过14天 | 不需要 |
| `HERMES_HOME` 下的空目录 | 始终删除 | 不需要 |
| `research` | 超过30天，且保留最近10个文件外 | 始终删除（仅深度扫描） |
| `chrome-profile` | 自标记起超过14天 | 始终删除（仅深度扫描） |
| 大于500 MB的文件 | 不会自动删除 | 始终删除（仅深度扫描） |

## 斜杠命令

```
/disk-cleanup status                     # breakdown + top-10 largest
/disk-cleanup dry-run                    # preview without deleting
/disk-cleanup quick                      # run safe cleanup now
/disk-cleanup deep                       # quick + list items needing prompt
/disk-cleanup track <path> <category>    # manual tracking
/disk-cleanup forget <path>              # stop tracking
```

## 安全性

- `is_safe_path()` 函数会拒绝位于 `HERMES_HOME` 或 `/tmp/hermes-*` 路径之外的任何文件或目录。
- Windows 系统下的挂载路径（如 `/mnt/c` 等）同样会被拒绝。
- 状态目录 `$HERMES_HOME/disk-cleanup/` 本身也不在监控范围内。
- `$HERMES_HOME/logs/`、`memories/`、`sessions/`、`skills/`、`plugins/` 目录以及各类配置文件均不会被跟踪。
- 备份与恢复操作仅针对 `tracked.json` 文件进行——该插件绝不会触碰代理的日志文件。
- 支持原子性写入操作：先写入临时文件，再进行备份，最后重命名。
