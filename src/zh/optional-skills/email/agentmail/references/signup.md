# AgentMail 自签注功能

当智能体尚未拥有 AgentMail API 密钥时，请使用此功能。此时需要由人工接收并提供一次性密码（OTP）。

## 注册流程

```bash
npm install -g agentmail-cli@latest
agentmail agent sign-up \
  --human-email you@example.com \
  --username my-agent \
  --source agentmail-cli \
  --referrer hermes-agent \
  --format json
```

导出返回的 `api_key`：

```bash
export AGENTMAIL_API_KEY="am_..."
```

通过一次性验证码进行验证：

```bash
agentmail agent verify --otp-code 123456
```

## 备注

- 使用真实的人类电子邮件地址作为 `--human-email` 的值。
- `human_email` 是注册时的幂等性密钥，但若使用相同的邮箱再次注册，则 API 密钥将会更换。
- 在通过验证之前，账户仅拥有一个收件箱，每日可发送 10 次消息，且只能发送至注册时使用的那个人类电子邮件地址。

## 首次检查

```bash
agentmail inboxes list --format json
agentmail inboxes:messages send \
  --inbox-id my-agent@agentmail.to \
  --to you@example.com \
  --subject "AgentMail verified" \
  --text "My AgentMail inbox is verified." \
  --format json
```

继续阅读 [core.md](core.md) 文档。
