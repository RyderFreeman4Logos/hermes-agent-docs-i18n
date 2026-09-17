# CLI 参考 — `sg` / `ast-grep`

本文档提供了该辅助工具所封装的底层 `sg` 工具的简明参考。当辅助工具功能不足或需要直接调用 `sg` 时，可使用本参考。

> **Linux 系统中的命令名**：建议优先使用 `ast-grep` 而非 `sg`，因为 `sg` 的名称与 `util-linux` 工具包中的 `setgroups` 命令冲突。

---

## `sg run` — 单次搜索/重写

默认子命令。`sg -p 'foo'` 是 `sg run -p 'foo'` 的简写形式。

```bash
sg run [OPTIONS] --pattern <PATTERN> [PATHS...]
```

| 标志 | 用途 |
|---|---|
| `-p, --pattern <P>` | 需要匹配的 AST 模式。在 shell 中**务必使用单引号**，以避免 `$VAR` 被展开。 |
| `-r, --rewrite <R>` | 替换模式。需与 `-U` 一起使用才能生效。 |
| `-l, --lang <LANG>` | 语言类型。若未指定，则根据文件扩展名自动推断。 |
| `--selector <KIND>` | 当模式存在歧义时，仅提取该类的 AST 元素。 |
| `--strictness <S>` | `cst` \| `smart`（默认）\| `ast` \| `relaxed` \| `signature` |
| `--debug-query[=<F>]` | 打印解析后的模式。F：`pattern` \| `ast` \| `cst` \| `sexp` |
| `--stdin` | 从标准输入读取代码而非文件。此时必须指定语言类型。 |
| `--globs <G>` | 包含或排除某些文件模式（可重复使用；前缀加 `!` 表示排除）。 |
| `--follow` | 跟随符号链接。 |
| `--no-ignore <T>` | 禁用某类忽略规则：`hidden`、`dot`、`exclude`、`global`、`parent`、`vcs`。 |
| `-i, --interactive` | 逐个检查匹配结果，并要求用户确认每次替换操作。 |
| `-U, --update-all` | 不经确认即应用所有替换操作。**与 `--json`（静默模式）互斥**。 |
| `--json[=<S>]` | 以 JSON 格式输出结果。S：`pretty` \| `stream` \| `compact`（`compact` 格式最适合作为管道输入）。 |
| `--color <W>` | 颜色显示模式：`auto` \| `always` \| `ansi` \| `never` |
| `--inspect <G>` | 详细程度：`nothing` \| `summary` \| `entity` |
| `-A, -B, -C <N>` | 每个匹配结果前后及周围的上下文行数。 |
| `-j, --threads <N>` | 线程数量（默认值：根据情况自动判断；`0` 表示自动）。 |

### `--update-all` + `--json` —— 一个陷阱

当设置了 `--json` 参数时，`sg` 会默默忽略 `--update-all` 参数。若要同时预览并应用更改，需执行**两次操作**：

```bash
# Pass 1: preview
sg run -p 'foo()' -r 'bar()' --json=compact src/

# Pass 2: apply
sg run -p 'foo()' -r 'bar()' --update-all src/
```

`ast_grep_helper.py replace --apply` 子命令可自动完成此项操作。

### 示例

```bash
# Basic search
sg run -p 'console.log($MSG)' --lang ts src/

# Search with context lines
sg run -p 'eval($CODE)' --lang js -C 3 .

# Rewrite, dry-run preview as JSON
sg run -p 'console.log($MSG)' -r 'logger.info($MSG)' --json=compact --lang ts src/

# Rewrite, apply
sg run -p 'console.log($MSG)' -r 'logger.info($MSG)' --update-all --lang ts src/

# Pattern from stdin
echo 'console.log("x")' | sg run -p 'console.log($MSG)' --lang js --stdin

# Limit to specific files
sg run -p 'foo()' --lang ts --globs 'src/**/*.ts' --globs '!**/*.test.ts' .

# Debug a pattern that returns 0 matches
sg run -p 'def $F($$$):' --lang py --debug-query=ast --stdin <<< 'def foo(): pass'
```

## `sg scan` — YAML规则扫描工具

用于在多个文件中执行YAML规则配置的扫描。适用于整个项目范围的代码检查与代码转换操作。

```bash
sg scan [OPTIONS] [PATHS...]
```

| 标志 | 用途 |
|---|---|
| `-c, --config <C>` | `sgconfig.yml` 的路径（默认：从当前工作目录向上查找）。 |
| `-r, --rule <F>` | 运行**单个**规则文件。与 `--config` 互斥。 |
| `--inline-rules <Y>` | 直接传入 YAML 规则文本。使用 `---` 分隔多个规则。 |
| `--filter <RE>` | 仅运行 `id` 匹配该正则表达式的规则。 |
| `--include-metadata` | 在 JSON 输出中包含规则的 `metadata` 字段。 |
| `-U, --update-all` | 自动应用 `fix:` 中指定的修复方案。 |
| `--report-style <S>` | `rich` \| `medium` \| `short` |
| `--format <F>` | `github` \| `sarif`（适用于持续集成环境的输出格式）。 |
| `--error[=ID]`, `--warning[=ID]`, `--info[=ID]`, `--hint[=ID]`, `--off[=ID]` | 提高/降低错误等级。 |
| `-i, --interactive` | 交互式确认每项修复操作。 |
| `--json[=<S>]` | 输出为 JSON 格式。 |

### 示例

```bash
# Run all rules in sgconfig.yml-discovered ruleDirs
sg scan src/

# Run a single rule file (no sgconfig.yml needed)
sg scan -r rules/no-console.yml src/

# Inline rule (great for one-offs and CI)
sg scan --inline-rules '
id: no-todo
language: TypeScript
severity: warning
rule: { pattern: TODO }' src/

# Apply all auto-fixes
sg scan -U src/

# CI-friendly GitHub annotations
sg scan --format github src/

# SARIF for security scanners
sg scan --format sarif src/ > sarif.json
```

## `sg test` — 运行规则快照测试

```bash
sg test [OPTIONS]
```

| 标志 | 用途 |
|---|---|
| `-c, --config <C>` | `sgconfig.yml` 文件的路径。 |
| `-t, --test-dir <D>` | 测试目录。 |
| `--snapshot-dir <D>` | 快照目录（默认值为 `__snapshots__`）。 |
| `--skip-snapshot-tests` | 仅验证测试代码是否能正确解析，而不进行快照对比。 |
| `-U, --update-all` | 更新所有已更改的快照。 |
| `-f, --filter <G>` | 根据规则 ID 使用通配符筛选测试用例。 |
| `--include-off` | 包含严重级别为 `off` 的规则。 |
| `-i, --interactive` | 逐个查看已更改的快照，并对每个快照进行接受或拒绝操作。 |

测试目录的结构如下：

```
test/
├── no-console.yml          # `valid:` and `invalid:` snippets
└── no-console-test.yml     # alternative test file format
__snapshots__/
└── no-console-snapshot.yml # expected match locations
```

## `sg new` — 框架生成工具

```bash
sg new <COMMAND> [NAME] [OPTIONS]
```

| 子命令 | 创建内容 |
|---|---|
| `project` | `sgconfig.yml` 文件，以及 `rules/`、`utils/`、`__snapshots__/` 目录结构 |
| `rule` | 在第一个 `ruleDirs` 指定的目录中创建一个新的 YAML 规则文件 |
| `test` | 在 `testConfigs[0].testDir` 路径下创建一个新的测试文件 |
| `util` | 在第一个 `utilDirs` 指定的目录中创建一个新的工具规则文件 |

```bash
# New project in current dir
sg new project --yes

# New rule
sg new rule no-console --lang typescript

# New test
sg new test no-console --yes
```

## `sg lsp` — 语言服务器

```bash
sg lsp -c sgconfig.yml
```

通过标准输入/输出接口传输 LSP 信号。请配置您的编辑器（如 VS Code 扩展、Neovim 的 `nvim-lspconfig`、Helix 的 `languages.toml`），以便在实时诊断时调用该命令。  

---

## `sg completions` —— shell 自动补全功能

```bash
sg completions bash >> ~/.bashrc
sg completions zsh > "${fpath[1]}/_sg"
sg completions fish > ~/.config/fish/completions/sg.fish
sg completions powershell >> $PROFILE
```

## 实用快捷命令

```bash
# Count matches per file
sg run -p 'console.log($_)' --lang ts --json=compact . \
  | jq -r '.[].file' | sort | uniq -c | sort -rn

# Find all unique kinds in a file (great for figuring out kind names)
sg run -p '$_' --lang ts --debug-query=cst src/foo.ts \
  | grep -oE 'kind: [a-z_]+' | sort -u

# Rewrite only in a subset of files
sg run -p 'foo()' -r 'bar()' --update-all --globs 'src/**/*.ts' --globs '!src/legacy/**' .

# Apply fixes from many rules but only ones matching a pattern in their id
sg scan --filter 'no-' -U src/

# Use ast-grep as a linter in pre-commit
sg scan --format github src/ || exit 1
```

## 相关内容

- `references/yaml-rules.md` — 规则架构（`pattern`、`kind`、`regex`、`inside`、`has`、`all`、`any`、`not`、`matches`、`transform`、`fix`）。
- `references/sgconfig.md` — 项目配置。
- 官方文档：<https://ast-grep.github.io/reference/cli.html>
