# YAML 规则参考 —— 原子规则、关系规则、复合规则、转换规则与修复规则

当您不再需要使用内联的 `sg run -p ...` 格式，而希望拥有可复用且可测试的规则时，可使用此功能。YAML 规则是 `sg scan` 的处理单元。只需将一个或多个文件放入通过 `sgconfig.yml` 配置的 `ruleDirs/` 目录中，它们就会自动被加载。

本页面为实用参考资料。完整的开源文档地址如下：

- <https://ast-grep.github.io/reference/yaml.html>
- <https://ast-grep.github.io/reference/rule.html>
- <https://ast-grep.github.io/cheatsheet/rule.html>

---

## 规则结构

单个 YAML 文件可以通过 `---` 符号分隔来包含多个规则。

```yaml
id: no-console
language: TypeScript
severity: warning
message: "Avoid console.* in production"
note: |
  Use a proper logger so we can route logs to stderr in production
  and silence them in tests.
url: https://internal.docs/rules/no-console

rule:
  pattern: console.$METHOD($$$ARGS)

fix: logger.$METHOD($$$ARGS)

constraints:
  METHOD:
    not:
      regex: '^(error|warn)$'

files:
  - 'src/**/*.ts'
ignores:
  - 'src/**/*.test.ts'

metadata:
  category: logging
```

## 顶层字段

| 字段 | 是否必填 | 描述 |
|---|---|---|
| `id` | 是 | 唯一标识符。请使用“kebab-case”格式。 |
| `language` | 是 | 可选值包括：`Bash`、`C`、`Cpp`、`CSharp`、`Css`、`Elixir`、`Go`、`Haskell`、`Html`、`Java`、`JavaScript`、`Json`、`Kotlin`、`Lua`、`Nix`、`Php`、`Python`、`Ruby`、`Rust`、`Scala`、`Solidity`、`Swift`、`TypeScript`、`Tsx`、`Yaml`。虽然以大写PascalCase格式书写为标准，但小写形式通常也可使用。 |
| `rule` | 是 | 匹配逻辑。包含一个或多个原子规则、关系规则或复合规则的对象。 |
| `constraints` | 否 | 对捕获的单个元变量（` $VAR`，而非 `$$$`）的过滤条件。 |
| `utils` | 否 | 本文件中`matches:`所引用的本地工具规则。 |
| `transform` | 否 | 在`fix`操作之前对元变量字符串进行的处理。 |
| `fix` | 否 | 用于自动重写的字符串或`FixConfig`配置。 |
| `rewriters` | 否 | 用于`rewrite`转换的重写规则。 |
| `severity` | 否 | `hint` \| `info` \| `warning` \| `error` \| `off`（默认值为`hint`）。 |
| `message` | 否 | 简洁的代码检查提示信息，可引用` $VAR`所捕获的文本。 |
| `note` | 否 | 详细的Markdown格式说明（不支持` $VAR`插值）。 |
| `labels` | 否 | 针对每个元变量的自定义诊断高亮标签。 |
| `files` | 否 | 全局通配符包含列表。 |
| `ignores` | 否 | 全局通配符排除列表。 |
| `url` | 否 | 在编辑器代码检查提示中显示的文档链接。 |
| `metadata` | 否 | 由`sg`忽略的自由格式数据，可用于外部工具。 |

---

## 原子规则 —— 匹配单个节点

### `pattern`

按结构模式进行匹配。这是最常用的规则。

```yaml
# String form
rule:
  pattern: console.log($MSG)

# Object form (when context is needed)
rule:
  pattern:
    context: 'class C { $FIELD = $INIT }'
    selector: field_definition
    strictness: relaxed   # optional, default: smart
```

### `kind`

根据 AST 节点类型名称进行匹配。此选项为 Tree-sitter 语法所特有。

```yaml
rule:
  kind: call_expression
```

ast-grep 0.39+ 版本支持有限的 ESQuery 选择器：

```yaml
rule:
  kind: call_expression > identifier   # direct child
  kind: call_expression + identifier   # next sibling
  kind: call_expression ~ identifier   # following sibling
  kind: call_expression identifier     # descendant
```

若要确定合适的 `kind`，可解析一个已知正常的文件：

```bash
sg run -p '$_' --lang ts --debug-query=cst src/foo.ts | head -40
```

### `regex`

使用 Rust 正则表达式来匹配节点文本。仅支持全文本匹配（不支持部分匹配）。为提升性能，务必与 `kind` 或 `pattern` 一同使用。

```yaml
rule:
  all:
    - kind: identifier
    - regex: '^[A-Z][a-z]+$'   # PascalCase
```

内联标志有效：`(?i)apple`、`(?m)^foo`。不支持环视匹配，也不允许使用反向引用。

### `nthChild`

根据**已命名的**兄弟元素中的基于 1 的索引进行匹配。其设计灵感源自 CSS 的 `:nth-child`。

```yaml
rule:
  nthChild: 1                # first sibling

# Functional form
rule:
  nthChild: 2n+1             # odd siblings

# With reverse and ofRule
rule:
  nthChild:
    position: 1
    reverse: true            # last
    ofRule:
      kind: function_declaration
```

### `range`

通过字符范围进行匹配。适用于需要精确定位已知位置的工具。

```yaml
rule:
  range:
    start: { line: 0, column: 0 }
    end:   { line: 0, column: 11 }
```

## 关系规则——根据与其他节点的关系进行匹配

这四种规则均需要一个子规则对象，此外还可选择性地指定 `stopBy` 参数，以及针对 `inside`/`has` 规则的 `field` 参数。

### `inside` — 目标节点位于与父节点/祖先节点匹配的子规则范围内

```yaml
rule:
  pattern: this.$PROP
  inside:
    kind: class_body
    stopBy: end                # walk up to file root, default: neighbor
```

### `has` — 目标对象包含符合子规则的子节点/后代元素

```yaml
rule:
  kind: function_declaration
  has:
    kind: throw_statement
    stopBy: end
```

### `precedes` — 目标项位于与它匹配的同级子规则之前

```yaml
rule:
  kind: import_statement
  precedes:
    kind: function_declaration
```

### `follows` — 在匹配到同级子规则后显示目标内容

```yaml
rule:
  pattern: super($$$)
  follows:
    pattern: $X = $Y
```

### `stopBy`

| 值 | 行为 |
|---|---|
| `"neighbor"`（默认值） | 在直接的上级/子节点/同级节点处停止。 |
| `"end"` | 一直遍历到根节点/叶节点/序列边界。 |
| 规则对象 | 当子规则匹配时停止（包含匹配的情况）。 |

### `field`

指定目标在其父节点中的语义角色（例如 `name`、`body`、`value`、`key`）。

```yaml
rule:
  kind: pair
  has:
    field: key
    regex: '^password$'
```

## 组合规则——合并子规则

| 规则 | 含义 |
|---|---|
| `all` | 所有子规则必须匹配同一个目标节点。所有子规则中的元变量会进行合并。 |
| `any` | 至少有一个子规则需要匹配。仅匹配到的分支中的元变量会被保留。 |
| `not` | 反向逻辑：目标节点不得匹配该子规则。 |
| `matches` | 按编号引用某个实用规则。 |

```yaml
rule:
  all:
    - kind: call_expression
    - pattern: $FN($$$ARGS)
    - inside:
        kind: function_declaration
        stopBy: end

rule:
  any:
    - pattern: console.log($X)
    - pattern: console.warn($X)
    - pattern: console.error($X)

rule:
  all:
    - pattern: $E.unwrap()
    - not:
        inside:
          kind: function_item
          has:
            kind: result_type
            stopBy: end

rule:
  matches: is-react-component
```

> 组合规则仅适用于**单个**目标。若要表达“节点 X 同时拥有数字类型的子节点和字符串类型的子节点”，应在顶层使用两条关联规则，而非在 `has` 中使用 `all`。详情请参阅 `references/pitfalls.md` 的第 10 节。

---

## 隐式 `all` — 多个规则字段

包含多个字段的规则对象会被视为具有隐式 `all` 功能：

```yaml
# These two are equivalent
rule:
  pattern: this.$PROP
  inside: { kind: class_body }

rule:
  all:
    - pattern: this.$PROP
    - inside: { kind: class_body }
```

当捕获顺序至关重要时（虽较为罕见，但可通过后续的 `transform` 功能实现），请使用显式的 `all` 数组。  

---

## `constraints` — 匹配后的元变量过滤  

在主 `rule` 发生匹配后，会对被捕获的各个元变量进行进一步检查：

```yaml
rule:
  pattern: function $NAME($$$P) { $$$B }

constraints:
  NAME:
    regex: '^[a-z][a-zA-Z0-9]*$'   # camelCase only
    not:
      regex: '^_'                   # not starting with _
```

这些限制**仅适用于单个元变量**（`'$VAR'`），而不适用于多个元变量（`'$$$$VAR'`）。

---

## `utils` — 本地可复用子规则

```yaml
utils:
  is-literal:
    any:
      - kind: number
      - kind: string
      - kind: 'true'
      - kind: 'false'

rule:
  all:
    - pattern: $X = $Y
    - has:
        matches: is-literal      # references utils.is-literal
```

对于需要在多个规则文件中通用的工具函数，可在 `sgconfig.yml` 中使用 `utilDirs` 参数，并将每个工具函数分别放入独立的 YAML 文件中，同时指定其 `id` 和 `language` 属性。

---

## `transform` — 在 `fix` 操作之前处理捕获内容

支持的运算操作包括：`replace`、`substring`、`convert`、`rewrite`。

### `replace` — 对捕获到的字符串进行正则表达式搜索与替换

```yaml
rule:
  pattern: $OLD_FN($$$A)
constraints:
  OLD_FN:
    regex: '^debug_'
transform:
  NEW_FN:
    replace:
      source: $OLD_FN
      replace: '^debug_'
      by: 'release_'
fix: $NEW_FN($$$A)
```

### `substring` — 字符切片功能（支持负数索引）

```yaml
transform:
  INNER:
    substring:
      source: $WRAPPED
      startChar: 1
      endChar: -1
```

### `convert` — 大小写转换

```yaml
transform:
  KEBAB:
    convert:
      source: $CAMEL
      toCase: kebabCase   # camelCase | snakeCase | kebabCase | pascalCase | upperCase | lowerCase | capitalize
      separatedBy: [underscore]   # optional: dash | dot | space | slash | underscore | caseChange
```

### `rewrite` — 应用其他重写规则（实验性功能）

```yaml
rewriters:
  - id: stringify
    rule: { pattern: "'' + $A" }
    fix: "String($A)"

rule:
  pattern: stringify-all($EXPR)
transform:
  REWRITTEN:
    rewrite:
      source: $EXPR
      rewriters: [stringify]
      joinBy: "\n"
fix: $REWRITTEN
```

### 转换操作可串联使用

后续的转换操作可以引用前面转换所生成的变量：

```yaml
transform:
  KEBABED:
    convert: { source: $X, toCase: kebabCase }
  PREFIXED:
    replace:
      source: $KEBABED
      replace: '^'
      by: 'css-'
fix: $PREFIXED
```

## `fix` — 自动重写

### 字符串格式

```yaml
fix: logger.log($$$ARGS)

# Empty string deletes the match
fix: ""
```

### FixConfig 表单（用于需要扩展范围以删除列表项的场景）

在从逗号分隔的列表中删除某一项时，还需同时移除末尾的逗号。此时可使用 `expandEnd` 参数：

```yaml
rule:
  kind: pair
  has:
    field: key
    regex: '^password$'

fix:
  template: ''
  expandEnd:
    regex: ','
```

`expandStart` 和 `expandEnd` 接受用于指定应被纳入重写范围的字符的 `regex` 表达式。  

---

## `rewriters` — 用于 `rewrite` 转换的子规则库

用于定义一个或多个命名重写规则的顶层字段：

```yaml
rewriters:
  - id: nullable-to-optional
    rule: { pattern: $X | null }
    fix: '$X | undefined'

  - id: stringify
    rule: { pattern: "'' + $A" }
    fix: 'String($A)'
```

通过 `rewrite` 操作在 `transform` 内部使用（见上文）。

---

## `labels` — 自定义诊断高亮显示

```yaml
rule:
  pattern: $FN($$$ARGS)

labels:
  FN:
    style: primary
    message: "this function shouldn't be called"
  ARGS:
    style: secondary
    message: "with these arguments"
```

编辑器插件会使用这些标签来呈现诊断结果。通常情况下，使用默认设置即可。

```yaml
files:
  - 'src/**/*.ts'
  - 'lib/**/*.ts'

ignores:
  - 'src/**/*.test.ts'
  - '**/__generated__/**'
```

如果未指定，则该规则会作用于所有匹配其 `language` 参数的文件。这些通配符仅对该规则有效，可覆盖 `sgconfig.yml` 中设置的对应通配符。

对象形式（较少使用）：

```yaml
files:
  - pattern: 'src/**/*.ts'
    case_sensitive: true
```

## 相关参考

- `references/recipes.md` — 按编程语言分类的规则模板。
- `references/cli.md` — `sg scan`、`sg test` 命令的使用说明。
- `references/sgconfig.md` — 项目级配置指南。
- 官方规则参考文档：<https://ast-grep.github.io/reference/rule.html>
- 快速参考手册：<https://ast-grep.github.io/cheatsheet/rule.html>、<https://ast-grep.github.io/cheatsheet/yaml.html>
