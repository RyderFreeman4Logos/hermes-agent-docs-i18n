---
title: "Telephony — Give Hermes phone capabilities without core tool changes"
sidebar_label: "Telephony"
description: "Give Hermes phone capabilities without core tool changes"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 电话功能

无需修改核心工具即可为 Hermes 添加电话功能。该功能可配置并持久保存 Twilio 号码，实现短信/MMS 的收发、直接通话，以及通过 Bland.ai 或 Vapi 发起人工智能驱动的外呼。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/productivity/telephony` 安装 |
| 路径 | `optional-skills/productivity/telephony` |
| 版本 | `1.0.0` |
| 开发者 | Nous Research |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `telephony`、`phone`、`sms`、`mms`、`voice`、`twilio`、`bland.ai`、`vapi`、`calling`、`texting` |
| 相关技能 | [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps)、[`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace)、[`agentmail`](/docs/user-guide/skills/optional/email/email-agentmail) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 电话功能——无需修改核心工具即可实现号码、通话与短信功能

这款可选技能可在不将电话功能纳入核心工具列表的情况下，为 Hermes 提供实用的电话功能。

它附带了一个辅助脚本 `scripts/telephony.py`，可用于：
- 将服务提供商的凭证保存到 `~/.hermes/.env` 中
- 搜索并购买 Twilio 电话号码
- 在后续会话中记住已拥有的号码
- 从该号码发送短信/MMS
- 无需 webhook 服务器即可轮询该号码的来电短信
- 使用 TwiML 的 `<Say>` 或 `<Play>` 标签直接拨打 Twilio 电话
- 将已拥有的 Twilio 号码导入 Vapi
- 通过 Bland.ai 或 Vapi 发起人工智能驱动的外呼

## 解决的问题

该技能旨在满足用户实际需要的各类电话操作：
- 外拨电话
- 发送短信
- 拥有一个可重复使用的智能体号码
- 查看发送到该号码的消息
- 在不同会话之间保留该号码及相关标识符
- 为未来接收来电短信及其他自动化场景提供完善的电话身份管理

请注意，它**不会**将 Hermes 转变为实时的来电电话网关。来电短信功能是通过轮询 Twilio REST API 实现的，对于许多工作流而言已足够使用，包括通知发送及一次性验证码获取等场景，且无需额外搭建核心 webhook 基础设施。

## 安全规则——必须遵守

1. 每次拨打电话或发送短信前务必确认。
2. 绝不对紧急号码进行拨打。
3. 禁止利用电话功能实施骚扰、垃圾信息发送、身份冒充或任何非法行为。
4. 将第三方电话号码视为敏感的操作数据：
   - 不得将其保存在 Hermes 的内存中
   - 除非用户明确要求，否则不得在技能文档、摘要或后续记录中提及这些号码
5. 可以持久保存**智能体拥有的 Twilio 号码**，因为这属于用户的配置内容。
6. VoIP 号码**无法保证**适用于所有第三方双重身份验证流程。请谨慎使用，并向用户明确说明相关限制。

## 决策树——选择哪种服务？

建议使用以下逻辑而非硬编码的服务提供商路由方式来做出选择：

### 1) “我希望 Hermes 拥有一个真实的电话号码”
选择 **Twilio**。

原因：
- 购买并保留号码的流程最为简单
- SMS/MMS 支持最为完善
- 接收来电短信的轮询方案最简单
- 未来升级为接收 webhook 或处理来电的路径最为清晰

适用场景：
- 后续接收短信
- 发送部署警报或定时任务通知
- 为智能体维护一个可重复使用的电话身份
- 日后尝试基于电话的认证流程

### 2) “我现在只需要最简单的人工智能外呼功能”
选择 **Bland.ai**。

原因：
- 设置速度最快
- 仅需一个 API 密钥
- 无需自行购买或导入号码

权衡点：
- 灵活性稍低
- 语音质量尚可，但并非最优

### 3) “我需要最佳的语音对话人工智能体验”
选择 **Twilio + Vapi**。

原因：
- Twilio 可让智能体拥有自己的号码
- Vapi 能提供更优质的语音对话人工智能通话体验以及更多语音/模型选项

推荐流程：
1. 购买/保存一个 Twilio 号码
2. 将其导入 Vapi
3. 保存返回的 `VAPI_PHONE_NUMBER_ID`
4. 使用 `ai-call --provider vapi` 发起呼叫

### 4) “我想使用自定义预录语音消息进行通话”
使用带有公共音频 URL 的 **Twilio 直拨功能**。

原因：
- 播放自定义 MP3 文件的最简单方式
- 可与 Hermes 的 `text_to_speech` 功能结合使用，再通过公共文件托管服务或隧道传输音频

## 文件与持久化状态

该技能将电话相关状态保存在两个位置：

### `~/.hermes/.env`
用于存储长期有效的服务提供商凭证及已拥有号码的标识符，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER`（人工智能通话服务提供商：bland 或 vapi）

### `~/.hermes/telephony_state.json`
用于存储仅在技能层面且需在会话之间保留的状态信息，例如：
- 记住的默认 Twilio 号码/SID
- 记住的 Vapi 电话号码 ID
- 用于轮询收件箱的上一条来电消息的 SID/日期

这意味着：
- 下次加载该技能时，`diagnose` 功能可以告知当前已配置的号码
- `twilio-inbox --since-last --mark-seen` 命令可以从上一次的轮询点继续工作

## 查找辅助脚本

安装此技能后，可通过以下方式找到该脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 的值为空，说明该技能尚未安装。

## 安装

这是一项官方提供的可选技能，因此请通过 Skills Hub 进行安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

## 提供商配置

### Twilio — 自有号码、短信/MMS、直接通话、接收短信轮询

注册地址：
- https://www.twilio.com/try-twilio

随后将凭证保存至Hermes中：

```bash
python3 "$SCRIPT" save-twilio ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_auth_token_here
```

搜索可用的号码：

```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 5
```

购买并记住一个号码：

```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

列出已拥有的号码：

```bash
python3 "$SCRIPT" twilio-owned
```

稍后可将其中之一设置为默认值：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# or
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

### Bland.ai — 最简单的智能外呼工具

注册地址：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

### Vapi — 更出色的对话语音质量

注册地址：
- https://dashboard.vapi.ai

请先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将您拥有的 Twilio 号码导入 Vapi，并保存返回的电话号码标识符：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果您已经知道 Vapi 电话号码的 ID，可直接将其保存：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

## 诊断当前状态

随时查看该智能体已掌握的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，请首先使用此方法。

## 常见工作流程

### A. 购买代理号码并持续使用

1. 保存 Twilio 凭证：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买后将其保存至 `~/.hermes/.env` 文件中，并设置对应状态：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 在下一次会话中，运行如下命令：
```bash
python3 "$SCRIPT" diagnose
```
此处显示了已保存的默认号码以及收件箱检查点状态。

### B. 从智能体号码发送短信

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Your deployment completed successfully."
```

支持媒体文件：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Here is the chart." --media-url "https://example.com/chart.png"
```

### C. 无 Webhook 服务器时，后续手动查看接收到的短信

轮询默认的 Twilio 号码的收件箱以获取消息：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示在上一个检查点之后收到的消息，阅读完毕后即可将检查点向前推进：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这正是针对“如何在技能再次加载时获取该号码接收到的消息？”这一问题的核心解答。

### D. 使用内置文本转语音功能直接发起 Twilio 呼叫

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "Hello! This is Hermes calling with your status update." --voice Polly.Joanna
```

### E. 使用预录或自定义语音消息发起通话

这是复用 Hermes 现有 `text_to_speech` 功能的主要途径。

适用于以下情况：
- 您希望通话使用 Hermes 配置好的文本转语音，而非 Twilio 的 `<Say>` 功能
- 您需要单向语音传达信息（如简报、提醒、笑话、通知或状态更新）
- 您不需要实时对话式电话通话

请先单独生成或托管音频文件，然后：

```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS -> Twilio Play 工作流程如下：

1. 使用 Hermes 的 `text_to_speech` 功能生成音频文件。
2. 将生成的 MP3 文件设置为可公开访问。
3. 通过 `--audio-url` 参数发起 Twilio 通话。

示例智能体处理流程：
- 使用 `text_to_speech` 请求 Hermes 生成语音消息。
- 如有需要，可通过临时静态主机、隧道或对象存储 URL 公开该文件。
- 使用 `twilio-call --audio-url ...` 将音频通过电话传输给对方。

适合存储 MP3 文件的方案包括：
- 临时的公共对象/存储 URL
- 连接到本地静态文件服务器的短生命周期隧道
- 电话服务提供商可直接获取的任何现有 HTTPS URL

重要提示：
- Hermes TTS 非常适用于预录的外呼消息。
- 对于**实时对话式 AI 通话**，Bland/Vapi 是更佳选择，因为它们能够自行处理实时的电话音频处理流程。
- 本方案并未将 Hermes 的 STT/TTS 功能作为完整的双工电话通话引擎使用；若要实现该功能，需要比当前方案更为复杂的流媒体/ webhook 集成。

### F. 使用 Twilio 直接通话功能导航电话树/IVR 系统

如果需要在通话建立后输入数字，可使用 `--send-digits` 参数。
Twilio 会将参数 `w` 解释为短暂等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "Connecting to billing now." --send-digits "ww1w2w3"
```

该功能有助于在将通话转接给人工客服或发送简短状态信息之前，先进入特定的菜单分支。 

### G. 使用 Bland.ai 进行外呼智能电话通话

```bash
python3 "$SCRIPT" ai-call "+15551230000" "Call the dental office, ask for a cleaning appointment on Tuesday afternoon, and if they do not have Tuesday availability, ask for Wednesday or Thursday instead." --provider bland --voice mason --max-duration 3
```

查看状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

完成后可提出与Bland分析相关的问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "Was the appointment confirmed?,What date and time?,Any special instructions?"
```

### H. 使用 Vapi 从您自己的号码发起 AI 外呼电话

1. 将您的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2. 发起通话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "You are calling to make a dinner reservation for two at 7:30 PM. If that is unavailable, ask for the nearest time between 6:30 and 8:30 PM." --provider vapi --max-duration 4
```

3. 查看结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

## 建议的智能体操作流程

当用户请求拨打电话或发送短信时：

1. 通过决策树确定适合该请求的处理路径。
2. 若配置状态不明确，则运行 `diagnose` 命令进行诊断。
3. 收集完整的任务详情。
4. 在拨打电话或发送短信前向用户确认。
5. 使用正确的命令执行操作。
6. 如有需要，轮询查询操作结果。
7. 概述操作结果，同时避免将第三方电话号码存储在 Hermes 内存中。

## 该功能目前尚不支持的功能

- 实时接听来电
- 基于 webhook 的实时短信推送至智能体处理流程
- 对任意第三方双重验证服务提供商的全面支持

这些功能需要比普通可选技能更复杂的基础设施。

## 常见问题与注意事项

- Twilio 的试用账户及地区限制可能会影响可拨打/发送短信的对象。
- 部分服务不接受使用 VoIP 号码进行双重验证。
- `twilio-inbox` 功能是通过轮询 REST API 获取信息的，而非即时推送。
- Vapi 的外呼功能仍依赖于已正确导入的有效号码。
- Bland.ai 提供的语音效果最为简单，但未必是最佳音质。
- 请勿将任意第三方电话号码存储在 Hermes 内存中。

## 验证清单

完成设置后，仅使用该功能即可实现以下所有操作：

1. 通过 `diagnose` 命令查看服务提供商的可用状态及已保存的配置信息。
2. 搜索并购买 Twilio 号码。
3. 将该号码保存至 `~/.hermes/.env` 文件中。
4. 使用该号码发送短信。
5. 后续轮询查询该号码接收到的短信。
6. 直接使用 Twilio 进行通话。
7. 通过 Bland.ai 或 Vapi 发起人工智能语音通话。

## 参考资料

- Twilio 电话号码相关文档：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息服务相关文档：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音服务相关文档：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai 网站：https://app.bland.ai/
