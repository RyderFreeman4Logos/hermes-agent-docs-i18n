# 批量操作

当需要处理的数量超过少量文件时，请使用此工作流。在开始处理之前，请先选择当前的 OAuth 操作主体，因为该主体仅能处理其具有访问权限的内容。

## 工作流流程

```
Inventory → classify if needed → plan → confirm → execute → verify → report
```

## 清单管理与规划

```bash
box folders:items <FOLDER_ID> --json --max-items 1000 --fields id,name,type,parent
```

逐页查看直至所有项目均被处理完毕。需记录下各项的ID、名称、类型、目标文件夹ID以及处理完成状态日志。在执行大规模移动操作、访问权限变更或使用AI功能之前，应先列出相关范围及存在歧义的情况以获取批准。

## 内容分类

建议优先采用确定的文件名、扩展名及现有元数据规则。对于语义分类，则应使用Box AI而非下载文件内容本身：

```bash
box ai:ask --items=id=<FILE_ID>,type=file \
  --prompt "Classify as invoice, receipt, contract, report, or other." --json
```

对于已知字段，请使用 `ai:extract-structured`；对于可变字段，则请使用 `ai:extract`。在处理大批量数据之前，应先抽取少量具有代表性的样本进行测试。在处理重要的人工智能任务批次之前，必须公开说明所使用的 Box AI 资源，并获得相关确认。

## 执行与恢复

需完整翻译输入内容，不得提前终止处理流程。

```bash
box folders:create <PARENT_ID> "Category" --json --fields id,name
box files:move <FILE_ID> <TARGET_FOLDER_ID> --json --fields id,name,parent
```

应以串行方式处理按顺序提交的 CLI 操作，并记录每一次操作的成败情况。遇到 `409` 状态码时，应查找并重新使用现有的目标资源；遇到 `429` 状态码时，则需遵循 `Retry-After` 指令并重新发起相同请求。恢复处理时应从“库存中已完成的 ID”列表继续，切勿盲目重启。

当相关命令支持时，请使用文档中规定的 `--bulk-file-path` 工作流程。仅当应用程序自身能够负责重试、确保操作幂等性以及处理速率限制时，才应使用带并发限制的 SDK。

## 验证与报告

需列出每个目标位置及对应的源文件夹，然后将其中的 ID 和数量与计划方案进行比对。同时要提供指向源文件夹、目标文件夹以及异常情况的链接。除非用户要求生成清单，否则无需列出数百个项目的链接。
