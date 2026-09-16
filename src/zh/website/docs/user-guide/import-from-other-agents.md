---
sidebar_position: 9
title: "Import from Other Agents"
description: "One-command import of a Claude Code (~/.claude) or OpenAI Codex CLI (~/.codex) setup into Hermes — instructions, allowlists, MCP servers, skills, and memories."
---

# 从其他 Agent 导入

`hermes import-agent` 可通过一条命令将您现有的 **Claude Code** 或 **OpenAI Codex CLI** 环境导入 Hermes。它采用了与 [`hermes claw migrate`](../guides/migrate-from-openclaw.md) 相同的“先预览”模式：在实际执行任何操作之前，您都会看到针对每个项目的详细计划，且 `--dry-run` 参数绝对不会对磁盘进行任何写入操作。

```bash
hermes import-agent                    # auto-detect ~/.claude or ~/.codex
hermes import-agent claude-code        # import from ~/.claude
hermes import-agent codex              # import from ~/.codex
hermes import-agent claude-code --dry-run          # preview only
hermes import-agent codex --source /path/to/.codex # custom location
hermes import-agent claude-code --overwrite --yes  # replace conflicts, skip prompts
```

## 会被导入的内容

### Claude Code（`~/.claude`）

| Claude Code | Hermes |
|---|---|
| `CLAUDE.md`（全局指令） | `~/.hermes/memories/MEMORY.md` 中的记忆条目 |
| `settings.json` → `permissions.allow`（`Bash(...)` 规则） | `config.yaml` 中的 `command_allowlist` |
| `settings.json` → `permissions.deny`（`Bash(...)` 规则） | `config.yaml` 中的 `approvals.deny` |
| `mcpServers`（来自 `~/.claude.json` 和 `settings.json`） | `config.yaml` 中的 `mcp_servers` |
| `skills/<name>/`（包含 `SKILL.md` 的目录） | `~/.hermes/skills/claude-code-imports/<name>/` |
| `commands/*.md`（斜杠命令） | 会被跳过并附带提示——建议将其转换为技能 |

Claude 中以 `Bash(npm run test:*)` 形式的规则会转换为 `npm run test*` 这种通配符形式。非 `Bash` 类型的权限规则（如 `Read(...)`, `WebFetch` 等）用于控制 Claude 特有的工具，这类规则会被标记为未映射而非被导入。

### Codex CLI（`~/.codex`）

| Codex CLI | Hermes |
|---|---|
| `AGENTS.md`（全局指令） | `~/.hermes/memories/MEMORY.md` 中的记忆条目 |
| `config.toml` → `[mcp_servers.*]` | `config.yaml` 中的 `mcp_servers` |
| `memories/*.md` | `~/.hermes/memories/MEMORY.md` 中的记忆条目 |
| `skills/<name>/`（包含 `SKILL.md` 的目录） | `~/.hermes/skills/codex-imports/<name>/` |

## 永远不会被导入的内容

**API 密钥与凭据。** 系统绝不会读取凭据文件（如 `~/.claude/.credentials.json`、`~/.codex/auth.json`），同时也会移除 MCP 服务器环境变量或名称中带有敏感信息特征的请求头（如 `*_TOKEN`、`*_API_KEY`、`Authorization` 等），并将其列出在报告中，以便您手动重新添加。如需配置提供程序，可运行 `hermes setup`；或将敏感信息添加到 `~/.hermes/.env` 文件中。

## 行为说明

- **始终先预览。** 该命令会在执行前先输出完整的操作计划；在非交互式会话中，除非您使用 `--yes` 参数，否则会停留在预览阶段。
- **合并而非替换。** 系统会根据您现有的 `MEMORY.md` 文件对内存条目进行去重处理；允许列表/拒绝列表规则则会与 `config.yaml` 中的现有规则合并。
- **默认跳过冲突项。** 若 MCP 服务器或技能已在 Hermes 中存在，系统会将其标记为冲突项；如需替换该内容，请使用 `--overwrite` 参数。
- **格式错误的文件不会导致运行中断。** 即使 `settings.json` 或 `config.toml` 文件存在错误，系统也只会将相关错误记录在报告中，其余内容仍会正常导入。
- 如果您是从 OpenClaw 迁移过来的，请使用 [`hermes claw migrate`](../guides/migrate-from-openclaw.md) 工具。
