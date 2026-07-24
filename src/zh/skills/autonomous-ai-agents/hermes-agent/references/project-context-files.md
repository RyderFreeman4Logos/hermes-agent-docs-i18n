# 项目上下文文件

Hermes 会通过读取工作目录中的上下文文件，将项目级指令注入系统提示词中。文件的查找顺序遵循“**首次匹配即生效**”原则——每个会话仅加载一个项目上下文来源。

| 文件（按优先级排序） | 查找方式 | 适用场景 |
|---|---|---|
| `.hermes.md` / `HERMES.md` | 从当前目录向上遍历至 git 根目录，最终在根目录停止 | 需要分层级的项目规则（根目录规则 + 各包的覆盖规则） |
| `AGENTS.md` / `agents.md` | **仅限当前目录**——子目录及父目录中的副本将被忽略 | 需要可在 Hermes、Claude Code、Codex 等工具中通用且保持一致的智能体指令 |
| `CLAUDE.md` / `claude.md` | 仅限当前目录 | 与 AGENTS.md 类似，但针对 Claude 环境优化 |
| `.cursorrules` / `.cursor/rules/*.mdc` | 仅限当前目录 | 从 Cursor 迁移过来的用户使用 |

位于 `$HERMES_HOME` 目录下的 `SOUL.md` 文件独立存在，只要存在就会始终被加载——它用于设置智能体的身份信息，而非项目规则。

### 如何选择合适的文件

- **使用 `.hermes.md`**：当您需要适用于整个项目（根目录及子目录）的 Hermes 特有行为，或希望规则能从父目录继承时使用。由于遍历会在 git 根目录停止，因此位于用户主目录下的 `.hermes.md` 文件不会影响其他项目（git 仓库的根目录即为边界）。
- **使用 `AGENTS.md`**：当同一个项目还需要由其他智能体（如 Codex、Claude Code、OpenCode）处理时适用。这些工具对 `AGENTS.md` 都有各自的格式规范，而“仅限当前目录”的设计确保了该文件的通用性。
- **请勿将项目规则放入 `~/.hermes/AGENTS.md`**（或任何其他用户主目录下的位置）。当 Hermes 以该目录作为当前目录运行时，虽然文件会被加载，但仅对该目录有效。如需跨项目共享上下文，请使用位于 `$HERMES_HOME` 的 `SOUL.md`（仅用于设置身份信息），或通过 `hermes skills install` 前往安装技能。

### 文件大小与截断处理

每份上下文文件的字符数上限为 20,000 字符。超过此限制的文件会被**截取开头和结尾部分**（中间内容会被删除，并显示 `[...truncated...]` 标记）。对于内容庞大的项目规则，建议将其拆分为多个技能，而非将其全部塞入一个文件中。

### 安全性

所有上下文文件在进入系统提示词之前都会经过威胁模式扫描器检测。任何匹配到提示词注入或恶意提示词特征的内容都会被替换为 `[BLOCKED: ...]` 占位符。这意味着，即使 `AGENTS.md` 文件中包含明显的注入尝试，相关内容也不会传递给模型——扫描器会拦截内容本身，而不会阻止整个文件的加载。

### 临时禁用上下文加载

使用 `hermes --ignore-rules` 可以跳过所有项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`.cursorrules`）以及 `SOUL.md` 中的身份信息，同时还会忽略用户配置、插件和 MCP 服务器的加载。此选项可用于判断问题出在您的设置上，还是 Hermes 本身。

### 示例：一个简单的 `.hermes.md` 文件

```markdown
# My Project

Hermes: when working in this repo, follow these rules.

## Build
- Always run `make test` before declaring a change done.
- Use `uv run` for Python, not `pip install`.

## Style
- Prefer `pathlib.Path` over `os.path`.
- No `print()` in production code — use the `logger`.
```

当 Hermes 在 `/home/me/projects/myrepo` 的任意子目录中运行时，会自动加载位于 `/home/me/projects/myrepo/.hermes.md` 的该文件；但若在 `/home/me/other-project` 中运行，则不会加载该文件。
