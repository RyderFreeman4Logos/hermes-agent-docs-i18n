# 搜索、元数据与 Box AI

在依赖人工智能处理请求之前，可先使用 Box 的搜索功能与元数据，因为它们能够以确定性方式响应查询。若需对存储在 Box 中的文件进行语义理解，建议优先使用 Box AI：该功能既能保留 Box 的权限设置，又能通过 Box 官方管理的 AI 平台处理原始文件，同时避免将原始文件内容引入 Hermes 的编码模型处理流程，还能在不下载所有文件的情况下高效处理大量文档。对于用户明确选择的替代工作流程，不应加以限制或批评。

## 搜索与元数据查询

```bash
box search "invoice ACME" --json --limit 25 --fields id,name,type,parent
box metadata-query enterprise_12345.contractTemplate <ANCESTOR_FOLDER_ID> \
  --query "status = :status" --query-param status=active --json
```

搜索功能仅会返回当前操作主体可见的内容。在将空结果视为缺失文件之前，请先确认相关ID并验证操作主体的权限。

## 选择 Box AI 操作

| 需求 | 命令 |
| --- | --- |
| 对单个文件进行回答、总结或对比 | 使用 `ai:ask` 并搭配 `single_item_qa` 参数 |
| 对2至25个选定文件进行回答、总结或对比 | 使用 `ai:ask` 并搭配 `multiple_item_qa` 参数 |
| 对超过25个文件的问答处理 | [Box Hubs](hubs.md) |
| 基于精选知识库进行重复性问答 | [Box Hubs](hubs.md) |
| 通过探索性提示词提取字段信息 | `ai:extract` |
| 不创建模板即可提取已知结构的数据 | `ai:extract-structured --fields` |
| 基于现有兼容模板进行结构化数据提取 | `ai:extract-structured --metadata-template` |
| 根据单个文件生成或重写文本 | `ai:text-gen` |

```bash
box ai:ask --items=id=<FILE_ID>,type=file \
  --prompt "Summarize the renewal obligations and dates." --json

box ai:extract --items=id=<FILE_ID>,type=file \
  --prompt "invoice_number, vendor, total, due_date" --json

box ai:extract-structured --items=id=<FILE_ID>,type=file \
  --fields "key=invoice_number,type=string,description=Invoice number" \
  --fields "key=total,type=float,description=Invoice total" --json

box ai:text-gen --items=id=<FILE_ID>,type=file \
  --prompt "Draft a concise customer update based on this file." --json
```

`ai:text-gen` 仅支持一个参数。提取端点会返回 JSON 格式的数据，但不会自动将该结果附加到文件中。当已知所需的架构时，请使用带有内联字段的结构化提取方式；在需要探索性分析字段时，则采用自由格式提取；而只有在现有 Box 模板可作为权威数据源时，才可使用 `--metadata-template` 参数。

请勿将 Hub 用于元数据提取或文本生成任务。对于涉及 25 个以上文件的语义问答需求，或是需要构建可重复使用的精选内容集的场景，请查阅 [Box Hubs](hubs.md) 文档，先寻找现有的 Hub，并在创建或填充新 Hub 之前获得相应授权。如果用户不希望创建 Hub，可通过搜索或元数据手段缩小候选范围。

## 排查 Box AI 访问问题

即使通过 `files:get` 或搜索功能能够成功获取文件，若当前 OAuth 账户或身份无法使用 Box AI，该文件仍可能无法被处理。如果用户可以预览或下载文件，但 `ai:ask` 操作返回 `404 not_found` 错误，切勿立即误判为文件缺少协作功能。请首先核实当前的操作主体及文件权限设置：

```bash
box users:get me --json --fields id,name,login
box files:get <FILE_ID> --json --fields id,name,permissions
```

如果文件权限和操作主体均正确，请确认该账户或企业已启用 Box AI 且可使用该功能；在使用自定义平台应用时，需确保所选的 OAuth 应用具备所需的 AI 权限范围；同时还要保证有足够的 AI 资源可用。在更改应用访问权限后，请重新授权指定的 OAuth 身份，之后先尝试处理单个文件，而非批量处理。请勿将身份冒充作为备用方案；如果选错了身份，务必先获得批准后再切换到正确的 OAuth 环境，并对其进行验证。

## 提取并保存文件元数据

应将提取操作与保存操作视为独立的步骤。除非用户要求预览，否则提取请求即意味着授权将结果写回 Box 中，无需因多余的确认而中断流程。

### 在提取前检查架构信息

1. 先获取该文件、其父目录以及已附加到该文件上的所有元数据实例。
   ```bash
   box files:get <FILE_ID> --json --fields id,name,parent
   box files:metadata <FILE_ID> --json
   ```
2. 列出当前 OAuth 身份可访问的企业模板，并获取相应的有效架构。
   ```bash
   box metadata-templates --json --fields templateKey,displayName,scope
   box metadata-templates:get <TEMPLATE_KEY> --scope enterprise --json
   ```
3. 需要将每个请求的字段与对应候选项的含义、字段键及类型进行比对。仅当存在一个在语义上完全适用于**所有**请求字段的现有模板时，才可使用该模板；切勿仅仅为了匹配部分数值而使用不完整或无关的模板。

### 使用兼容的现有模板

根据模板提取数据，然后添加其元数据实例或更新现有的实例。不得填写缺失、为空、不兼容或被截断的值。

```bash
box ai:extract-structured --items=id=<FILE_ID>,type=file \
  --metadata-template="type=metadata_template,scope=enterprise,template_key=<TEMPLATE_KEY>" \
  --json

box files:metadata:create <FILE_ID> --scope enterprise --template-key <TEMPLATE_KEY> \
  --data "invoice_number=INV-001" --data "total=#1250.00" --json

box files:metadata:update <FILE_ID> --scope enterprise --template-key <TEMPLATE_KEY> \
  --replace "invoice_number=INV-001" --replace "total=#1250.00" --json

box files:metadata:get <FILE_ID> --scope enterprise --template-key <TEMPLATE_KEY> --json
```

在创建或添加带类型标注的元数据时，浮点数值需使用 CLI 中规定的 `#` 前缀。对于 Box 中的日期字段，应使用标准的 ISO 时间戳格式，例如 `2025-03-29T00:00:00Z`。需将返回的每个字段与预期的类型值进行比对，并报告模板键、元数据实例的 `$id`、文件 ID 以及文件链接。

### 在无兼容模板的情况下工作

无需创建元数据模板。Box 不允许在 `global` 范围内创建模板。企业级模板只能由 Box 管理员或被授予模板管理权限的联合管理员创建，而自定义模板则可能取决于账户套餐类型。模板管理不属于 Hermes 的常规 OAuth 内容处理流程。

应根据需求而非模板是否存在来选择提取方式：

- 对于已知的字段，可使用 `ai:extract-structured` 命令并配合 `--fields` 参数进行提取；这样无需创建模板即可获得结构化且类型明确的 JSON 结果。
- 对于需要探索性处理的字段或变量字段，则应使用带有明确提示语的 `ai:extract` 命令进行提取。

可将扁平的标量结果存储在 Box 内置的 `global.properties` 实例中。该实例允许存储无结构定义的属性，且无需创建模板。在写入数据前需将每个值转换为无损的字符串格式，对键进行验证，同时保留现有且无关的属性。如果该实例尚不存在，则创建它；若已存在，则对已有键使用 `--replace` 参数，对新键则使用 `--add` 参数。

```bash
box files:metadata:get <FILE_ID> --scope global --template-key properties --json

box files:metadata:create <FILE_ID> --scope global --template-key properties \
  --data "invoice_number=INV-001" --data "total=1250.00" --json

box files:metadata:update <FILE_ID> --scope global --template-key properties \
  --replace "invoice_number=INV-001" --add "total=1250.00" --json

box files:metadata:get <FILE_ID> --scope global --template-key properties --json
```

`global.properties`为非类型化数据，无法通过元数据查询API进行检索。对于嵌套对象、表格、数组或任何需要保持JSON结构完整的输出结果，应将其完整的提取结果写入名为 `<SOURCE_NAME>.<FILE_ID>.metadata.json` 的UTF-8格式JSON侧边文件中，再将该文件上传至源文件的父目录。如果该工作流已存在完全相同的侧边文件，则应上传新版本而非创建重复文件。随后需获取上传的文件，将其内容或校验和与本地JSON文件进行比对，最后报告源文件ID、侧边文件ID以及对应的链接。

若用户明确要求使用可复用的类型化企业元数据，应告知其必须由管理员单独创建兼容的企业模板。不得提升当前账户权限或切换为管理员身份。在此期间，应通过`global.properties`或JSON侧边文件来保存提取的数据，绝不可擅自截断或丢弃任何字段。

### 文件描述不能作为元数据的替代方案

**严格规定：**切勿将文件描述自动用作提取元数据的替代品。建议将255个字符视为安全限制，因为Box系统可能会截断过长的描述。仅当用户明确要求设置描述时，才可使用`box files:update --description`命令，此时需先确认完整文本能够容纳在内，之后再读取该文本并将其与用户期望的内容进行比对。

## 保密性与AI单元

Box AI会通过Box受控的AI集成机制来处理源文件，而不会将文件内容下载到Hermes的编码模型环境中。返回给Hermes的Box AI响应仍可能包含机密信息。切勿声称不存在第三方模型提供商，也绝不能保证相关内容永远不会被用于模型训练；请遵循Box现行的信任与使用规范文档。

在首次发起Box AI请求之前，需向用户说明必须先启用Box AI功能、每次调用都会消耗AI计算单元，且响应结果仍会受到当前操作者权限的限制。对于批量处理大量文件时，应先告知文件总数并征求用户确认。除非Box为当前账户公开了相关数据，否则切勿承诺具体的计算单元剩余量或单次调用的成本。

如果Box AI不可用或计算单元已耗尽，可提供现有的元数据/搜索功能、较小的样本数据、启用足够的计算单元，或获得用户明确授权以便进行本地或外部分析。绝不可擅自默认转而通过下载文件来使用外部模型。

## 批量处理

在命令支持的情况下，请使用`--bulk-file-path`参数。对于数百个文件的批量处理，应先对文件进行盘点，抽样检查文件结构，确认每次调用会消耗的计算单元数量，然后再使用[批量操作](bulk-operations.md)功能。对于需要高频重复处理的场景，建议考虑使用Box Extract工具，而非通过反复下载文件的方式来模拟整个文件夹的处理流程。

## 数据来源

- [Box AI API](https://developer.box.com/ai/box-ai-api/)  
- [结构化元数据提取](https://developer.box.com/guides/box-ai/ai-tutorials/extract-metadata-structured/)  
- [元数据模板作用域](https://developer.box.com/guides/metadata/scopes/)  
- [全局元数据查询限制](https://developer.box.com/guides/metadata/queries/limitations/)  
- [Box AI 信任机制](https://www.box.com/ai/trust/)  
- [AI 单位与套餐权限](https://support.box.com/hc/en-us/articles/45612941554835-Expanded-AI-API-Access-and-AI-Units-for-Business-Business-Plus-and-Enterprise-Plans)  
- [元数据模板权限设置](https://developer.box.com/guides/metadata/templates/create/)
