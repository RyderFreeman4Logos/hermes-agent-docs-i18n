---
sidebar_position: 16
title: "LSP — Semantic Diagnostics"
description: "Real language servers (pyright, gopls, rust-analyzer, …) wired into the post-write lint check used by write_file and patch."
---

# 语言服务器协议（LSP）

Hermes 以后台子进程的形式运行多种完整的语言服务器——如 pyright、gopls、rust-analyzer、typescript-language-server、clangd 以及另外约 20 种——并将这些语言服务器检测到的语义错误信息反馈给 `write_file` 和 `patch` 函数所使用的写入后代码检查机制。当智能体编辑文件时，它能够准确识别出该操作引入的所有错误——不仅包括语法错误，还包括语言服务器检测出的**类型错误、未定义的名称、缺失的导入项，以及整个项目范围内的语义问题**。

这正是顶级编程智能体所采用的架构。Hermes 以独立封装的形式提供这一功能：无需额外的编辑器主机，无需安装插件，也无需管理独立的守护进程。

## LSP 的运行时机

LSP 的运行取决于**Git 工作区检测结果**。当智能体的工作目录（或正在编辑的文件）位于 Git 仓库中时，LSP 便会针对该工作区启动检测。若两者均不在 Git 仓库中，LSP 将保持休眠状态——这对于那些工作目录为用户主目录且没有需要分析的项目的消息传递系统尤为有用。

该检查过程是分层的：首先进行进程内的语法检查（耗时微秒级），只有在语法检查通过后才会启动 LSP 的语义检测。即便语言服务器出现故障或无法正常工作，也不会影响写入操作——所有的 LSP 检测失败情况都会自动回退到仅基于语法的结果。

具体而言，在每次成功的 `write_file` 或 `patch` 操作之后：

1. Hermes 会首先获取该文件当前的诊断信息作为基准。
2. 执行写入操作。
3. 再次向语言服务器发起查询，过滤掉那些已存在于基准中的诊断信息，仅显示新增的诊断结果。

Agent 接收到的输出如下所示：

```
{
  "bytes_written": 42,
  "dirs_created": false,
  "lint": {"status": "ok", "output": ""},
  "lsp_diagnostics": "LSP diagnostics introduced by this edit:\n<diagnostics file=\"/path/to/foo.py\">\nERROR [42:5] Cannot find name 'foo' [reportUndefinedVariable] (Pyright)\nERROR [50:1] Argument of type \"str\" is not assignable to \"int\" [reportArgumentType] (Pyright)\n</diagnostics>"
}
```

`lint` 字段用于存储语法检查结果（通过 `ast.parse`、`json.loads` 等方法在进程内进行的解析耗时，以微秒为单位）；而 `lsp_diagnostics` 字段则承载来自真实语言服务器的语义诊断信息。这两个通道为独立的信号——对于存在语义问题但语法正常的文件，代理会将其标记为 `lint: ok`，同时生成相应的 `lsp_diagnostics` 数据。

## 支持的语言

| 语言 | 服务器程序 | 自动安装方式 |
|------|----------|--------------|
| Python | `pyright-langserver` | npm |
| TypeScript / JavaScript / JSX / TSX | `typescript-language-server` | npm |
| Vue | `@vue/language-server` | npm |
| Svelte | `svelte-language-server` | npm |
| Astro | `@astrojs/language-server` | npm |
| Go | `gopls` | `go install` |
| Rust | `rust-analyzer` | 手动安装（通过 rustup） |
| C / C++ | `clangd` | 手动安装（依赖 LLVM） |
| Bash / Zsh | `bash-language-server` | npm |
| YAML | `yaml-language-server` | npm |
| Lua | `lua-language-server` | 手动安装（从 GitHub 仓库下载） |
| PHP | `intelephense` | npm |
| OCaml | `ocaml-lsp` | 手动安装（通过 opam） |
| Dockerfile | `dockerfile-language-server-nodejs` | npm |
| Terraform | `terraform-ls` | 手动安装 |
| Dart | `dart language-server` | 手动安装（依赖 dart sdk） |
| Haskell | `haskell-language-server` | 手动安装（通过 ghcup） |
| Julia | `julia` + LanguageServer.jl | 手动安装 |
| Clojure | `clojure-lsp` | 手动安装 |
| Nix | `nixd` | 手动安装 |
| Zig | `zls` | 手动安装 |
| Gleam | `gleam lsp` | 手动安装（通过 gleam install） |
| Elixir | `elixir-ls` | 手动安装 |
| Prisma | `prisma language-server` | 手动安装 |
| Kotlin | `kotlin-language-server` | 手动安装 |
| Java | `jdtls` | 手动安装 |
| PowerShell | `PowerShellEditorServices`（基于 `pwsh` 运行） | 手动安装（从发布包中下载） |

对于“手动安装”类别的语言，需使用该语言对应的工具链管理器进行安装（如 rustup、ghcup、opam、brew 等）。Hermes 会自动检测 PATH 中或 `<HERMES_HOME>/lsp/bin/` 目录下的对应二进制文件。

### PowerShell

PowerShellEditorServices并非单一的二进制文件，而是由`pwsh`（PowerShell 7+版本）或`powershell`主机启动的PowerShell模块包。设置步骤如下：

1. 安装[PowerShell](https://github.com/PowerShell/PowerShell)，确保`pwsh`（或Windows自带的`powershell`）已添加到系统路径中。
2. 从[PowerShellEditorServices版本发布页面](https://github.com/PowerShell/PowerShellEditorServices/releases)下载最新版本的压缩包并解压。
3. 指定Hermes使用解压后的模块包——即包含`PowerShellEditorServices/Start-EditorServices.ps1`文件的目录。可通过以下任一方式实现：
   - 在`config.yaml`文件中设置`lsp.servers.powershell.command: ["/path/to/bundle"]`；
   - 将解压后的文件复制到`<HERMES_HOME>/lsp/PowerShellEditorServices`目录；
   - 设置环境变量`PSES_BUNDLE_PATH=/path/to/bundle`。

一旦检测到`pwsh`，执行`hermes lsp status`命令就会显示“已安装”状态；如果缺少该模块包，日志中会显示包含下载链接的警告信息。

部分服务器在安装时还会依赖其他需手动引入的包，npm不会自动下载这些依赖。目前典型的例子是`typescript-language-server`，它需要从同一个`node_modules`目录中导入`typescript` SDK——当您执行`hermes lsp install typescript`命令时，或首次使用时触发自动安装功能，Hermes会同时安装这两个包。

```
hermes lsp status          # service state + per-server install status
hermes lsp list            # registry, optionally --installed-only
hermes lsp install <id>    # eagerly install one server
hermes lsp install-all     # try every server with a known recipe
hermes lsp restart         # tear down running clients
hermes lsp which <id>      # print resolved binary path
```

`hermes lsp status` 是最佳的起始点——它会显示哪些语言今天能够获得语义分析功能，以及哪些语言需要先安装对应的二进制文件。

## 配置

默认设置已适用于常规环境；只要相关二进制文件已在系统路径中，便无需进行任何额外配置。

```yaml
# config.yaml
lsp:
  # Master toggle. Disabling skips the entire subsystem — no servers
  # spawn, no background event loop runs.
  enabled: true

  # How long to wait for diagnostics after each write.
  wait_mode: document      # "document" or "full"
  # Max seconds to wait for the server to re-check the file after an
  # edit. Only *fresh* diagnostics (produced for the post-edit
  # content) are ever reported; if the server doesn't finish within
  # this budget, the edit reports "no LSP data" rather than stale
  # errors from before the edit. Raise this for slow servers on big
  # projects (tsserver, rust-analyzer mid-indexing).
  wait_timeout: 5.0

  # How to handle missing server binaries.
  #   auto    — install via npm/pip/go install into <HERMES_HOME>/lsp/bin
  #   manual  — only use binaries already on PATH
  install_strategy: auto

  # How long an unused language-server client stays alive (seconds).
  # Idle servers are shut down automatically and respawned on the next
  # relevant file operation. Set to 0 to disable idle reaping and keep
  # servers alive for the life of the process. Values below 30s are
  # clamped to 30 so a sweep can never reap a client mid-operation.
  idle_timeout: 600

  # Per-server overrides (all optional).
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      env: { PYRIGHT_LOG_LEVEL: "info" }
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true       # skip TS even when its extensions match
```

### 每个服务器的配置参数

* `disabled: true` — 即使该服务器的扩展与配置文件匹配，也完全跳过该服务器。
* `command: [bin, ...args]` — 指定自定义二进制文件的路径，从而绕过自动安装流程。
* `env: {KEY: value}` — 向启动的进程传递额外的环境变量。
* `initialization_options: {...}` — 该参数会与 LSP 的 `initializationOptions` 参数合并，一同通过 `initialize` 握手过程发送。这些参数为服务器专用，具体详情请参考对应语言服务器的文档。

## 安装位置

当设置为 `install_strategy: auto` 时，Hermes 会将二进制文件安装到 `<HERMES_HOME>/lsp/bin/` 目录中。NPM 包则会被安装到 `<HERMES_HOME>/lsp/node_modules/` 目录下，并在其上一级目录生成二进制文件符号链接。Go 语言的二进制文件则是通过 `go install` 命令生成的，此时 `GOBIN` 指向临时目录。

Hermes 绝不会将任何文件安装到 `/usr/local/`、`~/.local/` 或其他共享目录中——所有临时文件都由 Hermes 独自管理，当用户重置配置文件时，这些临时文件也会被清除。

## 性能特点

LSP 服务器会在首次使用时**延迟启动**。如果正在编辑的项目之前从未产生过与 `.py` 文件相关的处理请求，Hermes 会随即启动 pyright；对于大多数服务器而言，启动时间在 1 到 3 秒之间（而对于全新的 Rust 项目，rust-analyzer 的启动时间可能超过 10 秒）。在同一个工作区中进行后续编辑时，系统会直接复用已运行的服务器。

在没有生成任何诊断信息的情况下，LSP 层会在正常写入操作的基础上增加几毫秒的延迟。一旦有诊断信息被输出，系统的等待时间上限为 `wait_timeout` 秒——通常 pyright 和 tssserver 的响应时间在几十毫秒以内，而正在执行索引构建任务的 rust-analyzer 响应时间则可能在几秒左右。

诊断功能采用了**新鲜度过滤机制**：只有当服务器针对当前编辑的内容生成结果时，该结果才会被计入（即在修改发生时或之后发送的`publishDiagnostics`消息，或是修改之后处理的拉取请求），否则就会显示“无数据”——绝不会将昨天的错误再次当作当前问题报告。

服务器在处于使用状态时会保持运行，若在`lsp.idle_timeout`秒（默认为600秒）内没有文件操作，就会关闭。那些需要处理大量工作树的长时间运行的网关，不会再为每个工作区永久维持一个语言服务器进程。被关闭的服务器会在下次有相关文件操作时自动重新启动。如需禁用此机制并让所有服务器的索引在整个进程运行期间始终保持活跃状态，可将`idle_timeout`设置为`0`。

支持多根工作区的服务器（目前为pyright）在每个Hermes进程内以**单个进程**的形式运行：第一个Python项目会启动该进程，后续的所有项目根目录——例如由并行子代理处理的同级git工作树——都会作为额外的工作区文件夹附加到同一个服务器上，而不会再启动新的进程副本。

## 禁用方式

若要完全禁用该子系统，可在`config.yaml`中设置`lsp.enabled: false`。此时，写入后的检查将会回退到进程内的语法检查方式（Python使用`ast.parse`，JSON使用`json.loads`等），其实现方式与早期版本保持一致。

如需仅禁用某种语言而无需关闭整个功能层：

```yaml
lsp:
  servers:
    rust-analyzer:
      disabled: true
```

## 故障排除

**`hermes lsp status` 显示服务器为“缺失”状态**

该二进制文件既不在 PATH 环境变量指定的路径中，也不位于 `<HERMES_HOME>/lsp/bin/` 目录下。您可以运行 `hermes lsp install <server_id>` 以尝试自动安装，或者通过对应语言的常规工具链手动安装该二进制文件。

**`hermes lsp status` 中的“后端警告”部分**

某些服务器实际上只是外部 CLI 工具的简化封装，用于执行实际诊断功能——即便侧载二进制文件缺失，这类服务器仍能正常启动并接收请求，但不会报错。最常见的例子就是 `bash-language-server`，它会将诊断任务委托给 `shellcheck` 工具。当 `hermes lsp status` 显示“后端警告”部分时，请通过操作系统的包管理器安装相应的工具：

```
apt install shellcheck      # Debian / Ubuntu
brew install shellcheck     # macOS
scoop install shellcheck    # Windows
```

在服务器启动时，相同的警告信息会一次性记录到 `~/.hermes/logs/agent.log` 文件中。

**服务器已启动但未返回任何诊断信息**

请查看 `~/.hermes/logs/agent.log` 文件中的 `[agent.lsp.client]` 相关记录——语言服务器输出的错误信息以及协议错误都会被记录到这里。某些服务器（尤其是 rust-analyzer）需要在生成整个项目的索引之后才能提供针对单个文件的诊断信息；因此，在服务器启动后的首次编辑可能不会产生任何诊断结果，后续的编辑则可能会显示相关信息。

**服务器崩溃**

发生崩溃的服务器会被加入“故障集合”中，在当前会话剩余时间内不会再被尝试重启。请运行 `hermes lsp restart` 命令来清除该集合，之后再进行编辑即可重新启动服务器。

**在非 git 仓库中的文件进行编辑**

按设计要求，LSP 仅能在 git 仓库内部运行。如果项目尚未初始化，请先运行 `git init` 命令以启用 LSP 诊断功能。否则，系统将采用仅处理语法问题的本地备用方案。
