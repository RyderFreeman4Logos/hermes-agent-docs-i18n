# Box CLI 使用指南

通过 Hermes 的 `terminal` 工具来执行 Box 命令。请优先使用本技能文档中记载的命令，而非通过尝试性调用帮助功能来获取指令。仅当此处未列出必需的选项，或已安装的 CLI 无法识别该命令语法时，才使用帮助功能。

## 统一使用命令执行器

在执行任何 Box 操作之前，需先确定要使用的命令执行器：

1. 检查运行时 shell 中是否已存在 `box` 命令（在 macOS/Linux 上可使用 `command -v box`，在 PowerShell 中可使用 `Get-Command box`）。如果已存在，则直接使用该命令，无需考虑 Hermes 或 Box CLI 是安装在了何处。
2. 如果未找到该命令，则需在可写且持久的 Hermes 运行时目录下安装并验证一个独立的 CLI。推荐使用当前 Hermes 安装目录下的 `tools/box-cli` 路径；`HERMES_HOME` 参数并非必需，若未设置，Hermes 会使用对应操作系统的默认路径（macOS/Linux 为 `~/.hermes`，Windows 为 `%LOCALAPPDATA%\hermes`）。
3. 如果该目录不可写，则需在运行时环境中指定一个可写的持久目录。切勿假设 Hermes 的源代码目录、全局 npm 前缀或用户主目录具备写入权限。如果系统中存在非标准的 CLI 且其路径不在 `PATH` 环境变量中，应直接询问该命令的可执行文件路径，而非在系统中盲目搜索。

只有在 Hermes 安装并验证完对应的本地 CLI 复制版之后，才可使用 `npm exec --prefix` 命令。请将下述每个安装步骤作为一次终端命令来执行，记录下命令输出的已验证绝对路径，后续操作均使用该确切路径。切勿依赖在单独的 Hermes 终端会话中依然有效的 shell 变量，也绝不能向用户提供未经验证的 `npm exec --prefix` 命令让其直接运行。

Box CLI 4 需要 Node.js 18 或更高版本。在安装之前，请在 Hermes 所使用的相同运行时和shell环境中执行 `node --version` 和 `npm --version` 命令。如果系统中没有 Node.js，或其主版本低于 18，需通过常规机制申请安装或启用受支持的 Node 运行时，之后再重新执行上述检查。若 npm 不可用或文件系统不可写，请申请适合该运行时的安装环境或可写入的 Hermes 安装目录；切勿默认使用系统包管理器、桌面环境或提升后的权限。  

在 macOS/Linux 系统上：

```bash
node --version
npm --version
BOX_CLI_HOME="${HERMES_HOME:-$HOME/.hermes}/tools/box-cli"
mkdir -p "$BOX_CLI_HOME"
npm install --prefix "$BOX_CLI_HOME" @box/cli
npm exec --prefix "$BOX_CLI_HOME" -- box --version
cd "$BOX_CLI_HOME" && pwd -P
```

在 Windows PowerShell 中：

```powershell
node --version
npm --version
$boxCliHome = Join-Path $(if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA "hermes" }) "tools\box-cli"
New-Item -ItemType Directory -Force -Path $boxCliHome | Out-Null
npm install --prefix $boxCliHome @box/cli
npm exec --prefix $boxCliHome -- box --version
Resolve-Path $boxCliHome
```

在整个任务执行过程中，请保持已确定的运行器不变。当 Hermes 安装了本地副本后，需将所有示例中的开头 `box` 替换为下方对应的 `npm exec --prefix` 运行器。否则，则直接使用已确定的 `box` 命令来运行这些示例。

其他参考资料中的示例使用了 `bash` 的代码块以及 POSIX 格式的 `\` 继续符。在 PowerShell 中，虽然要保持相同的 Box 参数，但应将该命令写在单行上，或使用 PowerShell 的反引号继续符。仅在 PowerShell 示例中才可使用 PowerShell 变量。

在 macOS/Linux 系统上：

```bash
npm exec --prefix "<VERIFIED_ABSOLUTE_PREFIX>" -- box
```

在 Windows PowerShell 中：

```powershell
npm exec --prefix "<VERIFIED_ABSOLUTE_PREFIX>" -- box
```

例如在 macOS/Linux 系统上：

```bash
npm exec --prefix "<VERIFIED_ABSOLUTE_PREFIX>" -- box users:get me --json --fields id,name,login
```

请勿尝试进行全局 npm 安装，也不要使用 `sudo` 命令、更改 npm 的全局前缀或修改 `PATH` 环境变量。

## 校验身份并控制输出

在 macOS/Linux 系统上：

```bash
command -v box
box --version
box users:get me --json --fields id,name,login
box folders:items 0 --json --max-items 20 --fields id,name,type
```

在 Windows PowerShell 中：

```powershell
Get-Command box -ErrorAction SilentlyContinue
box --version
box users:get me --json --fields id,name,login
box folders:items 0 --json --max-items 20 --fields id,name,type
```

如需生成机器可读的输出，请使用 `--json` 参数；若只想获取所需字段，则可使用 `--fields` 参数。文件夹 `0` 仅为当前操作主体的根目录，并非完整的访问清单：请勿依据该清单来拒绝共享的文件或文件夹，也绝不可用它来查找 Box Hubs。

## 环境与操作主体

```bash
box configure:environments:list
box configure:environments:set-current <ENVIRONMENT_NAME>
box users:get me --json --fields id,name,login
```

CLI目前仅支持一个运行环境。在切换环境之前请务必确认，随后还需验证操作主体。应使用该环境所对应的OAuth身份来执行常规的Hermes任务，严禁冒充其他用户。

独立的npm安装仅能隔离CLI可执行文件，而无法隔离其已认证的运行环境。Box CLI会将各运行环境及访问令牌存储在运行时系统的用户目录下；在条件允许时会使用平台级的凭证存储机制，否则则退而使用`~/.box`作为存储路径。因此，以同一系统用户身份运行的Hermes配置文件及并发会话可以共享当前的Box运行环境。在设置过程中需对此共享状态予以提示，每执行一项任务前都要验证操作主体，并明确告知更改当前环境可能会影响该系统账户下的其他Hermes会话以及常规的Box CLI使用。

在Linux系统中，Box CLI的安全存储功能依赖于Secret Service/libsecret模块的支持。如果CLI提示使用明文存储方式，则需提醒用户凭证可能会保存在`~/.box/box_environments.json`及token-cache文件中。严禁读取或打印这些文件。建议在正式投入使用前配置运行时系统所支持的Secret Service/libsecret模块，或使用完全隔离的运行时用户账户；切勿仅为了发出警告就依赖包管理器或要求额外的确认步骤。

```bash
box folders:items <FOLDER_ID> --json --max-items 100 --fields id,name,type
box search "quarterly review" --json --limit 20 --fields id,name,type,parent
box metadata-query enterprise_12345.contractTemplate <ANCESTOR_FOLDER_ID> \
  --query "status = :status" --query-param status=active --json
```

在执行批量操作之前，请先完整分页查询库存信息。进行元数据查询时，需要提供模板范围/键以及父文件夹 ID。

## REST 临时解决方案

当 CLI 中没有对应的专用命令时，可通过 `box request` 命令保留已配置的认证信息，进而执行所需的常规操作。即便该操作基于 REST 协议，也无需因此止步——请参阅 [REST API 备用方案](rest-api.md)，了解针对不同端点的请求体与请求头格式。

```bash
box request /files/<FILE_ID> --json
box request /files/<FILE_ID> -X PUT --body '{"name":"renamed.pdf"}' --json
box request /folders -X POST --body '{"name":"New folder","parent":{"id":"0"}}' --json
```

可将 `box request` 作为基于 CLI 的 REST 备用方案。仅在 CLI 不可用，或应用程序代码确实需要直接调用 REST 接口时，才使用 SDK 或原始 HTTP 请求。

## 批量输入与操作

许多 Box CLI 命令支持通过 `--bulk-file-path` 参数传入 CSV 或 JSON 格式的批量数据。请在确认目标对象列表并确保数据能成功写入后，再使用该参数。对于有序移动、版本更新以及其他可恢复的操作，应保留操作日志并依次处理。仅在应用程序 SDK 明确规定了重试机制和速率限制策略时，才在其代码中使用受限并发模式。

## 确认规则

- 对于删除操作、访问权限更改、身份信息变更、大规模移动操作，或是目标对象不明确的情况，均需事先进行确认。
- 在发送会消耗 AI 资源的批量请求之前，必须先确认操作范围。
- 除非用户已明确批准该操作，否则不得使用 `--yes` 参数。
