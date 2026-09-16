# Webhook与事件

若需针对文件或文件夹发送推送通知，可使用Webhook。如需进行数据补传、回溯操作或获取持久化游标，则建议使用Events API的轮询功能。管理Webhook需要一个具有**管理Webhook**权限范围的自定义OAuth平台应用；官方Box CLI OAuth应用无法满足此需求。应使用拥有目标对象访问权限的普通OAuth身份进行操作，除非目标操作本身要求使用管理员身份。 

## 创建与查看Webhook

```bash
box webhooks:list --json
box webhooks:create folder <FOLDER_ID> \
  --triggers FILE.UPLOADED,FILE.VERSION_UPLOADED \
  --address https://example.com/box/webhook --json
```

当前执行主体需具备访问目标对象的权限，同时应用程序也需拥有相应的权限范围。在创建 Webhook 之前，请先确认目标 URL 及事件触发条件。

## 使用持久化游标轮询用户事件

如需进行用户数据补录或回填操作，可通过选定的 OAuth 身份来调用用户事件 API。请勿使用 CLI 中默认的 `box events` 命令，因为它默认会获取企业级管理员日志流。在每次成功获取响应后，请保存返回的 `next_stream_position` 值，然后在下一次轮询时使用该值：

```bash
box request /events --query "stream_type=changes&stream_position=now" --json
box request /events --query "stream_type=changes&stream_position=<SAVED_CURSOR>" --json
```

请仅将 `stream_position=now` 用于初始化未来事件的游标。若需回填数据，应先使用已确认的有效历史游标或先对目标文件夹进行对账处理，随后将每个返回的游标与已处理的事件 ID 以原子方式一同持久化存储。

## 应用处理程序规范

在实现正式发布的应用程序时，请遵循以下要求：

1. 在解析消息内容或执行相应操作之前，务必验证 Box 签名。
2. 由于数据传输可能会重复，需妥善保存幂等性键。
3. 迅速确认接收并异步处理任务。
4. 从 Box 获取当前文件或文件夹的信息，切勿将事件载荷视为最终状态。
5. 在轮询时，需持久化存储 Events API 的游标。

建议对有效事件、重复事件、无效签名以及重启/补传流程进行测试。

## 参考资料

- [Box Webhook 文档](https://developer.box.com/guides/webhooks/)
- [Events 资源文档](https://developer.box.com/reference/resources/event/)
- [用户事件相关指南](https://developer.box.com/guides/events/user-events/for-user/)
