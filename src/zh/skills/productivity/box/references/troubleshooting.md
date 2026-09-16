# 故障排除

在尝试其他解决方法之前，请先记录下执行操作的主体、对象ID与类型、具体命令、状态码以及安全的错误信息内容。

## 初步检查

```bash
box users:get me --json --fields id,name,login
box configure:environments:list
box files:get <FILE_ID> --json --fields id,name,parent
box folders:get <FOLDER_ID> --json --fields id,name,parent
box hubs --scope all --max-items 1000 --json
box hubs:get <HUB_ID> --json
```

请确认当前的执行主体、资源类型、ID、针对特定资源的协作设置、应用权限范围以及所选环境。请勿使用文件夹“0”作为访问测试对象：该文件夹无法定位到中心节点，且可能无法列出所有共享的文件或文件夹。

## 常见故障问题

| Signal | Likely cause | Next action |
| --- | --- | --- |
| local OAuth reports `EADDRINUSE`, opens an unusable result, or never returns to the CLI | occupied or mismatched loopback callback port | stop the waiting login process; for the official app, retry `3001`, `4000`, `5000`, then `8080`; for a custom app, register the exact new callback URI before retrying |
| remote OAuth browser ends on an unreachable localhost page | expected `--code` redirect or wrong topology | if Hermes is remote, return the URL's `code` and `state` to the waiting CLI; if Hermes and the browser are on the same host, stop and restart without `--code` |
| 401 or 403 | expired auth, missing scope, insufficient role | verify identity, reauthorize the app, and check folder role |
| shared file/folder absent from root or 404 | wrong actor, an access-only/shared item, or missing file/folder collaboration | verify `users:get me`, then fetch the known file/folder ID directly; only change collaboration after confirming the target and actor |
| Hub absent from root or 404 | root listing cannot discover Hubs, wrong actor, or missing Hub collaboration | run `box hubs --scope all` and `box hubs:get <HUB_ID>`; verify Hub collaboration separately from underlying-file access |
| 409 | duplicate name, existing collaboration, metadata conflict | list the parent/template and reuse or rename deliberately |
| 429 | rate limit | honor `Retry-After`, retry the same request, and reduce batch rate |
| Box AI access error | feature disabled, plan/unit restriction, unsupported content | explain the limitation and offer metadata/search, a sample, units, or approved fallback |

如果发现两个Hermes配置文件或会话似乎互相改变了对方的Box操作主体，需谨记：对于同一操作系统用户而言，私有的npm安装并不会隔离Box CLI环境。请先列出所有环境，确认当前的操作主体，再考虑进行切换。在Linux系统中，若CLI提示将使用明文凭证作为备用方案，应发出警告，提示存在`~/.box`目录，但无需读取或显示其中的凭证文件，并建议配置Secret Service/libsecret或使用独立的运行时用户。

在确认身份与访问权限之前，切勿试图诊断内容缺失的问题。也请勿通过悄悄更改操作主体、扩大共享范围或下载机密源文件等方式来作为临时解决方案。
