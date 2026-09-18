---
title: "Ast Grep — AST-aware structural code search and rewrite via ast-grep"
sidebar_label: "Ast Grep"
description: "AST-aware structural code search and rewrite via ast-grep"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Ast Grep

通过 ast-grep 实现基于抽象语法树的结构化代码搜索与重写功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/software-development/ast-grep` 安装 |
| 路径 | `optional-skills/software-development\ast-grep` |
| 版本 | `1.0.0` |
| 开发者 | Yeongyu Kim (code-yeongyu)，由 Hermes Agent 改编 |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `ast`、`codemod`、`refactoring`、`structural-search`、`code-search`、`rewrite`、`tree-sitter` |
| 相关技能 | [`simplify-code`](/docs/user-guide/skills/bundled/software-development/software-development-simplify-code)、[`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，智能体所看到的指令即为此内容。
:::

# ast-grep

`ast-grep`（其二进制文件名也为 `sg`）是一款支持 **25 种语言**的、基于抽象语法树的搜索与重写工具。它将您的搜索模式视为代码，以与解析项目代码相同的方式对其进行解析，并基于结构进行匹配。每当您的需求取决于代码的结构而非文本字节时，它都是理想的工具。

该技能提供了一个位于 `scripts/ast_grep_helper.py` 的 Python 封装脚本，以及分别适用于 POSIX 系统的 `install.sh` 和 Windows 系统的 `install.ps1` 安装脚本。该辅助工具具备离线模式下的正则表达式验证功能、两阶段写入技巧以及二进制文件自动解析能力，建议将其作为默认的查询入口。

上游来源：该技能源自 [code-yeongyu/ast-grep-skill](https://github.com/code-yeongyu/ast-grep-skill)（采用 MIT 许可协议），并已包含在 oh-my-openagent 的 shared-skills 包中。

---

## 何时使用此技能

当查询内容涉及**代码结构**而非字节数据时，可使用此技能：

- “找出所有接受 `Request` 参数的函数。”
- “将所有的 `console.log(x)` 替换为 `logger.info(x)`。”
- “移除所有 `as any` 类型的类型转换。”
- “在整个项目中将 `require(...)` 替换为 `import`。”
- “查找所有空的 catch 块。”
- “将 `Optional[X]` 转换为 `X | None`。”
- “对这 200 个文件应用此代码修改规则。”
- “运行我们的 YAML 格式检查规则并显示违规项。”

当查询内容为文本形式（如字符串字面量、注释、许可证头信息、文件名或跨语言正则表达式）时，建议使用 `search_files`（或直接使用 `rg`）。如有疑问，可自问：“答案是否依赖于该语言的语法树，还是仅取决于文件的字节数据？”若是前者，则选择 ast-grep；若是后者，则选择 search_files。

Hermes 集成说明：
- 通过 `terminal` 工具运行辅助工具及 `sg`。需为每个模式加上单引号，以防止 shell 扩展 `$VAR` 的值。
- 对匹配项周围的查找→读取操作链，建议使用 `--json-out` 输出结果，并通过 `execute_code` 处理，而非将其传递给解释器处理。
- 该工具是对 Hermes 自带 `patch` 工具的补充（而非替代）：`patch` 用于执行用户自定义的精准编辑，而 ast-grep 则适用于基于模式对多个目标进行批量重写。

---

## Agent 需要牢记的三大要点

### 1. ast-grep 并非正则表达式

其通配符为 `$VAR`（表示一个 AST 节点）和 `$$$`（表示零个或多个节点）。正则表达式语法在此处将导致静默失败：

| 用户输入 | ast-grep 的解析结果 | 实际需求 |
|---|---|---|
| `foo\|bar` | 将 `foo` 和 `bar` 视为按位或运算 | 执行两次独立的搜索 |
| `.*foo` | 无法解析 | 应使用 `$$$ foo`（若 `$$$` 表示节点列表），或改用 rg |
| `\w+` | 无法解析 | 应使用 `$VAR` 来匹配任意标识符 |
| `[a-z]` | 字符类，无法解析 | 应改用 rg |

完整的错误用例表详见 `references/pitfalls.md` 的第 1 节。辅助工具的 `validate` 子命令可自动检测这些错误——在手动排查“无匹配结果”问题之前，建议先调用此命令。

### 2. 模式必须是有效的代码

模式本身必须能够被解析。例如 `def $FN($$$):` 因结尾的冒号导致语句不完整，应改为 `def $FN($$$)`。不含参数或代码体的 `function $NAME` 也无法通过验证，应写成 `function $NAME($$$) { $$$ }`。各语言的详细规则可见 `references/pitfalls.md` 的第 2 节。

### 3. `--update-all` 与 `--json` 参数无法同时使用（会静默失败）

在编写脚本时，这是个最容易让人忽视的陷阱。《sg run -p P -r R --json --update-all》命令虽然会返回 JSON 格式的结果，但**并不会修改任何文件**。若需同时查看预览结果并实际应用更改，必须执行**两次操作**：

```bash
sg run -p P -r R --json=compact .   # pass 1: see what would change
sg run -p P -r R --update-all .     # pass 2: actually apply
```

当您调用 `replace --apply` 时，该辅助工具会自动执行此操作。详情请参阅 `references/pitfalls.md` 的第 9 节。

---

## 辅助脚本 — `scripts/ast_grep_helper.py`

这是一个基于 Python 3 标准库的单文件封装程序，在所有操作系统中格式一致，也是代理程序的默认入口点。

### `search` — 查找模式的所有匹配项

```bash
python scripts/ast_grep_helper.py search 'console.log($MSG)' --lang ts src/
```

首先会离线验证该模式是否有效。如果该模式属于正则表达式形式（如 `\w`、`.*`、`|` 等），该工具会给出提示后直接退出，而不会调用 `sg` 函数——从而避免不必要的往返操作。如需跳过验证，可使用 `--force` 参数。

标志选项：
- `--lang ts`（或任意 25 种语言；也支持 `js`、`py`、`rs`、`kt` 等别名）
- `--globs '!**/*.test.ts'`（可重复使用；前缀 `!` 表示排除）
- `-C 3`（上下文行数）
- `--json-out`（以原始 JSON 格式输出，而非易读格式）

### `replace` — 按模式重写内容，默认为试运行模式

```bash
# Dry-run preview (default — no files mutated)
python scripts/ast_grep_helper.py replace 'console.log($MSG)' 'logger.info($MSG)' --lang ts src/

# Actually apply
python scripts/ast_grep_helper.py replace 'console.log($MSG)' 'logger.info($MSG)' --lang ts src/ --apply
```

该辅助工具的功能如下：
1. 检查 `pattern` 和 `rewrite` 的内容，确保不存在可被提示系统识别的错误。
2. 使用 `--json=compact` 参数运行第一轮扫描，以收集匹配结果并显示预览内容。
3. 若指定了 `--apply` 参数，则会使用 `--update-all` 参数运行第二轮扫描，从而对文件进行实际修改。

### `scan` — 执行 YAML 规则扫描

```bash
# Discover sgconfig.yml from cwd and run all rules
python scripts/ast_grep_helper.py scan src/

# Run a single rule file
python scripts/ast_grep_helper.py scan -r rules/no-console.yml src/

# Apply auto-fixes
python scripts/ast_grep_helper.py scan -U src/

# CI-friendly GitHub annotations
python scripts/ast_grep_helper.py scan --report-style short src/
```

### `validate` — 离线模式检查（无需调用 `sg`）

适用于 CI 代码检查、预提交钩子以及快速合理性验证：

```bash
python scripts/ast_grep_helper.py validate '\w+' --lang ts
# → exit 2: regex \w not supported. Use $VAR for identifiers.

python scripts/ast_grep_helper.py validate 'console.log($MSG)' --lang ts
# → exit 0: pattern looks plausible for ast-grep.
```

### `langs` / `doctor` / `install`

```bash
python scripts/ast_grep_helper.py langs       # list 25 supported languages and aliases
python scripts/ast_grep_helper.py doctor      # check ast-grep binary availability
python scripts/ast_grep_helper.py install     # delegate to install.sh / install.ps1
```

`new` 和 `test` 子命令会直接调用 `sg new` 和 `sg test`。  

---

## 直接使用 `sg`（当辅助工具不够用时）

该辅助工具存在一定的固有限制。如需完全掌控操作流程，可直接使用 `sg`。该技能在 `references/cli.md` 中提供了 CLI 使用指南，其中列出了最基本的操作方式：

```bash
# Search
sg run -p 'console.log($MSG)' --lang ts src/

# Search with JSON for scripting
sg run -p 'console.log($MSG)' --lang ts --json=compact src/

# Rewrite, dry-run
sg run -p 'console.log($MSG)' -r 'logger.info($MSG)' --lang ts --json=compact src/

# Rewrite, apply
sg run -p 'console.log($MSG)' -r 'logger.info($MSG)' --lang ts --update-all src/

# Pattern from stdin (great for ad-hoc experiments)
echo 'console.log("hi")' | sg run -p 'console.log($MSG)' --lang js --stdin

# Debug a pattern that returns 0 matches
sg run -p '<your pattern>' --lang <lang> --debug-query=ast --stdin <<< '<sample-code>'

# Run YAML rules
sg scan src/

# Inline YAML rule (one-off)
sg scan --inline-rules '
id: no-todo
language: TypeScript
severity: warning
rule: { pattern: TODO }' src/
```

在shell中直接使用`sg`命令时，**务必对模式使用单引号**，这样才能避免shell对` $VAR `进行扩展。
```
USER asks for "find/rewrite/codemod"
│
├─ structural pattern (function shape, call, class, import, control flow)
│  └→ ast-grep (this skill)
│
├─ text pattern (regex, alternation, character classes, file names)
│  └→ search_files / rg
│
├─ semantic question (what variable does this refer to? does this throw?)
│  └→ LSP tools, TypeScript compiler, Pyright, Semgrep with type inference
│
└─ multiple repos / federated search
   └→ a search engine + then ast-grep / rg / LSP per-repo
```
<!-- ascii-guard-ignore-end -->

如果用户输入“find all”或“every”，且目标为结构化元素（函数、类、调用、导入、语句），则默认使用ast-grep进行搜索；若目标为文本内容（字符串、注释、许可证头、文件名、标识符子串），则默认使用search_files。

---

## 重写时务必先执行试运行

错误的模式可能会在不知不觉中修改错误的内容。正因如此，该工具的`replace`功能默认会先进行试运行。操作流程如下：

1. 先搜索以确认匹配项：`helper search '<pattern>' --lang X .`
2. 执行试运行重写：`helper replace '<pattern>' '<rewrite>' --lang X .`（不使用`--apply`选项）
3. 查看试运行结果摘要：包括匹配数量、受影响的文件以及各位置的预览内容。
4. 若结果有误，则优化模式，返回步骤1。
5. 若结果正确，则执行：`helper replace '<pattern>' '<rewrite>' --lang X . --apply`。

切勿在不先进行试运行的情况下直接应用重写结果。在Git仓库中使用`--apply`选项后，应在提交前通过`git diff --stat`检查变更内容。

---

## 当`sg`显示无匹配项但您确定代码存在时

请按以下优先级顺序处理：

1. **运行 `helper validate '<pattern>' --lang <lang>`** — 用于检测正则表达式使用错误、函数体缺失以及 Python 代码中多余的冒号。  
2. **检查 `--lang` 参数** — `sg` 会根据文件扩展名自动推断语言类型；若你传入 `.tsx` 文件却指定 `--lang ts`（而非 `tsx`），JSX 将无法被解析。  
3. **查看已解析的模式**：使用命令 `sg run -p '<pattern>' --lang <lang> --debug-query=ast --stdin <<< '<sample>'`。若输出中出现 `ERROR` 节点，说明该模式格式有误。  
4. **检查目标文件的抽象语法树（AST）**：执行命令 `sg run -p '$_' --lang <lang> --debug-query=cst path/to/file | head -40`，即可找到你需要匹配的节点类型。  
5. **使用在线演示工具**：&lt;https://ast-grep.github.io/playground.html&gt; — 仅需粘贴代码与模式，即可实时查看处理结果。

切勿盲目尝试不同变体重新运行。每次失败都有其原因，需找出具体问题所在。

---

## 何时使用 YAML 规则与内联 `-p` 模式

**选择内联 `-p` 模式**的情况包括：  
- 临时性的即兴查询；  
- 模式较为简单（无约束条件，也无修复模板）；  
- 正在探索功能时。

**选择 YAML 规则**（规则文件存放在 `rules/` 目录中，通过 `sg scan` 命令运行）的情况包括：  
- 该模式会被重复使用（如代码检查规则、在 CI 环境中运行的代码修改工具）；  
- 需要使用约束条件、转换功能、复杂的 `inside`/`has` 判断或复合逻辑；  
- 希望实现自动修复功能（通过 `fix:` 字段实现）；  
- 希望对规则进行测试（通过 `sg test` 执行快照测试）。

完整的 YAML 规则结构定义位于 `references/yaml-rules.md` 文件中。项目配置相关内容（如 `sgconfig.yml`、`ruleDirs`、`utilDirs`）则记载在 `references/sgconfig.md` 中。

---

## 输出规范

- 使用 `sg run --json=compact` 命令会生成一个匹配对象数组，每个对象的结构为：`{ file, range: {start, end}, text, replacement?, lines, language, ... }`。
- 若不使用 `--json` 参数，`sg` 命令会输出适合在终端中查看的彩色格式文本。
- 该辅助工具的默认输出格式为易读形式（文件名：行号：列号 + 匹配内容预览）；如需获取原始 JSON 数据，请使用 `--json-out` 参数。
- 该辅助工具在执行替换操作时，总会同步显示汇总信息：匹配总数、受影响的文件数量以及各位置的匹配内容预览。

在向用户总结结果时，**务必同时说明受影响的文件数量，而不仅仅是匹配总数**。因为用户关心的是错误影响的范围。

---

## 推荐阅读资料（按优先级排序）

1. `references/patterns.md` —— 元变量、命名规则及严格程度设置。当不确定某个模式为何无法匹配时，请查阅此文档。
2. `references/pitfalls.md` —— 失败模式指南。当发现没有匹配结果时，请先阅读此文档。
3. `references/recipes.md` —— 按编程语言分类的现成模式模板。开始新任务时，首先阅读此文档。
4. `references/cli.md` —— 包含 `sg run`、`sg scan`、`sg test`、`sg new`、`sg lsp` 等命令的使用说明。当辅助工具无法满足需求时，请查阅此文档。
5. `references/yaml-rules.md` —— YAML 规则结构说明。当内联模式已无法满足需求时，请阅读此文档。
6. `references/sgconfig.md` —— 项目级配置设置。在为实际项目配置 `sg scan` 功能时，请查阅此文档。
7. `references/install.md` —— 各操作系统的安装方法。仅当 `install.sh` / `install.ps1` 脚本执行失败时才需查阅。

---

## 不可违背的规则（严禁更改）

- **搜索前先进行验证。** 当通过编程方式生成匹配模式时，应首先调用 `helper validate` 函数。该函数能捕获约 70% 导致“未找到匹配项”的错误，这类错误大多源于正则表达式的误用。
- **应用前先进行试运行。** 在未先查看匹配结果的情况下，切勿直接运行 `sg run -r ... --update-all` 命令。该工具的 `replace` 功能会默认强制执行此步骤。
- **分两步完成写入操作。** 若需直接使用 `sg` 函数同时进行预览和实际应用，应分别执行两次调用——因为 `--json` 参数会忽略 `--update-all` 的作用。
- **在 Shell 中请使用单引号包裹模式。** 应使用 `'$VAR'` 而非 `"$VAR"`。因为在双引号中，Shell 会将 `$VAR` 替换为空字符串，从而导致匹配模式失效。
- **匹配模式属于代码而非正则表达式。** 若模式中需要使用 `|`、`.*`、`\w` 或 `[a-z]` 等符号，建议改用 `search_files` 函数。切勿强行将 ast-grep 强制转换为正则表达式格式。
- **通过标准输入时必须指定语言参数。** 当使用 `--stdin` 参数传递数据时，需明确设置 `--lang` 参数；因为 `sg` 函数无法仅通过文件扩展名推断语言类型。
- **在 Linux 系统中，建议优先使用 `ast-grep` 而非 `sg`**，原因是 `sg` 的名称可能与 `util-linux` 工具中的 `setgroups` 命令发生冲突。该辅助工具已解决了这一问题；若直接调用 `sg`，可为其设置别名：`alias sg=ast-grep`。
