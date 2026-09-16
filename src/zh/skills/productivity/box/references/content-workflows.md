# 内容工作流

在项目被解析后，应使用标识符而非路径来操作。如果当前的 OAuth 身份无法访问目标资源，请确认项目的准确标识符，并请该资源的所有者将该身份添加到相应的文件、文件夹或 Hub 中。

## 浏览与创建文件夹

```bash
box folders:get <FOLDER_ID> --json --fields id,name,parent,item_collection
box folders:items <FOLDER_ID> --json --max-items 100 --fields id,name,type
box folders:create <PARENT_ID> "Customer-123" --json --fields id,name,parent
```

若某个父目录中存在重复的名称，系统将返回 `409` 错误。此时应直接使用现有的文件夹 ID，而非盲目重试。

## 验证共享文件或文件夹

当当前的 OAuth 账户收到文件或文件夹的共享邀请时，若其 Box URL 中包含对应 ID，请直接使用该 ID 来获取目标资源。切勿将文件夹 `0` 不存在这一情况视为访问失败的证明，因为那只是该账户的根目录列表而已。如果仅知道文件或文件夹的名称，可通过 Box 搜索功能查找对应的 ID，之后再获取该资源：

```bash
box search "Quarterly plan" --json --limit 20 --fields id,name,type,parent
box files:get <FILE_ID> --json --fields id,name,parent
box folders:get <FOLDER_ID> --json --fields id,name,parent
```

如需获取 Hub 邀请链接，请使用 [Box Hubs](hubs.md)：Hub 并非文件或文件夹，需单独进行查找。

## 上传、下载及管理文件版本

```bash
box files:upload ./artifact.pdf --parent-id <FOLDER_ID> --json --fields id,name,size
box files:get <FILE_ID> --json --fields id,name,size,sha1,parent
box files:download <FILE_ID> --destination . --save-as local-copy.pdf
box files:versions:upload <FILE_ID> ./updated.pdf --json --fields id,name,sha1
box files:versions:list <FILE_ID> --json
box files:versions:download <FILE_ID> <VERSION_ID> --destination . --save-as older.pdf
```

仅当任务确实需要本地编辑，或用户明确允许进行外部分析时，才下载源代码字节。相比通过重命名来替换无关文件，更建议创建新版本。

## 创建原生 Box Note

当用户请求创建 Box Note 时，应通过 `box request` 功能基于 Markdown 内容生成原生笔记，而非使用名为 `.boxnote` 的上传文本文件。有关具体的请求及验证命令，请参阅 [REST API 备用方案](rest-api.md)。如果目标路径明确或无疑属于用户的根目录，则应立即创建笔记；否则需先询问用户要使用哪个文件夹。

## 重命名、添加标签及移动

```bash
box files:update <FILE_ID> --name "Renamed.pdf" --json --fields id,name
box files:update <FILE_ID> --description "Updated by Hermes" --tags "reviewed,2026" --json
box files:move <FILE_ID> <NEW_PARENT_ID> --json --fields id,name,parent
box folders:move <FOLDER_ID> <NEW_PARENT_ID> --json --fields id,name,parent
```

每次执行写入操作后，都应重新读取该文件或其父目录的内容。移动文件夹时其内部内容也会随之移动；在执行大规模移动操作之前，请务必先进行确认。

## 文件描述

建议将255个字符作为安全的文件描述长度限制；Box系统可能会对过长的描述进行截断。切勿将文件描述作为提取元数据的备用方案。只有当用户明确要求提供描述时才设置描述，在写入之前需确认完整文本能够容纳在指定长度内，随后读取文件并将返回的描述与预期内容进行比对。建议使用[搜索与AI功能](search-and-ai.md)将提取的结果以元数据或JSON侧载文件的形式持久保存。

## 协作与共享

```bash
box collaborations:create <FOLDER_ID> folder --role editor --login collaborator@example.com --json
box shared-links:create <FILE_ID> file --access company --json
box shared-links:create <FOLDER_ID> folder --access open --json
```

请使用权限最低的协作角色。创建或调整共享链接会改变访问权限，因此必须获得明确确认。

## 在不更改权限的情况下进行导航

对于调用方已知晓的项，可直接提供以下链接，此类链接不会生成共享链接：
- 文件：`https://app.box.com/file/<FILE_ID>`
- 文件夹：`https://app.box.com/folder/<FOLDER_ID>`

请在链接中附上该项的ID。如果普通用户无法打开仅对关联的Box账户可见的项，应直接说明情况，而无需创建具有更宽泛访问权限的链接。

## 读取和写入元数据

```bash
box files:metadata:get <FILE_ID> --scope global --template-key properties --json
box files:metadata:create <FILE_ID> --scope global --template-key properties \
  --data invoice_id=INV-001 --json
```

`global.properties` 是 Box 内置的、无需遵循特定架构的元数据实例，因此无需创建模板。它的数值并非可重复使用的结构化企业级架构，也无法被元数据查询 API 所使用。在写入新数据之前，请先读取所有现有的元数据实例，以便保留那些无关的属性。当需要从文档内容中提取元数据时，请使用 [Search and AI](search-and-ai.md) 功能，切勿使用不完整、无关或仅部分匹配的企业级模板。
