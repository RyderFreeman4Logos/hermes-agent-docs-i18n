# Box Hubs

您可以使用 Box Hubs 对经过筛选的知识库进行定期问答。直接通过 Box AI Ask 提交请求时，最多可处理 25 个选定文件；而通过 Hub 提交请求则只需发送一个 `hubs` 对象，系统便会检索该 Hub 中已索引的内容。请勿将 Hub 用于元数据提取或文本生成任务。

## 检查功能可用性并查找现有 Hub

Box 免费开发者计划已包含 Hubs API、Box AI API 以及用于开发和测试的月度 AI 单位额度。请勿将 Box Web 应用计划的条款视为普遍适用的 API 使用限制。CLI 也会调用相同的 API，且不会绕过账户权限设置：实际功能可用性仍取决于组织的订阅计划及 Box 配置。

在首次发送 Hub AI 请求之前，需向用户说明必须先启用 Box AI 功能，且该功能会消耗 AI 单位；无需等待用户确认。同时要告知用户，系统给出的答案仅来源于当前操作者有权访问的已索引文件。Hub 并非文件或文件夹：因此绝不能使用 `folders:items 0` 这类方式来查找或拒绝 Hub 邀请。在提议创建新 Hub 之前，应先确认当前操作者身份，再列出可访问的 Hub 列表：

```bash
box users:get me --json --fields id,name,login
box hubs --scope all --max-items 1000 --json
box hubs --query "Product" --scope all --sort relevance --json
box hubs:get <HUB_ID> --json
box hubs:items <HUB_ID> --max-items 100 --json
```

若已知 Hub 的 URL 或 ID，即使列表为空也可直接运行命令 `box hubs:get <HUB_ID>`。每个 Hub 应以 `https://app.box.com/hubs/<HUB_ID>` 的格式进行标识。在提出问题之前，请先检查 `is_ai_enabled` 的状态，随后发送一次受限的 Hub Ask 请求以确认 API 是否真正可用。在创建 Hub 之前必须先启用 Box AI for Hubs，这样 Box 才能对其内容进行索引。如果 Hub AI 不可用，则需区分是功能被禁用、Hub 创建于 AI 功能启用之前、索引延迟、缺少 Hub 协作功能、无法访问底层文件，还是 AI 计算单元已耗尽等情况；切勿擅自将源文件下载到 Hermes 的模型上下文中。

## 在整个 Hub 中提问

可使用单个 Hub 项目并结合 `single_item_qa` 功能。请请求引用信息，以便 Hermes 能够指出答案对应的源文件。进行 Hub 相关的问答时，请使用 `box request`（或 SDK），而非依赖 `box ai:ask`，因为后者的某些已安装 CLI 版本可能不支持 Hub 项目类型。此方法会使用 Box AI Ask 接口；对于 `/hubs` 管理端点而言需要添加 `box-version: 2025.0` 标头，但该请求则无需。

```bash
box request /ai/ask -X POST \
  --body '{"mode":"single_item_qa","items":[{"id":"<HUB_ID>","type":"hubs"}],"prompt":"Summarize the approved renewal terms and cite each source.","include_citations":true}' \
  --json
```

在回答中需注明Hub ID及导航链接。当Box返回引用信息时，需列出相关的文件ID、文件名称及文件链接。答案的内容应仅限于已索引且可访问的Hub内容，不得声称已搜索过未索引或用户无法访问的文件。

## 创建并填充Hub

请勿自动创建Hub。对于涉及25个以上文件的问答任务，或是需要重复使用的精选内容集，应先寻找现有的可用Hub。若没有合适的选项，则可提议创建一个精选Hub，并在创建或填充内容之前获得明确批准。如果用户拒绝，可通过搜索或元数据来缩小本次查询的范围。

获得批准后，再创建该Hub，告知其链接，并进行验证：

```bash
box hubs:create "Policy knowledge base" --description "Approved policy reference" --json
box hubs:get <HUB_ID> --json
```

添加某个项目仅会创建对应的引用记录，并不会移动该文件或文件夹本身。对于明确要求的小规模添加操作，系统可直接执行而无需重复提示。在进行批量添加或删除操作之前，请务必先确认操作，随后仔细核对所有返回的结果，并重新查看Hub中的项目列表。由于API在处理多项目更改时可能会返回部分成功的状态，因此不能仅凭单次请求的成功响应就认定所有项目都已成功添加。

```bash
box hubs:items:manage <HUB_ID> \
  --add id=<FILE_ID>,type=file --json
box hubs:items:manage <HUB_ID> \
  --add id=<FOLDER_ID>,type=folder --json
box hubs:items <HUB_ID> --max-items 100 --json
```

如果未指定 `parent-id`，CLI 会将该项目添加到第一个项目列表块中。若要定位特定的项目列表块，首先需使用 `box hubs:document:pages <HUB_ID> --json` 列出页面，再通过 `box hubs:document:blocks <HUB_ID> <PAGE_ID> --json` 获取对应的块，最后将返回的项目列表块 ID 作为 `parent-id` 使用。

在启用或禁用 Hub AI、删除或复制 Hub，或是更改共享权限之前，请务必先进行确认。可通过 `box hubs:get`、`box hubs:items` 或 `box hubs:collaborations` 命令来验证各项更改是否生效。

```bash
box hubs:update <HUB_ID> --ai-enabled --json
box hubs:collaborations <HUB_ID> --max-items 100 --json
box hubs:collaborations:create <HUB_ID> --role viewer --user-id <USER_ID> --json
```

## 处理索引、权限与限制问题

新添加的内容通常会在几分钟内完成索引，但在极端情况下也可能需要长达一小时的时间。建议先确认内容是否已成功添加，若未显示则可等待或重试一定次数，并将状态标记为“可重试索引中”，而非直接判定该资源不存在。权限问题需单独排查：只要`box hubs`或`box hubs:get`命令能成功执行，即说明具备访问Hub的权限，但不代表能访问其中的所有文件。Hub的响应会依据查询者的实际权限来决定其能访问哪些底层文件。

Box AI for Hubs为每个Hub以及整个企业设置了服务使用限制。目前Box的官方指南规定每个Hub最多可存储20,000个文件；在接近该限制值时，请务必查阅当前账户或产品的具体文档。请注意，这一数值并非不可更改的绝对标准。此外，只有支持格式的文档文本表示中的前4 MB内容会被索引。在发起首次请求之前，应先说明AI单元的使用方式，并确认是需要处理大量数据还是针对整个Hub的批量查询。

## 参考资料

- [Box Hubs API概述](https://developer.box.com/guides/hubs-api/)
- [Box免费开发者计划](https://developer.box.com/guides/getting-started/free-developer-plan/)
- [Box AI Ask API](https://developer.box.com/reference/post-ai-ask/)
- [向Hub提问的方法](https://developer.box.com/guides/box-ai/ai-tutorials/ask-questions/)
- [Box AI for Hubs](https://support.box.com/hc/en-us/articles/29347206309395-Box-AI-for-Hubs)
- [Box Hubs的限制规定](https://support.box.com/hc/en-us/articles/28323495455123-Box-Hubs-Known-Issues-and-Limitations)
