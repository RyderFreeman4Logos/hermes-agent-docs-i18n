# 模式语法 —— 元变量与模式解析方式

ast-grep **并非正则表达式**。模式采用与目标语言（TypeScript、Python、Go 等）**相同的语法**编写，ast-grep 会基于每个文件的抽象语法树（AST）来匹配这些模式。其中的通配符被称为**元变量**。

本页面是官方的标准入门指南。如果模式匹配失败，90% 的情况都是由于本文中提到的问题所致。

---

## 三种元变量

| 语法 | 匹配内容 | 是否捕获 |
|---|---|---|
| `$VAR` | **恰好一个** AST 节点 | 是，可按名称捕获 |
| `$$$` | **零个或多个** AST 节点（即一个列表） | 否（匿名处理） |
| `$$$VAR` | 零个或多个 AST 节点 | 是，可按名称捕获 |
| `$_` | 一个 AST 节点 | 否（匿名处理） |

元变量始终替换的是**整个 AST 节点**，而非节点中的子字符串。` $VAR` 无法匹配标识符的前三个字符，只能匹配整个标识符（或表达式、语句，具体取决于上下文）。

### 命名规则

- 必须以 `$` 开头。
- 后续可为大写字母 `A-Z`、数字或下划线。
- **有效名称**：` $X`、` $VAR`、` $VAR_1`、` $_`、` $_VAR`、` $ARG1`。
- **无效名称**：` $lower`、` $kebab-case`、以数字开头的 ` $1`、用于匿名情况的 ` $$single`（应使用 ` $_`）。

### 同名即同内容

模式中出现的同一个元变量必须捕获**完全相同的文本**：

```ts
// Pattern
$X === $X

// Matches
a === a
foo.bar === foo.bar

// Does NOT match
a === b
foo === foo.bar
```

有助于发现多余的比较操作、重复赋值等情况。

### `$$$` 具有贪婪性

当您编写 `foo($$$A, b, $$$C)` 时，匹配器不会回溯或尝试所有可能的分割方式。它会贪婪地填充 `$$$A`，直到模式能够与 `b` 匹配，之后剩余的所有内容才会被放入 `$$$C` 中。

```ts
// Pattern
foo($$$A, b, $$$C)

// Input
foo(a, c, b, b, c)

// Capture
$$$A = [a, c]
$$$C = [b, c]
```

如果需要不同的分割方式，可以重构模式（例如添加约束条件）。

---

## 模式必须是有效的代码

该模式本身必须符合目标语言的语法规范。ast-grep在解析时会将` $VAR`和`$$$`视为标识符或参数列表，随后再从结构上进行匹配。

### 常见错误

| 错误模式 | 失败原因 | 解决方案 |
|---|---|---|
| `function $NAME` | 函数声明缺少函数体——在JS/TS/Go/Rust等语言中这不是有效的AST节点。 | `function $NAME($$$) { $$$ }` |
| `def $FN($$$):` | 末尾有多余的冒号。ast-grep会将其解析为完整的函数定义；而冒号则使其成为语句。 | `def $FN($$$)` |
| `class Foo:` | 同上——Python类缺少函数体。 | `class Foo($$$)` |
| `fn $NAME` | Rust语言的函数缺少签名。 | `fn $NAME($$$) -> $RET { $$$ }` |
| `if x` | `if`语句不完整——大多数语言要求必须包含函数体。 | （大括号语言）使用`if x { $$$ }`；（Python则使用`pattern.context`/`selector`替代） |
| `"key": "$VAL"` | JSON模式——单独的键值对并非有效的JSON格式。 | 应使用`pattern: { context: '{"key": "$VAL"}', selector: pair }` |

### 当子表达式本身无效时

有时您希望匹配某种语言仅允许在更大上下文内使用的*表达式*。此时可使用`pattern`对象形式来实现：

```yaml
pattern:
  context: 'class A { $FIELD = $INIT }'
  selector: field_definition
```

此处说明：将 `class A { $FIELD = $INIT }` 作为一个整体进行解析，然后仅保留 `field_definition` 子树作为实际的模式。

---

## 严格程度级别

当 CST 节点并不完全匹配时（存在额外空格、不同的无名标点符号），ast-grep 可以表现出不同程度的宽容度。您可以在 CLI 中使用 `--strictness <LEVEL>` 参数来指定，或是在 YAML 规则中设置该值：

| 级别 | 匹配内容 |
|---|---|
| `cst` | 所有节点，包括无名节点（逗号、括号等） |
| `smart`（默认值） | 除 **目标** 中不在模式内的无名节点之外的所有节点 |
| `ast` | 仅限带名称的 AST 节点 |
| `relaxed` | 带名称的 AST 节点，忽略注释 |
| `signature` | 仅匹配节点类型——文本节点和无名节点将被忽略 |

几乎在所有情况下，您都应该选择 `smart` 级别。而当您希望匹配“任何名为 `foo` 的函数”（无论其参数如何）时，则应使用 `signature` 级别。

---

## 测试模式

有两种工具可帮助您确认模式能按预期方式解析：

```bash
# Print the AST of the pattern itself
sg run -p 'console.log($MSG)' --lang ts --debug-query=ast

# Print the parsed CST of a file (great for figuring out kind names)
sg run -p '$_' --lang ts --debug-query=cst src/example.ts | head -40
```

`--debug-query=ast` 仅显示命名的 AST 节点（更为简洁）。`--debug-query=cst` 则会显示包括标点符号在内的所有内容。这两种输出都会被发送到标准错误流，因此不会干扰标准输出中的 JSON 数据。

在线演示工具也同样快速：<https://ast-grep.github.io/playground.html>。

---

## 何时不宜使用 ast-grep

如果您的匹配模式本质上属于文本形态，建议改用 `grep` / `rg`：

- **针对任意文本**在多个文件中进行匹配 → 使用 `rg`
- 需要支持跨语言的交替匹配模式 → 使用 `rg -e foo -e bar`
- 仅匹配注释内容 → 使用 `rg --type ts '^\s*//.*TODO'`
- 匹配 URL、邮箱地址或许可证头部信息 → 使用 `rg`

ast-grep 适用于分析**代码结构**，如函数形态、调用模式、控制流、类型注解、导入语句以及错误处理机制。如果您的“匹配模式”仅依赖于文件中的字节内容而非语法结构，那么正则表达式才是更合适的工具。

---

## 参考资料

- `references/pitfalls.md` — 具体的正则表达式反模式及各语言特有的陷阱。
- `references/recipes.md` — 适用于 TS/JS/Py/Go/Rust 的可直接复制的匹配模式。
- `references/yaml-rules.md` — 包含 `kind`、`regex`、`inside`、`has`、`all`、`any`、`not`、`matches` 等规则。
- 官方文档：<https://ast-grep.github.io/guide/pattern-syntax.html>
