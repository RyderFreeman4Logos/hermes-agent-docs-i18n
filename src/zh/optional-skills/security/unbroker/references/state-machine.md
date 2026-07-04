# 案例状态机

一个案例对应一对（主体 x 经纪商）。“pdd.py record”工具会依据该状态机表验证每一次状态转换，并将其记录到`audit.jsonl`文件中。权威的定义则存储在`scripts/ledger.py`中。

## 状态说明

| 状态 | 含义 |
|---|---|
| `new` | 案例已创建，尚未执行任何操作 |
| `searching` | 正在扫描中 |
| `not_found` | 未找到该主体（将在下一个周期重新检查） |
| `found` | 已确认存在该主体，需采取相应措施 |
| `indirect_exposure` | 该主体的个人身份信息（邮箱/电话/姓名）出现在**第三方**的记录中（例如出现在亲属的“家庭成员”字段中）。此类信息无法通过自助退出功能删除，需通过专门的CCPA/GDPR“删除我的个人身份信息”请求来处理 |
| `action_selected` | 已选择处理级别/方式 |
| `submitted` | 退出申请已提交 |
| `verification_pending` | 正在等待邮件/电话验证 |
| `awaiting_processing` | 申请已提交，无需验证，正在由经纪商处理中 |
| `confirmed_removed` | 已确认信息已被删除 |
| `reappeared` | 曾被删除，现在又重新出现 |
| `human_task_queued` | 需要人工介入处理（如验证码验证、身份信息核验、电话/传真/邮件沟通等） |
| `blocked` | 经纪商服务中断或系统故障 → 需标记以便在数据库中重新进行验证 |

## 允许的状态转换

```
new                  -> searching | found | not_found | indirect_exposure | blocked
searching            -> not_found | found | indirect_exposure | blocked
not_found            -> searching | found | indirect_exposure | blocked
found                -> action_selected | submitted | human_task_queued | indirect_exposure | blocked
indirect_exposure    -> submitted | human_task_queued | not_found | found | blocked
action_selected      -> submitted | human_task_queued | blocked
submitted            -> verification_pending | awaiting_processing | human_task_queued | blocked
verification_pending -> awaiting_processing | confirmed_removed | human_task_queued | blocked
awaiting_processing  -> confirmed_removed | human_task_queued | blocked
confirmed_removed    -> reappeared | confirmed_removed   (recheck refreshes the date)
reappeared           -> found | indirect_exposure
human_task_queued    -> found | indirect_exposure | action_selected | submitted | verification_pending
                        | awaiting_processing | confirmed_removed | blocked
blocked              -> searching | found | not_found | indirect_exposure | action_selected
                        | human_task_queued
```

系统始终允许状态回退至相同状态（即操作具有幂等性）。

## 实际工作中发现的注意事项/常见陷阱

- **`submitted -> not_found` 是不被允许的。** 当提交的请求未能找到匹配的配置文件时，系统应直接进入 `awaiting_processing` 状态，而绝不能回退到 `not_found` 状态。（这就是为什么在用户已提交请求后，若匹配器显示“无结果”，系统仍会将其状态记录为 `awaiting_processing` 而非 `not_found`。）
- **直接从 `blocked` 状态跳转至 `submitted` 是非法的**——正确的状态流转路径应为 `blocked -> action_selected -> submitted`。
- **记录操作员的手动判定结果：** 需附加 `operator_manual_check` 类型的证据备注。对于已无法访问/返回 404 错误的网站，或经操作员确认“无结果”的搜索，均可视为有效的 `not_found` 状态。
- **`--evidence` 参数的 shell 使用陷阱：** 若在 `--evidence` 参数后使用包含字面量 `&` 的 JSON 字符串，会触发 shell 的后台处理保护机制——此时应使用单词 “and” 代替 `&`。
