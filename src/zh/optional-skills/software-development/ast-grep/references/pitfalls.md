# 常见陷阱——导致模式失效的原因及解决方案

本文档为故障模式指南。`scripts/ast_grep_helper.py validate` 子命令会在调用 `sg` 之前自动检查第1节中列出的各项；其余故障虽然出现频率较低，但依然较为常见。

---

## 1. 正则表达式语法无效

ast-grep **不支持**在模式中解析正则表达式。以下所有写法均会失败：

| 错误写法 | 原因 | 推荐替代方案 |
|---|---|---|
| `foo\|bar` | `\|` 是正则表达式的或运算符，而 ast-grep 不支持或运算。 | 分别执行两次查询，或在 YAML 规则中使用 `any: [pattern: foo, pattern: bar]`，或使用 `rg -e foo -e bar`。 |
| `foo.*bar` | `.*` 是正则表达式的通配符。 | 如果节点间存在分隔，可使用 `foo($$$) bar`；否则请改用 `rg`。 |
| `\w+`, `\d+`, `\s` | 正则表达式字符类。 | 使用 `$VAR` 来捕获任意标识符；若仅需数字，则使用 `kind: number_literal`。 |
| `[a-z]+` | 正则表达式字符类。 | AST 语法中没有对应功能——请改用 `rg`。 |
| `^foo$^` | 正则表达式锚点。 | 应通过 AST 特性定位：使用 `kind: program > expression_statement`，或结合 `inside`/`not has` 属性。 |

**为何会出现这种情况**：大型语言模型通常习惯以正则思维处理问题。需要转变的观念是——“ast-grep 的模式是*代码*，而非*字符串*”。

当确实需要使用正则表达式时，可在 YAML 中使用 `regex` 规则字段（通过 Rust 正则表达式匹配节点文本）：

```yaml
rule:
  all:
    - kind: identifier
    - regex: '^[A-Z][a-z]+$'   # CamelCase identifiers only
```

注意：`regex` 用于匹配**整个节点文本**，不会进行部分匹配。为提升性能，建议将其与 `kind` 或 `pattern` 结合使用。

---

## 2. 不完整的 AST 节点

模式必须是解析器能够识别为完整节点的有效代码。常见错误包括：

```text
# JS/TS
function foo                              ❌ no params, no body
function $NAME($$$) { $$$ }               ✅

async function $NAME                      ❌
async function $NAME($$$) { $$$ }         ✅

# Python
def foo:                                  ❌ trailing colon makes it a statement
def $FN($$$)                              ✅
class Foo:                                ❌
class $C($$$)                             ✅

# Go
func foo                                  ❌
func $NAME($$$) { $$$ }                   ✅

# Rust
fn foo                                    ❌
fn $NAME($$$) -> $RET { $$$ }             ✅
fn $NAME($$$) { $$$ }                     ✅ (-> () inferred)

# Java
public void foo                           ❌
public void $NAME($$$) { $$$ }            ✅
```

如果某个模式匹配结果为0且看起来正确，可运行命令 `sg run -p '<pattern>' --lang <lang> --debug-query=ast --stdin <<< 'echo'`，以此查看解析器对该模式的理解。若返回 `ERROR` 节点，则说明该模式结构有误。

---

## 3. 模式被错误地解析为其他类型

类字段初始化语句 `a = 123` 也会被解析为赋值表达式。若您只想获取字段定义，就必须进行区分处理：

```yaml
# WRONG — pattern parses as assignment_expression, not field_definition
pattern: a = 123
kind: field_definition

# CORRECT — use pattern object with context + selector
pattern:
  context: 'class C { a = 123 }'
  selector: field_definition
```

`kind` 和 `pattern` 是**相互独立的约束条件**，而非彼此的修饰项。ast-grep 不会根据 `kind` 的值来改变其解析方式。

---

## 4. `|` 的歧义问题

在大多数编程语言中，模式中的单独 `|` 符号被解释为按位或运算，**而非**选择/交替含义。因此：

```yaml
pattern: foo | bar          # parses as: foo bitwise-or'd with bar
```

……它匹配的是诸如 `x | y` 这样的表达式，而非“foo 或 bar”这类形式。若需实现选择逻辑，请使用 `any`：

```yaml
rule:
  any:
    - pattern: foo
    - pattern: bar
```

在 TypeScript 的联合类型（`A | B`）中，`|` 是类型语法的一部分——`pattern: A | B` 能被正确解析为联合类型，并符合该语法规范。

---

## 5. 同名元变量发生冲突

```ts
// Pattern: $X = $X
// Captures only when both sides are TEXTUALLY identical.

// Matches:
a = a
foo.bar = foo.bar

// Does NOT match:
a = b
let x = compute()      // because $X needs to bind once and re-use
```

如果您确实需要两次独立的捕获，应为它们起不同的名称：` $X = $Y `。

---

## 6. `$$$` 采用贪婪匹配模式后再执行提交

`$$$` **不会**回溯。它会尽可能多地捕获内容，之后才进行提交。如果您的模式需要非贪婪匹配，需采用不同的结构来编写：

```ts
// You want "match foo($X), where $X is any single arg"
// BAD:  foo($$$X)        // matches foo(a), foo(a, b), foo(a, b, c) - too broad
// GOOD: foo($X)          // matches only single-arg calls

// You want "match foo() with at least one arg"
// BAD:  foo($$$X)        // also matches foo()
// GOOD: foo($X, $$$REST) // forces at least one arg
```

## 7. `kind` 名称取决于 tree-sitter 语法

对于 JavaScript，`kind: function_declaration` 即可生效；而 Python 使用 `function_definition`，Rust 使用 `function_item`，Go 则同样使用 `function_declaration`（巧合的是与 JavaScript 一致）。若要确定正确的名称，可解析一个已知正常的文件：

```bash
sg run -p '$_' --lang python --debug-query=cst path/to/example.py | grep -i function
```

或者打开 <https://ast-grep.github.io/playground.html>，点击某个节点即可查看其 `kind` 值。

---

## 8. `inside` / `has` 的默认值为 `stopBy: neighbor`

```yaml
inside:
  kind: function_declaration   # only checks the IMMEDIATE parent
```

如果您希望“在函数的任意位置（任意嵌套层级）”：

```yaml
inside:
  kind: function_declaration
  stopBy: end                  # walks up to the file root
```

对于 `has`（后代节点）也是如此：

```yaml
has:
  kind: return_statement
  stopBy: end                  # walks down the whole subtree
```

若未指定 `stopBy: end`，`has` 仅会匹配直接子节点。

```bash
sg run -p 'foo()' -r 'bar()' --json=compact --update-all .
```

……虽然会生成 JSON 格式的输出，但**实际并不会修改任何文件**。当指定了 `--json` 参数时，ast-grep 会自动忽略 `--update-all` 参数。若需同时进行预览和实际应用操作，需执行**两次处理**：

```bash
# Pass 1: preview as JSON
sg run -p 'foo()' -r 'bar()' --json=compact .

# Pass 2: actually apply
sg run -p 'foo()' -r 'bar()' --update-all .
```

当设置了 `--apply` 参数时，`scripts/ast_grep_helper.py replace` 函数会自动执行该操作。

---

## 10. 复合规则适用于单个节点

`all` 和 `any` 模式每次都会针对**一个目标节点**进行评估：

```yaml
# WRONG — wants "node has BOTH a number child AND a string child"
has:
  all:
    - kind: number       # impossible: one node cannot be both at once
    - kind: string

# CORRECT
all:
  - has: { kind: number }
  - has: { kind: string }
```

当关系为“父节点拥有 X 个符合 Y 条件的子节点”时，可将此类关系规则从复合规则中分离出来。  

## 11. 字段顺序无法保证  

当一个规则对象包含多个字段时：

```yaml
rule:
  pattern: $X = compute()
  has: { kind: number }
```

...ast-grep 会将这些元变量视为隐式的 `all` 值来处理，但无法保证捕获元变量的**顺序**。如果您的 `transform` 或 `fix` 功能依赖于捕获顺序，请使用显式的 `all` 数组：

```yaml
rule:
  all:
    - pattern: function $F() { $$$ }
    - has: { pattern: $F() }     # $F captured by pattern first; here we just check
```

## 12. 未指定 `kind` 的 `regex` 操作速度较慢

单独使用 `regex` 时会扫描文件中的所有节点文本。在大型代码库中，这一操作的速度会明显变慢。建议始终结合使用：

```yaml
# Slow
rule:
  regex: '^TODO'

# Fast
rule:
  all:
    - kind: comment
    - regex: '^//\s*TODO'
```

## 13. 不支持作用域/类型/数据流分析

ast-grep 是一种**基于结构**的匹配工具。它无法判断：

- 两个 `foo` 引用是否指向同一个变量；
- 是否存在变量被遮蔽的情况；
- 函数是否为异步函数、是否会抛出异常、是否返回 Promise；
- 值是否从输入流向输出。

对于这类问题，建议使用真正具备类型感知能力的工具：TypeScript LSP、Pyright、带有类型推断功能的 Semgrep、CodeQL 等。

当您关注的是*语法结构*时，ast-grep 非常实用，例如：“查找所有调用 `eval(...)` 的地方”、“查找所有使用 `as any` 的地方”、“查找所有空的 catch 块”。但对于“查找所有从未被使用过的变量”这类任务，它的能力较为有限。

---

## 14. 模式测试是最高效的调试方式

当某个模式没有返回任何匹配结果且您不明白原因时：

1. 打开 <https://ast-grep.github.io/playground.html>；
2. 将您的代码粘贴到左侧面板，将对应的模式粘贴到右上角；
3. 右下角会显示解析后的抽象语法树，以及哪些节点被匹配（高亮显示）或未匹配。

或者也可以在本地操作：

```bash
sg run -p '<pattern>' --lang <lang> --debug-query=ast --stdin <<< '<sample-code>'
```

标准错误输出会显示已解析的模式，而标准输出则展示 JSON 匹配结果。如果模式显示为 `ERROR (XXX)`，则表示该模式未能被成功解析。

---

## 参考资料

- `references/patterns.md` — 元变量、严格程度及命名规则。
- `references/recipes.md` — 各语言中经过验证的有效模式。
- `references/cli.md` — `--debug-query`、`--strictness`、`--update-all` 参数说明。
