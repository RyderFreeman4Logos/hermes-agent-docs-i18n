# CCPA / CPRA（加利福尼亚州）

适用于加利福尼亚州居民（`residency_jurisdiction` 的值以 `US-CA` 开头），实际上也适用于许多在全国范围内响应 CCPA 类请求的美国经纪商。

## 可行使的权利

- **删除**个人信息（《加利福尼亚州民法典》第 1798.105 条）。
- **选择不参与**个人信息的出售或共享（第 1798.120 条）。

## 请求内容

通过 `legal.render_request("ccpa", broker, fields)` 生成内容，输出文件为 `templates/emails/ccpa-deletion.txt`。请求中仅需包含：完整的法定姓名、用于沟通的电子邮箱地址以及已确认的房源网址。**不得**包含社会安全号码或政府颁发的身份证明号码。

## 授权代理人

如代表其他已同意处理的主体行事，需使用 `render_request("ccpa_agent", ...)`（对应模板为 `templates/emails/ccpa-authorized-agent.txt`），并附上存档中的授权文件（`consent.authorization_artifact`）。经纪商可另行核实消费者的身份。

## 备注

- 经纪商必须在 45 天内予以回复（该期限可延长）。在确认处理结果之前，状态应标记为 `awaiting_processing`。
- “隐藏于免费搜索结果”并不等同于信息已删除。在将状态标记为 `confirmed_removed` 之前，必须确认相关记录确实已被移除。
