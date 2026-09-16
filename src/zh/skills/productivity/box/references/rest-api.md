# REST API 作为备用方案

当 CLI 缺少专用子命令时，可使用 `box request` 来扩展其功能。该方式会复用已配置的 Box 身份信息，因此无需让用户手动选择 REST 作为备用方案，即可继续执行常规请求操作。仅在需要删除数据、更改访问权限或身份信息、处理规模较大或成本较高的批量操作，或是目标与范围不明确时，才建议使用此方法。只有在 CLI 不可用，或者应用程序代码需要 SDK 无法提供的原始接口时，才应直接使用 REST。

使用 REST 并不会绕过 Box 的元数据安全规则：必须首先检查元数据实例及现有架构，绝不可创建或修改元数据模板，并且在每次写入操作后都需检索并比对元数据实例。切勿将文件描述视为隐式的元数据备用方案。

## CLI 请求的应急出口

```bash
box request /files/<FILE_ID> --json
box request /files/<FILE_ID> -X PUT --body '{"name":"renamed.pdf"}' --json
box request /folders -X POST --body '{"name":"New folder","parent":{"id":"0"}}' --json
```

## 创建原生 Box Note

当需要创建 Box Note 时，请使用 Box Notes API 来生成原生笔记，而非上传带有 `.boxnote` 后缀的纯文本文件。请指定正确的父文件夹（仅当用户的目标明确为其根目录时才可使用 `0`），随后获取返回的文件以进行验证：

```bash
box request /notes/convert -X POST \
  --header "box-version: 2026.0" \
  --body '{"content":"# Hello world\n\nhello world","content_format":"markdown","parent":{"id":"0"},"name":"hello-world"}' \
  --json
box files:get <RETURNED_FILE_ID> --json --fields id,name,type,parent
```

`content`字段采用Markdown格式，其大小限制为1 MB。请报告返回的文件ID以及该文件在Box平台上的常规链接。

## OAuth身份权限边界

`box request`功能会使用用户所选的OAuth CLI环境，而不会绕过用户的Box权限设置。如果无法使用CLI，可按照[SDK开发](sdk-development.md)文档中的说明，使用经过OAuth授权的SDK客户端。严禁将OAuth令牌或客户端密钥输出、记录到日志中，或提交至版本控制系统中。

## 参考资料

- [Box API参考文档](https://developer.box.com/reference/)
- [Box Notes API：从Markdown创建笔记](https://developer.box.com/guides/box-notes/convert-markdown/)
- [OAuth 2.0标准](https://developer.box.com/guides/authentication/oauth2/)
