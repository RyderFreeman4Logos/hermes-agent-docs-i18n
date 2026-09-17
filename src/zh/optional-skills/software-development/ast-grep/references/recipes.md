# 模板集——按语言分类的复制粘贴模板

该文件中的所有模板均已通过标准语法验证。它们仅作为参考起点，您可以根据实际需求调整占位符名称及约束条件。

请配合以下辅助工具使用这些模板：

```bash
ast-grep-helper search '<PATTERN>' --lang <LANG> [path]
ast-grep-helper replace '<PATTERN>' '<REWRITE>' --lang <LANG> [path]   # dry-run
ast-grep-helper replace '<PATTERN>' '<REWRITE>' --lang <LANG> [path] --apply
```

或者直接：

```bash
sg run -p '<PATTERN>' --lang <LANG> [path]
sg run -p '<PATTERN>' -r '<REWRITE>' --update-all --lang <LANG> [path]
```

## TypeScript / TSX / JavaScript

### 查找结构模式

```typescript
// Every function declaration
function $NAME($$$PARAMS) { $$$BODY }

// Every async function
async function $NAME($$$PARAMS) { $$$BODY }

// Every arrow function (any param shape)
($$$PARAMS) => $$$BODY

// Every method on a class
class $C { $$$ $METHOD($$$P) { $$$B } $$$ }

// Every import statement
import { $$$NAMES } from '$MOD'
import $DEFAULT from '$MOD'
import * as $NS from '$MOD'

// Every console.* call
console.$METHOD($$$ARGS)

// Every JSX element of a given name
<MyComponent $$$PROPS>$$$CHILDREN</MyComponent>

// Every try/catch
try { $$$BODY } catch ($E) { $$$HANDLER }

// Every throw
throw $EXPR

// Every new expression
new $CLASS($$$ARGS)

// Every type assertion to any (anti-pattern!)
$EXPR as any
$EXPR as unknown as $T
```

### 常见重写方式

```bash
# console.log -> logger.info
sg run -p 'console.log($$$A)' -r 'logger.info($$$A)' --lang ts --update-all .

# require -> import (one-arg case)
sg run -p 'const $V = require($M)' -r 'import $V from $M' --lang ts --update-all .

# .then(callback) -> await on the same line (use with caution; needs async function context)
sg run -p '$P.then($CB)' -r 'const $TMP = await $P; $CB($TMP)' --lang ts --update-all .

# Strip `as any`
sg run -p '$E as any' -r '$E' --lang ts --update-all .

# Rename a function call site
sg run -p 'oldName($$$A)' -r 'newName($$$A)' --lang ts --update-all .
```

## Python

> **提醒**：切勿在 Python 模式语句的末尾使用冒号。模式语句会被视为一个完整的陈述句，因此 `def foo($$$):` 是无效的写法。

```python
# Every function definition
def $FN($$$PARAMS)

# Every class definition
class $C($$$BASES)

# Every decorator usage
@$DEC
def $FN($$$P)

# Every print call (Python 3)
print($$$ARGS)

# Every f-string
f"$STR"

# Every with-statement
with $CTX as $VAR: $$$BODY

# Every try/except
try: $$$BODY
except $EXC: $$$HANDLER

# Every list comprehension
[$EXPR for $VAR in $ITER]

# Every async def
async def $FN($$$PARAMS)

# Type hints — Optional[X]
Optional[$T]

# Type hints — X | None (PEP 604)
$T | None
```

### 常见重写方式

```bash
# print(...) -> logger.info(...)
sg run -p 'print($$$A)' -r 'logger.info($$$A)' --lang py --update-all .

# Optional[X] -> X | None
sg run -p 'Optional[$T]' -r '$T | None' --lang py --update-all .

# from typing import List -> remove (built-in list works in 3.9+)
sg run -p 'from typing import List' -r 'from typing import List  # TODO: remove, use list' --lang py --update-all .
```

## Go 语言版本

```go
// Every function
func $NAME($$$PARAMS) $$$RET { $$$BODY }

// Every method
func ($RECV $TYPE) $NAME($$$PARAMS) $$$RET { $$$BODY }

// The classic err nil-check
if err != nil { $$$BODY }

// Every fmt.Println / fmt.Printf / fmt.Sprintf
fmt.$METHOD($$$ARGS)

// Every defer
defer $EXPR

// Every goroutine
go $EXPR

// Every channel send/recv
$CH <- $VAL
$VAL := <-$CH

// Every type assertion
$EXPR.($TYPE)
```

### 常见重写方式

```bash
# fmt.Println -> log.Println
sg run -p 'fmt.Println($$$A)' -r 'log.Println($$$A)' --lang go --update-all .

# Add error wrapping
sg run -p 'return $ERR' -r 'return fmt.Errorf("operation failed: %w", $ERR)' --lang go --update-all .
```

## Rust语言

```rust
// Every fn
fn $NAME($$$PARAMS) -> $RET { $$$BODY }
fn $NAME($$$PARAMS) { $$$BODY }       // no return type

// Every async fn
async fn $NAME($$$PARAMS) -> $RET { $$$BODY }

// Every method on impl
impl $TYPE { fn $METHOD($$$P) -> $R { $$$B } }

// Every trait impl
impl $TRAIT for $TYPE { $$$ITEMS }

// Every match expression
match $EXPR { $$$ARMS }

// Every Result-returning fn that uses ?
fn $N($$$P) -> Result<$T, $E> { $$$ }

// .unwrap() / .expect() (anti-patterns)
$EXPR.unwrap()
$EXPR.expect($MSG)

// Every println!/eprintln!/format!
println!($$$ARGS)
format!($$$ARGS)
```

### 常见重写方式

```bash
# unwrap() -> ? in Result-returning fns (caution: needs context)
sg run -p '$E.unwrap()' -r '$E?' --lang rust --update-all .

# eprintln! -> log::error!
sg run -p 'eprintln!($$$A)' -r 'log::error!($$$A)' --lang rust --update-all .
```

## Java

```java
// Every public class
public class $NAME { $$$BODY }

// Every method (any modifier)
$$$MOD $RET $NAME($$$P) { $$$BODY }

// Every System.out.println / System.err.println
System.$STREAM.println($$$ARGS)

// Every try-with-resources
try ($$$RES) { $$$BODY } catch ($EXC $E) { $$$HANDLER }

// Every annotation usage
@$ANNOTATION
$DECL
```

## C / C++

```cpp
// Every printf-family call
printf($$$ARGS)
sprintf($$$ARGS)
fprintf($$$ARGS)

// Every malloc / free pair (find-only — pairing requires data flow)
malloc($SIZE)
free($PTR)

// Every for-loop
for ($INIT; $COND; $POST) { $$$BODY }

// C++ smart pointer make
std::make_shared<$T>($$$ARGS)
std::make_unique<$T>($$$ARGS)
```

### 重写功能

```bash
# malloc(N * sizeof(T)) -> calloc(N, sizeof(T)) - safer
sg run -p 'malloc($N * sizeof($T))' -r 'calloc($N, sizeof($T))' --lang c --update-all .
```

## CSS

```css
/* Every rule with a specific property */
{ $$$ color: $VAL; $$$ }

/* Every @media query */
@media $QUERY { $$$BODY }

/* Every var() reference */
var($NAME)
```

## HTML

```html
<!-- Every img without alt -->
<img $$$ />

<!-- Every script tag -->
<script $$$>$$$BODY</script>

<!-- Every link to stylesheet -->
<link rel="stylesheet" href=$URL />
```

## Bash / Shell 脚本

```bash
# Every for-loop
for $VAR in $$$LIST; do $$$BODY; done

# Every if-statement
if $$$COND; then $$$BODY; fi

# Every function definition
$NAME() { $$$BODY }

# Every subshell call
$( $$$CMD )
```

## YAML 规则配方（用于 `sg scan`）

这些是完整的 YAML 规则，可直接放入 `rules/*.yml` 文件中，随后通过 `sg scan` 命令执行。完整的规则结构说明请参阅 `references/yaml-rules.md`。

### no-console（TypeScript）

```yaml
id: no-console
language: TypeScript
severity: warning
message: "Avoid console.* in production"
rule:
  pattern: console.$METHOD($$$ARGS)
fix: logger.$METHOD($$$ARGS)
```

### no-as-any（TypeScript）

```yaml
id: no-as-any
language: TypeScript
severity: error
message: "`as any` defeats type safety. Use a proper type."
rule:
  pattern: $EXPR as any
fix: $EXPR
```

### 空捕获（JavaScript）

```yaml
id: empty-catch
language: JavaScript
severity: error
message: "Empty catch swallows errors silently."
rule:
  all:
    - pattern: try { $$$T } catch ($E) { $$$H }
    - has:
        kind: catch_clause
        has:
          kind: statement_block
          not:
            has:
              kind: statement
              stopBy: end
```

### 打印到日志器（Python）

```yaml
id: print-to-logger
language: Python
severity: hint
message: "Use logger.info instead of print"
rule:
  pattern: print($$$ARGS)
fix: logger.info($$$ARGS)
```

### no-unwrap（Rust语言）

```yaml
id: no-unwrap
language: Rust
severity: warning
message: "Avoid .unwrap() in production code; propagate or handle the error."
rule:
  pattern: $EXPR.unwrap()
```

## 相关参考

- `references/patterns.md` — 元变量规则说明。
- `references/yaml-rules.md` — 完整的 YAML 规则架构（原子型 / 关联型 / 复合型 / 转换型 / 修复型）。
- `references/cli.md` — `sg run`、`sg scan`、`sg test`、`sg new` 命令的使用指南。
- 官方产品目录：<https://ast-grep.github.io/catalog/>（由社区维护，可按编程语言筛选）。
