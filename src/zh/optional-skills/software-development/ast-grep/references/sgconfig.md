# sgconfig.yml — 项目配置

`sgconfig.yml` 位于项目的根目录中（与 `package.json`、`Cargo.toml`、`pyproject.toml` 等文件处于同一位置），用于告知 `sg scan`/`sg test` 在何处查找规则和测试用例。

`sg` 会从当前目录**向上递归搜索**，直到找到 `sgconfig.yml`。您也可以直接通过 `--config <路径>` 参数指定配置文件的位置。

---

## 最简项目结构

```
my-project/
├── sgconfig.yml
├── rules/
│   ├── no-console.yml
│   └── no-as-any.yml
├── utils/
│   └── is-literal.yml
├── tests/
│   ├── no-console.yml
│   └── __snapshots__/
│       └── no-console-snapshot.yml
└── src/
    └── ...
```

```yaml
# sgconfig.yml
ruleDirs:
  - rules

testConfigs:
  - testDir: tests
    snapshotDir: __snapshots__

utilDirs:
  - utils
```

就是这样。执行 `sg scan src/` 命令后，系统会加载 `rules/` 目录下的所有 `.yml` 文件，找出所有符合对应规则 `language` 要求的 `.ts`、`.py` 等格式的文件，并报告其中的违规问题。

---

## 完整架构说明

```yaml
# Rule directories — required
ruleDirs:
  - rules
  - team-rules
  - vendor/sg-rules

# Test directories — optional
testConfigs:
  - testDir: tests
    snapshotDir: __snapshots__
  - testDir: integration-tests

# Utility rule directories — optional
# Files here become global utilities accessible via `matches: <id>` from any rule.
utilDirs:
  - utils
  - team-utils

# Override file-extension -> language mapping — optional
# Useful when your code uses non-standard extensions.
languageGlobs:
  html:
    - '*.vue'
    - '*.svelte'
    - '*.astro'
  json:
    - '.eslintrc'
    - '.prettierrc'
  cpp:
    - '*.c'                  # treat C as C++
  tsx:
    - '*.ts'                 # treat all .ts as TSX (so TSX rules work everywhere)

# Custom tree-sitter languages (experimental) — optional
customLanguages:
  mojo:
    libraryPath: tree-sitter-mojo.so
    extensions: [mojo, '🔥']
    expandoChar: _           # Replace $ in patterns when language uses $ syntactically
    languageSymbol: tree_sitter_mojo

# Language injection — embedded code in another language (experimental) — optional
# Example: CSS inside styled-components template literals.
languageInjections:
  - hostLanguage: js
    rule:
      pattern: 'styled.$TAG`$CONTENT`'
    injected: css
```

## 逐项说明

### `ruleDirs`（必填）

`Array<string>` — 包含规则 YAML 文件的目录。该路径是相对于 `sgconfig.yml` 解析得到的。

这些目录中的每个 `.yml`/`.yaml` 文件都会被加载为一个规则。一个文件中可以通过 `---` 符号分隔多个规则。

### `testConfigs`

`Array<TestConfig>`，其中每个元素包含：

- `testDir`（必填）：测试 YAML 文件所在的目录。
- `snapshotDir`（可选，默认值为 `__snapshots__`）：快照文件存放的目录。

每个测试文件的格式如下：

```yaml
id: no-console
valid:
  - 'logger.info("hi")'
invalid:
  - 'console.log("hi")'
```

`sg test` 会运行所有测试，将匹配结果与快照进行比对，若存在差异则测试失败。首次使用 `-U` 参数运行时，系统会自动创建快照。

### `utilDirs`

`Array<string>` — 包含全局工具规则的目录。每个工具文件都必须包含 `id` 和 `language` 属性。项目中的任何规则均可通过 `matches: <id>` 来引用这些工具。

### `languageGlobs`

`HashMap<string, Array<string>>` — 用于自定义哪些文件扩展名对应哪种语言。其设置会优先于内置的默认配置。

该功能适用于以下场景：

- 自定义文件扩展名（例如 `.eslintrc` 对应 JSON 格式）。
- 强制将 `.ts` 文件视为 TSX 文件，从而支持 JSX 风格的正则匹配。
- Vue/Svelte/Astro 等框架的文件（这些文件的宿主语言为 HTML）。

### `customLanguages`（实验性功能）

用于注册 ast-grep 未内置的 tree-sitter 解析器。使用时需要提供以下参数：

- `libraryPath`：包含对应语法规则的已编译 `.so` / `.dylib` / `.dll` 文件的路径。
- `extensions`：需要识别的文件扩展名列表。
- `languageSymbol`：该语法规则所导出的 C 语言符号（通常为 `tree_sitter_<名称>`）。
- `expandoChar`（可选）：当宿主语言在语法中使用了 `$` 符号时，用于替换正则表达式中 `$` 的字符（如 PHP、jQuery 等语言）。

实际上**很少需要使用此功能**——因为 ast-grep 本身已预置支持 25 种语言。

### `languageInjections`（实验性功能）

用于匹配嵌入在其它语言中的模式。例如：在 JS 模板字面量中使用的 CSS 代码（如 styled-components、emotion 库中的用法）。

```yaml
languageInjections:
  - hostLanguage: js
    rule:
      pattern: 'styled.$TAG`$CONTENT`'
    injected: css
```

此后，匹配模式为 `color: $C` 的 `css` 规则将适用于 `$CONTENT` 字符串。

---

## 常见配置

### 使用共享规则的单仓库项目

```
monorepo/
├── sgconfig.yml          # root config — applies to entire monorepo
├── shared-rules/
│   ├── no-todo.yml
│   └── no-as-any.yml
└── packages/
    ├── frontend/
    │   ├── sgconfig.yml  # extends root with frontend-specific rules
    │   └── rules/
    └── backend/
        ├── sgconfig.yml  # extends root with backend-specific rules
        └── rules/
```

每个软件包的 `sgconfig.yml` 文件都会同时引用该软件包自身的规则以及共享规则：

```yaml
# packages/frontend/sgconfig.yml
ruleDirs:
  - rules
  - ../../shared-rules
```

### 单规则文件（无项目）

如仅需临时使用，则可直接跳过 `sgconfig.yml` 文件：

```bash
sg scan -r path/to/single-rule.yml src/
```

### 内联规则（无需文件）

```bash
sg scan --inline-rules '
id: no-todo
language: TypeScript
severity: warning
rule: { pattern: TODO }' src/
```

用 `---` 分隔的多条规则：

```bash
sg scan --inline-rules '
id: no-todo
language: TypeScript
rule: { pattern: TODO }
---
id: no-fixme
language: TypeScript
rule: { pattern: FIXME }' src/
```

## 编辑器集成

VS Code / Neovim / Helix 能自动检测到 `sgconfig.yml` 文件，并显示每条规则对应的诊断信息。若未配置 `sgconfig.yml`，LSP 将在未加载任何规则的情况下运行。

若要在您的编辑器中启用模式验证，请在每个规则文件的开头添加相应的头部信息：

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/ast-grep/ast-grep/main/schemas/rule.json
id: no-console
language: TypeScript
rule:
  pattern: console.log($_)
```

## 相关文档

- `references/yaml-rules.md` — 规则架构（原子型 / 关系型 / 复合型 / 转换型 / 修复型）。
- `references/cli.md` — `sg scan`、`sg test`、`sg new project` 命令用法。
- 官方文档：<https://ast-grep.github.io/reference/sgconfig.html>、<https://ast-grep.github.io/guide/project/project-config.html>
