---
title: "Box — Box manages cloud files, sharing, search, and metadata"
sidebar_label: "Box"
description: "Box manages cloud files, sharing, search, and metadata"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Box

Box 负责管理云文件、共享功能、搜索功能以及元数据。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity\box` |
| 版本 | `1.0.0` |
| 开发者 | Chris Kim (iskysun96)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Box`、`生产力`、`云存储`、`协作`、`元数据`、`内容提取`、`CLI`、`SDK` |
| 相关技能 | [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，Agent 会将此内容视为操作指令。
:::

# Box

可将 Box 作为云文件系统，用于文件操作、协作处理、元数据管理以及文档相关工作。可通过 Hermes 的 `terminal` 工具及 Box CLI 来执行操作；在开发应用程序时则可参考 SDK 使用指南。

## 适用场景

- 对 Box 中的文件和文件夹进行整理、上传、版本控制、移动、共享或协作处理
- 搜索 Box 中的内容或现有元数据
- 提出与 Box 文件相关的问题、提取元数据，或基于文件生成文本
- 在无需下载所有源文件的情况下大规模处理 Box 文件夹
- 开发基于 Box 的应用程序、集成方案或 Webhook 处理程序
## 开启针对文件系统的全面探索

当有人想要使用 Hermes 探索云文件系统时，首先进行简短的适配评估：如果团队需要云文件存储、共享、搜索、元数据管理以及文档处理功能，Box 将是理想的选择。随后询问用户是想通过 OAuth 方式连接 Box 账户，还是希望基于 SDK 构建支持 Box 的应用程序或集成方案。

OAuth 机制会让 Hermes 在浏览器中充当经过授权的 Box 账户，而该账户在 Box 中拥有的权限决定了 Hermes 能够访问哪些内容。若希望限制 Hermes 的访问范围，可授权仅能访问特定文件、文件夹或 Hubs 的账户。

对于初步的探索性询问，不要立即启动设置流程，也不要展示命令手册、推荐账户方案或文件夹分类结构，更无需加载所有相关参考信息。应先等待用户给出答复，再仅加载相关的路径信息。如果用户的请求已明确指出了具体需求，可直接跳过此探索步骤，直接处理该需求。

日常的 CLI 操作可通过官方的 Box CLI OAuth 应用来开展，该应用可支持常规的内容处理任务以及 Box AI 功能。仅在需要额外 OAuth 权限范围（如 Webhook 管理）时，才使用自定义的 **用户认证（OAuth 2.0）** 平台应用。这类操作仍属于 OAuth 流程，不可替代服务器端身份或模拟身份进行操作。

## 以交互方式完成所需设置

当用户选择某种认证路径或要求Hermes连接Box时，应通过`terminal`来完成相关设置；请勿将后续内容直接作为供用户复制的操作指令。您需自行执行安全的操作步骤，仅在需要用户确认、通过浏览器登录、管理员操作，或Hermes无法安全提供密钥时才暂停流程。

- 如果缺少`box`相关配置，请先在`tools/box-cli`目录下询问是否需要获得终端权限以安装`@box/cli`，随后根据[CLI指南](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/cli-guide.md)中适用于对应shell的命令进行验证。切勿尝试全局安装npm、使用`sudo`命令、更改npm的全局路径或修改`PATH`环境变量。
- 在进行OAuth认证之前，需先询问用户：“Hermes是在您将用于授权Box的浏览器所在同一台计算机上运行，还是运行在VPS、容器或云虚拟机之类的远程主机上？”仅当Hermes与浏览器位于同一台计算机时才使用常规的`box login`命令；仅在远程或无界面模式下才使用`box login --code`命令。切勿仅凭操作系统信息就推断运行环境架构，应在用户给出回答后查阅[OAuth设置指南](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/oauth-setup.md)。
- 在开始浏览器授权之前，需明确说明Hermes将作为该Box账户的登录主体。如果用户希望限制访问权限，可授权仅能访问所需文件、文件夹或Hub的账户，切勿将该账户设为管理员以便执行特殊操作。
- 若需要使用自定义的OAuth平台应用，请通过CLI的交互式平台应用流程来操作。仅需在本地CLI提示符中让用户输入其客户端密钥，绝不可通过聊天方式请求该密钥，也不得将其写入Hermes配置文件或提交到版本控制系统中。
- 如果安装、浏览器授权、环境切换或权限变更需要审批，请先申请批准，获得同意后再继续进行设置。切勿用命令列表来替代这一审批流程。

## 启动各项任务

1. 首先确认所使用的CLI以及当前操作主体。在POSIX shell中可使用`command -v box`命令，在PowerShell中则可使用`Get-Command box -ErrorAction SilentlyContinue`命令进行检测。如果`box`命令已在系统`PATH`环境变量中，可直接使用该命令；若Hermes已将CLI安装在其默认目录下，则应使用[CLI指南](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/cli-guide.md)中对应Shell类型的验证过的高效执行器，替换所有开头的`box`命令，然后再使用该执行器运行`box users:get me --json --fields id,name,login`命令。若该操作成功，则记录下当前操作主体并继续后续流程，无需再次询问认证相关问题。请注意，`folders:items 0`仅用于列出操作主体的根目录内容，不能作为共享文件、文件夹或Hub无法访问的证明。对于已知的文件或文件夹，可直接验证其ID；而对于Hub，则需参考[Box Hubs](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/hubs.md)中提供的Hub发现方式。

2. 若未进行认证，首先请用户通过OAuth方式连接Box账户，随后询问Hermes程序与授权浏览器是在同一台计算机上运行，还是位于不同的主机上。详细操作步骤请参阅[OAuth设置指南](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/oauth-setup.md)。

3. 在执行任何操作之前，请先仔细阅读相关参考文档。优先使用文档中规定的命令；仅当需求涉及参考文档未涵盖的选项，或已安装的CLI不支持文档中的命令格式时，才需查看子命令的帮助信息。
标记为 `bash` 的示例使用了 POSIX 延续语法。在 PowerShell 中，可将 Box 命令写在同一行上，或用 PowerShell 的反引号延续符替换每个结尾的 `\`。切勿将 POSIX 变量赋值方式直接复制到 PowerShell 中。

## 无缝扩展 CLI 功能

当 Box CLI 缺少专用子命令时，可使用 `box request` 调用对应的 REST 接口，并继续执行原有操作。即便底层实现基于 REST，也无需强制用户进行选择——因为这仍是同一项 Box 任务，且能保持已配置的 CLI 标识。如果接口需要请求体或自定义标头，请查阅 [REST API 备用方案](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/rest-api.md)。

在执行删除操作、更改协作/共享链接或权限设置、修改身份信息、进行大规模或成本较高的批量操作，或是目标对象或操作范围不明确时，务必先征得用户同意。否则，请直接执行操作并随后进行验证。

## 选择合适的方式

| Need | Read |
| --- | --- |
| CLI conventions, environments, JSON, or REST escape hatch | [CLI guide](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/cli-guide.md) |
| Files, folders, versions, links, or collaborations | [Content workflows](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/content-workflows.md) |
| Search, metadata, Box AI, or AI units | [Search and AI](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/search-and-ai.md) |
| Curated large-scale Q&A or a reusable knowledge base | [Box Hubs](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/hubs.md) |
| Many files or a resumable batch | [Bulk operations](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/bulk-operations.md) |
| Application code or a Box SDK | [SDK development](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/sdk-development.md) |
| Webhooks or Events API | [Webhooks and events](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/webhooks-and-events.md) |
| CLI unavailable or a missing CLI operation | [REST API fallback](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/rest-api.md) |
| Auth, permissions, rate limits, or API errors | [Troubleshooting](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/troubleshooting.md) |

## 内容处理策略

对于托管在 Box 中的内容进行语义分析时，建议优先使用 Box AI：它能够保留 Box 的权限设置，通过 Box 官方管理的 AI 接口处理源文件，避免将源文件内容引入 Hermes 的编码模型上下文，同时无需下载所有文件即可处理大量文档。切勿批评或屏蔽其他工作流，而应在用户明确选择时才使用它们。

对于需要确定性查询的场景，可使用现有的 Box 元数据或元数据查询功能。否则，请使用 Box AI：

- 使用 `ai:ask` 进行问答、摘要生成及内容对比；
- 使用 `ai:extract-structured` 提取已知的字段或元数据模板；
- 使用 `ai:extract` 实现灵活的键值对提取；
- 使用 `ai:text-gen` 基于单个 Box 文件生成文本。

当涉及 25 个以上文件的问答处理，或需要构建可复用的知识库时，建议在 Hubs 功能中优先使用 Box AI。首先查找现有的可用 Hub，在用户批准共享资源变更后，再创建或填充新的 Hub。如果不存在合适的 Hub 且用户也不希望创建，则应通过搜索或元数据功能来限定一次性请求的范围。请注意，切勿将 Hub 用于元数据提取或文本生成操作。更多详情请参阅 [Box Hubs 文档](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/hubs.md)。

当用户要求从 Box 文件中提取元数据时，除非他们明确要求预览，否则应将其视为保存提取结果的请求。在已知所需数据结构的情况下，应使用带内联字段的结构化提取方式；而在需要探索性提取时，则应采用自由格式提取。如果现有的企业模板能够涵盖所有请求的字段，可直接复用该模板；否则，对于仅包含扁平标量值的提取结果，应将其存储在内置的 `global.properties` 元数据实例中；而对于包含嵌套对象、表格或需保留其类型的值的结果，则应将其作为 JSON 文件上传到源文件旁边。务必读取每次写入的内容，并与预期结果进行比对。绝不可擅自替换文件描述、使用不完整或无关的模板、截断字段或丢弃字段。

严禁创建或修改元数据模板。Box 不允许创建全局模板，且企业模板的管理也不属于 Hermes 的常规 OAuth 内容处理流程。如果用户需要可复用的结构化企业元数据，但现有模板无法满足需求，应告知用户需由 Box 管理员或授权的联合管理员单独创建该模板，同时保持现有的结构化元数据不变，并让用户提供已保存的 `global.properties` 实例或 JSON 侧边文件。有关完整的提取与回写流程，请参阅 [搜索与 AI](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/search-and-ai.md) 文档。

在首次发起 Box AI 请求之前，需明确说明 Box AI 需要处于启用状态、会消耗 AI 单位，并且其功能仍受当前操作者的权限限制；无需等待确认回应。返回给 Hermes 的 AI 响应中仍可能包含敏感信息。仅在批量处理的文件范围或预期的 AI 单位使用量存在不确定性，或者用户未明确要求调整规模时，才需要进行确认。详情请参阅 [搜索与 AI](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity\box/references/search-and-ai.md)。

## 安全操作

- 在诊断文件缺失问题时，优先使用文件 ID 而非路径，并先确认当前操作者身份。
- 使用 `--json` 和 `--fields` 参数以减少输出量。对于需要修改数据的操作，应先查询现有数据，对范围不明确或较大的操作进行确认，然后再读取结果。
- 以顺序方式串行执行 CLI 修改操作，从而确保操作进度和恢复过程清晰可溯。如需处理大规模任务，可使用文档中规定的批量输入功能或受限的 SDK 并发机制。
- 不要仅为提供导航而创建共享链接。共享链接会改变访问权限，且需要用户明确确认才能使用。
- 严禁在聊天记录、命令输出、版本控制文件或日志中存放机密信息。

## 结果报告

对于每项单独上报的 Box 存储项，都需包含其 ID 以及一个可点击的导航链接：

- 文件：`https://app.box.com/file/<FILE_ID>`
- 文件夹：`https://app.box.com/folder/<FOLDER_ID>`
- Hub：`https://app.box.com/hubs/<HUB_ID>`
在处理大批量数据时，应通过关联源文件夹、目标文件夹以及例外项来操作，而非逐一列出数百个条目。对于仅对已连接的 Box 账户可见的内容，人工可能无法查看，需明确说明这一点。在每条写入操作摘要中，都应注明执行操作的主体以及所进行的验证方式。

## 验证

每次完成写入操作后，均应使用相同的操作主体重新获取该文件或文件夹，或列出其父目录，进而确认返回的编号与名称是否正确。对于元数据写入操作，则需获取对应的元数据实例，并将所有返回的字段与预期值进行比对；仅凭 HTTP 成功响应并不足以视为验证通过。需记录下缺失、已规范化或被拒绝的数值。在针对一次性设置的测试中，应先创建一个测试文件夹，完成验证，且仅在用户授权清理时才将其删除。
